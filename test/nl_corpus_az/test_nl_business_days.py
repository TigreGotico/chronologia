"""Business-day counting (az): "N işgünü sonra". Holiday-blind default: Mon-Fri
only, strictly after Tue 2017-06-27. Grid: Wed28(1) Thu29(2) Fri30(3) Mon
Jul3(4) Tue4(5) Wed5(6). The closed compound "işgünü" is used (two-word "iş
günü" is not a single-token marker)."""
from datetime import date, datetime, timedelta
import pytest
from chronologia import extract_timespan
from chronologia.astrodate import AstroDate

A = datetime(2017, 6, 27, 13, 4)

def start(text):
    r = extract_timespan(text, "az", A)
    assert r is not None, f"{text!r} did not parse"
    return r[0].start

def _ad(d):
    return AstroDate(d.year, d.month, d.day)

@pytest.mark.parametrize("text,expected", [
    ("1 işgünü sonra", date(2017, 6, 28)),
    ("2 işgünü sonra", date(2017, 6, 29)),
    ("3 işgünü sonra", date(2017, 6, 30)),
    ("4 işgünü sonra", date(2017, 7, 3)),
    ("5 işgünü sonra", date(2017, 7, 4)),
    ("6 işgünü sonra", date(2017, 7, 5)),
])
def test_count_blind(text, expected):
    assert start(text) == _ad(expected)

def test_business_day_is_day_wide():
    r = extract_timespan("3 işgünü sonra", "az", A)
    assert r[0].width == timedelta(days=1)

@pytest.mark.parametrize("text", ["işgünü", "ağır işgünü", "işə qayıdış"])
def test_negatives(text):
    assert extract_timespan(text, "az", A) is None
