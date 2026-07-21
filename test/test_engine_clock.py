"""clock_time stage: minute-wide spans against the fixed anchor
datetime(2017, 6, 27, 13, 4), plus composition with a date construction
and adversarial inputs that must never raise.

The synthetic ``zz`` locale exercises the construction in isolation:
digit times (``15:30``), bare "at N" / "N o'clock", the quarter/half
fraction system ("half past ten", "quarter to five"), am/pm meridiem, and
prefer_future roll-over."""
from datetime import datetime

import pytest
from engine_helpers import ANCHOR, zz_engine

from chronologia.astrodate import AstroDate
from chronologia.extract.resolver import compose_date_clock


def _one(text, anchor=ANCHOR):
    res = zz_engine().resolve(text, anchor)
    assert len(res) == 1, f"{text!r} -> {res}"
    return res[0]


# -- digit clock literals --------------------------------------------------

def test_digit_time_hh_mm():
    r = _one("15:30")
    assert r.value.start == AstroDate(2017, 6, 27, 15, 30)
    assert r.value.width.total_seconds() == 60          # minute-wide

def test_digit_time_with_seconds():
    assert _one("5:07:30", datetime(2017, 6, 27, 4, 0)).value.start \
        == AstroDate(2017, 6, 27, 5, 7, 30)

def test_digit_time_meridiem_pm():
    # 3:30 pm on the anchor day -> 15:30
    assert _one("3:30 zpm").value.start == AstroDate(2017, 6, 27, 15, 30)

def test_digit_time_meridiem_am_noon_is_midnight():
    # 12:00 am -> 00:00; prefer_future rolls to the next day (already past)
    assert _one("12:00 zam").value.start == AstroDate(2017, 6, 28, 0, 0)


# -- bare "at N" and "N o'clock" (minute 0) --------------------------------

def test_at_bare_hour():
    assert _one("zat 15").value.start == AstroDate(2017, 6, 27, 15, 0)

def test_oclock():
    assert _one("15 zoclock").value.start == AstroDate(2017, 6, 27, 15, 0)


# -- fraction system -------------------------------------------------------

def test_half_past_ten():
    # 10:30; already past on the anchor day -> prefer_future rolls +1 day
    assert _one("zhalf zpast 10").value.start == AstroDate(2017, 6, 28, 10, 30)

def test_quarter_past_ten_pm():
    assert _one("zquarter zpast 10 zpm").value.start \
        == AstroDate(2017, 6, 27, 22, 15)

def test_quarter_to_five_pm():
    # quarter to five = 4:45; pm -> 16:45
    assert _one("zquarter zto 5 zpm").value.start \
        == AstroDate(2017, 6, 27, 16, 45)


# -- prefer_future roll-over -----------------------------------------------

def test_prefer_future_rolls_past_times():
    # 09:00 is before the 13:04 anchor -> next day
    assert _one("zat 9").value.start == AstroDate(2017, 6, 28, 9, 0)

def test_prefer_future_keeps_future_times():
    assert _one("zat 20").value.start == AstroDate(2017, 6, 27, 20, 0)


# -- composition with a date construction ----------------------------------

def test_composes_calendar_date_and_clock():
    r = _one("zjun 5 2027 zat 15")
    assert r.value.start == AstroDate(2027, 6, 5, 15, 0)
    assert r.value.width.total_seconds() == 60

def test_composes_iso_date_and_clock():
    r = _one("2017-06-30 15:30")
    assert r.value.start == AstroDate(2017, 6, 30, 15, 30)

def test_compose_helper_intersects_day_and_time():
    (date_res,) = zz_engine().resolve("zjun 5 2027", ANCHOR)
    (clock_res,) = zz_engine().resolve("zat 15", datetime(2017, 6, 27, 1, 0))
    merged = compose_date_clock(date_res, clock_res)
    assert merged.value.start == AstroDate(2027, 6, 5, 15, 0)


# -- adversarial: impossible / garbage never raise -------------------------

@pytest.mark.parametrize("text", [
    "25:00", "15:99", "zat 99", "zzz garbage", "zquarter zto"])
def test_adversarial_never_raises(text):
    res = zz_engine().resolve(text, ANCHOR)
    for r in res:
        assert 0 <= r.value.start.hour <= 23
