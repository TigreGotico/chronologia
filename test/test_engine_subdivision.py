"""subdivision_time stage: French decimal time rescaled to civil time by
exact day-fraction arithmetic, against the fixed anchor datetime(2017, 6, 27).

The day divides into 10 decimal hours / 100 decimal minutes / 100 decimal
seconds; the rescaling is exact to the civil microsecond, and the span
width is the smallest named subdivision unit's civil duration."""
from datetime import timedelta

import pytest
from engine_helpers import ANCHOR, zz_engine

from chronologia.astrodate import AstroDate
from chronologia.cycles import DAY_SUBDIVISIONS


def _one(text):
    res = zz_engine().resolve(text, ANCHOR)
    assert len(res) == 1, f"{text!r} -> {res}"
    return res[0]


# -- exact rescaling -------------------------------------------------------

def test_five_decimal_hours_is_noon_exactly():
    r = _one("5 zdheure")
    assert r.value.start == AstroDate(2017, 6, 27, 12, 0, 0)
    # width = one decimal hour = 1/10 day = 2h24m
    assert r.value.width == timedelta(hours=2, minutes=24)

def test_two_and_a_half_decimal_hours_is_six_am():
    # 2 decimal hours + 50 decimal minutes = 0.2 + 0.05 = 0.25 day = 06:00:00
    r = _one("2 zdheure 50 zdmin")
    assert r.value.start == AstroDate(2017, 6, 27, 6, 0, 0)
    # width = one decimal minute = 86.4 civil seconds
    assert r.value.width == timedelta(seconds=86, microseconds=400000)

def test_full_decimal_reading_to_the_microsecond():
    # 7 dh 50 dm 0 ds = 0.7 + 0.05 = 0.75 day = 18:00:00
    r = _one("7 zdheure 50 zdmin 0 zdsec")
    assert r.value.start == AstroDate(2017, 6, 27, 18, 0, 0)
    # width = one decimal second = 0.864 civil seconds
    assert r.value.width == timedelta(microseconds=864000)

def test_midnight_zero_reading():
    assert _one("0 zdheure").value.start == AstroDate(2017, 6, 27, 0, 0, 0)


# -- registry facts --------------------------------------------------------

def test_french_decimal_fractions_exact():
    sub = DAY_SUBDIVISIONS["french_decimal"]
    assert sub.units_to_us(5, 0, 0) == 43_200_000_000     # noon, exact
    assert sub.unit_width_us("hour") == 8_640_000_000     # 2h24m


# -- adversarial -----------------------------------------------------------

@pytest.mark.parametrize("text", [
    "11 zdheure",          # >= 10 decimal hours overflows the day
    "5 zdheure 200 zdmin"])  # decimal minutes push past the day
def test_overflow_returns_nothing(text):
    assert all(r.value.start.day == 27 for r in zz_engine().resolve(text, ANCHOR))
