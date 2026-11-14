"""Pelatihan dan evaluasi model klasik (Logistic Regression dan Random Forest)."""

import json
from pathlib import Path

import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from src.config import SEED
from src.data_loader import load_csic, split_data
from src.evaluate import compute_metrics, dump_errors
from src.features import build_feature_union


def build_pipeline(kind: str) -> Pipeline:
    """Bangun pipeline fitur dan classifier untuk jenis model 'logreg' atau 'rf'."""
    if kind == "logreg":
        features = build_feature_union(max_features=20000)
        clf = LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=SEED,
        )
    elif kind == "rf":
        features = build_feature_union(max_features=5000)
        clf = RandomForestClassifier(
            n_estimators=100,
            n_jobs=-1,
            random_state=SEED,
        )
    else:
        raise ValueError(f"Jenis model tidak dikenal: {kind}")

    return Pipeline([("features", features), ("clf", clf)])


def main() -> None:
    """Latih kedua model klasik pada data CSIC 2010 lalu simpan model, metrik, dan sampel error."""
    Path("models").mkdir(exist_ok=True)
    Path("reports").mkdir(exist_ok=True)

    normal_candidates = [
        "data/raw/normalTrafficTraining.txt",
        "data/raw/normalTrafficTest.txt",
    ]
    anomalous_candidates = ["data/raw/anomalousTrafficTest.txt"]

    normal_paths = [p for p in normal_candidates if Path(p).exists()]
    anomalous_paths = [p for p in anomalous_candidates if Path(p).exists()]
    if not normal_paths or not anomalous_paths:
        raise FileNotFoundError("Berkas dataset CSIC 2010 di data/raw/ tidak lengkap.")

    df = load_csic(normal_paths, anomalous_paths)
    train_df, test_df = split_data(df)

    all_metrics: dict[str, dict] = {}
    print(f"{'Model':<10} {'Precision':>10} {'Recall':>10} {'F1':>10} {'TP':>7} {'FP':>7} {'FN':>7} {'TN':>7}")
    print("-" * 74)

    for kind in ("logreg", "rf"):
        pipeline = build_pipeline(kind)
        pipeline.fit(train_df["request"], train_df["label"])

        # Simpan model terlatih ke folder models/
        joblib.dump(pipeline, f"models/{kind}.joblib")

        y_pred = pipeline.predict(test_df["request"])
        metrics = compute_metrics(test_df["label"], y_pred)
        all_metrics[kind] = metrics

        # Simpan sampel kesalahan FP dan FN ke folder reports/
        dump_errors(test_df, y_pred, f"reports/{kind}")

        print(
            f"{kind:<10} "
            f"{metrics['precision']:>10.4f} "
            f"{metrics['recall']:>10.4f} "
            f"{metrics['f1']:>10.4f} "
            f"{metrics['tp']:>7d} "
            f"{metrics['fp']:>7d} "
            f"{metrics['fn']:>7d} "
            f"{metrics['tn']:>7d}"
        )

    with open("reports/classic_metrics.json", "w", encoding="utf-8") as f:
        json.dump(all_metrics, f, indent=2)


if __name__ == "__main__":
    main()
