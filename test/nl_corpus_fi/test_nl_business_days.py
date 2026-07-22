"""Business-day counting (fi): "N arkipäivän kuluttua" / "N työpäivän kuluttua".
Holiday-blind default (jurisdiction=None): Mon-Fri only, strictly after the
anchor Tue 2017-06-27. Grid: Wed28(1) Thu29(2) Fri30(3) Mon Jul3(4) Tue4(5)
Wed5(6). Every gold counted by hand."""
from datetime import date, datetime
import pytest
from chronologia import extract_timespan
from chronologia.astrodate import AstroDate

A = datetime(2017, 6, 27, 13, 4)

def start(text):
    r = extract_timespan(text, "fi", A)
    assert r is not None, f"{text!r} did not parse"
    return r[0].start

def _ad(d):
    return AstroDate(d.year, d.month, d.day)

@pytest.mark.parametrize("text,expected", [
    ('1 arkipäivän kuluttua', date(2017, 6, 28)),
    ('2 arkipäivän kuluttua', date(2017, 6, 29)),
    ('3 arkipäivän kuluttua', date(2017, 6, 30)),
    ('4 arkipäivän kuluttua', date(2017, 7, 3)),
    ('5 arkipäivän kuluttua', date(2017, 7, 4)),
    ('6 työpäivän kuluttua', date(2017, 7, 5)),
])
def test_count_blind(text, expected):
    assert start(text) == _ad(expected)

def test_business_day_is_day_wide():
    from datetime import timedelta
    r = extract_timespan('3 arkipäivän kuluttua', "fi", A)
    assert r[0].width == timedelta(days=1)

@pytest.mark.parametrize("text", ['arkipäivä', 'kova työpäivä', 'takaisin töihin'])
def test_negatives(text):
    assert extract_timespan(text, "fi", A) is None
