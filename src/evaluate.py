"""
evaluate.py — hitung metrik dan simpan sampel kesalahan.

Dua fungsi utama:
  - compute_metrics : hitung precision, recall, F1, dan confusion matrix dari prediksi.
  - dump_errors     : pisahkan FP dan FN, simpan ke CSV, kembalikan sebagai DataFrame.
"""

import random

import pandas as pd
from sklearn.metrics import (
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

# Seed acak sesuai aturan proyek (sama dengan config.py, tidak diimpor agar
# evaluate.py bisa berdiri sendiri tanpa ketergantungan pada config)
_SEED = 42


def compute_metrics(y_true, y_pred) -> dict:
    """Hitung precision, recall, F1, dan elemen confusion matrix; kembalikan sebagai dict.

    Kunci yang dikembalikan: 'precision', 'recall', 'f1', 'tn', 'fp', 'fn', 'tp'.
    Kelas positif = serangan (label 1), sesuai konvensi proyek.
    """
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    return {
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall":    recall_score(y_true, y_pred, zero_division=0),
        "f1":        f1_score(y_true, y_pred, zero_division=0),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
    }


def dump_errors(
    test_df: pd.DataFrame,
    y_pred,
    out_prefix: str,
    n: int = 20,
) -> tuple:
    """Pilih sampel FP dan FN dari test_df, simpan ke CSV, dan kembalikan (fp_df, fn_df).

    FP (False Positive): baris dengan label=0 yang diprediksi=1 (normal dianggap serangan).
    FN (False Negative): baris dengan label=1 yang diprediksi=0 (serangan terlewat).
    Sampling acak ber-seed (seed=42), maksimal n baris per jenis.
    File disimpan ke '<out_prefix>_fp.csv' dan '<out_prefix>_fn.csv'.
    """
    df = test_df.copy()
    df["_pred"] = list(y_pred)

    # Identifikasi FP dan FN
    fp_mask = (df["label"] == 0) & (df["_pred"] == 1)
    fn_mask = (df["label"] == 1) & (df["_pred"] == 0)

    fp_all = df[fp_mask].drop(columns=["_pred"])
    fn_all = df[fn_mask].drop(columns=["_pred"])

    # Sampling acak ber-seed, maksimal n baris
    rng = random.Random(_SEED)

    def _sample(frame: pd.DataFrame, k: int) -> pd.DataFrame:
        # Jika baris lebih sedikit dari k, kembalikan semua
        if len(frame) <= k:
            return frame.reset_index(drop=True)
        idx = rng.sample(range(len(frame)), k)
        return frame.iloc[sorted(idx)].reset_index(drop=True)

    fp_df = _sample(fp_all, n)
    fn_df = _sample(fn_all, n)

    # Simpan ke CSV
    fp_df.to_csv(f"{out_prefix}_fp.csv", index=False)
    fn_df.to_csv(f"{out_prefix}_fn.csv", index=False)

    return fp_df, fn_df
