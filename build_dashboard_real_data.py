from __future__ import annotations

import json
import shutil
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "AquaTwin-Alicante" / "Datasets"
OUTPUT_DIR = Path(__file__).resolve().parent / "dashboard_data_real"


def ensure_dirs() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def norm_series(s: pd.Series) -> pd.Series:
    if s.max() == s.min():
        return pd.Series(np.zeros(len(s)), index=s.index)
    return (s - s.min()) / (s.max() - s.min())


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df_real = pd.read_csv(DATA_DIR / "dataset_definitivo.csv")
    df_comp = pd.read_csv(DATA_DIR / "dataset_completo_v2_72meses.csv")
    pred = pd.read_csv(DATA_DIR / "stgcn_v2_predictions.csv")
    centroids = pd.read_csv(DATA_DIR / "centroids.csv")
    adjacency = pd.read_csv(DATA_DIR / "adjacency_matrix.csv", index_col=0)

    df_real["fecha"] = pd.to_datetime(df_real["fecha"], format="mixed")
    df_comp["fecha"] = pd.to_datetime(df_comp["fecha"], format="mixed")
    pred["fecha"] = pd.to_datetime(pred[["year", "month"]].assign(day=1))
    centroids["barrio"] = centroids["barrio"].astype(str).str.strip()
    adjacency.index = adjacency.index.astype(str).str.strip()
    adjacency.columns = adjacency.columns.astype(str).str.strip()
    return df_real, df_comp, pred, centroids, adjacency


def build_kpis(df_real: pd.DataFrame) -> dict:
    latest_date = df_real["fecha"].max()
    latest = df_real[df_real["fecha"] == latest_date].copy()
    previous = df_real[df_real["fecha"] == (latest_date - pd.offsets.MonthEnd(1))].copy()

    critical = int(latest["anomalia_yoy"].sum())
    warnings = int(((latest["yoy_ratio"].fillna(1).sub(1).abs() > 0.20) & (latest["anomalia_yoy"] == 0)).sum())
    active_nodes = int(latest["barrio_geo"].nunique())
    latest_total = float(latest["consumo_m3_total"].sum())
    previous_total = float(previous["consumo_m3_total"].sum()) if len(previous) else latest_total
    delta_pct = ((latest_total - previous_total) / previous_total * 100) if previous_total else 0.0

    return {
        "date": latest_date.strftime("%Y-%m-%d"),
        "critical_alerts": critical,
        "warnings": warnings,
        "active_nodes": active_nodes,
        "total_consumption_m3": round(latest_total, 2),
        "avg_per_capita_m3": round(float(latest["consumo_m3_per_capita"].mean()), 3),
        "tourism_pernoctaciones": round(float(latest["pernoctaciones"].mean()), 0),
        "delta_consumption_pct": round(delta_pct, 2),
    }


def build_map(df_real: pd.DataFrame, pred: pd.DataFrame, centroids: pd.DataFrame) -> list[dict]:
    latest_date = df_real["fecha"].max()
    latest = df_real[df_real["fecha"] == latest_date].copy()
    latest["barrio_geo"] = latest["barrio_geo"].astype(str).str.strip()

    pred_latest = pred[(pred["year"] == 2024) & (pred["month"] == 12)].copy()
    pred_latest["barrio_geo"] = pred_latest["barrio_geo"].astype(str).str.strip()

    latest = latest.merge(centroids, left_on="barrio_geo", right_on="barrio", how="left")
    latest = latest.merge(
        pred_latest[["barrio_geo", "pred_m3_hab", "true_m3_hab", "rmse_barrio"]],
        on="barrio_geo",
        how="left",
    )

    latest["risk_raw"] = (
        0.40 * norm_series(latest["consumo_m3_per_capita"])
        + 0.30 * norm_series(latest["yoy_ratio"].fillna(1).sub(1).abs())
        + 0.20 * latest["anomalia_yoy"].fillna(0)
        + 0.10 * norm_series(latest["rmse_barrio"].fillna(latest["rmse_barrio"].median()))
    )
    latest["risk_score"] = latest["risk_raw"].clip(0, 1)
    latest["risk_level"] = pd.cut(
        latest["risk_score"],
        bins=[-0.001, 0.35, 0.65, 1.0],
        labels=["bajo", "medio", "alto"],
    ).astype(str)
    latest["breakdown_probability"] = (
        0.04
        + 0.40 * latest["risk_score"]
        + 0.10 * norm_series(latest["temp_media_c"])
        + 0.05 * norm_series(latest["precip_mm"])
    ).clip(0, 0.95)
    latest["total_alerts"] = (
        latest["anomalia_yoy"].fillna(0).astype(int)
        + (latest["breakdown_probability"] > 0.45).astype(int)
        + (latest["yoy_ratio"].fillna(1).sub(1).abs() > 0.20).astype(int)
    )

    records = []
    for row in latest.sort_values(["risk_score", "consumo_m3_per_capita"], ascending=[False, False]).itertuples():
        records.append(
            {
                "barrio": row.barrio_geo,
                "lat": round(float(row.lat), 6) if pd.notna(row.lat) else None,
                "lon": round(float(row.lon), 6) if pd.notna(row.lon) else None,
                "consumo_m3_per_capita": round(float(row.consumo_m3_per_capita), 4),
                "consumo_m3_total": round(float(row.consumo_m3_total), 2),
                "n_contratos_total": int(row.n_contratos_total),
                "temp_media_c": round(float(row.temp_media_c), 2),
                "precip_mm": round(float(row.precip_mm), 2),
                "yoy_ratio": round(float(row.yoy_ratio), 3) if pd.notna(row.yoy_ratio) else None,
                "anomalia_yoy": int(row.anomalia_yoy),
                "risk_score": round(float(row.risk_score), 4),
                "risk_level": row.risk_level,
                "total_alerts": int(row.total_alerts),
                "breakdown_probability": round(float(row.breakdown_probability), 4),
                "pred_m3_hab": round(float(row.pred_m3_hab), 4) if pd.notna(row.pred_m3_hab) else None,
                "true_m3_hab": round(float(row.true_m3_hab), 4) if pd.notna(row.true_m3_hab) else None,
                "rmse_barrio": round(float(row.rmse_barrio), 4) if pd.notna(row.rmse_barrio) else None,
            }
        )
    return records


def build_prediction(df_real: pd.DataFrame, pred: pd.DataFrame) -> dict:
    monthly_real = (
        df_real.groupby(["year", "month"], as_index=False)
        .agg(
            historical_consumption_m3=("consumo_m3_total", "sum"),
            avg_risk_proxy=("yoy_ratio", lambda s: float(np.nanmean(np.abs(s.fillna(1) - 1)))),
            anomalies_count=("anomalia_yoy", "sum"),
        )
        .sort_values(["year", "month"])
    )

    pred_join = pred.merge(
        df_real[["year", "month", "barrio_geo", "poblacion_estimada"]].drop_duplicates(),
        on=["year", "month", "barrio_geo"],
        how="left",
    )
    pred_join["pred_total_proxy"] = pred_join["pred_m3_hab"] * pred_join["poblacion_estimada"]
    pred_join["rmse_total_proxy"] = pred_join["rmse_barrio"] * pred_join["poblacion_estimada"]
    monthly_pred = (
        pred_join.groupby(["year", "month"], as_index=False)
        .agg(
            forecast_consumption_m3=("pred_total_proxy", "sum"),
            forecast_band=("rmse_total_proxy", "sum"),
        )
        .sort_values(["year", "month"])
    )

    merged = monthly_real.merge(monthly_pred, on=["year", "month"], how="left")
    labels = [f"{int(r.year)}-{int(r.month):02d}" for r in merged.itertuples()]

    forecast = []
    forecast_min = []
    forecast_max = []
    for row in merged.itertuples():
        if pd.isna(row.forecast_consumption_m3):
            forecast.append(None)
            forecast_min.append(None)
            forecast_max.append(None)
        else:
            f = float(row.forecast_consumption_m3)
            band = float(row.forecast_band) if pd.notna(row.forecast_band) else 0.0
            forecast.append(round(f, 2))
            forecast_min.append(round(max(f - band, 0), 2))
            forecast_max.append(round(f + band, 2))

    return {
        "labels": labels,
        "historical_consumption_m3": [round(float(v), 2) for v in merged["historical_consumption_m3"]],
        "forecast_consumption_m3": forecast,
        "forecast_min_m3": forecast_min,
        "forecast_max_m3": forecast_max,
        "avg_risk_score": [round(float(v), 4) for v in merged["avg_risk_proxy"].fillna(0)],
        "breakdowns": [int(v) for v in merged["anomalies_count"].fillna(0)],
    }


def build_alerts(map_records: list[dict]) -> list[dict]:
    alerts = []
    for rec in map_records[:8]:
        if rec["anomalia_yoy"]:
            title = "Anomalía interanual detectada"
            desc = f'{rec["barrio"]} · YoY {rec["yoy_ratio"]:.2f} · consumo {rec["consumo_m3_per_capita"]:.2f} m³/hab'
            level = "danger"
        elif rec["risk_level"] == "alto":
            title = "Riesgo elevado de demanda"
            desc = f'{rec["barrio"]} · score {rec["risk_score"]:.2f} · prob. avería {rec["breakdown_probability"]:.0%}'
            level = "danger"
        elif rec["risk_level"] == "medio":
            title = "Barrio en observación"
            desc = f'{rec["barrio"]} · consumo {rec["consumo_m3_total"]:.0f} m³ · temperatura {rec["temp_media_c"]:.1f} °C'
            level = "warn"
        else:
            title = "Zona estable"
            desc = f'{rec["barrio"]} · comportamiento dentro de rango'
            level = "ok"
        alerts.append({"level": level, "title": title, "description": desc})
    return alerts


def build_seasonality(df_real: pd.DataFrame) -> list[dict]:
    monthly = df_real.groupby("month", as_index=False).agg(
        consumo_m3_per_capita=("consumo_m3_per_capita", "mean"),
        temp_media_c=("temp_media_c", "mean"),
        precip_mm=("precip_mm", "mean"),
        pernoctaciones=("pernoctaciones", "mean"),
    )
    monthly["season_index"] = monthly["consumo_m3_per_capita"] / monthly["consumo_m3_per_capita"].mean() * 100
    return monthly.to_dict(orient="records")


def build_graph_overlay(
    adjacency: pd.DataFrame, centroids: pd.DataFrame, map_records: list[dict]
) -> dict:
    risk_lookup = {rec["barrio"]: rec["risk_score"] for rec in map_records}
    cent = centroids.copy().dropna(subset=["lat", "lon"]).drop_duplicates(subset="barrio", keep="first")
    cent["barrio"] = cent["barrio"].astype(str).str.strip()
    cent = cent.set_index("barrio")

    common = [b for b in adjacency.index if b in cent.index]
    adj = adjacency.reindex(index=common, columns=common).fillna(0)

    nodes = []
    for barrio in common:
        nodes.append(
            {
                "barrio": barrio,
                "lat": round(float(cent.at[barrio, "lat"]), 6),
                "lon": round(float(cent.at[barrio, "lon"]), 6),
                "degree": int(adj.loc[barrio].sum()),
                "risk_score": round(float(risk_lookup.get(barrio, 0.0)), 4),
            }
        )

    edges = []
    for i, b1 in enumerate(common):
        for j, b2 in enumerate(common):
            if j <= i:
                continue
            if int(adj.iat[i, j]) == 1:
                edges.append(
                    {
                        "source": b1,
                        "target": b2,
                        "source_lat": round(float(cent.at[b1, "lat"]), 6),
                        "source_lon": round(float(cent.at[b1, "lon"]), 6),
                        "target_lat": round(float(cent.at[b2, "lat"]), 6),
                        "target_lon": round(float(cent.at[b2, "lon"]), 6),
                    }
                )
    return {"nodes": nodes, "edges": edges}


def main() -> None:
    ensure_dirs()
    df_real, df_comp, pred, centroids, adjacency = load_data()
    kpis = build_kpis(df_real)
    map_records = build_map(df_real, pred, centroids)
    prediction = build_prediction(df_real, pred)
    alerts = build_alerts(map_records)
    seasonality = build_seasonality(df_real)
    graph_overlay = build_graph_overlay(adjacency, centroids, map_records)

    (OUTPUT_DIR / "dashboard_kpis.json").write_text(json.dumps(kpis, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUTPUT_DIR / "dashboard_map.json").write_text(json.dumps(map_records, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUTPUT_DIR / "dashboard_prediction.json").write_text(json.dumps(prediction, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUTPUT_DIR / "dashboard_alerts.json").write_text(json.dumps(alerts, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUTPUT_DIR / "dashboard_seasonality.json").write_text(json.dumps(seasonality, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUTPUT_DIR / "dashboard_graph.json").write_text(json.dumps(graph_overlay, indent=2, ensure_ascii=False), encoding="utf-8")
    shutil.copy2(DATA_DIR / "barrios_Alicante.geojson", OUTPUT_DIR / "barrios_Alicante.geojson")

    meta = {
        "source_files": [
            "dataset_definitivo.csv",
            "dataset_completo_v2_72meses.csv",
            "stgcn_v2_predictions.csv",
            "centroids.csv",
            "adjacency_matrix.csv",
        ],
        "real_period": {
            "from": str(df_real["fecha"].min().date()),
            "to": str(df_real["fecha"].max().date()),
        },
        "n_barrios": int(df_real["barrio_geo"].nunique()),
        "prediction_period": "2024-01 to 2024-12",
    }
    (OUTPUT_DIR / "README.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
