# Web Attack Detector (Detektor Serangan Web)

## Tentang Proyek
Proyek ini adalah sistem deteksi serangan web berbasis *machine learning* untuk memenuhi Tugas Ujian Akhir Semester (UAS) mata kuliah **Keamanan Informasi**. Sistem ini mengklasifikasikan permintaan HTTP mentah menjadi lalu lintas **normal (`0`)** atau **serangan (`1`)** menggunakan penggabungan fitur **TF-IDF *character n-gram* (2–4)** dan **6 fitur buatan tangan (*handcrafted features*: `panjang`, `n_karakter_khusus`, `n_persen`, `n_kata_sql`, `n_kata_script`, `n_digit`)**, kemudian membandingkan performa model klasik (**Logistic Regression** dan **Random Forest**) terhadap model bahasa lokal (**Ollama `llama3.2:3b`**) pada dataset **CSIC 2010 HTTP Dataset**.

> **Catatan Etika & Keamanan:** Proyek ini murni melakukan klasifikasi teks pasif terhadap log permintaan HTTP untuk keperluan akademik. Tidak ada kode yang mengirim atau mengeksekusi payload ke sistem mana pun.

---

## Setup Lokal

1. Pastikan **Python 3.11+** sudah terpasang di komputer Anda.
2. Buat dan aktifkan *virtual environment*:
   ```bash
   python -m venv .venv
   # Windows (PowerShell):
   .\.venv\Scripts\Activate.ps1
   ```
3. Pasang seluruh dependensi dari `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
4. Pastikan ketiga file dataset CSIC 2010 berada di dalam folder `data/raw/`:
   - `data/raw/normalTrafficTraining.txt`
   - `data/raw/normalTrafficTest.txt`
   - `data/raw/anomalousTrafficTest.txt`
5. Untuk menjalankan modul perbandingan LLM lokal (`src/compare.py`), pastikan aplikasi **Ollama** sudah berjalan di latar belakang dan model `llama3.2:3b` sudah diunduh:
   ```bash
   ollama pull llama3.2:3b
   ```

---

## Cara Menjalankan Program & Pengujian

1. **Menjalankan Seluruh Unit Test (26 Test):**
   ```bash
   pytest -v
   ```
2. **Melatih Model Klasik (`logreg` & `rf`) dan Mengekspor Laporan FP/FN:**
   ```bash
   python -m src.train_classic
   ```
   Output: `models/logreg.joblib`, `models/rf.joblib`, `reports/classic_metrics.json`, serta daftar kesalahan di `reports/{logreg,rf}_{fp,fn}.csv`.
3. **Menjalankan Perbandingan Model Klasik vs LLM Lokal (400 Sampel Uji):**
   ```bash
   python -m src.compare
   ```
   Output: `reports/comparison.csv` dan `reports/comparison_metrics.json`.
4. **Menjalankan Demo CLI untuk Memeriksa Satu Permintaan HTTP:**
   ```bash
   # Contoh pemeriksaan permintaan normal (model klasik saja):
   python -m src.demo --request "GET /tienda1/index.jsp HTTP/1.1"

   # Contoh pemeriksaan serangan SQL Injection (model klasik + LLM lokal):
   python -m src.demo --request "GET /tienda1/publico/anadir.jsp?id=1' OR '1'='1 HTTP/1.1" --llm
   ```

---

## Ringkasan Hasil Eksperimen

### 1. Evaluasi Model Klasik pada Dataset Uji Penuh CSIC 2010 (`10.382` Permintaan)
Dataset latih: `6.000` permintaan (`4.000` normal + `2.000` serangan). Dataset uji: `10.382` permintaan (`5.592` normal + `4.790` serangan). Sumber: `reports/classic_metrics.json`.

| Model | Precision | Recall | F1-Score | TP | FP | FN | TN |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression (`logreg`)** | `0.9894` | `0.8741` | `0.9282` | 4.187 | 45 | 603 | 5.547 |
| **Random Forest (`rf`)** | `0.9811` | **`0.9315`** | **`0.9557`** | 4.462 | 86 | 328 | 5.506 |

- **Model Terbaik:** **Random Forest (`rf`)** mencapai **F1-score `0.9557`** dan berhasil menurunkan jumlah serangan yang lolos (*False Negative*) hampir setengahnya dibanding Logistic Regression (dari `603` menjadi `328` FN), sambil mempertahankan *Precision* di atas `98%`.

### 2. Perbandingan Model Klasik vs LLM Lokal (`llama3.2:3b`) pada Subset Uji (`400` Permintaan)
Dievaluasi pada 400 sampel berimbang (`200` normal + `200` serangan, `seed=42`). Sumber: `reports/comparison_metrics.json`.

| Pendekatan | Precision | Recall | F1-Score | TP | FP | FN | TN | Waktu Rata-Rata / Request |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Klasik (`logreg`)** | **`1.0000`** | **`0.8950`** | **`0.9446`** | 179 | **0** | 21 | 200 | `< 0.001` detik |
| **LLM Lokal (`llama3.2:3b`)** | `0.4917` | `0.8900` | `0.6335` | 178 | 184 | 22 | 16 | `2.37` detik (`0` gagal parse) |

- **Temuan Utama:** Meskipun `llama3.2:3b` memiliki *Recall* yang hampir setara (`89.0%` vs `89.5%`), pendekatan LLM *zero-shot* menghasilkan **False Positive yang sangat tinggi (`184` dari `200` trafik normal dikira serangan)** karena menganggap form panjang dan encoding karakter Latin-1 Spanyol (`%F3`, `%F1`) sebagai payload berbahaya. Selain itu, model klasik ribuan kali lebih cepat sehingga jauh lebih cocok untuk penyaringan lalu lintas web secara *real-time*.

### 3. Ringkasan Analisis Kesalahan (20 FP & 20 FN dari Random Forest)
Detail lengkap 40 sampel tersedia di `reports/error_analysis.md`:
- **Penyebab Utama False Positive (FP):** Didominasi oleh **karakter non-ASCII bahasa Spanyol (`%F1`, `%F3`, `%E9`) pada parameter keranjang `anadir.jsp` dan form `registro.jsp` (10/20 FP)** yang menaikkan hitungan encoding `%XX`, serta **kemiripan sub-kata kunci SQL pada kata bahasa Spanyol `modo=insertar` (6/20 FP)** yang memicu fitur kata kunci `insert`.
- **Penyebab Utama False Negative (FN):** Didominasi oleh **serangan sisipan satu karakter (*single-byte fuzzing* seperti `*`, `?`, `/`, `|`, `'`, `+`) di tengah kata normal (14/20 FN)**, diikuti **anomali nilai numerik/panjang digit (*integer overflow* 16–22 digit atau kuantitas negatif `cantidad=-12`) sebanyak 4/20 FN**, serta **manipulasi metode HTTP (`PUT` / *Verb Tampering*) sebanyak 2/20 FN**.
- **Implikasi Keamanan:** Dalam sistem perbankan atau *e-commerce*, **FN lebih berbahaya daripada FP** karena serangan seperti kuantitas negatif (`cantidad=-12`) atau *overflow* nominal pembayaran yang lolos dapat merugikan sistem secara langsung, sedangkan FP hanya menghambat sementara transaksi pengguna sah yang dapat diatasi dengan verifikasi tambahan.

---

## Keterbatasan Proyek & Dataset CSIC 2010

1. **Dataset Berusia Lama & Sintetis (Tahun 2010):** Dataset CSIC 2010 dibangkitkan secara otomatis terhadap satu aplikasi web simulasi berbahasa Spanyol (`/tienda1/`). Oleh karena itu, pola URL, nama parameter (`dni`, `ntc`, `modo=insertar`), dan encoding Latin-1 (`ISO-8859-1`) sangat spesifik terhadap aplikasi tersebut.
2. **Belum Mencakup Vektor Serangan Web Modern:** CSIC 2010 berfokus pada serangan klasik berbasis form dan query string (SQLi, XSS, *Buffer Overflow*, *Parameter Tampering*), tetapi belum mencakup trafik web modern seperti payload **JSON / REST API**, **GraphQL injection**, **manipulasi token JWT**, **Server-Side Request Forgery (SSRF)**, maupun **deserialisasi objek**.
3. **Generalisasi ke Lalu Lintas Produksi Nyata:** Karena fitur TF-IDF mempelajari distribusi n-gram karakter dari endpoint `/tienda1/`, model yang dilatih pada CSIC 2010 tidak dapat langsung dipasang pada aplikasi produksi dengan skema URL berbeda tanpa pelatihan ulang (*retraining*) atau normalisasi path terlebih dahulu.
4. **Keterbatasan Fitur Statis pada Permintaan Tunggal:** Model saat ini menilai setiap permintaan HTTP secara terpisah (*stateless*) dan belum mengekstrak fitur metode HTTP secara eksplisit maupun memvalidasi tipe/rentang semantik nilai parameter, sehingga serangan *HTTP Verb Tampering* (`PUT`) dan manipulasi angka logika bisnis (`cantidad=-12`) masih dapat lolos.

---

## Pembagian Tugas
- **Orang A:** Koordinator repositori, pemuat & pembersih data CSIC 2010 (`src/data_loader.py`), alur pelatihan model klasik (`src/train_classic.py`), analisis kesalahan `FP-01..07` & `FN-01..07`, dan integrasi laporan akhir.
- **Orang B:** Rekayasa fitur buatan tangan + TF-IDF (`src/features.py`), metrik evaluasi & ekspor kesalahan (`src/evaluate.py`), antarmuka baris perintah / demo (`src/demo.py`), dan analisis kesalahan `FP-08..14` & `FN-08..14`.
- **Orang C:** Klasifikator LLM lokal Ollama (`src/llm_classifier.py`), skrip perbandingan model klasik vs LLM (`src/compare.py`), pengujian demo CLI, dan analisis kesalahan `FP-15..20` & `FN-15..20`.

---

## Catatan Temuan Anggota
- [Catatan Orang A](docs/catatan-A.md)
- [Catatan Orang B](docs/catatan-B.md)
- [Catatan Orang C](docs/catatan-C.md)
- [Laporan Analisis Kesalahan Gabungan (FP & FN)](reports/error_analysis.md)
