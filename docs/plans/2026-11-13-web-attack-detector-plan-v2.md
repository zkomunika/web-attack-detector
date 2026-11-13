# Detektor Serangan Web: Rencana Implementasi (v2, tiga laptop)

> **Untuk pelaksana (anggota kelompok dan agen koding Antigravity):** kerjakan task berurutan dan centang `- [ ]` saat selesai. Terminal Execution Policy di Antigravity harus **Request Review**. Pemilik tiap task wajib bisa menjawab "Cek pemahaman" di akhir task sebelum lanjut ke task berikutnya.

**Goal:** Program yang mengklasifikasikan permintaan HTTP sebagai normal atau serangan memakai model klasik dan LLM lokal, dengan evaluasi precision, recall, F1, dan analisis FP/FN, siap didemokan Sabtu 14 November 2026.

**Architecture:** Satu paket Python kecil di `src/`, satu file satu tanggung jawab: memuat data, membuat fitur, melatih, mengevaluasi, memanggil LLM, membandingkan, dan demo CLI. Model klasik adalah jalur utama (opsi A di desain). LLM lokal lewat Ollama hanya pembanding pada subset kecil.

**Tech Stack:** Python 3.10 atau lebih baru, pandas, scikit-learn, joblib, requests, pytest, Ollama (lokal).

**Spec:** https://claude.ai/artifact/TL4Ja6wcVjHm11o3HuEyBZ (Desain Proyek: Detektor Serangan Web, ML dan LLM Lokal)

## Global Constraints

- Kelas serangan = positif (label 1), normal = label 0.
- Metrik wajib: precision, recall, F1, plus analisis FP/FN.
- Dataset: CSIC 2010. Tidak ada data bank sungguhan dan tidak ada target nyata.
- LLM: Ollama lokal hanya di Laptop C (RTX 4050), model terkuantisasi yang muat di VRAM (mulai dari `llama3.2:3b`), suhu 0, keluaran satu kata `NORMAL` atau `ATTACK`.
- Subset awal untuk LLM: 100 sampel normal dan 100 serangan; naik ke 200 dan 200 bila rata-rata di bawah 5 detik per permintaan.
- Payload dari dataset hanya diklasifikasikan, tidak pernah dijalankan atau dikirim ke sistem mana pun.
- Antigravity: Terminal Execution Policy = Request Review, bekerja hanya di folder proyek.
- Seed acak selalu 42.
- Setiap anggota bisa menjelaskan bagiannya di video.
- Fixture test (`small_df`, `test_df`, `subset`, `tiny_pipeline`, `tiny_model_path`) didefinisikan di file test task masing-masing, bukan di `conftest.py`, agar tidak bentrok di git.
- Catatan temuan ditulis di catatan pribadi masing-masing, bukan di README.md. Hanya Orang A yang mengubah README.md dan `src/config.py`; Orang C boleh mengubah `OLLAMA_MODEL` dan `SUBSET_PER_CLASS` di `config.py`, dengan commit terpisah dan kabar ke yang lain.

## Pembagian Tiga Laptop

| Orang | Laptop | Task | Catatan |
|---|---|---|---|
| A | ThinkPad T490 (RAM 12 GB, sekitar 3 GB bebas, tanpa GPU khusus) | 0, 1, 3b | Menggabungkan laporan akhir dan README |
| B | MSI Thin 15 (RAM 7,9 GB, sekitar 1 GB bebas) | 2, 3a, 7 | RAM paling sempit: jangan latih model besar di sini |
| C | Lenovo 83S0 (RAM 15,5 GB, RTX 4050) | 5, 6 | Satu-satunya mesin untuk Ollama dan demo utama |
| A, B, C | | 4, 8 | Dibagi rata |

**Urutan merge ke `main`:** Task 0 → Task 1, 2, 3a, 5 (paralel) → Task 3b → Task 4 dan 6 (paralel) → Task 7 → Task 8. Tiap task punya branch sendiri. Task 3b butuh Task 1, 2, dan 3a. Task 7 butuh Task 3b dan 5. Dataset tidak masuk repo: tiap laptop mengunduh sendiri.

## Review Focus

Hal yang paling mungkin menggigit, walau tidak disebut eksplisit di desain. Tiap baris punya test di task yang disebut.

1. **Artefak header pada dataset buatan.** Model bisa belajar dari header (misalnya cookie atau host) dan bukan dari isi serangan, sehingga F1 tampak nyaris sempurna. Keluaran yang diharapkan: teks fitur hanya berisi baris permintaan dan body. Test di Task 1 (`test_extract_text_drops_headers`). Ini kekhawatiran saya soal dataset buatan, belum diverifikasi pada CSIC 2010.
2. **Payload ter-encode URL.** `%27%20OR%201%3D1` harus diperlakukan sama dengan `' OR 1=1`. Test di Task 1.
3. **Permintaan kosong atau sangat panjang** tidak boleh membuat program crash. Test di Task 2, 5, dan 7.
4. **Keluaran LLM bertele-tele atau tidak bisa di-parse** harus dihitung dan dilaporkan, bukan diam-diam dianggap benar. Test di Task 5 dan 6.
5. **Ollama tidak berjalan atau timeout** harus memberi pesan jelas, dan demo tetap jalan dengan model klasik saja. Test di Task 5 dan 7.

---

## Struktur File

```
web-attack-detector/
  AGENTS.md
  README.md              (ringkasan proyek, diisi Orang A)
  docs/plans/            (rencana ini)
  docs/catatan-A.md  docs/catatan-B.md  docs/catatan-C.md   (catatan temuan pribadi)
  requirements.txt
  data/raw/              (CSIC 2010, tidak di-commit)
  models/                (hasil latih, tidak di-commit)
  reports/               (metrik, sampel kesalahan, hasil banding)
  src/
    __init__.py
    config.py            konstanta bersama
    data_loader.py       baca data, ekstrak teks, split
    features.py          fitur teks dan fitur buatan sendiri
    evaluate.py          metrik dan sampel kesalahan
    train_classic.py     latih dan simpan model klasik
    llm_classifier.py    klasifikasi lewat Ollama
    compare.py           banding klasik vs LLM pada subset
    demo.py              demo CLI
  tests/
    test_data_loader.py  test_features.py  test_evaluate.py
    test_llm_classifier.py  test_compare.py  test_demo.py
```

---

### Task 0: Setup (Jumat, sesi 1)

**Pemilik:** Orang A (ThinkPad). Orang B dan C melakukan `git clone`, venv, dan unduh dataset sendiri setelah A mem-push.

**Files:**
- Create: `AGENTS.md`, `requirements.txt`, `.gitignore`, `README.md`, `docs/catatan-A.md`, `docs/catatan-B.md`, `docs/catatan-C.md`, `src/__init__.py`, `tests/__init__.py`, `src/config.py`

**Interfaces:**
- Produces di `src/config.py`: `SEED = 42`, `MAX_REQUEST_CHARS = 1000`, `OLLAMA_HOST = "http://localhost:11434"`, `OLLAMA_MODEL = "llama3.2:3b"`, `LLM_TIMEOUT_S = 120`, `SUBSET_PER_CLASS = 50`.

- [ ] **Step 1: Buat folder, venv, dan paket**

Di PowerShell: `py -m venv .venv`, lalu `.venv\Scripts\Activate.ps1`. Bila skrip aktivasi diblokir, panggil `.venv\Scripts\python.exe` langsung di semua perintah. Isi `requirements.txt` dengan: `pandas`, `scikit-learn`, `joblib`, `requests`, `pytest`. Jalankan `pip install -r requirements.txt`.
Verifikasi: `python -c "import pandas, sklearn, joblib, requests; print('ok')"` mencetak `ok`.

- [ ] **Step 2: Tulis `AGENTS.md` persis seperti ini**

```
# Aturan untuk agen koding
- Proyek: detektor serangan web (kuliah Keamanan Informasi). Hanya klasifikasi; jangan membuat kode yang menjalankan atau mengirim payload ke sistem mana pun.
- Bekerja hanya di folder proyek ini. Jangan membaca file di luar folder.
- Jangan menjalankan perintah terminal tanpa persetujuan; jelaskan dulu perintahnya.
- Jangan mengunduh data atau paket selain yang tercantum di requirements.txt dan rencana.
- Tulis kode sederhana dengan komentar bahasa Indonesia singkat; jangan menambah fitur di luar rencana.
- Seed acak selalu 42. Kelas serangan = 1.
- Jelaskan tiap fungsi dalam satu kalimat agar anggota kelompok bisa mengulanginya.
```

- [ ] **Step 3: Atur Antigravity**

Terminal Execution Policy = Request Review, Review Policy = Request Review, buka hanya folder `web-attack-detector`. Verifikasi: minta agen menjalankan `python --version`; Antigravity harus meminta persetujuan Anda dulu.

- [ ] **Step 4: Tulis `src/config.py`** dengan konstanta di atas.

- [ ] **Step 5: Unduh dataset**

Unduh CSIC 2010 dari halaman resmi (`tic.itefi.csic.es/dataset`) ke `data/raw/`. Bila tautan unduhan mati, cari mirror dan catat sumbernya di catatan pribadi (`docs/catatan-<A|B|C>.md`). Verifikasi: catat di catatan pribadi (`docs/catatan-<A|B|C>.md`) nama file dan ukurannya, dan mana yang berisi lalu lintas normal dan mana yang anomali.

- [ ] **Step 6: Commit** (bila git belum ada, lewati dan simpan salinan folder)

```bash
git init
git add .
git commit -m "chore: setup proyek"
```

**Cek pemahaman:** Kenapa agen koding tidak boleh menjalankan perintah tanpa persetujuan di proyek tentang serangan?

---

### Task 1: Pemuat data dan pembagian (Jumat, sesi 1-2)

**Pemilik:** Orang A. Branch `task-1-data`.

**Files:**
- Create: `src/data_loader.py`
- Test: `tests/test_data_loader.py`

**Interfaces:**
- Consumes: `SEED` dari `src/config.py`.
- Produces:
  - `extract_text(raw_request: str) -> str`: hanya baris permintaan dan body, header dibuang, lalu `urllib.parse.unquote_plus` sekali.
  - `load_csic(normal_paths: list[str], anomalous_paths: list[str]) -> pd.DataFrame` dengan kolom `request` (str, hasil `extract_text`) dan `label` (int, 0 atau 1).
  - `split_data(df: pd.DataFrame, test_size: float = 0.3, seed: int = SEED) -> tuple[pd.DataFrame, pd.DataFrame]`: hapus duplikat berdasarkan `request` dulu, lalu pisah terstratifikasi menurut `label`.

- [ ] **Step 1: Periksa format file mentah**

Lihat 30 baris pertama tiap file (`Get-Content -TotalCount 30 data\raw\<file>`). Tulis tiga baris di catatan pribadi (`docs/catatan-<A|B|C>.md`): bagaimana satu permintaan dipisah dari yang berikutnya, di mana letak body, dan apakah ada header. Hasil yang diperiksa: Anda bisa menunjuk di mana satu permintaan berakhir. Keputusan parser bergantung pada ini.

- [ ] **Step 2: Tulis test yang gagal** di `tests/test_data_loader.py`

```python
def test_extract_text_drops_headers():
    raw = "GET /a?q=1 HTTP/1.1\nHost: x\nCookie: JSESSIONID=abc\n\n"
    out = extract_text(raw)
    assert "GET /a?q=1" in out
    assert "Cookie" not in out and "Host" not in out

def test_extract_text_decodes_url_encoding():
    raw = "GET /?q=%27%20OR%201%3D1 HTTP/1.1\nHost: x\n\n"
    assert "' OR 1=1" in extract_text(raw)

def test_split_no_overlap_and_both_classes(small_df):
    # fixture small_df: 100 permintaan normal + 60 serangan, semua unik
    train, test = split_data(small_df)
    assert set(train.request).isdisjoint(set(test.request))
    assert set(train.label) == {0, 1} and set(test.label) == {0, 1}

def test_split_drops_duplicates(small_df):
    df = pd.concat([small_df, small_df.iloc[:5]])
    train, test = split_data(df)
    assert len(train) + len(test) == len(small_df)
```

- [ ] **Step 3: Jalankan, pastikan gagal**

Run: `pytest tests/test_data_loader.py -v`
Expected: FAIL dengan `ImportError` atau `NameError`.

- [ ] **Step 4: Implementasikan ketiga fungsi di `src/data_loader.py`**

Parser pemisah permintaan mengikuti temuan Step 1. `load_csic` memberi label 0 untuk semua `normal_paths` dan 1 untuk semua `anomalous_paths`.

- [ ] **Step 5: Jalankan test, pastikan lulus**

Run: `pytest tests/test_data_loader.py -v`
Expected: 4 passed.

- [ ] **Step 6: Muat data asli dan catat angkanya**

Jalankan `load_csic` pada file asli lalu `split_data`. Catat di catatan pribadi (`docs/catatan-<A|B|C>.md`): jumlah per kelas sebelum dan sesudah hapus duplikat, serta ukuran train dan test. Angka ini muncul di laporan.

- [ ] **Step 7: Commit** (`git commit -m "feat: pemuat data dan split"`)

**Cek pemahaman:** Kenapa header dibuang, dan kenapa duplikat dihapus sebelum split?

---

### Task 2: Fitur (Jumat, sesi 2)

**Pemilik:** Orang B (MSI). Branch `task-2-features`.

**Files:**
- Create: `src/features.py`
- Test: `tests/test_features.py`

**Interfaces:**
- Consumes: `request: str` dari Task 1.
- Produces:
  - `handcrafted_features(requests) -> np.ndarray` berbentuk `(n, 6)`, urutan kolom: `[panjang, n_karakter_khusus, n_persen, n_kata_sql, n_kata_script, n_digit]`. Karakter khusus: `' " < > ; ( ) % = -`. Kata SQL dihitung dengan regex tanpa membedakan huruf besar kecil: `\b(select|union|insert|drop|or|and|sleep)\b|--`. Kata script: `script|alert|onerror|javascript`.
  - `build_feature_union(max_features: int = 20000) -> sklearn.pipeline.FeatureUnion` berisi `TfidfVectorizer(analyzer="char", ngram_range=(2, 4), lowercase=True)` dan fitur buatan sendiri lewat `FunctionTransformer` lalu `StandardScaler(with_mean=False)`.

- [ ] **Step 1: Tulis test yang gagal**

```python
def test_handcrafted_shape_and_order():
    X = handcrafted_features(["GET /a", "GET /?id=1' OR '1'='1"])
    assert X.shape == (2, 6)
    assert X[1, 0] > X[0, 0]      # panjang
    assert X[1, 3] > X[0, 3]      # n_kata_sql

def test_empty_request_does_not_crash():
    assert handcrafted_features([""]).shape == (1, 6)

def test_very_long_request_does_not_crash():
    assert handcrafted_features(["A" * 100000]).shape == (1, 6)

def test_feature_union_fit_transform():
    m = build_feature_union().fit_transform(["GET /a", "GET /b?x=<script>"])
    assert m.shape[0] == 2
```

- [ ] **Step 2: Jalankan, pastikan gagal** (`pytest tests/test_features.py -v`, Expected: FAIL `ImportError`)

- [ ] **Step 3: Implementasikan kedua fungsi di `src/features.py`**

- [ ] **Step 4: Jalankan, pastikan lulus** (Expected: 4 passed)

- [ ] **Step 5: Commit** (`git commit -m "feat: fitur teks dan fitur buatan sendiri"`)

**Cek pemahaman:** Apa yang ditangkap TF-IDF n-gram karakter yang tidak ditangkap hitungan kata SQL, dan sebaliknya?

---

### Task 3: Latih model klasik dan evaluasi (Jumat, sesi 2 sampai malam; dibagi 3a dan 3b)

**Pemilik:** Step 1-4 (`evaluate.py`) Orang B, branch `task-3a-evaluate`. Step 5-8 (`train_classic.py`) Orang A, branch `task-3b-train`, setelah Task 1, 2, dan 3a digabung ke `main`.

**Files:**
- Create: `src/evaluate.py`, `src/train_classic.py`
- Test: `tests/test_evaluate.py`

**Interfaces:**
- Consumes: `load_csic`, `split_data` (Task 1), `build_feature_union` (Task 2).
- Produces:
  - `compute_metrics(y_true, y_pred) -> dict` dengan kunci `precision`, `recall`, `f1`, `tn`, `fp`, `fn`, `tp` (serangan = 1).
  - `dump_errors(test_df: pd.DataFrame, y_pred, out_prefix: str, n: int = 20) -> tuple[pd.DataFrame, pd.DataFrame]` mengembalikan `(fp_df, fn_df)` (sampel acak ber-seed, maksimal `n` baris tiap jenis) dan menyimpan CSV `<out_prefix>_fp.csv` dan `<out_prefix>_fn.csv`.
  - `build_pipeline(kind: str) -> sklearn.pipeline.Pipeline` untuk `kind` di `{"logreg", "rf"}`. Isinya: feature union lalu classifier. `logreg` = `LogisticRegression(max_iter=1000, class_weight="balanced")` dengan 20000 fitur TF-IDF. `rf` = `RandomForestClassifier(n_estimators=100, n_jobs=-1, random_state=SEED)` dengan 5000 fitur TF-IDF (agar muat di RAM laptop).
  - `main()` di `train_classic.py`: melatih kedua model pada train, menyimpan `models/logreg.joblib` dan `models/rf.joblib`, menulis `reports/classic_metrics.json` dan CSV kesalahan per model.

- [ ] **Step 1: Tulis test yang gagal**

```python
def test_compute_metrics_known_case():
    m = compute_metrics([1, 1, 0, 0], [1, 0, 1, 0])
    assert (m["tp"], m["fp"], m["fn"], m["tn"]) == (1, 1, 1, 1)
    assert m["precision"] == 0.5 and m["recall"] == 0.5 and m["f1"] == 0.5

def test_dump_errors_picks_right_rows(tmp_path):
    df = pd.DataFrame({"request": list("abcd"), "label": [1, 1, 0, 0]})
    fp, fn = dump_errors(df, [1, 0, 1, 0], str(tmp_path / "x"))
    assert list(fp.request) == ["c"] and list(fn.request) == ["b"]
```

- [ ] **Step 2: Jalankan, pastikan gagal** (`pytest tests/test_evaluate.py -v`, Expected: FAIL `ImportError`)

- [ ] **Step 3: Implementasikan `compute_metrics` dan `dump_errors` di `src/evaluate.py`**

- [ ] **Step 4: Jalankan, pastikan lulus** (Expected: 2 passed)

- [ ] **Step 5: Implementasikan `build_pipeline` dan `main` di `src/train_classic.py`**

- [ ] **Step 6: Latih model asli**

Run: `python -m src.train_classic`
Expected: tercetak tabel precision, recall, F1 untuk `logreg` dan `rf`, dan file di `models/` dan `reports/` terbentuk. Bila `rf` lebih dari 10 menit atau kehabisan memori, turunkan `n_estimators` ke 50 dan catat di catatan pribadi (`docs/catatan-<A|B|C>.md`).

- [ ] **Step 7: Periksa hasil yang terlalu bagus**

Bila F1 salah satu model 0,99 atau lebih, jangan senang dulu. Cetak 15 koefisien terbesar `logreg`, ambil 10 sampel yang diprediksi benar, lalu tulis di catatan pribadi (`docs/catatan-<A|B|C>.md`) fitur apa yang paling berpengaruh dan apakah itu masuk akal (lihat Review Focus no. 1).

- [ ] **Step 8: Commit dan push, termasuk `reports/`** (`git commit -m "feat: model klasik dan evaluasi"`), agar B dan C bisa memakai CSV kesalahan untuk Task 4.

**Cek pemahaman:** Kenapa serangan dijadikan kelas positif, dan apa arti FP dan FN dalam konteks aplikasi bank?

---

### Task 4: Analisis FP/FN (Jumat malam, manual, tanpa kode)

**Pemilik:** A, B, dan C, dibagi rata.

**Files:**
- Create: `reports/error_analysis_A.md`, `reports/error_analysis_B.md`, `reports/error_analysis_C.md` (satu per orang), lalu digabung jadi `reports/error_analysis.md`

- [ ] **Step 1: Pilih model terbaik menurut F1** dan baca `reports/<model>_fp.csv` dan `reports/<model>_fn.csv`.

- [ ] **Step 2: Bagi baris di antara tiga anggota; tiap orang mengisi tabel di berkasnya sendiri**

Kolom: `id | jenis (FP/FN) | cuplikan permintaan | kategori penyebab | dugaan kenapa model keliru`. Contoh kategori: normal tapi memuat tanda kutip, serangan yang disamarkan, serangan sangat pendek. Hasil yang diperiksa: minimal 20 FP dan 20 FN terisi (atau semuanya bila kesalahannya kurang dari 20), masing-masing punya kategori.

- [ ] **Step 3: Orang A menggabungkan ketiga berkas menjadi `reports/error_analysis.md`, lalu menulis ringkasan lima baris**: jumlah per kategori dan dua kategori kesalahan yang paling sering.

- [ ] **Step 4: Sesi saling menjelaskan 15 menit**: tiap anggota menjelaskan dua baris miliknya dengan kata sendiri.

- [ ] **Step 5: Commit** (`git commit -m "docs: analisis FP/FN"`)

**Cek pemahaman:** Kategori kesalahan mana yang paling berbahaya untuk bank, FP atau FN, dan kenapa?

---

### Task 5: Klasifikasi LLM lokal (Jumat, paralel dengan Task 1-3)

**Pemilik:** Orang C (Lenovo RTX 4050). Branch `task-5-llm`. Kode dan test tidak butuh Ollama; Step 5-6 butuh.

**Files:**
- Create: `src/llm_classifier.py`
- Test: `tests/test_llm_classifier.py`

**Interfaces:**
- Consumes: `OLLAMA_HOST`, `OLLAMA_MODEL`, `LLM_TIMEOUT_S`, `MAX_REQUEST_CHARS` dari `src/config.py`.
- Produces:
  - `build_prompt(request: str) -> str`: memotong `request` ke `MAX_REQUEST_CHARS`, menyuruh model menjawab hanya `NORMAL` atau `ATTACK`.
  - `parse_label(raw: str) -> int | None`: token huruf pertama (tanpa membedakan huruf besar kecil): `ATTACK` → 1, `NORMAL` → 0, selain itu `None`.
  - `classify_request(request: str, model: str = OLLAMA_MODEL) -> tuple[int | None, float]`: mengembalikan `(label, detik)`. Memanggil `POST {OLLAMA_HOST}/api/generate` dengan `{"model": model, "prompt": ..., "stream": False, "options": {"temperature": 0, "num_predict": 5}}` dan `timeout=LLM_TIMEOUT_S`. `requests.ConnectionError` diubah menjadi `RuntimeError("Ollama tidak berjalan di <host>")`.

- [ ] **Step 1: Tulis test yang gagal**

```python
@pytest.mark.parametrize("raw,exp", [("ATTACK", 1), (" attack.", 1), ("NORMAL", 0),
                                      ("normal request", 0), ("I think this is bad", None), ("", None)])
def test_parse_label(raw, exp):
    assert parse_label(raw) == exp

def test_build_prompt_contains_request_and_labels():
    p = build_prompt("GET /a HTTP/1.1")
    assert "GET /a HTTP/1.1" in p and "NORMAL" in p and "ATTACK" in p

def test_build_prompt_truncates_and_handles_empty():
    assert len(build_prompt("A" * 100000)) < 100000
    assert isinstance(build_prompt(""), str)

def test_classify_request_parses_response(monkeypatch):
    monkeypatch.setattr("requests.post", lambda *a, **k: FakeResp({"response": "ATTACK"}))
    label, secs = classify_request("GET /?id=1' OR '1'='1")
    assert label == 1 and secs >= 0

def test_classify_request_ollama_down(monkeypatch):
    def boom(*a, **k): raise requests.ConnectionError()
    monkeypatch.setattr("requests.post", boom)
    with pytest.raises(RuntimeError, match="Ollama tidak berjalan"):
        classify_request("x")
```

- [ ] **Step 2: Jalankan, pastikan gagal** (`pytest tests/test_llm_classifier.py -v`, Expected: FAIL `ImportError`)

- [ ] **Step 3: Implementasikan ketiga fungsi di `src/llm_classifier.py`**

- [ ] **Step 4: Jalankan, pastikan lulus** (Expected: 10 passed)

- [ ] **Step 5: Pasang Ollama dan unduh model (Laptop C)**

Tutup aplikasi berat dulu. Pasang Ollama dari situs resminya. Biarkan Ollama hanya mendengarkan di localhost (bawaan): jangan diubah agar bisa diakses dari jaringan, apalagi ada Tailscale di laptop ini. Jalankan `ollama pull llama3.2:3b`, lalu `ollama list` untuk memastikan nama modelnya. Bila namanya berbeda, ubah `OLLAMA_MODEL` di `config.py` (commit terpisah, kabari yang lain). Verifikasi GPU terpakai: jalankan `ollama run llama3.2:3b "Jawab satu kata: apa ibu kota Indonesia?"`, lalu di terminal lain jalankan `ollama ps`. Kolom prosesor harus menyebut GPU. Bila hanya CPU, perbarui driver NVIDIA dan mulai ulang Ollama sebelum lanjut.

- [ ] **Step 6: Uji kecepatan pada 10 contoh**

Task 1 belum tentu sudah digabung, jadi susun sendiri 10 permintaan contoh berpanjang 300 sampai 600 karakter (tambahkan parameter dan nilai), campuran normal dan serangan. Panggil `classify_request` pada ke-10 contoh dan cetak rata-rata detik per permintaan. Aturan keputusan: rata-rata 5 detik atau kurang → `SUBSET_PER_CLASS = 200`. Antara 5 dan 15 detik → biarkan 100. Lebih dari 15 detik → periksa `ollama ps` (apakah GPU terpakai) atau coba `llama3.2:1b`, lalu catat. Ubah `SUBSET_PER_CLASS` di `config.py` dengan commit terpisah. Ulangi pengukuran kecepatan di Task 6 memakai data asli. Catat angkanya di catatan pribadi.

- [ ] **Step 7: Commit** (`git commit -m "feat: klasifikasi LLM lokal"`)

**Cek pemahaman:** Kenapa suhu 0 dan keluaran dibatasi satu kata, dan apa yang terjadi bila LLM menjawab kalimat panjang?

---

### Task 6: Perbandingan klasik vs LLM (Sabtu, pagi)

**Pemilik:** Orang C. Branch `task-6-compare`, setelah Task 3b digabung. A dan B meninjau hasilnya.

**Files:**
- Create: `src/compare.py`
- Test: `tests/test_compare.py`

**Interfaces:**
- Consumes: `compute_metrics` (Task 3), `classify_request` (Task 5), model `models/<best>.joblib` (Task 3), test split (Task 1).
- Produces:
  - `sample_subset(test_df: pd.DataFrame, n_per_class: int = SUBSET_PER_CLASS, seed: int = SEED) -> pd.DataFrame`: `n_per_class` baris tiap label, deterministik.
  - `run_comparison(subset: pd.DataFrame, classic_pipeline, classify=classify_request) -> pd.DataFrame` dengan kolom `request`, `label`, `pred_classic`, `pred_llm`, `llm_unparsed` (bool), `llm_seconds`. Keluaran `None` dari LLM dipetakan ke `pred_llm = 0` dan `llm_unparsed = True`.
  - `main()`: menulis `reports/comparison.csv` dan `reports/comparison_metrics.json` (metrik kedua model pada subset, rata-rata detik LLM, jumlah `llm_unparsed`).

- [ ] **Step 0: Siapkan Laptop C**: `git pull`, unduh dataset ke `data/raw/`, jalankan `python -m src.train_classic` (seed 42 membuat hasilnya sama dengan di laptop A), dan pastikan Ollama berjalan (`ollama ps`).

- [ ] **Step 1: Tulis test yang gagal**

```python
def test_sample_subset_balanced_deterministic(test_df):
    a = sample_subset(test_df, n_per_class=5)
    b = sample_subset(test_df, n_per_class=5)
    assert a.label.value_counts().to_dict() == {0: 5, 1: 5}
    assert list(a.request) == list(b.request)
    assert set(a.request) <= set(test_df.request)

def test_run_comparison_with_fake_llm(subset, tiny_pipeline):
    out = run_comparison(subset, tiny_pipeline, classify=lambda r: (1, 0.1))
    assert (out.pred_llm == 1).all() and not out.llm_unparsed.any()

def test_unparsed_is_counted_not_hidden(subset, tiny_pipeline):
    out = run_comparison(subset, tiny_pipeline, classify=lambda r: (None, 0.1))
    assert out.llm_unparsed.all() and (out.pred_llm == 0).all()
```

- [ ] **Step 2: Jalankan, pastikan gagal** (`pytest tests/test_compare.py -v`, Expected: FAIL `ImportError`)

- [ ] **Step 3: Implementasikan `sample_subset`, `run_comparison`, dan `main` di `src/compare.py`**

- [ ] **Step 4: Jalankan test, pastikan lulus** (Expected: 3 passed)

- [ ] **Step 5: Jalankan perbandingan asli**

Run: `python -m src.compare`
Expected: `reports/comparison.csv` dan `reports/comparison_metrics.json` terbentuk. Bila macet atau jauh lebih lambat dari uji 10 sampel, hentikan, perkecil subset, dan catat.

- [ ] **Step 6: Catat temuan di catatan pribadi (`docs/catatan-<A|B|C>.md`)**

Tulis metrik kedua model, jumlah `llm_unparsed`, rata-rata detik LLM, dan lima kasus tempat LLM benar dan klasik salah (dan sebaliknya). Itu bahan video.

- [ ] **Step 7: Commit** (`git commit -m "feat: perbandingan klasik vs LLM"`)

**Cek pemahaman:** Kenapa kedua model dibandingkan pada subset yang sama persis, dan apa arti `llm_unparsed` yang tinggi?

---

### Task 7: Demo CLI (Sabtu, pagi-siang)

**Pemilik:** Orang B. Branch `task-7-demo`, setelah Task 3b dan Task 5 digabung.

**Files:**
- Create: `src/demo.py`
- Test: `tests/test_demo.py`

**Interfaces:**
- Consumes: `build_pipeline` (Task 3), `classify_request` (Task 5), `models/<best>.joblib`.
- Produces:
  - `predict_classic(request: str, pipeline) -> tuple[int, float]`: `(label, probabilitas serangan)`. Masukannya dalam format yang sama dengan fitur latih (baris permintaan dan body, tanpa header).
  - `main(argv: list[str] | None = None) -> int` dengan argumen `--request TEXT`, `--llm` (opsional), dan `--model-path` (default `models/logreg.joblib`, ganti ke model terbaik). Keluaran: `Model klasik: ATTACK (p=0.97)`, dan bila `--llm`: `LLM: ATTACK (4.2 s)`. Bila Ollama tidak berjalan, cetak peringatan lalu lanjut dengan hasil klasik, kode keluar tetap 0.

- [ ] **Step 1: Tulis test yang gagal**

```python
def test_predict_classic_returns_valid(tiny_pipeline):
    for text in ["GET /a HTTP/1.1", "", "A" * 100000]:
        label, p = predict_classic(text, tiny_pipeline)
        assert label in (0, 1) and 0.0 <= p <= 1.0

def test_main_prints_classic_verdict(capsys, tiny_model_path):
    code = main(["--request", "GET /a HTTP/1.1", "--model-path", tiny_model_path])
    assert code == 0 and "Model klasik:" in capsys.readouterr().out

def test_main_continues_when_ollama_down(capsys, tiny_model_path, monkeypatch):
    monkeypatch.setattr("src.demo.classify_request",
                        lambda r: (_ for _ in ()).throw(RuntimeError("Ollama tidak berjalan")))
    code = main(["--request", "GET /a HTTP/1.1", "--llm", "--model-path", tiny_model_path])
    out = capsys.readouterr().out
    assert code == 0 and "Model klasik:" in out and "Ollama tidak berjalan" in out
```

- [ ] **Step 2: Jalankan, pastikan gagal** (`pytest tests/test_demo.py -v`, Expected: FAIL `ImportError`)

- [ ] **Step 3: Implementasikan `predict_classic` dan `main` di `src/demo.py`** dengan `argparse`.

- [ ] **Step 4: Jalankan, pastikan lulus** (Expected: 3 passed). Lalu `pytest -v` untuk seluruh suite, semuanya harus lulus.

- [ ] **Step 5: Coba demo dengan contoh**

```
python -m src.demo --request "GET /index.html HTTP/1.1" --llm
python -m src.demo --request "GET /item?id=1' OR '1'='1 HTTP/1.1" --llm
```
Yang diharapkan (bukan jaminan): contoh pertama NORMAL, contoh kedua ATTACK. Bila model salah, catat di catatan pribadi (`docs/catatan-<A|B|C>.md`) sebagai temuan nyata, jangan disembunyikan.

- [ ] **Step 6: Latihan demo**

Demo utama dijalankan di Laptop C (ada GPU dan Ollama). Tiap anggota menjalankan demo sekali dan menjelaskan keluarannya. Siapkan 3 contoh: satu normal, satu serangan yang terdeteksi, satu yang salah (untuk menunjukkan analisis FP/FN).

- [ ] **Step 7: Commit** (`git commit -m "feat: demo CLI"`)

**Cek pemahaman:** Kenapa demo tetap jalan bila Ollama mati?

---

### Task 8: Setelah demo, sebelum UAS (checklist, tidak dirinci)

**Pemilik:** A, B, dan C; tiap orang mengerjakan bagian miliknya, A merangkum laporan.

- [ ] Naikkan subset LLM (200 normal dan 200 serangan, atau lebih bila cepat), lalu jalankan ulang Task 6. Opsional: coba model lebih besar (7B sampai 8B) bila muat di VRAM, dan bandingkan.
- [ ] Rapikan analisis FP/FN dan bandingkan jenis kesalahan klasik vs LLM.
- [ ] Tulis bagian keterbatasan: CSIC 2010 adalah dataset lama dan buatan, tidak memuat serangan modern, dan hasilnya belum tentu berlaku di lalu lintas nyata.
- [ ] Rekam video 5 sampai 10 menit: semua anggota tampil dan menjelaskan bagiannya sendiri.
- [ ] Tulis laporan (pendahuluan, metode, pembahasan, kesimpulan). Sebelum mengutip angka serangan FortiGuard, ambil dari laporan primernya.

---

## Self-Review

- **Cakupan spec:** data dan fitur (Task 1-2), model klasik dan evaluasi P/R/F1 (Task 3), analisis FP/FN (Task 4), LLM lokal dan perbandingan (Task 5-6), demo (Task 7), video dan laporan (Task 8), etika dan pengaturan Antigravity (Task 0 dan Global Constraints). Pengujian di DVWA sengaja tidak ada, sesuai keputusan setelah melihat spek laptop.
- **Konsistensi tipe:** `extract_text`, `load_csic`, `split_data`, `compute_metrics`, `dump_errors`, `build_pipeline`, `classify_request`, `parse_label`, `sample_subset`, `run_comparison`, `predict_classic` dipakai dengan nama dan parameter yang sama di semua task.
- **Review Focus:** kelima baris punya test di task yang disebut.
- **Tiga laptop:** tiap task punya pemilik dan branch, urutan merge ditetapkan di bagian Pembagian, dan tidak ada dua orang yang mengedit berkas yang sama (fixture ada di file test masing-masing, catatan di berkas pribadi).
- **Proporsi:** isi tiap langkah berupa tanda tangan fungsi, nama test, dan nilai dari spec. Badan fungsi sengaja tidak ditulis, karena itu bagian yang dikerjakan dan dijelaskan oleh kalian.
