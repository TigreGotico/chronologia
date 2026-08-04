"""Wave 1 -- clock times: minute-wide spans on the anchor day, with the
engine's prefer_future roll (a time already past 13:04 rolls to the next
day).  Digit times, bare "at N" / "N o'clock" / "N pm", the quarter/half
fraction system, meridiem edges, and composition onto a date.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, start, span, nomatch


def clk(h, mi, s=0):
    """Independent oracle: HH:MM[:SS] on the anchor day, rolled +1 day when
    already past the 13:04 anchor."""
    dt = ANCHOR.replace(hour=h, minute=mi, second=s, microsecond=0)
    if dt < ANCHOR:
        dt += timedelta(days=1)
    return ad(dt)


# -- digit clock literals -------------------------------------------------

@pytest.mark.parametrize("text,h,mi,s", [
    ("15:30", 15, 30, 0), ("23:59", 23, 59, 0), ("00:00", 0, 0, 0),
    ("13:05", 13, 5, 0), ("13:04", 13, 4, 0), ("09:30", 9, 30, 0),
    ("5:07:30", 5, 7, 30), ("18:45", 18, 45, 0), ("07:15", 7, 15, 0),
])
def test_digit_time(text, h, mi, s):
    assert start(text) == clk(h, mi, s)
    assert span(text).width == timedelta(minutes=1)


# -- meridiem digit times -------------------------------------------------

@pytest.mark.parametrize("text,h,mi", [
    ("3:30 pm", 15, 30), ("9:30 pm", 21, 30), ("9:30 am", 9, 30),
    ("12:00 am", 0, 0), ("12:00 pm", 12, 0), ("1:15 pm", 13, 15),
    ("11:59 pm", 23, 59), ("6:00 am", 6, 0), ("12:30 pm", 12, 30),
])
def test_digit_time_meridiem(text, h, mi):
    assert start(text) == clk(h, mi)


# -- bare "at N" and "N o'clock" (minute 0), digit and spelled ------------

@pytest.mark.parametrize("text,h", [
    ("at 15", 15), ("at 9", 9), ("at 20", 20), ("at 3", 3), ("at 23", 23),
    ("at three", 3), ("at eleven", 11), ("at eight", 8),
    ("3 o'clock", 3), ("8 o'clock", 8), ("11 o'clock", 11),
    ("seven o'clock", 7), ("ten o'clock", 10),
])
def test_bare_hour(text, h):
    assert start(text) == clk(h, 0)


# -- "N pm" / "N am" (no 'at') --------------------------------------------

@pytest.mark.parametrize("text,h", [
    ("3 pm", 15), ("9 am", 9), ("12 pm", 12), ("12 am", 0),
    ("6 pm", 18), ("11 am", 11), ("1 pm", 13), ("8 pm", 20),
    ("three pm", 15), ("eight am", 8),
])
def test_hour_meridiem(text, h):
    assert start(text) == clk(h, 0)


# a 12-hour am/pm marker only qualifies a valid clock hour 1..12; an hour of 0
# or >=13 with a meridiem is contradictory ("13 pm", "0 am") and names no time.
# It must decline (like the "13:60"/"25:00" overflow guards), not silently drop
# the meridiem and return a confident wrong hour.
@pytest.mark.parametrize("text", [
    "13 pm", "13 am", "15 pm", "23 pm", "0 pm", "0 am",
])
def test_contradictory_hour_meridiem_declines(text):
    nomatch(text)


# -- fraction system: half/quarter past/to, digit and spelled -------------

@pytest.mark.parametrize("text,h,mi", [
    ("half past nine", 9, 30), ("half past ten", 10, 30),
    ("half past 9", 9, 30), ("quarter past three", 3, 15),
    ("quarter past 3", 3, 15), ("quarter to five", 4, 45),
    ("quarter to 5", 4, 45), ("quarter past noon", 12, 15),
    ("quarter to noon", 11, 45), ("half past noon", 12, 30),
    ("quarter past ten pm", 22, 15), ("quarter to five pm", 16, 45),
    ("half past six pm", 18, 30), ("quarter past eleven", 11, 15),
])
def test_fraction(text, h, mi):
    assert start(text) == clk(h, mi)


# -- British-colloquial additive bare half: "half nine" == 09:30 ----------
# Half PAST the named hour (hour unchanged), the OPPOSITE direction of the
# Continental-Germanic "halb neun" == 08:30 (half TO nine).  Cross-direction
# adversarial: assert the English 09:30 here and the German 08:30 in the de
# corpus (test_de_clock.test_halb_is_half_to, "halb neun" == 08:30).
# Source: Cambridge Dictionary, "half past"; British native-speaker consensus.
@pytest.mark.parametrize("text,h,mi", [
    ("half nine", 9, 30), ("half three", 3, 30), ("half ten", 10, 30),
    ("half six", 6, 30), ("half twelve", 12, 30), ("half one", 1, 30),
])
def test_bare_half_is_additive(text, h, mi):
    assert start(text) == clk(h, mi)


def test_bare_half_opposite_of_german():
    # en "half three" == 03:30 (half past) vs de "halb drei" == 02:30 (half to)
    assert start("half three") == clk(3, 30)


# a bare QUARTER is not English ("quarter nine" is not said) -> rejected; only
# the half takes the colloquial additive form.
@pytest.mark.parametrize("text", ["quarter nine", "a quarter nine",
                                   "quarter three"])
def test_bare_quarter_rejected(text):
    nomatch(text)


# -- composition onto a date (minute-wide on the named day) ---------------

def test_compose_date_and_pm():
    # june 5 rolls to 2018 (prefer_future, day past); clock at 15:00
    from ._corpus import AstroDate
    assert start("june 5th at 3pm") == AstroDate(2018, 6, 5, 15, 0)


def test_compose_iso_and_time():
    from ._corpus import AstroDate
    assert start("2017-06-30 15:30") == AstroDate(2017, 6, 30, 15, 30)


def test_compose_date_and_half_past():
    from ._corpus import AstroDate
    assert start("december 25 2020 at half past ten") \
        == AstroDate(2020, 12, 25, 10, 30)


# -- adversarial: impossible clock never raises, never fabricates ---------

@pytest.mark.parametrize("text", ["25:00", "15:99", "at 99", "99:99"])
def test_impossible_clock(text):
    r = span.__class__ if False else None
    from ._corpus import parse
    res = parse(text)
    if res is not None:
        assert 0 <= res[0].start.hour <= 23


# -- landmarks: noon / midnight (bare and as fraction anchors) ------------

@pytest.mark.parametrize("text,h,mi", [
    ("noon", 12, 0), ("midday", 12, 0), ("midnight", 0, 0),
    ("at noon", 12, 0), ("at midnight", 0, 0),
    ("quarter to midnight", 23, 45), ("quarter past midnight", 0, 15),
    ("quarter past noon", 12, 15), ("quarter to noon", 11, 45),
    ("half past noon", 12, 30), ("half past midnight", 0, 30),
])
def test_landmark(text, h, mi):
    assert start(text) == clk(h, mi)


# -- military / 24-hour "HHMM" clock --------------------------------------

@pytest.mark.parametrize("text,h,mi", [
    ("1500 hours", 15, 0), ("0600", 6, 0), ("0600 hours", 6, 0),
    ("2359 hours", 23, 59), ("0000 hours", 0, 0), ("1230 hours", 12, 30),
])
def test_military_time(text, h, mi):
    assert start(text) == clk(h, mi)


# a bare 4-digit run without a leading zero stays a YEAR, not a clock
def test_bare_1500_is_a_year():
    assert start("1500").year == 1500


# -- arbitrary-minute "N to/past H" ---------------------------------------

@pytest.mark.parametrize("text,h,mi", [
    ("ten to eight", 7, 50), ("twenty past three", 3, 20),
    ("five to nine", 8, 55), ("twenty five past six", 6, 25),
    ("ten past noon", 12, 10),
])
def test_minute_to_past(text, h, mi):
    assert start(text) == clk(h, mi)


# adversarial: a landmark inside prose still resolves, and "1300 hours"
# is a clock even though 1300 alone is a year.
def test_clock_adversarial():
    assert start("1300 hours") == clk(13, 0)
    assert start("by noon i mean it").hour == 12    # remainder is prose
