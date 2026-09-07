"""The leap day, with and without a year.

A bare day-and-month with no year names the next time that day comes round.
From the corpus anchor (2027-05-12) February is already past and 2028 is a
leap year, so ``2월 29일`` and ``2월 28일`` both land in 2028.  The year that
February 29 skips shows from an anchor just after one: past 2028-02-29 the
next 29 February is 2032's.

Korean writes the year first.  2020 has a 29 February and resolves there;
2019 does not and the reading is declined rather than corrected.
"""
from datetime import datetime, timedelta

from ._corpus import ad, nomatch, parse


def test_bare_feb_29_rolls_to_the_next_leap_year():
    r = parse("2월 29일", datetime(2028, 3, 1, 13, 4))
    assert r is not None
    assert r.span.start == ad(datetime(2032, 2, 29))
    assert r.span.end - r.span.start == timedelta(days=1)
    assert r.remainder == ""


def test_bare_feb_29_stays_in_the_coming_leap_year():
    r = parse("2월 29일")
    assert r is not None
    assert r.span.start == ad(datetime(2028, 2, 29))
    assert r.remainder == ""


def test_bare_feb_28_keeps_the_ordinary_roll():
    r = parse("2월 28일")
    assert r is not None
    assert r.span.start == ad(datetime(2028, 2, 28))
    assert r.remainder == ""


def test_named_leap_year_resolves_in_that_year():
    r = parse("2020년 2월 29일")
    assert r is not None
    assert r.span.start == ad(datetime(2020, 2, 29))
    assert r.remainder == ""


def test_named_year_without_a_leap_day_is_declined():
    # The speaker named 2019 and 2019 has no 29 February.  The forward roll
    # guesses a year only when none was said; correcting the year someone
    # gave would hand back a date they did not ask for.
    nomatch("2019년 2월 29일")
