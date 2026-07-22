"""Business-day counting (eu): "N lanegun barru". Holiday-blind default:
Mon-Fri only, strictly after Tue 2017-06-27. Grid: Wed28(1) Thu29(2) Fri30(3)
Mon Jul3(4) Tue4(5) Wed5(6)."""
from datetime import date, datetime, timedelta
import pytest
from chronologia import extract_timespan
from chronologia.astrodate import AstroDate

A = datetime(2017, 6, 27, 13, 4)

def start(text):
    r = extract_timespan(text, "eu", A)
    assert r is not None, f"{text!r} did not parse"
    return r[0].start

def _ad(d):
    return AstroDate(d.year, d.month, d.day)

@pytest.mark.parametrize("text,expected", [
    ("1 lanegun barru", date(2017, 6, 28)),
    ("2 lanegun barru", date(2017, 6, 29)),
    ("3 lanegun barru", date(2017, 6, 30)),
    ("4 lanegun barru", date(2017, 7, 3)),
    ("5 lanegun barru", date(2017, 7, 4)),
    ("6 lanegun barru", date(2017, 7, 5)),
])
def test_count_blind(text, expected):
    assert start(text) == _ad(expected)

def test_business_day_is_day_wide():
    r = extract_timespan("3 lanegun barru", "eu", A)
    assert r[0].width == timedelta(days=1)

@pytest.mark.parametrize("text", ["lanegun", "lanegun gogorra", "lanera itzuli"])
def test_negatives(text):
    assert extract_timespan(text, "eu", A) is None
