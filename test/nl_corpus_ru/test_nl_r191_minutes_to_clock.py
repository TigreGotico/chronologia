# -*- coding: utf-8 -*-
"""Russian subtractive "без N <hour>" clock: general minute counts, not only
the fixed quarter idiom.

"без четверти девять" (a quarter to nine == 08:45) already worked through
CLOCKDIR ("без") + FRACTION ("четверти").  Any other minute count uses the
same subtractive direction with a genitive cardinal numeral instead of the
fraction word: "без пяти девять" == without five == 08:55, "без десяти
девять" == without ten == 08:50, "без двадцати девять" == without twenty ==
08:40.  The genitive numeral optionally carries the noun "минут" ("minutes"):
"без пяти минут девять" is the same 08:55.  Digit numerals work the same way
("без 5 девять").  Every value: hour named is the REACHED hour, minute =
60 - N, exactly the "без четверти" arithmetic already in production.

Citation: gramota.ru (Russian State Language reference service), telling the
time.  Anchor Fri 2026-08-14 10:00: every gold time below (08:40..08:55) is
already past on the anchor day, so -- exactly as "без четверти девять"
already rolls -- the reached hour lands on 2026-08-15.  Gold hand-derived,
independent of the parser.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate

LANG = "ru"
ANCHOR = datetime(2026, 8, 14, 10, 0)


def span(text):
    r = extract_timespan(text, LANG, ANCHOR)
    assert r is not None, f"{text!r} did not resolve"
    return r[0].start, r[0].end


def _gold(minute):
    return (AstroDate(2026, 8, 15, 8, minute),
             AstroDate(2026, 8, 15, 8, minute + 1))


# -- genitive numeral, bare (no "минут") ------------------------------------

@pytest.mark.parametrize("text,minute", [
    ("без пяти девять", 55),
    ("без десяти девять", 50),
    ("без пятнадцати девять", 45),
    ("без двадцати девять", 40),
])
def test_genitive_minutes_to_bare(text, minute):
    assert span(text) == _gold(minute)


# -- genitive numeral with the explicit noun "минут" -------------------------

@pytest.mark.parametrize("text,minute", [
    ("без пяти минут девять", 55),
    ("без десяти минут девять", 50),
    ("без пятнадцати минут девять", 45),
    ("без двадцати минут девять", 40),
])
def test_genitive_minutes_to_with_word(text, minute):
    assert span(text) == _gold(minute)


# -- digit numeral in the same subtractive frame ------------------------

@pytest.mark.parametrize("text,minute", [
    ("без 5 девять", 55),
    ("без 10 девять", 50),
    ("без 15 девять", 45),
    ("без 20 девять", 40),
])
def test_digit_minutes_to(text, minute):
    assert span(text) == _gold(minute)


# -- boundary: the "двадцать пять" (25) compound genitive does not compose --
#
# "двадцати пяти" is two genitive number-words ("of twenty" + "of five");
# unlike the single-token forms above, the fold engine's number-word run
# scanner cannot tell this compound apart from an ordinary "MINUTE HOUR"
# adjacency and drops it rather than guess -- refused, not silently wrong.

def test_compound_25_genitive_not_supported():
    assert extract_timespan("без двадцати пяти девять", LANG, ANCHOR) is None


# -- controls that must not regress -----------------------------------------

def test_control_bez_chetverti_devyat():
    assert span("без четверти девять") == _gold(45)


def test_control_spoken_clock_v_chasov():
    assert span("в 9 часов") == (
        AstroDate(2026, 8, 15, 9, 0), AstroDate(2026, 8, 15, 9, 1))


def test_control_poldevyatogo_contraction():
    assert span("полдевятого") == (
        AstroDate(2026, 8, 15, 8, 30), AstroDate(2026, 8, 15, 8, 31))


def test_control_offset_genitive_two_days_ago():
    r = extract_timespan("два дня назад", LANG, ANCHOR)
    assert r is not None
    assert r[0].start == AstroDate(2026, 8, 12, 10, 0)
