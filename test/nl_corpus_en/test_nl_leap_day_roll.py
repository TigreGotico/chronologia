"""The leap day, and the dates that are not dates.

A bare day-and-month with no year names the next time that day comes round.
At the corpus anchor (2017-06-27) February is already past and 2018 is not a
leap year, so "29 february" is 2020-02-29 -- the next February with a 29th.

A named year is the speaker's own: "29 february 2019" is wrong and stays
declined, and so does a day number no year holds.
"""
from datetime import datetime, timedelta

from ._corpus import ad, nomatch, parse


def test_bare_leap_day_rolls_to_the_next_leap_year():
    r = parse("29 february")
    assert r is not None
    assert r.span.start == ad(datetime(2020, 2, 29))
    assert r.span.end - r.span.start == timedelta(days=1)
    assert r.remainder == ""


def test_bare_feb_28_keeps_the_ordinary_roll():
    r = parse("28 february")
    assert r is not None
    assert r.span.start == ad(datetime(2018, 2, 28))
    assert r.remainder == ""


def test_named_leap_year_resolves_in_that_year():
    r = parse("29 february 2020")
    assert r is not None
    assert r.span.start == ad(datetime(2020, 2, 29))
    assert r.remainder == ""


def test_named_year_without_a_leap_day_is_declined():
    # The speaker named 2019 and 2019 has no 29 February.  The forward roll
    # guesses a year only when none was said; correcting the year someone
    # gave would hand back a date they did not ask for.
    nomatch("29 february 2019")


def test_a_year_the_construction_cannot_bind_still_declines():
    # "this year" is the speaker naming 2017, which has no 29 February.  The
    # English day-of-month order does not bind it as a YEAR token, so without
    # the stranded-year veto the roll would answer 2020 and leave the words
    # that said otherwise sitting in the remainder.
    nomatch("the 29th of February this year")


def test_day_no_year_holds_is_declined():
    nomatch("30 february")
