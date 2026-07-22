"""Business-day counting (el): "σε N εργάσιμες ημέρες". Holiday-blind default:
Mon-Fri only, strictly after Tue 2017-06-27. Grid: Wed28(1) Thu29(2) Fri30(3)
Mon Jul3(4) Tue4(5) Wed5(6)."""
from datetime import date, datetime, timedelta
import pytest
from chronologia import extract_timespan
from chronologia.astrodate import AstroDate

A = datetime(2017, 6, 27, 13, 4)

def start(text):
    r = extract_timespan(text, "el", A)
    assert r is not None, f"{text!r} did not parse"
    return r[0].start

def _ad(d):
    return AstroDate(d.year, d.month, d.day)

@pytest.mark.parametrize("text,expected", [
    ("σε 1 εργάσιμη ημέρα", date(2017, 6, 28)),
    ("σε 2 εργάσιμες ημέρες", date(2017, 6, 29)),
    ("σε 3 εργάσιμες ημέρες", date(2017, 6, 30)),
    ("σε 4 εργάσιμες ημέρες", date(2017, 7, 3)),
    ("σε 5 εργάσιμες ημέρες", date(2017, 7, 4)),
    ("σε 6 εργάσιμες ημέρες", date(2017, 7, 5)),
])
def test_count_blind(text, expected):
    assert start(text) == _ad(expected)

def test_business_day_is_day_wide():
    r = extract_timespan("σε 3 εργάσιμες ημέρες", "el", A)
    assert r[0].width == timedelta(days=1)

@pytest.mark.parametrize("text", ["εργάσιμη ημέρα", "δύσκολη μέρα", "πίσω στη δουλειά"])
def test_negatives(text):
    assert extract_timespan(text, "el", A) is None
