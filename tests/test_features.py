"""
Test untuk src/features.py (Task 2).
Fixture didefinisikan di file ini, bukan di conftest.py.
"""

import numpy as np
import pytest

from src.features import build_feature_union, handcrafted_features


# ---------------------------------------------------------------------------
# Test handcrafted_features
# ---------------------------------------------------------------------------

def test_handcrafted_shape_and_order():
    # Pastikan bentuk array (n, 6) dan urutan kolom: panjang & n_kata_sql benar
    X = handcrafted_features(["GET /a", "GET /?id=1' OR '1'='1"])
    assert X.shape == (2, 6)
    assert X[1, 0] > X[0, 0]      # kolom 0: panjang — permintaan kedua lebih panjang
    assert X[1, 3] > X[0, 3]      # kolom 3: n_kata_sql — permintaan kedua ada OR


def test_empty_request_does_not_crash():
    # Permintaan kosong tidak boleh crash; tetap menghasilkan baris (1, 6)
    assert handcrafted_features([""]).shape == (1, 6)


def test_very_long_request_does_not_crash():
    # Permintaan sangat panjang (100.000 karakter) tidak boleh crash
    assert handcrafted_features(["A" * 100000]).shape == (1, 6)


# ---------------------------------------------------------------------------
# Test build_feature_union
# ---------------------------------------------------------------------------

def test_feature_union_fit_transform():
    # FeatureUnion harus bisa fit_transform dua string dan menghasilkan 2 baris
    m = build_feature_union().fit_transform(["GET /a", "GET /b?x=<script>"])
    assert m.shape[0] == 2

