"""
features.py — ekstraksi fitur untuk detektor serangan web.

Dua fungsi utama:
  - handcrafted_features: hitung 6 fitur numerik dari daftar string permintaan.
  - build_feature_union : gabungkan TF-IDF karakter dan fitur buatan sendiri.
"""

import re

import numpy as np
from sklearn.pipeline import FeatureUnion
from sklearn.preprocessing import FunctionTransformer, StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer

# --- Pola regex (dikompilasi sekali untuk efisiensi) ---

# Karakter khusus yang dicurigai dalam serangan web
_RE_SPECIAL = re.compile(r"""['\"<>;()%=\-]""")

# Kata kunci SQL tanpa membedakan huruf besar kecil
_RE_SQL = re.compile(
    r"\b(select|union|insert|drop|or|and|sleep)\b|--",
    re.IGNORECASE,
)

# Kata kunci skrip/XSS
_RE_SCRIPT = re.compile(
    r"script|alert|onerror|javascript",
    re.IGNORECASE,
)


def handcrafted_features(requests) -> np.ndarray:
    """Hitung 6 fitur numerik per permintaan dan kembalikan array (n, 6).

    Urutan kolom:
        0  panjang          — jumlah karakter
        1  n_karakter_khusus — jumlah karakter ' \" < > ; ( ) % = -
        2  n_persen         — jumlah karakter '%'
        3  n_kata_sql       — jumlah kemunculan kata/pola SQL
        4  n_kata_script    — jumlah kemunculan kata XSS
        5  n_digit          — jumlah digit 0-9
    """
    rows = []
    for req in requests:
        # Gunakan string kosong bila masukan None
        teks = req if req is not None else ""

        panjang          = len(teks)
        n_karakter_khusus = len(_RE_SPECIAL.findall(teks))
        n_persen         = teks.count("%")
        n_kata_sql       = len(_RE_SQL.findall(teks))
        n_kata_script    = len(_RE_SCRIPT.findall(teks))
        n_digit          = sum(c.isdigit() for c in teks)

        rows.append([panjang, n_karakter_khusus, n_persen,
                     n_kata_sql, n_kata_script, n_digit])

    return np.array(rows, dtype=float)


def build_feature_union(max_features: int = 20000) -> FeatureUnion:
    """Buat FeatureUnion yang menggabungkan TF-IDF karakter dan fitur buatan sendiri.

    Komponen:
        tfidf  — TfidfVectorizer karakter n-gram (2–4), hingga max_features fitur.
        custom — handcrafted_features dibungkus FunctionTransformer lalu dinormalisasi
                 dengan StandardScaler(with_mean=False) agar cocok dengan matriks sparse.
    """
    tfidf = TfidfVectorizer(
        analyzer="char",
        ngram_range=(2, 4),
        lowercase=True,
        max_features=max_features,
    )

    custom_pipeline = FeatureUnion([
        ("custom_scaled", FeatureUnion([
            ("custom_raw", FunctionTransformer(handcrafted_features)),
        ])),
    ])

    # Pakai Pipeline kecil: FunctionTransformer → StandardScaler
    from sklearn.pipeline import Pipeline as _Pipeline
    custom_step = _Pipeline([
        ("extract", FunctionTransformer(handcrafted_features)),
        ("scale",   StandardScaler(with_mean=False)),
    ])

    return FeatureUnion([
        ("tfidf",  tfidf),
        ("custom", custom_step),
    ])

