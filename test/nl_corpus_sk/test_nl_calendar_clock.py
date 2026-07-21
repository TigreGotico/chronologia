"""Slovak calendar dates and clock times.

Dates run day-month-year with an ordinal-dot day and a genitive month
("15. augusta 2020").  Clock: digit literals and "N poobede/ráno/večer"
day-part meridiems.

Half-convention finding: traditional Slovak tells half and quarter hours
*forward to* the next hour -- "pol tretej" ("half of the third") is 2:30 and
"štvrť na osem" ("quarter on eight") is 7:15, half-/quarter-TO idioms with no
explicit direction token.  The engine's FRACTION+CLOCKDIR clock cannot express
them; recorded as a gap (test_nl_adversarial).
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, AstroDate, ad, span, start, start_end, parse


# -- dates ---------------------------------------------------------------

@pytest.mark.parametrize("text,y,m,d", [
    ("15. augusta 2020", 2020, 8, 15),
    ("3. januára 2020", 2020, 1, 3),
    ("1. mája 1945", 1945, 5, 1),
    ("29. februára 2020", 2020, 2, 29),
    ("31. decembra 1999", 1999, 12, 31),
    ("17. novembra 1989", 1989, 11, 17),
])
def test_full_date(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)


def test_full_date_is_day_wide():
    assert span("15. augusta 2020").width == timedelta(days=1)


@pytest.mark.parametrize("text,y,m,d", [
    ("15. augusta", 2017, 8, 15),
    ("10. apríla", 2018, 4, 10),
])
def test_day_month_prefer_future(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)


def test_iso_and_year():
    assert start("2017-06-30") == AstroDate(2017, 6, 30)
    assert start("2019") == AstroDate(2019, 1, 1)


# -- clock ---------------------------------------------------------------

def clk(h, mi, s=0):
    dt = ANCHOR.replace(hour=h, minute=mi, second=s, microsecond=0)
    if dt < ANCHOR:
        dt += timedelta(days=1)
    return ad(dt)


@pytest.mark.parametrize("text,h,mi", [
    ("15:30", 15, 30), ("23:59", 23, 59), ("00:00", 0, 0), ("09:30", 9, 30),
    ("7:15", 7, 15), ("14:30", 14, 30),
])
def test_digit_time(text, h, mi):
    assert start(text) == clk(h, mi)


@pytest.mark.parametrize("text,h", [
    ("3 poobede", 15), ("9 ráno", 9), ("8 večer", 20), ("6 ráno", 6),
])
def test_daypart_meridiem(text, h):
    assert start(text) == clk(h, 0)


@pytest.mark.parametrize("text,h,mi", [("poludnie", 12, 0), ("polnoc", 0, 0)])
def test_landmark(text, h, mi):
    assert start(text) == clk(h, mi)


def test_bare_1500_is_a_year():
    assert start("1500").year == 1500
