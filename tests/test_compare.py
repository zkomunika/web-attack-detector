"""
test_compare.py — test untuk src/compare.py (Task 6).
Fixture test_df, subset, tiny_pipeline didefinisikan di sini, bukan di conftest.py.
"""

import numpy as np
import pandas as pd
import pytest
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer

from src.compare import run_comparison, sample_subset


# ---------------------------------------------------------------------------
# Fixture lokal (tidak di conftest.py agar tidak bentrok di git)
# ---------------------------------------------------------------------------

@pytest.fixture
def test_df():
    """DataFrame 20 baris: 10 normal (label 0) + 10 serangan (label 1), semua unik."""
    normal = [f"GET /page{i} HTTP/1.1" for i in range(10)]
    attack = [f"GET /?id={i}' OR 1=1 HTTP/1.1" for i in range(10)]
    return pd.DataFrame({
        "request": normal + attack,
        "label":   [0] * 10 + [1] * 10,
    })


@pytest.fixture
def subset(test_df):
    """Subset seimbang 5 normal + 5 serangan dari test_df."""
    return sample_subset(test_df, n_per_class=5)


@pytest.fixture
def tiny_pipeline():
    """Pipeline minimal yang selalu memprediksi 0 (normal) untuk semua masukan."""
    # FunctionTransformer mengubah list string menjadi array angka dummy
    def _to_zeros(X):
        return np.zeros((len(X), 1))

    pipe = Pipeline([
        ("feat", FunctionTransformer(_to_zeros)),
    ])
    # Simulasikan pipeline sudah fit dengan menambahkan metode predict dan predict_proba
    pipe.predict = lambda X: np.zeros(len(X), dtype=int)
    pipe.predict_proba = lambda X: np.column_stack([
        np.ones(len(X)),
        np.zeros(len(X)),
    ])
    return pipe


# ---------------------------------------------------------------------------
# Test dari rencana
# ---------------------------------------------------------------------------

def test_sample_subset_balanced_deterministic(test_df):
    """sample_subset harus seimbang dan menghasilkan urutan yang sama setiap dipanggil."""
    a = sample_subset(test_df, n_per_class=5)
    b = sample_subset(test_df, n_per_class=5)
    # Tiap label harus muncul tepat 5 kali
    assert a.label.value_counts().to_dict() == {0: 5, 1: 5}
    # Dua pemanggilan dengan seed yang sama harus menghasilkan urutan yang sama
    assert list(a.request) == list(b.request)
    # Semua baris harus berasal dari test_df
    assert set(a.request) <= set(test_df.request)


def test_run_comparison_with_fake_llm(subset, tiny_pipeline):
    """run_comparison dengan LLM palsu yang selalu mengembalikan (1, 0.1) tidak boleh ada llm_unparsed."""
    out = run_comparison(subset, tiny_pipeline, classify=lambda r: (1, 0.1))
    assert (out.pred_llm == 1).all() and not out.llm_unparsed.any()


def test_unparsed_is_counted_not_hidden(subset, tiny_pipeline):
    """run_comparison dengan LLM yang mengembalikan None harus dicatat sebagai llm_unparsed=True dan pred_llm=0."""
    out = run_comparison(subset, tiny_pipeline, classify=lambda r: (None, 0.1))
    assert out.llm_unparsed.all() and (out.pred_llm == 0).all()
