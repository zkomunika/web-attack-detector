"""
compare.py — bandingkan model klasik vs LLM lokal pada subset test (Task 6).

Tiga fungsi utama:
  - sample_subset    : ambil n baris tiap kelas dari test DataFrame, deterministik.
  - run_comparison   : jalankan prediksi klasik dan LLM pada subset, kembalikan DataFrame.
  - main             : jalankan perbandingan lengkap dan simpan hasil ke reports/.
"""

import json
import os

import pandas as pd

from src.config import SEED, SUBSET_PER_CLASS
from src.evaluate import compute_metrics
from src.llm_classifier import classify_request


def sample_subset(
    test_df: pd.DataFrame,
    n_per_class: int = SUBSET_PER_CLASS,
    seed: int = SEED,
) -> pd.DataFrame:
    """Ambil n_per_class baris tiap label dari test_df secara acak ber-seed; hasilnya deterministik."""
    # Ambil n_per_class baris dari tiap label (0 dan 1) secara terpisah
    # agar kolom 'label' tidak hilang akibat perilaku groupby di pandas terbaru
    potongan_list = []
    for lbl in sorted(test_df["label"].unique()):
        grup = test_df[test_df["label"] == lbl]
        n = min(n_per_class, len(grup))
        potongan_list.append(grup.sample(n=n, random_state=seed))
    return pd.concat(potongan_list).reset_index(drop=True)


def run_comparison(
    subset: pd.DataFrame,
    classic_pipeline,
    classify=classify_request,
) -> pd.DataFrame:
    """Jalankan prediksi klasik dan LLM pada setiap baris subset; kembalikan DataFrame hasil."""
    requests_list = list(subset["request"])

    # Prediksi model klasik sekaligus (satu batch)
    pred_classic = list(classic_pipeline.predict(requests_list))

    # Prediksi LLM satu per satu
    pred_llm_list = []
    llm_unparsed_list = []
    llm_seconds_list = []

    for req in requests_list:
        label_llm, detik = classify(req)
        llm_seconds_list.append(detik)
        if label_llm is None:
            # Keluaran tidak bisa di-parse: dicatat sebagai unparsed, dipetakan ke 0
            pred_llm_list.append(0)
            llm_unparsed_list.append(True)
        else:
            pred_llm_list.append(int(label_llm))
            llm_unparsed_list.append(False)

    return pd.DataFrame({
        "request":      requests_list,
        "label":        list(subset["label"]),
        "pred_classic": pred_classic,
        "pred_llm":     pred_llm_list,
        "llm_unparsed": llm_unparsed_list,
        "llm_seconds":  llm_seconds_list,
    })


def main() -> None:
    """Muat model terbaik, jalankan perbandingan klasik vs LLM, simpan reports/comparison.csv dan comparison_metrics.json."""
    import joblib

    from src.data_loader import load_csic, split_data

    # Tentukan path data mentah
    data_dir = os.path.join("data", "raw")
    normal_files = [
        os.path.join(data_dir, f)
        for f in os.listdir(data_dir)
        if "normal" in f.lower() and f.endswith(".txt")
    ]
    anomalous_files = [
        os.path.join(data_dir, f)
        for f in os.listdir(data_dir)
        if "anomal" in f.lower() and f.endswith(".txt")
    ]

    print("Memuat dataset ...")
    df = load_csic(normal_files, anomalous_files)
    _, test_df = split_data(df)

    # Muat model terbaik (logreg lebih dulu, fallback ke rf)
    model_path = "models/logreg.joblib"
    if not os.path.exists(model_path):
        model_path = "models/rf.joblib"
    print(f"Muat model: {model_path}")
    pipeline = joblib.load(model_path)

    # Ambil subset seimbang dari test
    subset = sample_subset(test_df)
    print(f"Ukuran subset: {len(subset)} baris ({SUBSET_PER_CLASS} per kelas)")

    # Jalankan perbandingan
    print("Menjalankan perbandingan klasik vs LLM ...")
    hasil = run_comparison(subset, pipeline)

    # Simpan CSV
    os.makedirs("reports", exist_ok=True)
    csv_path = os.path.join("reports", "comparison.csv")
    hasil.to_csv(csv_path, index=False)
    print(f"Tersimpan: {csv_path}")

    # Hitung metrik
    metrik_klasik = compute_metrics(hasil["label"], hasil["pred_classic"])
    metrik_llm = compute_metrics(hasil["label"], hasil["pred_llm"])

    n_unparsed = int(hasil["llm_unparsed"].sum())
    rata_detik = float(hasil["llm_seconds"].mean())

    ringkasan = {
        "classic": metrik_klasik,
        "llm":     metrik_llm,
        "llm_avg_seconds": rata_detik,
        "llm_unparsed_count": n_unparsed,
    }

    json_path = os.path.join("reports", "comparison_metrics.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(ringkasan, f, ensure_ascii=False, indent=2)
    print(f"Tersimpan: {json_path}")

    # Cetak ringkasan ke layar
    print("\n=== Metrik pada Subset ===")
    for nama, m in [("Klasik", metrik_klasik), ("LLM", metrik_llm)]:
        print(f"  {nama}: P={m['precision']:.3f}  R={m['recall']:.3f}  F1={m['f1']:.3f}")
    print(f"  LLM rata-rata: {rata_detik:.2f} detik/permintaan")
    print(f"  LLM tidak terparsing: {n_unparsed} dari {len(hasil)}")


if __name__ == "__main__":
    main()
