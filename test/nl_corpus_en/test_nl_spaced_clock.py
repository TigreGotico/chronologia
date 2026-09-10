"""The spoken clock as two numerals: "eleven fifty five pm", "at 11 55 pm",
"seven thirty pm".  Below a hundred only a tens word takes a units digit
("twenty two"), so an hour followed by a minute count is two numbers, never
the single number the back-end used to keep.

Anchor: Tuesday 2017-06-27 13:04; a clock names its next occurrence.  Every
value is anchor arithmetic.
"""
from datetime import timedelta

import pytest

from chronologia import extract_duration

from ._corpus import ANCHOR, ad, nomatch, parse


def _next(h, m):
    cand = ANCHOR.replace(hour=h, minute=m, second=0, microsecond=0)
    if cand <= ANCHOR:
        cand += timedelta(days=1)
    return ad(cand)


@pytest.mark.parametrize("text,h,m,rem", [
    ("at 11 55 pm", 23, 55, ""),
    ("at eleven fifty five pm", 23, 55, ""),
    ("wake me at 11 55 pm", 23, 55, "wake me"),
    ("wake me at eleven fifty five pm", 23, 55, "wake me"),
    ("at seven thirty pm", 19, 30, ""),
    ("seven thirty pm", 19, 30, ""),
    ("at 7 30 am", 7, 30, ""),
    ("at 5 30", 5, 30, ""),
])
def test_hour_then_minutes(text, h, m, rem):
    res = parse(text)
    assert res is not None, f"{text!r} did not parse"
    assert res.remainder == rem
    assert res[0].start == _next(h, m)
    assert res[0].end == _next(h, m) + timedelta(minutes=1)


@pytest.mark.parametrize("text,h,m", [
    ("at eleven fifty five pm", 23, 55),
    ("at seven thirty pm", 19, 30),
])
def test_spelled_and_digit_forms_agree(text, h, m):
    digits = text.replace("eleven fifty five", "11 55").replace("seven thirty", "7 30")
    assert parse(text)[0].start == parse(digits)[0].start == _next(h, m)


@pytest.mark.parametrize("text", [
    "at 13 pm", "at 13 am", "at 23 am", "at 23 pm",
])
def test_contradictory_meridiem_is_refused(text):
    """An hour past twelve names its half of the day itself; a meridiem that
    contradicts or repeats it is not a time anyone means."""
    nomatch(text)


def test_a_bare_length_is_not_an_instant():
    nomatch("2 hours")
    assert extract_duration("2 hours", "en").duration == timedelta(hours=2)


@pytest.mark.parametrize("text,day", [
    ("twenty second of may", 22),
    ("the twenty first of may", 21),
])
def test_tens_plus_units_still_one_number(text, day):
    res = parse(text)
    assert res is not None
    assert res[0].start.day == day and res[0].start.month == 5


def test_spelled_year_is_untouched():
    res = parse("in nineteen eighty four")
    assert res is not None
    assert res[0].start.year == 1984
