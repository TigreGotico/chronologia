"""The leap day, and the day numbers no year holds.

A bare day-and-month with no year names the next time that day comes round.
At the corpus anchor (2017-06-27) February is already past, and 2018 is not a
leap year, so ``29. februarja`` is 2020-02-29 -- the next February that has a
29th.  ``28. februarja`` keeps the ordinary roll to 2018-02-28.

A day number no year holds is not a date and stays declined.
"""
from datetime import datetime, timedelta

from ._corpus import ad, nomatch, parse


def test_bare_feb_29_rolls_to_the_next_leap_year():
    r = parse("29. februarja")
    assert r is not None
    assert r.span.start == ad(datetime(2020, 2, 29))
    assert r.span.end - r.span.start == timedelta(days=1)
    assert r.remainder == ""


def test_bare_feb_28_keeps_the_ordinary_roll():
    r = parse("28. februarja")
    assert r is not None
    assert r.span.start == ad(datetime(2018, 2, 28))
    assert r.remainder == ""

def test_named_leap_year_resolves_in_that_year():
    r = parse("29. februarja 2020")
    assert r is not None
    assert r.span.start == ad(datetime(2020, 2, 29))
    assert r.remainder == ""


def test_named_year_without_a_leap_day_is_declined():
    # The speaker named 2019 and 2019 has no 29 February.  The forward roll
    # guesses a year only when none was said; correcting the year someone
    # gave would hand back a date they did not ask for.
    nomatch("29. februarja 2019")
