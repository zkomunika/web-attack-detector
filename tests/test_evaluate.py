"""
Test untuk src/evaluate.py (Task 3a).
Fixture tmp_path disediakan otomatis oleh pytest.
Tidak ada fixture tambahan di conftest.py.
"""

import pandas as pd
import pytest

from src.evaluate import compute_metrics, dump_errors


# ---------------------------------------------------------------------------
# Test compute_metrics
# ---------------------------------------------------------------------------

def test_compute_metrics_known_case():
    # Kasus diketahui: tp=1, fp=1, fn=1, tn=1 → precision=recall=f1=0.5
    m = compute_metrics([1, 1, 0, 0], [1, 0, 1, 0])
    assert (m["tp"], m["fp"], m["fn"], m["tn"]) == (1, 1, 1, 1)
    assert m["precision"] == 0.5 and m["recall"] == 0.5 and m["f1"] == 0.5


# ---------------------------------------------------------------------------
# Test dump_errors
# ---------------------------------------------------------------------------

def test_dump_errors_picks_right_rows(tmp_path):
    # df: a=serangan benar (TP), b=serangan salah-miss (FN),
    #     c=normal salah-alarm (FP), d=normal benar (TN)
    df = pd.DataFrame({"request": list("abcd"), "label": [1, 1, 0, 0]})
    fp, fn = dump_errors(df, [1, 0, 1, 0], str(tmp_path / "x"))
    assert list(fp.request) == ["c"] and list(fn.request) == ["b"]

