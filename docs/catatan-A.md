# Catatan Orang A

## Task 0 — Sumber dan Verifikasi Dataset CSIC 2010

- **Halaman resmi:** `https://tic.itefi.csic.es/dataset/` gagal dijangkau (`Could not resolve host: tic.itefi.csic.es`).
- **Mirror yang digunakan:**
  - `https://raw.githubusercontent.com/Monkey-D-Groot/Machine-Learning-on-CSIC-2010/master/` (`normalTrafficTraining.txt` dan `anomalousTrafficTest.txt`; berkas `normalTrafficTest.txt` di mirror ini mengembalikan `404: Not Found`).
  - `https://raw.githubusercontent.com/msudol/Web-Application-Attack-Datasets/master/OriginalDataSets/csic_2010/` (`normalTrafficTest.txt`).
- **Berkas di `data/raw/`:**
  - `normalTrafficTraining.txt` — `20.640.988` byte — lalu lintas **normal** (data latih asli CSIC 2010, label 0).
  - `normalTrafficTest.txt` — `20.151.204` byte — lalu lintas **normal** (data uji asli CSIC 2010, label 0).
  - `anomalousTrafficTest.txt` — `16.090.299` byte — lalu lintas **anomali / serangan** (data uji serangan CSIC 2010, label 1).

## Task 1 — Format Berkas Mentah & Statistik Split

- **Format mentah:** Setiap permintaan diawali baris permintaan (`GET/POST ... HTTP/1.1`), diikuti header (`User-Agent`, `Host`, `Cookie`, dll.), lalu baris kosong (`\n\n`). Permintaan `GET` dipisahkan dua baris kosong, sedangkan permintaan `POST` memiliki satu baris body setelah baris kosong pertama.
- **Jumlah sebelum hapus duplikat:** `97.065` permintaan (`0` normal = `72.000`, `1` serangan = `25.065`).
- **Jumlah setelah hapus duplikat:** `34.604` permintaan unik (`0` normal = `18.640`, `1` serangan = `15.964`).
- **Split `train` (70%):** `24.222` (`0` = `13.048`, `1` = `11.174`).
- **Split `test` (30%):** `10.382` (`0` = `5.592`, `1` = `4.790`).

## Task 3b — Hasil Pelatihan Model Klasik

| Model | Precision | Recall | F1 | TP | FP | FN | TN |
|---|---:|---:|---:|---:|---:|---:|---:|
| `logreg` | 0.9894 | 0.8741 | 0.9282 | 4187 | 45 | 603 | 5547 |
| `rf` | 0.9811 | 0.9315 | 0.9557 | 4462 | 86 | 328 | 5506 |

- Pelatihan berjalan normal dengan `n_estimators=100` pada `rf` (tidak kehabisan memori atau melebihi 10 menit).
- Kedua model memiliki F1 di bawah `0.99` (artinya tidak ada kebocoran artefak header). Model terbaik berdasarkan F1 adalah `rf` (`0.9557`) yang langsung akan digunakan sebagai dasar analisis FP/FN di Task 4.
