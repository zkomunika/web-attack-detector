"""
Test untuk src/demo.py (Task 7).
Fixture tiny_pipeline dan tiny_model_path didefinisikan di file ini,
bukan di conftest.py, agar tidak bentrok di git antar anggota.
"""

import joblib
import pytest
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer

from src.demo import main, predict_classic


# ---------------------------------------------------------------------------
# Fixture lokal
# ---------------------------------------------------------------------------

@pytest.fixture
def tiny_pipeline():
    """Pipeline minimal (TF-IDF + LogReg) yang sudah di-fit dengan 4 sampel."""
    pipe = Pipeline([
        ("tfidf", TfidfVectorizer(analyzer="char", ngram_range=(2, 3))),
        ("clf",   LogisticRegression(max_iter=200, random_state=42)),
    ])
    # Latih dengan sampel minimal: 2 normal (0) dan 2 serangan (1)
    X = [
        "GET /index.html HTTP/1.1",
        "GET /about.html HTTP/1.1",
        "GET /?id=1 OR 1=1 HTTP/1.1",
        "GET /?q=<script>alert(1)</script> HTTP/1.1",
    ]
    y = [0, 0, 1, 1]
    pipe.fit(X, y)
    return pipe


@pytest.fixture
def tiny_model_path(tmp_path, tiny_pipeline):
    """Simpan tiny_pipeline ke file .joblib sementara dan kembalikan pathnya."""
    path = str(tmp_path / "tiny_logreg.joblib")
    joblib.dump(tiny_pipeline, path)
    return path


# ---------------------------------------------------------------------------
# Test predict_classic
# ---------------------------------------------------------------------------

def test_predict_classic_returns_valid(tiny_pipeline):
    # Semua masukan — normal, kosong, sangat panjang — harus menghasilkan label valid
    for text in ["GET /a HTTP/1.1", "", "A" * 100000]:
        label, p = predict_classic(text, tiny_pipeline)
        assert label in (0, 1) and 0.0 <= p <= 1.0


# ---------------------------------------------------------------------------
# Test main
# ---------------------------------------------------------------------------

def test_main_prints_classic_verdict(capsys, tiny_model_path):
    # Tanpa --llm, main harus mencetak "Model klasik:" dan mengembalikan kode 0
    code = main(["--request", "GET /a HTTP/1.1", "--model-path", tiny_model_path])
    assert code == 0 and "Model klasik:" in capsys.readouterr().out


def test_main_continues_when_ollama_down(capsys, tiny_model_path, monkeypatch):
    # Bila Ollama mati (RuntimeError), demo tetap lanjut dan kode keluar 0
    monkeypatch.setattr(
        "src.demo.classify_request",
        lambda r: (_ for _ in ()).throw(RuntimeError("Ollama tidak berjalan")),
    )
    code = main(["--request", "GET /a HTTP/1.1", "--llm", "--model-path", tiny_model_path])
    out = capsys.readouterr().out
    assert code == 0 and "Model klasik:" in out and "Ollama tidak berjalan" in out
