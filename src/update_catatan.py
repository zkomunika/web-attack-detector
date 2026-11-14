"""
update_catatan.py — skrip bantu untuk mencetak ringkasan perbandingan dari
reports/comparison.csv dan reports/comparison_metrics.json ke layar,
agar bisa disalin ke docs/catatan-C.md (Step 6 Task 6).

Jalankan setelah python -m src.compare selesai:
  python -m src.update_catatan
"""

import json
import os

import pandas as pd


def main() -> None:
    """Baca hasil perbandingan dan cetak ringkasan siap salin ke catatan."""
    csv_path = os.path.join("reports", "comparison.csv")
    json_path = os.path.join("reports", "comparison_metrics.json")

    if not os.path.exists(csv_path) or not os.path.exists(json_path):
        print("Belum ada hasil. Jalankan dulu: python -m src.compare")
        return

    df = pd.read_csv(csv_path)
    with open(json_path, encoding="utf-8") as f:
        metrik = json.load(f)

    # Cetak metrik
    print("\n=== Metrik pada Subset ===")
    for nama, kunci in [("Klasik (logreg)", "classic"), ("LLM", "llm")]:
        m = metrik[kunci]
        print(f"  {nama}: P={m['precision']:.3f}  R={m['recall']:.3f}  F1={m['f1']:.3f}")
    print(f"  LLM rata-rata: {metrik['llm_avg_seconds']:.2f} detik/permintaan")
    print(f"  LLM tidak terparsing: {metrik['llm_unparsed_count']} dari {len(df)}")

    # Kasus LLM benar, klasik salah (klasik salah = pred_classic != label)
    llm_benar_klasik_salah = df[
        (df["pred_llm"] == df["label"]) &
        (df["pred_classic"] != df["label"])
    ]
    print(f"\n=== LLM benar, klasik salah: {len(llm_benar_klasik_salah)} kasus ===")
    for i, row in llm_benar_klasik_salah.head(5).iterrows():
        cuplikan = row["request"][:80].replace("\n", " ")
        print(f"  [{i}] label={row['label']} pred_klasik={row['pred_classic']} "
              f"pred_llm={row['pred_llm']} | {cuplikan}")

    # Kasus klasik benar, LLM salah
    klasik_benar_llm_salah = df[
        (df["pred_classic"] == df["label"]) &
        (df["pred_llm"] != df["label"])
    ]
    print(f"\n=== Klasik benar, LLM salah: {len(klasik_benar_llm_salah)} kasus ===")
    for i, row in klasik_benar_llm_salah.head(5).iterrows():
        cuplikan = row["request"][:80].replace("\n", " ")
        print(f"  [{i}] label={row['label']} pred_klasik={row['pred_classic']} "
              f"pred_llm={row['pred_llm']} | {cuplikan}")


if __name__ == "__main__":
    main()
