from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "reales"
OUTPUT_DIR = BASE_DIR / "synthetic_outputs"
MODEL_DIR = OUTPUT_DIR / "model"

SEED = 42


def set_seed(seed: int = SEED) -> np.random.Generator:
    return np.random.default_rng(seed)


def ensure_dirs() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)


def load_sources() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    water = pd.read_csv(
        DATA_DIR / "amaem-pda-agua-registrada-trimestral-explotacion-solo-alicante-amaem-pda-agua-registrada-trimest.csv",
        encoding="utf-8-sig",
    )
    water = water.rename(
        columns={
            "AÑO": "year",
            "TRIMESTRE": "quarter",
            "Explotación": "explotacion",
            "TOTAL Volumen agua potable registrada (m³)": "registered_m3",
        }
    )

    network = pd.read_csv(
        DATA_DIR / "amaem-pda-longitud-red-abastecimiento-explotacion-solo-alicante-amaem-pda-longitud-red-abastecim.csv",
        encoding="utf-8-sig",
    )
    network = network.rename(
        columns={
            "AÑO": "year",
            "EXPLOTACION": "explotacion",
            "LONGITUD RED ABASTECIMIENTO (km)": "network_km",
            "LONGITUD RED ABASTECIMIENTO INSPECCIONADA BUSCAFUGAS (km)": "inspected_km",
        }
    )
    for col in ["network_km", "inspected_km"]:
        network[col] = (
            network[col].astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False).astype(float)
        )
    network["inspected_ratio"] = network["inspected_km"] / network["network_km"]

    billing = pd.read_csv(
        DATA_DIR / "m3-registrados_facturados-tll_2025-solo-alicante-m3-registrados_facturados-tll_2025-solo-alicant.csv",
        encoding="utf-8-sig",
    )
    billing["FECHA FACTURA"] = pd.to_datetime(billing["FECHA FACTURA"], dayfirst=True)
    billing["FECHA LECTURA"] = pd.to_datetime(billing["FECHA LECTURA"], dayfirst=True)
    billing["FECHA PREVISTA LECTURA"] = pd.to_datetime(billing["FECHA PREVISTA LECTURA"], dayfirst=True)
    return water, network, billing


def build_training_frame(max_rows: int | None = 50000, seed: int = SEED) -> pd.DataFrame:
    water, network, billing = load_sources()

    df = billing.copy()
    df["periodicity"] = df["PERIODICIDAD"].fillna("DESCONOCIDA").astype(str).str.upper()
    df["year"] = df["FECHA FACTURA"].dt.year
    df["month"] = df["FECHA FACTURA"].dt.month
    df["quarter"] = df["FECHA FACTURA"].dt.quarter
    df["invoice_day"] = df["FECHA FACTURA"].dt.day
    df["reading_day"] = df["FECHA LECTURA"].dt.day
    df["planned_day"] = df["FECHA PREVISTA LECTURA"].dt.day
    df["planned_gap_days"] = (df["FECHA PREVISTA LECTURA"] - df["FECHA LECTURA"]).dt.days
    df["m3_to_bill"] = df["M3 A FACTURAR"].astype(float)
    df["is_zero"] = (df["m3_to_bill"] == 0).astype(int)
    df["log_m3"] = np.log1p(df["m3_to_bill"])
    df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12.0)
    df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12.0)

    quarter_stats = (
        df.groupby(["year", "quarter"], as_index=False)
        .agg(
            period_billed_m3=("m3_to_bill", "sum"),
            period_mean_m3=("m3_to_bill", "mean"),
            period_zero_share=("is_zero", "mean"),
            period_records=("m3_to_bill", "size"),
            period_monthly_share=("periodicity", lambda s: float((s == "MENSUAL").mean())),
        )
    )

    month_stats = (
        df.groupby(["year", "month"], as_index=False)
        .agg(
            month_billed_m3=("m3_to_bill", "sum"),
            month_mean_m3=("m3_to_bill", "mean"),
            month_zero_share=("is_zero", "mean"),
            month_records=("m3_to_bill", "size"),
        )
    )

    df = df.merge(water[["year", "quarter", "registered_m3"]], on=["year", "quarter"], how="left")
    df = df.merge(network[["year", "network_km", "inspected_km", "inspected_ratio"]], on="year", how="left")
    df = df.merge(quarter_stats, on=["year", "quarter"], how="left")
    df = df.merge(month_stats, on=["year", "month"], how="left")

    df["registered_to_network"] = df["registered_m3"] / df["network_km"]
    df["registered_to_inspected"] = df["registered_m3"] / df["inspected_km"]

    selected = df[
        [
            "year",
            "month",
            "quarter",
            "periodicity",
            "invoice_day",
            "reading_day",
            "planned_day",
            "DIAS LECTURA",
            "planned_gap_days",
            "m3_to_bill",
            "log_m3",
            "is_zero",
            "registered_m3",
            "network_km",
            "inspected_km",
            "inspected_ratio",
            "registered_to_network",
            "registered_to_inspected",
            "period_billed_m3",
            "period_mean_m3",
            "period_zero_share",
            "period_records",
            "period_monthly_share",
            "month_billed_m3",
            "month_mean_m3",
            "month_zero_share",
            "month_records",
            "month_sin",
            "month_cos",
        ]
    ].rename(columns={"DIAS LECTURA": "days_reading"})

    if max_rows is not None and len(selected) > max_rows:
        rng = set_seed(seed)
        groups = selected.groupby(["quarter", "periodicity"], group_keys=False)
        sampled_parts = []
        target_rows = max_rows
        total_rows = len(selected)
        for _, group in groups:
            group_target = max(50, int(round(target_rows * len(group) / total_rows)))
            sampled_parts.append(group.sample(n=min(group_target, len(group)), random_state=int(rng.integers(0, 10_000))))
        selected = pd.concat(sampled_parts, ignore_index=True)
        if len(selected) > max_rows:
            selected = selected.sample(n=max_rows, random_state=seed).reset_index(drop=True)

    return selected.reset_index(drop=True)


def save_prepared_dataset(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8")


@dataclass
class FeatureBundle:
    x: np.ndarray
    c: np.ndarray
    df: pd.DataFrame
    target_numeric: list[str]
    cond_numeric: list[str]
    cond_categorical: list[str]
    target_means: dict[str, float]
    target_stds: dict[str, float]
    cond_means: dict[str, float]
    cond_stds: dict[str, float]
    cond_categories: dict[str, list[str]]


def prepare_feature_bundle(df: pd.DataFrame) -> FeatureBundle:
    target_numeric = ["log_m3", "days_reading", "planned_gap_days", "is_zero", "invoice_day", "reading_day", "planned_day"]
    cond_numeric = [
        "year",
        "month",
        "quarter",
        "registered_m3",
        "network_km",
        "inspected_km",
        "inspected_ratio",
        "registered_to_network",
        "registered_to_inspected",
        "period_billed_m3",
        "period_mean_m3",
        "period_zero_share",
        "period_records",
        "period_monthly_share",
        "month_billed_m3",
        "month_mean_m3",
        "month_zero_share",
        "month_records",
        "month_sin",
        "month_cos",
    ]
    cond_categorical = ["periodicity"]

    target_means = {col: float(df[col].mean()) for col in target_numeric}
    target_stds = {col: float(df[col].std(ddof=0) or 1.0) for col in target_numeric}
    cond_means = {col: float(df[col].mean()) for col in cond_numeric}
    cond_stds = {col: float(df[col].std(ddof=0) or 1.0) for col in cond_numeric}

    x_parts = [((df[col] - target_means[col]) / target_stds[col]).to_numpy(dtype=np.float32).reshape(-1, 1) for col in target_numeric]
    c_parts = [((df[col] - cond_means[col]) / cond_stds[col]).to_numpy(dtype=np.float32).reshape(-1, 1) for col in cond_numeric]

    cond_categories: dict[str, list[str]] = {}
    for col in cond_categorical:
        categories = sorted(df[col].astype(str).unique().tolist())
        cond_categories[col] = categories
        for category in categories:
            c_parts.append((df[col].astype(str) == category).to_numpy(dtype=np.float32).reshape(-1, 1))

    x = np.hstack(x_parts).astype(np.float32)
    c = np.hstack(c_parts).astype(np.float32)
    return FeatureBundle(
        x=x,
        c=c,
        df=df,
        target_numeric=target_numeric,
        cond_numeric=cond_numeric,
        cond_categorical=cond_categorical,
        target_means=target_means,
        target_stds=target_stds,
        cond_means=cond_means,
        cond_stds=cond_stds,
        cond_categories=cond_categories,
    )


class NumpyCVAE:
    def __init__(self, input_dim: int, cond_dim: int, hidden_dim: int = 64, latent_dim: int = 12, seed: int = SEED):
        rng = set_seed(seed)
        self.input_dim = input_dim
        self.cond_dim = cond_dim
        self.hidden_dim = hidden_dim
        self.latent_dim = latent_dim
        self.params = {
            "W1": rng.normal(0, 0.08, size=(input_dim + cond_dim, hidden_dim)).astype(np.float32),
            "b1": np.zeros(hidden_dim, dtype=np.float32),
            "W_mu": rng.normal(0, 0.08, size=(hidden_dim, latent_dim)).astype(np.float32),
            "b_mu": np.zeros(latent_dim, dtype=np.float32),
            "W_lv": rng.normal(0, 0.08, size=(hidden_dim, latent_dim)).astype(np.float32),
            "b_lv": np.zeros(latent_dim, dtype=np.float32),
            "W2": rng.normal(0, 0.08, size=(latent_dim + cond_dim, hidden_dim)).astype(np.float32),
            "b2": np.zeros(hidden_dim, dtype=np.float32),
            "W_out": rng.normal(0, 0.08, size=(hidden_dim, input_dim)).astype(np.float32),
            "b_out": np.zeros(input_dim, dtype=np.float32),
        }
        self.opt_m = {key: np.zeros_like(value) for key, value in self.params.items()}
        self.opt_v = {key: np.zeros_like(value) for key, value in self.params.items()}
        self.opt_t = 0

    @staticmethod
    def relu(x: np.ndarray) -> np.ndarray:
        return np.maximum(x, 0.0)

    @staticmethod
    def relu_grad(x: np.ndarray) -> np.ndarray:
        return (x > 0).astype(np.float32)

    def forward(self, x: np.ndarray, c: np.ndarray, rng: np.random.Generator) -> tuple[np.ndarray, dict[str, np.ndarray]]:
        xc = np.hstack([x, c])
        a1 = xc @ self.params["W1"] + self.params["b1"]
        h1 = self.relu(a1)
        mu = h1 @ self.params["W_mu"] + self.params["b_mu"]
        logvar = h1 @ self.params["W_lv"] + self.params["b_lv"]
        eps = rng.normal(size=mu.shape).astype(np.float32)
        std = np.exp(0.5 * logvar)
        z = mu + std * eps
        zc = np.hstack([z, c])
        a2 = zc @ self.params["W2"] + self.params["b2"]
        h2 = self.relu(a2)
        x_hat = h2 @ self.params["W_out"] + self.params["b_out"]
        cache = {
            "xc": xc,
            "a1": a1,
            "h1": h1,
            "mu": mu,
            "logvar": logvar,
            "eps": eps,
            "std": std,
            "z": z,
            "zc": zc,
            "a2": a2,
            "h2": h2,
            "x_hat": x_hat,
        }
        return x_hat, cache

    def loss_and_grads(
        self, x: np.ndarray, c: np.ndarray, beta: float, rng: np.random.Generator
    ) -> tuple[float, float, float, dict[str, np.ndarray]]:
        x_hat, cache = self.forward(x, c, rng)
        batch_size = x.shape[0]

        recon = np.mean(np.sum((x_hat - x) ** 2, axis=1))
        kl = 0.5 * np.mean(np.sum(np.exp(cache["logvar"]) + cache["mu"] ** 2 - 1.0 - cache["logvar"], axis=1))
        loss = recon + beta * kl

        dx_hat = (2.0 / batch_size) * (x_hat - x)
        grads: dict[str, np.ndarray] = {}

        grads["W_out"] = cache["h2"].T @ dx_hat
        grads["b_out"] = dx_hat.sum(axis=0)

        dh2 = dx_hat @ self.params["W_out"].T
        da2 = dh2 * self.relu_grad(cache["a2"])
        grads["W2"] = cache["zc"].T @ da2
        grads["b2"] = da2.sum(axis=0)

        dzc = da2 @ self.params["W2"].T
        dz = dzc[:, : self.latent_dim]

        dmu = dz + (beta / batch_size) * cache["mu"]
        dlogvar = dz * (0.5 * cache["std"] * cache["eps"]) + (beta / batch_size) * 0.5 * (np.exp(cache["logvar"]) - 1.0)

        grads["W_mu"] = cache["h1"].T @ dmu
        grads["b_mu"] = dmu.sum(axis=0)
        grads["W_lv"] = cache["h1"].T @ dlogvar
        grads["b_lv"] = dlogvar.sum(axis=0)

        dh1 = dmu @ self.params["W_mu"].T + dlogvar @ self.params["W_lv"].T
        da1 = dh1 * self.relu_grad(cache["a1"])

        grads["W1"] = cache["xc"].T @ da1
        grads["b1"] = da1.sum(axis=0)

        return float(loss), float(recon), float(kl), grads

    def update(self, grads: dict[str, np.ndarray], lr: float, beta1: float = 0.9, beta2: float = 0.999, eps: float = 1e-8) -> None:
        self.opt_t += 1
        for key, grad in grads.items():
            self.opt_m[key] = beta1 * self.opt_m[key] + (1.0 - beta1) * grad
            self.opt_v[key] = beta2 * self.opt_v[key] + (1.0 - beta2) * (grad ** 2)
            m_hat = self.opt_m[key] / (1.0 - beta1 ** self.opt_t)
            v_hat = self.opt_v[key] / (1.0 - beta2 ** self.opt_t)
            self.params[key] -= lr * m_hat / (np.sqrt(v_hat) + eps)

    def reconstruct(self, x: np.ndarray, c: np.ndarray) -> np.ndarray:
        rng = set_seed(SEED)
        x_hat, _ = self.forward(x, c, rng)
        return x_hat

    def sample(self, c: np.ndarray, rng: np.random.Generator) -> np.ndarray:
        z = rng.normal(size=(c.shape[0], self.latent_dim)).astype(np.float32)
        zc = np.hstack([z, c])
        a2 = zc @ self.params["W2"] + self.params["b2"]
        h2 = self.relu(a2)
        return h2 @ self.params["W_out"] + self.params["b_out"]


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def denormalize_targets(x_hat: np.ndarray, bundle: FeatureBundle) -> pd.DataFrame:
    data: dict[str, np.ndarray] = {}
    for idx, col in enumerate(bundle.target_numeric):
        values = x_hat[:, idx] * bundle.target_stds[col] + bundle.target_means[col]
        data[col] = values

    out = pd.DataFrame(data)
    out["log_m3"] = out["log_m3"].clip(lower=0)
    out["m3_to_bill"] = np.expm1(out["log_m3"]).clip(lower=0)
    out["days_reading"] = out["days_reading"].round().clip(lower=0)
    out["planned_gap_days"] = out["planned_gap_days"].round().clip(-31, 31)
    out["is_zero_score"] = out["is_zero"]
    out["invoice_day"] = out["invoice_day"].round().clip(1, 31).astype(int)
    out["reading_day"] = out["reading_day"].round().clip(1, 31).astype(int)
    out["planned_day"] = out["planned_day"].round().clip(1, 31).astype(int)
    return out


def condition_matrix_from_df(df: pd.DataFrame, bundle: FeatureBundle) -> np.ndarray:
    parts = [
        ((df[col] - bundle.cond_means[col]) / bundle.cond_stds[col]).to_numpy(dtype=np.float32).reshape(-1, 1)
        for col in bundle.cond_numeric
    ]
    for col in bundle.cond_categorical:
        categories = bundle.cond_categories[col]
        values = df[col].astype(str)
        for category in categories:
            parts.append((values == category).to_numpy(dtype=np.float32).reshape(-1, 1))
    return np.hstack(parts).astype(np.float32)


def save_bundle_metadata(bundle: FeatureBundle) -> None:
    metadata = {
        "target_numeric": bundle.target_numeric,
        "cond_numeric": bundle.cond_numeric,
        "cond_categorical": bundle.cond_categorical,
        "target_means": bundle.target_means,
        "target_stds": bundle.target_stds,
        "cond_means": bundle.cond_means,
        "cond_stds": bundle.cond_stds,
        "cond_categories": bundle.cond_categories,
    }
    (MODEL_DIR / "bundle_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")


def train_model(
    prepared_csv: Path,
    epochs: int = 35,
    batch_size: int = 256,
    lr: float = 0.0015,
    beta: float = 0.02,
    hidden_dim: int = 64,
    latent_dim: int = 12,
    seed: int = SEED,
) -> tuple[NumpyCVAE, FeatureBundle, list[dict[str, float]]]:
    df = pd.read_csv(prepared_csv)
    bundle = prepare_feature_bundle(df)
    save_bundle_metadata(bundle)

    model = NumpyCVAE(bundle.x.shape[1], bundle.c.shape[1], hidden_dim=hidden_dim, latent_dim=latent_dim, seed=seed)
    rng = set_seed(seed)
    history: list[dict[str, float]] = []

    for epoch in range(1, epochs + 1):
        perm = rng.permutation(len(bundle.x))
        x = bundle.x[perm]
        c = bundle.c[perm]
        batch_losses = []
        batch_recons = []
        batch_kls = []

        for start in range(0, len(x), batch_size):
            end = start + batch_size
            xb = x[start:end]
            cb = c[start:end]
            loss, recon, kl, grads = model.loss_and_grads(xb, cb, beta=beta, rng=rng)
            model.update(grads, lr=lr)
            batch_losses.append(loss)
            batch_recons.append(recon)
            batch_kls.append(kl)

        history.append(
            {
                "epoch": epoch,
                "loss": float(np.mean(batch_losses)),
                "recon": float(np.mean(batch_recons)),
                "kl": float(np.mean(batch_kls)),
            }
        )

    np.savez_compressed(MODEL_DIR / "weights.npz", **model.params)
    (MODEL_DIR / "train_history.json").write_text(json.dumps(history, indent=2), encoding="utf-8")
    return model, bundle, history


def generate_synthetic(
    model: NumpyCVAE,
    bundle: FeatureBundle,
    num_rows: int,
    seed: int = SEED,
    condition_source: str = "real_sample",
) -> pd.DataFrame:
    rng = set_seed(seed)
    if condition_source == "real_sample":
        cond_df = bundle.df.sample(n=num_rows, replace=True, random_state=seed).reset_index(drop=True)
    else:
        cond_df = bundle.df.head(num_rows).copy().reset_index(drop=True)

    c = condition_matrix_from_df(cond_df, bundle)
    x_hat = model.sample(c, rng)
    generated = denormalize_targets(x_hat, bundle)
    zero_prob = (
        0.75 * cond_df["period_zero_share"].to_numpy(dtype=np.float32)
        + 0.25 * cond_df["month_zero_share"].to_numpy(dtype=np.float32)
        + 0.05 * (sigmoid(generated["is_zero_score"].to_numpy(dtype=np.float32)) - 0.5)
    )
    generated["is_zero"] = (rng.random(num_rows) < np.clip(zero_prob, 0.001, 0.95)).astype(int)
    generated.loc[generated["is_zero"] == 1, "m3_to_bill"] = 0.0

    out = pd.DataFrame(
        {
            "year": cond_df["year"].to_numpy(),
            "month": cond_df["month"].to_numpy(),
            "quarter": cond_df["quarter"].to_numpy(),
            "periodicity": cond_df["periodicity"].to_numpy(),
            "registered_m3": cond_df["registered_m3"].to_numpy(),
            "network_km": cond_df["network_km"].to_numpy(),
            "inspected_ratio": cond_df["inspected_ratio"].to_numpy(),
            "period_billed_m3": cond_df["period_billed_m3"].to_numpy(),
            "period_zero_share": cond_df["period_zero_share"].to_numpy(),
            "month_billed_m3": cond_df["month_billed_m3"].to_numpy(),
            "month_zero_share": cond_df["month_zero_share"].to_numpy(),
        }
    )
    out = pd.concat([out, generated[["m3_to_bill", "days_reading", "planned_gap_days", "is_zero", "invoice_day", "reading_day", "planned_day"]]], axis=1)
    return out


def compare_real_vs_synth(real_df: pd.DataFrame, synth_df: pd.DataFrame) -> str:
    real = real_df.copy()
    real["m3_to_bill"] = real["m3_to_bill"].astype(float)
    metrics = []
    for col in ["m3_to_bill", "days_reading", "planned_gap_days", "is_zero"]:
        metrics.append(
            [
                col,
                f"{real[col].mean():.4f}",
                f"{synth_df[col].mean():.4f}",
                f"{real[col].std(ddof=0):.4f}",
                f"{synth_df[col].std(ddof=0):.4f}",
            ]
        )

    real_corr = real[["m3_to_bill", "days_reading", "planned_gap_days", "is_zero"]].corr().round(4)
    synth_corr = synth_df[["m3_to_bill", "days_reading", "planned_gap_days", "is_zero"]].corr().round(4)

    lines = [
        "# Evaluación rápida del generador sintético",
        "",
        "## Comparación de momentos básicos",
        "",
        "| Variable | Media real | Media sintética | Desv. real | Desv. sintética |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in metrics:
        lines.append("| " + " | ".join(row) + " |")

    lines.extend(
        [
            "",
            "## Correlación real",
            "",
            real_corr.to_markdown(),
            "",
            "## Correlación sintética",
            "",
            synth_corr.to_markdown(),
            "",
        ]
    )
    return "\n".join(lines) + "\n"


def cli_prepare(args: argparse.Namespace) -> None:
    ensure_dirs()
    df = build_training_frame(max_rows=args.max_rows, seed=args.seed)
    save_prepared_dataset(df, OUTPUT_DIR / "prepared_training_data.csv")
    summary = {
        "rows": len(df),
        "columns": len(df.columns),
        "periodicity_counts": df["periodicity"].value_counts().to_dict(),
        "quarter_counts": df["quarter"].value_counts().sort_index().to_dict(),
    }
    (OUTPUT_DIR / "prepared_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


def cli_train(args: argparse.Namespace) -> None:
    ensure_dirs()
    prepared_csv = OUTPUT_DIR / "prepared_training_data.csv"
    if not prepared_csv.exists():
        df = build_training_frame(max_rows=args.max_rows, seed=args.seed)
        save_prepared_dataset(df, prepared_csv)
    model, bundle, history = train_model(
        prepared_csv=prepared_csv,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        beta=args.beta,
        hidden_dim=args.hidden_dim,
        latent_dim=args.latent_dim,
        seed=args.seed,
    )
    synth = generate_synthetic(model, bundle, num_rows=args.eval_rows, seed=args.seed + 1)
    synth.to_csv(OUTPUT_DIR / "synthetic_preview.csv", index=False, encoding="utf-8")
    evaluation = compare_real_vs_synth(bundle.df.head(len(synth)), synth)
    (OUTPUT_DIR / "evaluation.md").write_text(evaluation, encoding="utf-8")
    (OUTPUT_DIR / "latest_train_config.json").write_text(
        json.dumps(
            {
                "epochs": args.epochs,
                "batch_size": args.batch_size,
                "lr": args.lr,
                "beta": args.beta,
                "hidden_dim": args.hidden_dim,
                "latent_dim": args.latent_dim,
                "seed": args.seed,
                "final_loss": history[-1]["loss"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def cli_generate(args: argparse.Namespace) -> None:
    ensure_dirs()
    prepared_csv = OUTPUT_DIR / "prepared_training_data.csv"
    if not prepared_csv.exists():
        raise FileNotFoundError("No existe prepared_training_data.csv. Ejecuta antes el subcomando prepare o train.")

    df = pd.read_csv(prepared_csv)
    bundle = prepare_feature_bundle(df)
    weights = np.load(MODEL_DIR / "weights.npz")
    model = NumpyCVAE(bundle.x.shape[1], bundle.c.shape[1], hidden_dim=args.hidden_dim, latent_dim=args.latent_dim, seed=args.seed)
    for key in model.params:
        model.params[key] = weights[key]

    synth = generate_synthetic(model, bundle, num_rows=args.num_rows, seed=args.seed)
    synth.to_csv(OUTPUT_DIR / args.output_name, index=False, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Pipeline de preparación, entrenamiento y generación sintética con un CVAE tabular en NumPy.")
    sub = parser.add_subparsers(dest="command", required=True)

    prepare = sub.add_parser("prepare", help="Prepara el dataset correlacionable para entrenamiento.")
    prepare.add_argument("--max-rows", type=int, default=50000)
    prepare.add_argument("--seed", type=int, default=SEED)
    prepare.set_defaults(func=cli_prepare)

    train = sub.add_parser("train", help="Entrena el modelo CVAE y genera una vista previa sintética.")
    train.add_argument("--max-rows", type=int, default=50000)
    train.add_argument("--epochs", type=int, default=35)
    train.add_argument("--batch-size", type=int, default=256)
    train.add_argument("--lr", type=float, default=0.0015)
    train.add_argument("--beta", type=float, default=0.02)
    train.add_argument("--hidden-dim", type=int, default=64)
    train.add_argument("--latent-dim", type=int, default=12)
    train.add_argument("--eval-rows", type=int, default=3000)
    train.add_argument("--seed", type=int, default=SEED)
    train.set_defaults(func=cli_train)

    generate = sub.add_parser("generate", help="Genera nuevas filas sintéticas a partir del modelo entrenado.")
    generate.add_argument("--num-rows", type=int, default=10000)
    generate.add_argument("--output-name", type=str, default="synthetic_generated.csv")
    generate.add_argument("--hidden-dim", type=int, default=64)
    generate.add_argument("--latent-dim", type=int, default=12)
    generate.add_argument("--seed", type=int, default=SEED)
    generate.set_defaults(func=cli_generate)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
