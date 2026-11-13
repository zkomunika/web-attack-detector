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
