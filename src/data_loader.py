import re
import urllib.parse

import pandas as pd
from sklearn.model_selection import train_test_split

from src.config import SEED

# Pola awal tiap permintaan HTTP di berkas mentah CSIC 2010
_REQ_SPLIT_RE = re.compile(
    r"(?m)(?=^(?:GET|POST|PUT|DELETE|HEAD|OPTIONS|TRACE|CONNECT)\s+\S+\s+HTTP/\d\.\d)"
)


def extract_text(raw_request: str) -> str:
    """Ambil baris permintaan dan body tanpa header, lalu decode URL satu kali."""
    text = raw_request.replace("\r\n", "\n").strip()
    if not text:
        return ""

    # Pisahkan bagian kepala (request line + header) dan body pada baris kosong pertama
    head_part, _, body = text.partition("\n\n")
    request_line = head_part.split("\n", 1)[0].strip()
    body = body.strip()

    combined = f"{request_line}\n{body}" if body else request_line
    return urllib.parse.unquote_plus(combined)


def _read_requests_from_file(path: str) -> list[str]:
    """Baca satu berkas CSIC 2010 dan pecah menjadi daftar teks permintaan."""
    with open(path, encoding="latin-1") as f:
        raw_text = f.read().replace("\r\n", "\n")

    chunks = _REQ_SPLIT_RE.split(raw_text)
    return [extract_text(chunk) for chunk in chunks if chunk.strip()]


def load_csic(normal_paths: list[str], anomalous_paths: list[str]) -> pd.DataFrame:
    """Muat berkas CSIC 2010 normal (label 0) dan serangan (label 1) ke DataFrame."""
    requests: list[str] = []
    labels: list[int] = []

    for path in normal_paths:
        reqs = _read_requests_from_file(path)
        requests.extend(reqs)
        labels.extend([0] * len(reqs))

    for path in anomalous_paths:
        reqs = _read_requests_from_file(path)
        requests.extend(reqs)
        labels.extend([1] * len(reqs))

    return pd.DataFrame({"request": requests, "label": labels})


def split_data(
    df: pd.DataFrame,
    test_size: float = 0.3,
    seed: int = SEED,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Hapus duplikat berdasarkan teks permintaan lalu bagi train/test terstratifikasi."""
    clean = df.drop_duplicates(subset=["request"]).reset_index(drop=True)
    train, test = train_test_split(
        clean,
        test_size=test_size,
        random_state=seed,
        stratify=clean["label"],
    )
    return train.reset_index(drop=True), test.reset_index(drop=True)

