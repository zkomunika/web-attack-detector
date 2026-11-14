# Analisis FP/FN Bagian C (Random Forest)

**Pemilik:** Orang C (Laptop Lenovo 83S0)
**Model:** `rf` (Random Forest, seed 42)
**Sumber data:** `reports/rf_fp.csv` baris indeks 14–19 (FP-15 s/d FP-20) dan `reports/rf_fn.csv` baris indeks 14–19 (FN-15 s/d FN-20)

---

## Tabel Analisis

| id | jenis (FP/FN) | cuplikan permintaan | kategori penyebab | dugaan kenapa model keliru |
|---|---|---|---|---|
| FP-15 | FP | `POST /anadir.jsp` — `id=3&nombre=Jam?n Ib?rico&precio=100&cantidad=0&B1=A?adir al carrito` | Karakter non-ASCII / pola parameter keranjang | Karakter Latin-1 yang ter-encode rusak (`?` menggantikan `ñ`, `é`) membentuk pola n-gram langka yang mirip payload encoding, sehingga RF salah menandai permintaan belanja normal ini sebagai serangan. |
| FP-16 | FP | `POST /anadir.jsp` — `id=3&nombre=Queso Manchego&precio=100&cantidad=9&B1=A?adir al carrito` | Karakter non-ASCII / pola parameter keranjang | Sama seperti FP-15: karakter tombol "Añadir al carrito" ter-encode menjadi `?`, menghasilkan tri-gram/4-gram yang asing bagi model dan memicu prediksi serangan. |
| FP-17 | FP | `GET /pagar.jsp?modo=insertar&precio=9335&B1=Pasar por caja` | Permintaan pendek dengan nilai numerik besar | Nilai harga `precio=9335` yang besar dan frase `caja` (kotak/kas) tampak anomali di distribusi training; model tidak cukup melihat variasi angka harga, sehingga pola n-gram angka panjang memicu FP. |
| FP-18 | FP | `GET /pagar.jsp?modo=insertar&precio=3582&B1=Confirmar` | Permintaan pendek dengan nilai numerik besar | Pola `precio=` diikuti angka 4 digit membentuk n-gram yang mirip parameter serangan bertipe injeksi numerik; model RF kurang terlatih membedakan nilai harga valid dari nilai rekayasa. |
| FP-19 | FP | `POST /autenticar.jsp` — `modo=entrar&login=niu&pwd=bRoquel&remember=on&B1=Entrar` | Kombinasi password alfanumerik campuran huruf besar-kecil | Password `bRoquel` dengan huruf campur dan nilai `remember=on` membentuk n-gram karakter yang jarang muncul di data normal, membuat RF mengasosiasikannya dengan payload obfuscation. |
| FP-20 | FP | `POST /pagar.jsp` — `modo=insertar&precio=2&B1=Pasar por caja` | Permintaan pendek dengan nilai numerik besar | Harga sangat kecil (`precio=2`) dikombinasikan dengan frase `caja` menciptakan pola yang tidak umum; model terlalu sensitif terhadap kombinasi parameter checkout yang pendek dan nilai tidak wajar. |
| FN-15 | FN | `GET /editar.jsp?...&dni=A'0A5223S&...` | Karakter sisipan tunggal | Tanda kutip tunggal `'` yang disisipkan dalam nilai field `dni` adalah ciri khas SQL injection, namun karena hanya satu karakter di antara banyak parameter panjang, kontribusi n-gram-nya kecil dan RF melewatkannya. |
| FN-16 | FN | `POST /anadir.jsp` — `precio=85/&cantidad=7&B1=A?adir al carrito` | Karakter sisipan tunggal | Karakter garis miring `/` yang disisipkan setelah nilai numerik `precio=85/` adalah anomali halus; RF tidak menangkapnya karena n-gram karakter di sekitarnya (angka+slash) terlalu mirip URL path biasa. |
| FN-17 | FN | `POST /autenticar.jsp` — `pwd=/buldar&remember=off` | Karakter sisipan tunggal | Garis miring `/` di awal nilai password (`/buldar`) adalah teknik traversal/injeksi yang disamarkan; RF mengklasifikasikan login form biasa, dan slash satu karakter tidak cukup menggeser skor fitur melewati ambang serangan. |
| FN-18 | FN | `POST /editar.jsp` — `password=+laur938&nombre=Jorda?na&direccion=...1?C` | Karakter sisipan ganda pada beberapa field | Dua karakter anomali (`+` di password dan `?` pada beberapa field) tersebar di banyak parameter; masing-masing karakter menghasilkan sinyal lemah dan RF tidak mengakumulasinya menjadi keputusan serangan. |
| FN-19 | FN | `PUT /registro.jsp` — `modo=registro&login=alane&password=9u7Je&...` | Manipulasi metode HTTP | Metode `PUT` pada endpoint pendaftaran yang normalnya hanya menerima `POST`/`GET` adalah anomali jelas, namun fitur teks (n-gram karakter) tidak menyertakan kata metode HTTP secara eksplisit sehingga RF mengabaikannya. |
| FN-20 | FN | `GET /registro.jsp?...&ciudad=Villabasta de Vald/?avia&...` | Karakter sisipan tunggal | Kombinasi `/?` yang tertanam di nilai `ciudad` merupakan upaya path traversal/injeksi yang disamarkan dalam teks nama kota; konteks field yang panjang "mengencerkan" sinyal anomali sehingga RF gagal mendeteksinya. |

---

## Ringkasan Kategori

| Kategori penyebab | Jumlah | Jenis |
|---|:---:|---|
| Karakter non-ASCII / pola parameter keranjang | 2 | FP |
| Permintaan pendek dengan nilai numerik besar | 3 | FP |
| Kombinasi password alfanumerik campuran | 1 | FP |
| Karakter sisipan tunggal | 5 | FN |
| Karakter sisipan ganda pada beberapa field | 1 | FN |
| Manipulasi metode HTTP | 1 | FN |

**Dua kategori paling sering:**
1. **Karakter sisipan tunggal (FN)** — Model RF berbasis n-gram tidak sensitif terhadap satu karakter anomali (`'`, `/`, `+`) yang tersebar di parameter panjang.
2. **Permintaan pendek dengan nilai numerik besar (FP)** — Pola checkout/pembayaran normal menghasilkan n-gram yang mirip payload injeksi numerik, terutama bila data training tidak mewakili variasi harga yang cukup.
