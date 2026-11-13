# Panduan Eksekusi v2: Tiga Laptop

Rujukan: `2026-11-13-web-attack-detector-plan-v2.md` (letakkan di `docs/plans/` dan hapus versi pertama agar tidak membingungkan). File ini berisi cara kerja, urutan, dan prompt untuk Antigravity.

## 1. Pembagian

| Orang | Laptop | Task | Branch |
|---|---|---|---|
| A | ThinkPad T490 | 0, 1, 3b | `main`, `task-1-data`, `task-3b-train` |
| B | MSI Thin 15 | 2, 3a, 7 | `task-2-features`, `task-3a-evaluate`, `task-7-demo` |
| C | Lenovo 83S0 (RTX 4050) | 5, 6 | `task-5-llm`, `task-6-compare` |
| A, B, C | | 4, 8 | Dikerjakan manual, dibagi rata |

Alasan singkat: C memegang semua yang butuh Ollama dan GPU. B memegang pekerjaan yang ringan di RAM (MSI hanya sekitar 1 GB bebas saat dicek). A memegang jalur data dan pelatihan, karena RAM ThinkPad cukup untuk Random Forest.

## 2. Persiapan (sekali, semua orang)

1. Pastikan `git --version` dan `py --version` (Python 3.10 atau lebih baru) berfungsi.
2. **A:** buat repo kosong di GitHub (tanpa README dan `.gitignore`), undang B dan C sebagai collaborator.
3. **Semua:** di Antigravity, Terminal Execution Policy = **Request Review** dan Review Policy = **Request Review**. Buka hanya folder repo. Atur ini sendiri, jangan lewat agen.
4. **A:** jalankan prompt Task 0 (bagian 3), lalu `git remote add origin <url>` dan `git push -u origin main`.
5. **B dan C:** setelah A mem-push, `git clone <url>`, lalu `py -m venv .venv`, aktifkan (bila `Activate.ps1` diblokir, panggil `.venv\Scripts\python.exe` langsung), `pip install -r requirements.txt`.
6. **Semua:** unduh CSIC 2010 ke `data/raw/` di laptop masing-masing (tidak masuk repo).
7. Sebelum langkah berat (latih model, Ollama), tutup browser dan aplikasi berat, lalu cek RAM bebas di Task Manager. Ini penting terutama di MSI.

## 3. Prompt Task 0 (Orang A)

Taruh file rencana v2 di `docs/plans/` lebih dulu, lalu tempel prompt ini apa adanya:

```
Tugasmu: membuat KERANGKA repo saja. Ini setara Task 0 di docs/plans/2026-11-13-web-attack-detector-plan-v2.md, kecuali pembuatan venv, instalasi paket, dan pengunduhan dataset (itu dikerjakan manual oleh kami). Jangan mengerjakan task lain dan jangan menulis kode fitur. Jangan mengubah isi folder docs/plans.

Aturan: kerja hanya di folder proyek ini, jelaskan dulu setiap perintah terminal sebelum dijalankan, dan jangan mengunduh apa pun. Jangan menjalankan "git remote", "git push", atau perintah apa pun yang memakai akun atau jaringan.

Buat berkas dan folder berikut:

1. AGENTS.md dengan isi persis:
---
# Aturan untuk agen koding
- Proyek: detektor serangan web (kuliah Keamanan Informasi). Hanya klasifikasi; jangan membuat kode yang menjalankan atau mengirim payload ke sistem mana pun.
- Bekerja hanya di folder proyek ini. Jangan membaca file di luar folder.
- Jangan menjalankan perintah terminal tanpa persetujuan; jelaskan dulu perintahnya.
- Jangan mengunduh data atau paket selain yang tercantum di requirements.txt dan rencana.
- Tulis kode sederhana dengan komentar bahasa Indonesia singkat; jangan menambah fitur di luar rencana.
- Seed acak selalu 42. Kelas serangan = 1.
- Jelaskan tiap fungsi dalam satu kalimat agar anggota kelompok bisa mengulanginya.
---

2. requirements.txt berisi satu paket per baris: pandas, scikit-learn, joblib, requests, pytest.

3. .gitignore yang mengabaikan: .venv/, __pycache__/, *.pyc, .pytest_cache/, .env, data/raw/*, data/processed/*, models/* (tetapi tetap melacak file .gitkeep di tiap folder itu lewat aturan negasi "!"). Folder reports/ dan docs/ TIDAK diabaikan.

4. Folder dengan file .gitkeep: data/raw, data/processed, models, reports.

5. src/__init__.py dan tests/__init__.py (kosong).

6. src/config.py berisi PERSIS konstanta ini dan tidak lebih:
SEED = 42
MAX_REQUEST_CHARS = 1000
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2:3b"
LLM_TIMEOUT_S = 120
SUBSET_PER_CLASS = 100

7. docs/catatan-A.md, docs/catatan-B.md, docs/catatan-C.md: masing-masing hanya berisi satu judul, misalnya "# Catatan Orang A".

8. README.md dengan bagian (isi singkat atau placeholder): Tentang proyek (detektor serangan web, ML klasik vs LLM lokal, kuliah Keamanan Informasi), Setup lokal (py -m venv .venv, aktivasi, pip install -r requirements.txt, unduh dataset manual ke data/raw/), Pembagian tugas (tabel: Task | Penanggung jawab | Branch; isi sesuai tabel pembagian di rencana v2), Catatan temuan (satu kalimat: lihat docs/catatan-A.md, docs/catatan-B.md, docs/catatan-C.md).

Setelah itu: jalankan "git init", ganti nama branch menjadi main, "git add ." dan buat satu commit dengan pesan "chore: kerangka proyek".

Verifikasi dan laporkan hasilnya: (a) daftar struktur folder, (b) "git status" bersih, (c) "git log --oneline" menampilkan satu commit, (d) perintah python -c "from src import config; print(config.SEED)" mencetak 42. Terakhir, jelaskan satu kalimat untuk tiap berkas yang kamu buat.
```

Sebelum push, periksa `AGENTS.md` dan `src/config.py`: harus persis sama dengan yang diminta.

## 4. Alur git

Untuk tiap task, di laptop pemiliknya:

```
git checkout main
git pull origin main
git checkout -b <branch>
# kerjakan task (prompt di bagian 5)
pytest -v
git push -u origin <branch>
```

Lalu buat pull request di GitHub. **Orang lain** membaca perubahan itu minimal lima menit sebelum merge, dan pemilik task menjawab "Cek pemahaman" di rencana. Merge hanya bila `pytest -v` lulus.

Aturan:
- Satu task, satu branch. Tidak ada dua orang yang mengedit berkas yang sama.
- `src/config.py` hanya diubah A. Pengecualian: C boleh mengubah `OLLAMA_MODEL` dan `SUBSET_PER_CLASS`, dengan commit terpisah dan kabar ke yang lain.
- Catatan temuan ditulis di `docs/catatan-<huruf>.md` masing-masing.
- `git pull origin main` sebelum mulai dan sebelum membuat pull request.

**Urutan merge:** Task 0 → Task 1, 2, 3a, 5 (paralel) → Task 3b → Task 4 dan 6 (paralel) → Task 7 → Task 8.

## 5. Prompt per task

Template (ganti `<BRANCH>` dan `<SCOPE>` sesuai tabel di bawahnya):

```
Baca AGENTS.md dan docs/plans/2026-11-13-web-attack-detector-plan-v2.md. Kita sedang di branch <BRANCH>. Kerjakan HANYA: <SCOPE>. Ikuti urutan langkah di rencana: tulis test dulu, jalankan sampai gagal, implementasi, jalankan sampai lulus. Hanya buat atau ubah berkas yang tercantum di "Files" task itu; jangan menyentuh src/config.py dan jangan mengerjakan task lain. Fixture test didefinisikan di berkas test task ini, bukan di conftest.py. Jelaskan dulu setiap perintah terminal sebelum dijalankan. Boleh membuat commit di branch ini dengan pesan dari rencana. Jangan menjalankan git push, git merge, atau git remote. Setelah selesai, jelaskan tiap fungsi dalam satu kalimat dan tunjukkan hasil pytest.
```

| Task | Orang | `<BRANCH>` | `<SCOPE>` |
|---|---|---|---|
| 1 | A | `task-1-data` | Task 1 saja |
| 2 | B | `task-2-features` | Task 2 saja |
| 3a | B | `task-3a-evaluate` | Task 3 Step 1 sampai 4 saja (src/evaluate.py dan tests/test_evaluate.py) |
| 3b | A | `task-3b-train` | Task 3 Step 5 sampai 8 saja (src/train_classic.py); Task 1, 2, dan 3a sudah ada di main |
| 5 | C | `task-5-llm` | Task 5 Step 1 sampai 4 saja (src/llm_classifier.py dan tests/test_llm_classifier.py); Step 5 sampai 7 dikerjakan manual |
| 6 | C | `task-6-compare` | Task 6 saja; Task 3b sudah ada di main |
| 7 | B | `task-7-demo` | Task 7 saja; Task 3b dan Task 5 sudah ada di main |

Yang dikerjakan **manual, bukan lewat agen:**
- Menjalankan `python -m src.train_classic` pada data asli (A, Task 3b Step 6).
- Instal Ollama dan uji GPU dan kecepatan (C, Task 5 Step 5-6).
- Menjalankan `python -m src.compare` (C, Task 6 Step 5).
- Analisis FP/FN (Task 4) dan semua catatan temuan.

Agen cukup menulis kode dan test. Angka dan keputusan, kalian yang pegang.

## 6. Urutan kerja

**Jumat**

| Orang | Urutan |
|---|---|
| A | Task 0 (sekitar 30 menit) → Task 1 → tunggu Task 2 dan 3a digabung → Task 3b → Task 4 |
| B | Setup (clone, venv, dataset) → Task 2 → Task 3a → Task 4 |
| C | Setup → Task 5 (kode dan test) → instal Ollama dan uji GPU dan kecepatan → Task 4 |

**Sabtu**

| Orang | Urutan |
|---|---|
| C | Task 6 (pagi) |
| B | Task 7 (pagi sampai siang), setelah Task 3b dan 5 digabung |
| A | Meninjau pull request, siapkan README, latihan demo |
| Semua | Latihan demo di Laptop C (ada GPU dan Ollama), siapkan tiga contoh: normal, serangan terdeteksi, dan satu kesalahan |

Bila Task 3b terlambat, Task 6 dan 7 ikut bergeser. Titik putus tetap seperti di rencana: Sabtu siang, demo tetap jalan dengan model klasik bila LLM belum siap.

## 7. Kapan kembali ke saya

- Macet di satu langkah: kirim nomor task dan langkahnya, plus pesan error yang lengkap.
- Setelah Task 3b: kirim angka precision, recall, dan F1. Bila F1 nyaris 1,0, kita periksa bersama sebelum dipercaya.
- Setelah Task 6: kirim `comparison_metrics.json`, saya bantu menyusun narasi video.

## 8. Jika terhambat

- **MSI kehabisan RAM:** tutup aplikasi lain. Task 2, 3a, dan 7 ringan. Jangan menjalankan pelatihan Random Forest di MSI.
- **Random Forest terlalu berat di ThinkPad:** turunkan `n_estimators` ke 50 (sudah ada di rencana Task 3).
- **Ollama memakai CPU, bukan GPU:** perbarui driver NVIDIA dan mulai ulang Ollama. Bila tetap lambat, coba `llama3.2:1b`.
- **Program diblokir Windows (App Control):** salah satu kemungkinan penyebab bila installer atau executable gagal jalan. Ini dugaan, belum terbukti. Coba jalankan sebagai pengguna biasa, dan kabari saya dengan pesan errornya.
- **Dataset gagal diunduh:** cari mirror dan catat sumbernya di catatan pribadi.
- **Konflik git:** hampir selalu berarti dua orang mengedit berkas yang sama. Hentikan merge, jangan paksa, kabari kelompok.
