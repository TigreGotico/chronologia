"""Ordinal counting from the anchor (feature 2).

"3 fridays from now" = the 3rd occurrence of friday strictly after now;
"2 mondays ago" = the 2nd monday strictly before now; "the weekend after
next" = skip the next weekend, take the following one.

Anchor is 2017-06-27 (a Tuesday, weekday index 1, 13:04).  Expected values
come from independent Python arithmetic, never from the parser.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, AstroDate, parse, span, start, nomatch

_MID = ANCHOR.replace(hour=0, minute=0)
_WD = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
       "friday": 4, "saturday": 5, "sunday": 6}


def _nth(weekday, n, sign):
    target = _WD[weekday]
    if sign > 0:
        ahead = (target - ANCHOR.weekday()) % 7 or 7
        d = _MID + timedelta(days=ahead + 7 * (n - 1))
    else:
        back = (ANCHOR.weekday() - target) % 7 or 7
        d = _MID - timedelta(days=back + 7 * (n - 1))
    return AstroDate(d.year, d.month, d.day)


# -- N weekdays from now (strictly future) --------------------------------

@pytest.mark.parametrize("text,wd,n", [
    ("1 friday from now", "friday", 1),
    ("2 fridays from now", "friday", 2),
    ("3 fridays from now", "friday", 3),
    ("4 mondays from now", "monday", 4),
    ("3 tuesdays from now", "tuesday", 3),
    ("2 wednesdays from now", "wednesday", 2),
    ("5 sundays from now", "sunday", 5),
    ("1 sunday from now", "sunday", 1),
])
def test_weekdays_from_now(text, wd, n):
    assert start(text) == _nth(wd, n, +1)


# -- N weekdays ago (strictly past) ---------------------------------------

@pytest.mark.parametrize("text,wd,n", [
    ("1 monday ago", "monday", 1),
    ("2 mondays ago", "monday", 2),
    ("2 tuesdays ago", "tuesday", 2),
    ("3 saturdays ago", "saturday", 3),
    ("3 thursdays ago", "thursday", 3),
    ("2 fridays ago", "friday", 2),
])
def test_weekdays_ago(text, wd, n):
    assert start(text) == _nth(wd, n, -1)


# -- the weekend after next (skip one, take the following) ----------------

def test_weekend_after_next():
    # anchor week starts Mon 2017-06-26; this weekend is Sat 2017-07-01,
    # next is 2017-07-08, the one after next is 2017-07-15.
    s = span("the weekend after next")
    assert (s.start.year, s.start.month, s.start.day) == (2017, 7, 15)
    assert s.width == timedelta(days=2)


def test_count_is_day_wide():
    assert span("3 fridays from now").width == timedelta(days=1)


# -- negatives / confusables ----------------------------------------------

@pytest.mark.parametrize("text", [
    "a couple of fridays from now",     # no explicit digit count
    "3 fridays",                        # no from-now / ago marker
    "fridays from now",                 # no count
    "the week after next",              # not a weekend, not countable
])
def test_no_count_no_match(text):
    nomatch(text)


def test_next_weekend_unchanged():
    # a plain "next weekend" is untouched (the following weekend, not skipped)
    s = span("next weekend")
    assert (s.start.year, s.start.month, s.start.day) == (2017, 7, 8)
