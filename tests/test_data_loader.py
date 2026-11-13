import pandas as pd
import pytest

from src.data_loader import extract_text, split_data


@pytest.fixture
def small_df():
    # Membuat 100 permintaan normal (label 0) dan 60 serangan (label 1) yang semuanya unik
    normal = [f"GET /item?id={i} HTTP/1.1" for i in range(100)]
    serangan = [f"GET /item?id={i}' OR '1'='1 HTTP/1.1" for i in range(60)]
    return pd.DataFrame({
        "request": normal + serangan,
        "label": [0] * 100 + [1] * 60,
    })


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

