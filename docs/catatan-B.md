# Catatan Orang B

## Task 2 — Fitur (`src/features.py`)

- **Fungsi:**
  - `handcrafted_features(requests)`: Menghitung enam fitur numerik dari setiap string permintaan HTTP dan mengembalikannya sebagai array NumPy berbentuk `(n, 6)` dengan urutan `[panjang, n_karakter_khusus, n_persen, n_kata_sql, n_kata_script, n_digit]`.
  - `build_feature_union(max_features=20000)`: Membangun `FeatureUnion` yang menggabungkan `TfidfVectorizer(analyzer="char", ngram_range=(2, 4), lowercase=True)` dan keluaran `handcrafted_features` yang dibungkus `FunctionTransformer` lalu dinormalisasi `StandardScaler(with_mean=False)`.
- **Alasan keduanya saling melengkapi:**
  - TF-IDF n-gram karakter (2–4) menangkap potongan pola karakter lokal dan *obfuscation* sebagian (misalnya `'=`, `<sc`, `--`, atau kombinasi tanda baca tidak wajar) meskipun kata kunci serangan dipenggal atau disamarkan, hal yang tidak terdeteksi oleh regex kata utuh.
  - Sebaliknya, 6 fitur buatan sendiri menangkap statistik global yang eksplisit (panjang total permintaan, jumlah digit, total karakter khusus `' " < > ; ( ) % = -`, jumlah `%`, serta kemunculan kata kunci SQL/script utuh) yang bobotnya mudah terdilusi di vektor TF-IDF berdimensi ribuan.

## Task 3a — Evaluasi (`src/evaluate.py`)

- **Fungsi:**
  - `compute_metrics(y_true, y_pred)`: Menghitung metrik `precision`, `recall`, `f1`, serta komponen confusion matrix (`tn`, `fp`, `fn`, `tp`) dengan kelas serangan (`1`) sebagai kelas positif dan mengembalikannya sebagai kamus (`dict`).
  - `dump_errors(test_df, y_pred, out_prefix, n=20)`: Memisahkan baris kesalahan FP dan FN dari data uji, mengambil sampel acak deterministik (`seed=42`, maksimal `n` baris per jenis), menyimpannya ke `<out_prefix>_fp.csv` dan `<out_prefix>_fn.csv`, lalu mengembalikan `(fp_df, fn_df)`.
- **Kenapa serangan = kelas 1 & arti FP/FN untuk aplikasi perbankan:**
  - Kelas serangan dijadikan kelas positif (`1`) karena fokus utama detektor adalah mendeteksi ancaman, sehingga nilai *precision* dan *recall* langsung mengukur ketepatan peringatan dan kemampuan menangkap serangan yang sebenarnya.
  - **FP (False Positive):** Permintaan normal nasabah salah diklasifikasikan sebagai serangan; akibatnya transaksi sah terblokir atau tertunda sehingga mengganggu kenyamanan dan layanan pengguna.
  - **FN (False Negative):** Permintaan serangan nyata salah diklasifikasikan sebagai normal; bagi bank, FN jauh lebih berbahaya karena serangan seperti SQL injection atau XSS dapat lolos ke sistem, berisiko membocorkan data nasabah, memanipulasi transaksi, atau mengambil alih akun.

## Task 4 — Analisis FP/FN Bagian B (`reports/error_analysis_B.md`)

- **Dasar analisis:** Memeriksa 7 sampel FP (`FP-08` s.d. `FP-14` dari `reports/rf_fp.csv`) dan 7 sampel FN (`FN-08` s.d. `FN-14` dari `reports/rf_fn.csv`) pada model terbaik `rf` (`F1 = 0.9557`).
- **Temuan utama:**
  - **Penyebab FP:** Karakter pengganti non-ASCII pada data Spanyol (`Aadir`, `Peneds`), tanda baca wajar di alamat form panjang, permintaan pendek di endpoint populer (`caracteristicas.jsp`), dan kata normal `modo=insertar` yang n-gram karakternya mirip kata kunci SQL `insert`.
  - **Penyebab FN:** Serangan halus berupa penyisipan tunggal (`|`, `/`, `?`, `*`) yang belum tercakup di `_RE_SPECIAL` dan terdilusi oleh TF-IDF teks normal di sekitarnya, serta anomali panjang/format digit kartu kredit (`ntc`) tanpa simbol berbahaya.

## Task 7 — Demo CLI (`src/demo.py`)

- **Fungsi:**
  - `predict_classic(request, pipeline)`: Memprediksi label kelas (`0` atau `1`) dan probabilitas kelas serangan (`1`) dari satu string permintaan HTTP menggunakan pipeline model klasik yang diberikan.
  - `main(argv=None)`: Menjalankan antarmuka CLI dengan `argparse` (`--request`, `--llm`, `--model-path`), mencetak hasil prediksi model klasik serta hasil LLM opsional, dan selalu mengembalikan kode keluar `0`.
- **Cara kerja & alasan kode keluar tetap 0 saat Ollama mati:**
  - `main()` selalu memuat model klasik (`.joblib`) terlebih dahulu, memanggil `predict_classic`, dan mencetak vonisnya (`Model klasik: ATTACK/NORMAL (p=...)`).
  - Apabila argumen `--llm` diberikan, pemanggilan `classify_request(args.request)` dibungkus blok `try ... except RuntimeError`. Jika layanan Ollama lokal tidak berjalan atau mati, `RuntimeError` ditangkap lalu dicetak sebagai peringatan (`Peringatan: ...`) dan program tetap melanjutkan eksekusi serta keluar dengan kode `0` (*graceful degradation*) karena model klasik adalah jalur deteksi utama sedangkan LLM hanya pembanding opsional.
