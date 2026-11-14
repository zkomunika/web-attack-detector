"""
Test untuk src/llm_classifier.py (Task 5).
Fixture dan helper didefinisikan di sini, bukan di conftest.py.
"""

import pytest
import requests

from src.llm_classifier import build_prompt, classify_request, parse_label


# ---------------------------------------------------------------------------
# Helper: tiruan respons requests.post
# ---------------------------------------------------------------------------

class FakeResp:
    """Tiruan objek Response dari requests.post yang mengembalikan JSON tetap."""

    def __init__(self, data: dict):
        self._data = data

    def json(self):
        """Kembalikan dict data sebagai pengganti .json() asli."""
        return self._data

    def raise_for_status(self):
        """Tidak melakukan apa pun; anggap HTTP 200 OK."""
        pass


# ---------------------------------------------------------------------------
# Test parse_label
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw,exp", [
    ("ATTACK",              1),
    (" attack.",            1),
    ("NORMAL",              0),
    ("normal request",      0),
    ("I think this is bad", None),
    ("",                    None),
])
def test_parse_label(raw, exp):
    """Pastikan parse_label mengenali ATTACK→1, NORMAL→0, dan lainnya→None."""
    assert parse_label(raw) == exp


# ---------------------------------------------------------------------------
# Test build_prompt
# ---------------------------------------------------------------------------

def test_build_prompt_contains_request_and_labels():
    """Pastikan prompt memuat teks permintaan asli serta kata NORMAL dan ATTACK."""
    p = build_prompt("GET /a HTTP/1.1")
    assert "GET /a HTTP/1.1" in p and "NORMAL" in p and "ATTACK" in p


def test_build_prompt_truncates_and_handles_empty():
    """Pastikan prompt dipotong bila permintaan terlalu panjang dan tidak crash bila kosong."""
    assert len(build_prompt("A" * 100000)) < 100000
    assert isinstance(build_prompt(""), str)


# ---------------------------------------------------------------------------
# Test classify_request
# ---------------------------------------------------------------------------

def test_classify_request_parses_response(monkeypatch):
    """Pastikan classify_request memparsing respons Ollama dan mengembalikan (label, detik)."""
    monkeypatch.setattr("requests.post", lambda *a, **k: FakeResp({"response": "ATTACK"}))
    label, secs = classify_request("GET /?id=1' OR '1'='1")
    assert label == 1 and secs >= 0


def test_classify_request_ollama_down(monkeypatch):
    """Pastikan ConnectionError diubah menjadi RuntimeError dengan pesan yang jelas."""
    def boom(*a, **k):
        raise requests.ConnectionError()
    monkeypatch.setattr("requests.post", boom)
    with pytest.raises(RuntimeError, match="Ollama tidak berjalan"):
        classify_request("x")
