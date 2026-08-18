"""The Lithuanian spoken clock, which counts toward the COMING hour.

"pusė trijų" is half of the third hour -- 02:30, an hour earlier than the
English-shaped reading a reader might expect, and the hour is named in the
genitive.  "be penkių trys" ("without five, three") counts down to three:
02:55.  Both are pinned adversarially: the wrong reading is asserted absent,
not merely the right one asserted present.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, nomatch, start


def _next_time(h, mi):
    cand = ANCHOR.replace(hour=h, minute=mi, second=0, microsecond=0)
    if cand <= ANCHOR:
        cand += timedelta(days=1)
    return ad(cand)


@pytest.mark.parametrize("text,h,mi", [
    ("pusė trijų", 2, 30),
    ("pusė aštuonių", 7, 30),
    ("pusė devynių", 8, 30),
    ("pusė dešimties", 9, 30),
    ("pusė vienuolikos", 10, 30),
    ("pusė dvylikos", 11, 30),
    ("pusė vienos", 12, 30),
    ("pusė dviejų", 1, 30),
])
def test_half_names_the_coming_hour(text, h, mi):
    assert start(text) == _next_time(h, mi)


@pytest.mark.parametrize("text,wrong_hour", [
    ("pusė trijų", 3), ("pusė aštuonių", 8), ("pusė vienuolikos", 11),
])
def test_half_is_not_the_stated_hour(text, wrong_hour):
    """The additive reading ("half past three" = 03:30) must never occur."""
    assert start(text).hour != wrong_hour


def test_half_toward_one_reads_as_twelve():
    """Rolling back from one o'clock surfaces as twelve, not zero."""
    assert start("pusė vienos").hour == 12


@pytest.mark.parametrize("text,h,mi", [
    ("be penkių trys", 2, 55),
    ("be dešimties trys", 2, 50),
    ("be penkiolikos aštuoni", 7, 45),
    ("be dvylikos devyni", 8, 48),
])
def test_minutes_to_the_named_hour(text, h, mi):
    assert start(text) == _next_time(h, mi)


@pytest.mark.parametrize("text,wrong_hour", [
    ("be penkių trys", 3), ("be penkiolikos aštuoni", 8),
])
def test_minutes_to_rolls_the_hour_back(text, wrong_hour):
    assert start(text).hour != wrong_hour


@pytest.mark.parametrize("text,h,mi", [
    ("15:30", 15, 30), ("09:05", 9, 5), ("00:00", 0, 0), ("23:59", 23, 59),
])
def test_digit_clock(text, h, mi):
    s = start(text)
    assert (s.hour, s.minute) == (h, mi)


@pytest.mark.parametrize("text,h", [("vidurnaktis", 0), ("vidurdienis", 12)])
def test_clock_landmarks(text, h):
    assert start(text).hour == h


@pytest.mark.parametrize("text", [
    "pusė",             # a bare half with no hour
    "be",               # a bare direction with nothing to count from
    "be penkių",        # minutes with no hour named
    "pusė dienos",      # half of a DAY is a duration, not a clock reading
])
def test_incomplete_clock_is_not_a_time(text):
    nomatch(text)
