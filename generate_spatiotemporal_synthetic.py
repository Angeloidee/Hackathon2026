from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "synthetic_outputs" / "stgcn_ready"
PREPARED_PATH = BASE_DIR / "synthetic_outputs" / "prepared_training_data.csv"

SEED = 42


@dataclass(frozen=True)
class Barrio:
    name: str
    lat: float
    lon: float
    population_factor: float
    tourism_factor: float
    infrastructure_age: int
    base_pressure: float
    coastal: int


BARRIOS = [
    Barrio("CENTRO", 38.3453, -0.4831, 1.10, 0.55, 52, 4.3, 0),
    Barrio("BENALUA", 38.3388, -0.4905, 0.92, 0.20, 45, 4.0, 0),
    Barrio("CAROLINAS BAJAS", 38.3568, -0.4870, 0.95, 0.18, 61, 3.2, 0),
    Barrio("CAROLINAS ALTAS", 38.3604, -0.4895, 0.88, 0.15, 38, 3.8, 0),
    Barrio("ALTOZANO", 38.3590, -0.5013, 0.84, 0.10, 33, 4.1, 0),
    Barrio("VISTAHERMOSA", 38.3692, -0.4598, 0.70, 0.22, 18, 4.6, 0),
    Barrio("PLAYA SAN JUAN", 38.3782, -0.4066, 1.22, 1.00, 25, 4.1, 1),
    Barrio("GARBINET", 38.3620, -0.4785, 0.75, 0.10, 22, 4.4, 0),
    Barrio("SAN BLAS", 38.3470, -0.5020, 0.89, 0.12, 41, 3.9, 0),
]


MONTH_INDEX = {
    1: 72,
    2: 75,
    3: 82,
    4: 90,
    5: 105,
    6: 125,
    7: 168,
    8: 162,
    9: 118,
    10: 95,
    11: 80,
    12: 78,
}


def rng(seed: int = SEED) -> np.random.Generator:
    return np.random.default_rng(seed)


def ensure_dirs() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_month_profile() -> pd.DataFrame:
    if not PREPARED_PATH.exists():
        raise FileNotFoundError(
            f"No existe {PREPARED_PATH}. Ejecuta antes synthetic_cvae_pipeline.py prepare."
        )
    df = pd.read_csv(PREPARED_PATH)
    month_profile = (
        df.groupby("month", as_index=False)
        .agg(
            month_mean_m3=("m3_to_bill", "mean"),
            month_zero_share=("is_zero", "mean"),
            month_avg_days=("days_reading", "mean"),
            month_registered_m3=("registered_m3", "mean"),
        )
        .sort_values("month")
    )
    month_profile["month_season_index"] = month_profile["month"].map(MONTH_INDEX)
    month_profile["normalized_consumption"] = month_profile["month_mean_m3"] / month_profile["month_mean_m3"].mean()
    return month_profile


def pairwise_distance_matrix(barrios: list[Barrio]) -> np.ndarray:
    coords = np.array([[b.lat, b.lon] for b in barrios], dtype=np.float64)
    diff = coords[:, None, :] - coords[None, :, :]
    return np.sqrt((diff**2).sum(axis=2))


def build_graph(barrios: list[Barrio], k: int = 3) -> tuple[pd.DataFrame, pd.DataFrame]:
    dist = pairwise_distance_matrix(barrios)
    names = [b.name for b in barrios]
    adjacency = np.zeros_like(dist, dtype=np.int32)

    for i in range(len(barrios)):
        nearest = np.argsort(dist[i])[1 : k + 1]
        adjacency[i, nearest] = 1
    adjacency = np.maximum(adjacency, adjacency.T)

    edges = []
    for i in range(len(barrios)):
        for j in range(len(barrios)):
            if i == j:
                continue
            if adjacency[i, j]:
                weight = float(np.exp(-dist[i, j] * 40))
                edges.append([names[i], names[j], round(weight, 6)])

    adjacency_df = pd.DataFrame(adjacency, index=names, columns=names)
    edges_df = pd.DataFrame(edges, columns=["source", "target", "weight"])
    return adjacency_df, edges_df


def synthesize_timeseries(start: str = "2022-01-01", end: str = "2025-12-31", seed: int = SEED) -> pd.DataFrame:
    month_profile = load_month_profile()
    month_lookup = month_profile.set_index("month").to_dict(orient="index")
    calendar = pd.date_range(start=start, end=end, freq="D")
    random = rng(seed)

    rows = []
    for barrio in BARRIOS:
        latent_wear = barrio.infrastructure_age / 70.0
        coastal_bonus = 0.15 if barrio.coastal else 0.0
        for date in calendar:
            m = int(date.month)
            weekday = int(date.weekday())
            is_weekend = int(weekday >= 5)
            month_info = month_lookup[m]

            season_factor = float(month_info["normalized_consumption"])
            temp_c = (
                17
                + 8 * np.sin(2 * np.pi * (m - 1) / 12 - 0.8)
                + random.normal(0, 1.5)
                + 1.5 * barrio.coastal
            )
            rainfall_mm = max(
                0.0,
                18
                + 12 * np.cos(2 * np.pi * (m - 1) / 12)
                + random.normal(0, 9)
                - 4 * barrio.coastal,
            )
            holiday_pressure = 1.10 if (m in (7, 8) and barrio.coastal) else 1.0
            weekend_effect = 1.06 if is_weekend else 1.0
            tourism_multiplier = 1 + barrio.tourism_factor * (month_info["month_season_index"] - 100) / 220
            demand_noise = random.normal(0, 0.06)

            daily_consumption = (
                540
                * barrio.population_factor
                * season_factor
                * holiday_pressure
                * weekend_effect
                * tourism_multiplier
                * (1 + demand_noise)
            )
            daily_consumption = max(50.0, daily_consumption)

            flow_m3h = daily_consumption / 24.0 * (1.0 + random.normal(0, 0.05))
            pressure_drop = 0.18 * (daily_consumption / 700.0) + 0.03 * latent_wear * 10
            pressure_bar = barrio.base_pressure - pressure_drop + random.normal(0, 0.12)
            pressure_bar = float(np.clip(pressure_bar, 1.0, 8.5))

            anomaly_score = (
                0.28 * latent_wear
                + 0.18 * max(0, (temp_c - 27) / 10)
                + 0.15 * holiday_pressure
                + 0.14 * max(0, 3.0 - pressure_bar)
                + 0.12 * (flow_m3h / 35.0)
                + coastal_bonus
                + random.normal(0, 0.05)
            )
            risk_score = float(np.clip(anomaly_score, 0.0, 1.0))
            breakdown_prob = float(
                np.clip(
                    0.01
                    + 0.08 * latent_wear
                    + 0.10 * max(0, risk_score - 0.55)
                    + 0.03 * max(0, rainfall_mm - 20) / 25,
                    0.0,
                    0.55,
                )
            )
            breakdown_event = int(random.random() < breakdown_prob)

            pressure_alert = int(pressure_bar < 2.5 or pressure_bar > 7.0)
            flow_alert = int(flow_m3h < 12 or flow_m3h > 38)
            anomaly_alert = int(risk_score > 0.72)
            total_alerts = int(pressure_alert + flow_alert + anomaly_alert + breakdown_event)

            rows.append(
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "year": int(date.year),
                    "month": m,
                    "day": int(date.day),
                    "weekday": weekday,
                    "is_weekend": is_weekend,
                    "barrio": barrio.name,
                    "lat": barrio.lat,
                    "lon": barrio.lon,
                    "population_factor": barrio.population_factor,
                    "tourism_factor": barrio.tourism_factor,
                    "infrastructure_age": barrio.infrastructure_age,
                    "coastal": barrio.coastal,
                    "season_index": month_info["month_season_index"],
                    "temperature_c": round(float(temp_c), 3),
                    "rainfall_mm": round(float(rainfall_mm), 3),
                    "consumption_m3_day": round(float(daily_consumption), 3),
                    "flow_m3h": round(float(flow_m3h), 3),
                    "pressure_bar": round(float(pressure_bar), 3),
                    "risk_score": round(risk_score, 4),
                    "breakdown_probability": round(breakdown_prob, 4),
                    "breakdown_event": breakdown_event,
                    "pressure_alert": pressure_alert,
                    "flow_alert": flow_alert,
                    "anomaly_alert": anomaly_alert,
                    "total_alerts": total_alerts,
                }
            )

    df = pd.DataFrame(rows)
    df["risk_level"] = pd.cut(
        df["risk_score"],
        bins=[-0.001, 0.40, 0.70, 1.0],
        labels=["bajo", "medio", "alto"],
    ).astype(str)
    return df


def build_dashboard_exports(df: pd.DataFrame) -> tuple[dict, list[dict], dict]:
    latest_date = df["date"].max()
    latest = df[df["date"] == latest_date].copy()

    kpis = {
        "date": latest_date,
        "critical_alerts": int((latest["risk_level"] == "alto").sum()),
        "warnings": int((latest["risk_level"] == "medio").sum()),
        "active_nodes": int(latest["barrio"].nunique()),
        "mean_pressure_bar": round(float(latest["pressure_bar"].mean()), 2),
        "network_flow_m3h": round(float(latest["flow_m3h"].sum()), 2),
    }

    map_records = (
        latest[
            [
                "barrio",
                "lat",
                "lon",
                "pressure_bar",
                "flow_m3h",
                "infrastructure_age",
                "risk_score",
                "risk_level",
                "total_alerts",
                "breakdown_probability",
            ]
        ]
        .sort_values("risk_score", ascending=False)
        .to_dict(orient="records")
    )

    monthly = (
        df.groupby(["year", "month"], as_index=False)
        .agg(
            total_consumption_m3=("consumption_m3_day", "sum"),
            avg_risk_score=("risk_score", "mean"),
            total_breakdowns=("breakdown_event", "sum"),
        )
        .sort_values(["year", "month"])
    )
    prediction_payload = {
        "labels": [f"{int(r.year)}-{int(r.month):02d}" for r in monthly.itertuples()],
        "historical_consumption_m3": [round(float(v), 2) for v in monthly["total_consumption_m3"]],
        "avg_risk_score": [round(float(v), 4) for v in monthly["avg_risk_score"]],
        "breakdowns": [int(v) for v in monthly["total_breakdowns"]],
    }
    return kpis, map_records, prediction_payload


def main() -> None:
    ensure_dirs()
    df = synthesize_timeseries()
    adjacency_df, edges_df = build_graph(BARRIOS, k=3)
    kpis, map_records, prediction_payload = build_dashboard_exports(df)

    df.to_csv(OUTPUT_DIR / "synthetic_spatiotemporal_daily.csv", index=False, encoding="utf-8")
    adjacency_df.to_csv(OUTPUT_DIR / "adjacency_matrix.csv", encoding="utf-8")
    edges_df.to_csv(OUTPUT_DIR / "edge_list.csv", index=False, encoding="utf-8")
    (OUTPUT_DIR / "dashboard_kpis.json").write_text(json.dumps(kpis, indent=2), encoding="utf-8")
    (OUTPUT_DIR / "dashboard_map.json").write_text(json.dumps(map_records, indent=2), encoding="utf-8")
    (OUTPUT_DIR / "dashboard_prediction.json").write_text(json.dumps(prediction_payload, indent=2), encoding="utf-8")

    metadata = {
        "rows": int(len(df)),
        "date_min": str(df["date"].min()),
        "date_max": str(df["date"].max()),
        "num_barrios": len(BARRIOS),
        "columns": df.columns.tolist(),
        "targets_for_stgcn": ["consumption_m3_day", "breakdown_probability", "flow_m3h", "pressure_bar", "risk_score"],
        "node_column": "barrio",
        "time_column": "date",
    }
    (OUTPUT_DIR / "README.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
