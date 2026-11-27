"""Higher-ordinal Nth-weekday-of-month for Italian.

Regression for the cross-Romance silent-wrong where an ordinal spelled like
its fraction ("terzo" = third *and* a-third, "quarto" = fourth *and* a-quarter)
was held out of the number fold, so ``scoped_ordinal`` silently dropped the
weekday and landed on a bare next-weekday in the wrong month.  Low ordinals
(primo/secondo, not fraction homographs) always worked; the break started at
"terzo".  Expected dates are hand-derived from the calendar, anchor a Tuesday
2017-06-27.

Ruling 1 (changed on 26 November 2026): a part of a month with no year takes
the year the month alone takes, so marzo and maggio (ended at the anchor) are
2018.  May 2018 has only four Mondays (7, 14, 21, 28), so the fifth-ordinal
case uses the fifth Tuesday (1, 8, 15, 22, 29) instead of the fifth Monday.
"""
import pytest

from ._corpus import start, nomatch


@pytest.mark.parametrize("text,y,mo,d", [
    # low ordinals -- regression pins, must stay correct
    # ruling 1: marzo has ended at the anchor, so it is March 2018 (Mondays
    # 5, 12, 19, 26)
    ("il primo lunedì di marzo", 2018, 3, 5),
    ("il secondo lunedì di marzo", 2018, 3, 12),
    # the previously-broken higher ordinals (fraction homographs)
    ("il terzo lunedì di marzo", 2018, 3, 19),
    ("il quarto lunedì di marzo", 2018, 3, 26),
    ("il quarto giovedì di novembre", 2017, 11, 23),
    ("il terzo giovedì di novembre", 2017, 11, 16),
    # ruling 1: maggio has ended at the anchor, so it is May 2018 (no fifth
    # Monday there; the fifth Tuesday is May 29)
    ("il quinto martedì di maggio", 2018, 5, 29),
])
def test_nth_weekday_of_month(text, y, mo, d):
    s = start(text)
    assert (s.year, s.month, s.day) == (y, mo, d)


@pytest.mark.parametrize("text", [
    # March 2018 has only four Mondays -- no fifth exists
    "il quinto lunedì di marzo",
    # February 2018 has only four Thursdays -- no fifth exists
    "il quinto giovedì di febbraio",
])
def test_nonexistent_nth_is_none(text):
    nomatch(text)
