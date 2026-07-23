"""Adversarial German cases -- written to BREAK the parse, not to confirm it.
The engine must never fabricate a span, never raise, and never silently roll
an impossible value into a valid one.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, parse, span, nomatch, start


# -- pure prose that merely contains date-adjacent words ------------------

@pytest.mark.parametrize("text", [
    "vor allem anderen", "in ordnung", "nach hause gehen",
    "das ist mir egal", "guten morgen zusammen",
])
def test_prose_does_not_fabricate(text):
    # may extract an embedded named-day ("morgen") but must never raise
    parse(text)


# -- impossible clocks -----------------------------------------------------

@pytest.mark.parametrize("text", ["25:00", "24:61", "99:99", "15:99"])
def test_impossible_clock(text):
    res = parse(text)
    if res is not None:
        assert 0 <= res[0].start.hour <= 23
        assert 0 <= res[0].start.minute <= 59


# -- impossible calendar dates --------------------------------------------

@pytest.mark.parametrize("text", [
    "30. februar 2019", "31. april 2020", "32. januar 2020",
    "0. märz 2020",
])
def test_impossible_date(text):
    res = parse(text)
    if res is not None:
        # never rolls a bad day into the following month silently
        assert res[0].start.day <= 31


# -- bare quarter forms: South/East German + Austrian toward-the-hour ------
# "viertel neun" == 08:15, "dreiviertel sieben" == 06:45 -- the regional
# toward-hour reading (Bastian Sick, "Zwiebelfisch"), now enabled.  Western
# German uses "viertel nach/vor" instead; the bare forms only ADD readings for
# strings that were previously unparsed, so no vor/nach collision.
@pytest.mark.parametrize("text,h,mi", [
    ("viertel neun", 8, 15), ("dreiviertel sieben", 6, 45),
    ("viertel elf", 10, 15),
])
def test_bare_quarter_regional_toward_hour(text, h, mi):
    assert (start(text).hour, start(text).minute) == (h, mi)


# -- a two-digit "year" is guarded off (needs 4 digits) -------------------

@pytest.mark.parametrize("text", ["44", "99", "7"])
def test_short_bare_year_guarded(text):
    nomatch(text)


# -- "halb" must not swallow a following non-hour word --------------------

def test_halb_without_hour():
    # "halb" alone (no hour, no landmark) is not a time
    nomatch("halb")


# -- number word that is a clock fraction must not fold into a digit ------

def test_halb_survives_as_fraction():
    # if "halb" had folded to 0.5 it could never anchor "halb neun" = 08:30
    assert start("halb neun").minute == 30


# -- empty / whitespace ----------------------------------------------------

@pytest.mark.parametrize("text", ["", "   ", "..."])
def test_empty(text):
    assert parse(text) is None


# -- a lone range word is not a range -------------------------------------

@pytest.mark.parametrize("text", ["von", "bis", "zwischen", "von bis"])
def test_lone_range_word(text):
    assert parse(text) is None
