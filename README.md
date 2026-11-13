# Detektor Serangan Web

## Tentang Proyek
Proyek ini adalah detektor serangan web untuk mata kuliah Keamanan Informasi yang mengklasifikasikan permintaan HTTP sebagai lalu lintas normal atau serangan dengan membandingkan model Machine Learning klasik (Logistic Regression & Random Forest) dan LLM lokal (melalui Ollama).

## Setup Lokal
1. Buat virtual environment:
   ```powershell
   py -m venv .venv
   ```
2. Aktifkan virtual environment:
   ```powershell
   .venv\Scripts\Activate.ps1
   ```
3. Pasang paket dependensi:
   ```powershell
   pip install -r requirements.txt
   ```
4. Unduh dataset CSIC 2010 secara manual dan simpan ke dalam folder `data/raw/`.

## Pembagian Tugas

| Task | Penanggung jawab | Branch |
|---|---|---|
| Task 0: Setup kerangka proyek | Orang A (ThinkPad T490) | `main` |
| Task 1: Pemuat data dan pembagian | Orang A (ThinkPad T490) | `task-1-data` |
| Task 2: Fitur teks dan buatan sendiri | Orang B (MSI Thin 15) | `task-2-features` |
| Task 3a: Evaluasi (`evaluate.py`) | Orang B (MSI Thin 15) | `task-3a-evaluate` |
| Task 3b: Latih model klasik (`train_classic.py`) | Orang A (ThinkPad T490) | `task-3b-train` |
| Task 4: Analisis FP/FN | Orang A, B, C | `task-4-fp-fn` |
| Task 5: Klasifikasi LLM lokal | Orang C (Lenovo 83S0) | `task-5-llm` |
| Task 6: Perbandingan klasik vs LLM | Orang C (Lenovo 83S0) | `task-6-compare` |
| Task 7: Demo CLI | Orang B (MSI Thin 15) | `task-7-demo` |
| Task 8: Penyelesaian akhir & laporan | Orang A, B, C | `main` |

## Catatan Temuan
Catatan temuan dan hasil pengamatan masing-masing anggota dapat dilihat di `docs/catatan-A.md`, `docs/catatan-B.md`, dan `docs/catatan-C.md`.
