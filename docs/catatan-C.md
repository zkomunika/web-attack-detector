# Catatan Orang C
Menjalankan pengujian 10 sampel...
Sampel 01: Label=0, Waktu=4.17 s
Sampel 02: Label=1, Waktu=2.14 s
Sampel 03: Label=0, Waktu=2.12 s
Sampel 04: Label=1, Waktu=2.36 s
Sampel 05: Label=1, Waktu=2.30 s
Sampel 06: Label=0, Waktu=2.39 s
Sampel 07: Label=0, Waktu=2.41 s
Sampel 08: Label=1, Waktu=2.45 s
Sampel 09: Label=0, Waktu=2.39 s
Sampel 10: Label=1, Waktu=2.42 s

Rata-rata: 2.51 detik/permintaan
Rekomendasi: SUBSET_PER_CLASS = 200

---

## Task 6 — Perbandingan Klasik vs LLM

### Konfigurasi
- `SUBSET_PER_CLASS = 200` (200 normal + 200 serangan = 400 baris)
- Model klasik: `models/logreg.joblib` (seed 42, sama dengan Laptop A)
- LLM: `llama3.2:3b` via Ollama lokal (GPU RTX 4050)

### Metrik pada Subset (isi setelah `python -m src.compare`)

| Model | Precision | Recall | F1 |
|-------|-----------|--------|----|
| Klasik (logreg) | — | — | — |
| LLM (llama3.2:3b) | — | — | — |

- LLM rata-rata: — detik/permintaan
- LLM tidak terparsing: — dari 400

### Lima kasus LLM benar, klasik salah (FN klasik)

| # | Cuplikan permintaan | Label | Pred klasik | Pred LLM |
|---|---------------------|-------|-------------|----------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

### Lima kasus klasik benar, LLM salah (FN atau FP LLM)

| # | Cuplikan permintaan | Label | Pred klasik | Pred LLM |
|---|---------------------|-------|-------------|----------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

### Temuan dan Catatan
- (isi setelah menjalankan perbandingan asli)