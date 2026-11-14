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

### Metrik pada Subset (hasil python -m src.compare)

| Model | Precision | Recall | F1 | TP | FP | FN | TN |
|---|---:|---:|---:|---:|---:|---:|---:|
| Klasik (logreg) | 1.000 | 0.895 | 0.945 | 179 | 0 | 21 | 200 |
| LLM (llama3.2:3b) | 0.492 | 0.890 | 0.633 | 178 | 184 | 22 | 16 |

- LLM rata-rata: 2.37 detik/permintaan
- LLM tidak terparsing: 0 dari 400 (semua keluaran berupa format NORMAL/ATTACK yang valid)

### Lima kasus LLM benar, klasik salah (FN klasik)

| # | Cuplikan permintaan | Label | Pred klasik | Pred LLM | Analisis singkat |
|---|---|:---:|:---:|:---:|---|
| [202] | `POST .../autenticar.jsp modo=entrar&login=k?ar+ie&pwd=40c7c0o...` | 1 | 0 | 1 | Karakter anomali `?` dan `+` di kolom login; logreg melewatkannya karena tidak ada kata kunci SQL besar, namun LLM menangkapnya. |
| [218] | `POST .../registro.jsp ...&ciudad=Ca*sar+es&cp=47182...` | 1 | 0 | 1 | Karakter wildcard `*` dan `+` disisipkan di kolom kota; diabaikan oleh logreg, terdeteksi oleh LLM. |
| [238] | `POST .../editar.jsp ...&dni=96068417Q?&direccion=...` | 1 | 0 | 1 | Tanda tanya `?` di akhir nomor DNI/identitas; anomali format halus yang dikenali LLM. |
| [239] | `POST .../editar.jsp modo=registro&login=+mel/hem&password=quEratItiS...` | 1 | 0 | 1 | Karakter anomali `+` dan `/` di username login; LLM menandai sebagai serangan. |
| [250] | `GET .../autenticar.jsp?modo=entrar&login=tahani97&pwd=buja/RR,N...` | 1 | 0 | 1 | Karakter `/` dan `,` pada parameter password yang mencurigakan; terlewat oleh logreg. |

### Lima kasus klasik benar, LLM salah (FP LLM)

| # | Cuplikan permintaan | Label | Pred klasik | Pred LLM | Analisis singkat |
|---|---|:---:|:---:|:---:|---|
| [0] | `POST .../registro.jsp modo=registro&login=horatio&password=Bál!tEo...` | 0 | 0 | 1 | Permintaan pendaftaran normal dengan password bertanda seru `!`; LLM terlalu sensitif dan menganggapnya serangan (FP). |
| [1] | `POST .../editar.jsp ...&ciudad=Lorcha/Orxa, l'&...` | 0 | 0 | 1 | Nama kota bahasa Spanyol normal yang memuat garis miring `/` dan kutip `'`; LLM salah mengira sebagai SQLi. |
| [2] | `GET .../autenticar.jsp?modo=entrar&login=smoot&pwd=desvanecido...` | 0 | 0 | 1 | Permintaan login normal via query string; LLM menganggap pengiriman kredensial di URL sebagai serangan. |
| [3] | `GET .../anadir.jsp?id=1&nombre=Vino Rioja&precio=85&cantidad=24...` | 0 | 0 | 1 | Permintaan keranjang belanja normal; parameter angka dan teks belanjaan salah dicurigai oleh LLM. |
| [5] | `POST .../autenticar.jsp modo=entrar&login=asme&pwd=r57qu0ller3...` | 0 | 0 | 1 | Form login normal dengan kombinasi password acak huruf-angka; LLM menilainya mencurigakan. |

### Temuan dan Catatan

1. **Performa & Kecepatan:**
   - Inferensi LLM lokal (`llama3.2:3b` pada GPU RTX 4050) memerlukan rata-rata **2.37 detik per permintaan** (total durasi ~15,8 menit untuk 400 sampel).
   - Parsing output LLM 100% sukses (0 unparsed dari 400).
2. **Perbandingan Presisi & Recall:**
   - Model klasik (`logreg`) sangat presisi (**Precision = 1.000, FP = 0**), artinya tidak ada satu pun lalu lintas normal yang salah diblokir.
   - LLM memiliki recall setara (**Recall = 0.890 vs 0.895**), namun mengalami masalah **False Positive yang sangat tinggi (FP = 184 dari 200 sampel normal)**, menyebabkan **Precision anjlok ke 0.492** dan **F1 hanya 0.633**.
3. **Karakteristik Kesalahan:**
   - **Kelebihan LLM:** Mampu mendeteksi anomali karakter tunggal atau format yang tidak wajar (`?`, `*`, `+` pada username/DNI) yang terlewat oleh model n-gram klasik (21 kasus FN klasik berhasil diselamatkan LLM).
   - **Kelemahan LLM:** Terlalu paranoid (*false alarm* tinggi); teks normal dengan parameter otentikasi (`login`, `pwd`), karakter Spanyol, atau tanda baca wajar langsung dicap sebagai `ATTACK`. Untuk deployment nyata, model klasik jauh lebih aman bagi pengalaman pengguna (tidak memblokir pengguna asli).


---

## Task 7 — Uji Coba Demo CLI (Step 5)

**Tanggal:** 14 November 2026
**Model:** `models/rf.joblib` (Random Forest, seed 42)
**LLM:** `llama3.2:3b` via Ollama lokal (GPU RTX 4050)
**Branch:** `task-4-c`

### Perintah dan Hasil

**Demo (a) — Permintaan normal (`GET /index.html HTTP/1.1`):**

```
$ python -m src.demo --request "GET /index.html HTTP/1.1" --llm --model-path models/rf.joblib
Model klasik: ATTACK (p=0.98)
LLM: NORMAL (6.1 s)
```

**Temuan:** Model RF salah prediksi (FP) — `GET /index.html` yang sangat pendek dan tanpa parameter justru diprediksi ATTACK dengan probabilitas tinggi (p=0.98). LLM benar menyebutnya NORMAL. Ini menunjukkan kelemahan model RF: permintaan sangat pendek tanpa parameter yang dikenal menghasilkan n-gram asing yang terpetakan ke pola serangan di training data.

---

**Demo (b) — Permintaan SQL injection (`GET /item?id=1' OR '1'='1 HTTP/1.1`):**

```
$ python -m src.demo --request "GET /item?id=1' OR '1'='1 HTTP/1.1" --llm --model-path models/rf.joblib
Model klasik: ATTACK (p=0.94)
LLM: ATTACK (2.5 s)
```

**Temuan:** Kedua model benar — payload SQLi klasik dengan `' OR '1'='1` terdeteksi sebagai ATTACK oleh RF (p=0.94) maupun LLM. Ini kasus ideal di mana model klasik cepat (inferensi lokal) dan akurat untuk serangan dengan pola jelas.

---

**Demo (c) — Contoh FN dari `rf_fn.csv` (serangan yang lolos dari RF):**

```
$ python -m src.demo --request "GET http://localhost:8080/tienda1/miembros/editar.jsp?modo=registro&login=simser&password=Canj4l9n&nombre=Kimberley&apellidos=Romaso&email=partsalev@easyviaggio.web&dni=A'0A5223S&direccion=Calle Alfonso Paso 143 &ciudad=Constantina&cp=42138&provincia=Lleida&ntc=9910614404544138&B1=Registrar HTTP/1.1" --llm --model-path models/rf.joblib
Model klasik: NORMAL (p=0.24)
LLM: ATTACK (2.5 s)
```

**Temuan:** Contoh FN nyata dari dataset — permintaan pendaftaran panjang dengan sisipan tanda kutip tunggal `'` di field `dni` (`dni=A'0A5223S`) adalah SQL injection, namun RF hanya memberinya probabilitas serangan 0.24 dan memprediksi NORMAL. LLM berhasil mendeteksinya sebagai ATTACK. Ini bahan demo yang kuat untuk menunjukkan analisis FP/FN: satu karakter sisipan di antara banyak parameter panjang "mengencerkan" sinyal n-gram hingga di bawah ambang RF.

---

### Ringkasan Uji Demo

| Contoh | Perintah ringkas | Hasil RF | Hasil LLM | Benar? |
|---|---|---|---|---|
| (a) `GET /index.html HTTP/1.1` | `--llm --model-path models/rf.joblib` | ATTACK (p=0.98) FP | NORMAL (6.1 s) | LLM benar, RF salah |
| (b) `GET /item?id=1' OR '1'='1 HTTP/1.1` | `--llm --model-path models/rf.joblib` | ATTACK (p=0.94) | ATTACK (2.5 s) | Keduanya benar |
| (c) GET editar.jsp + dni=A'0A5223S | `--llm --model-path models/rf.joblib` | NORMAL (p=0.24) FN | ATTACK (2.5 s) | LLM benar, RF salah |
