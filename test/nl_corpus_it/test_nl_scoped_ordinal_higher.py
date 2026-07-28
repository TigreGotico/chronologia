"""Higher-ordinal Nth-weekday-of-month for Italian.

Regression for the cross-Romance silent-wrong where an ordinal spelled like
its fraction ("terzo" = third *and* a-third, "quarto" = fourth *and* a-quarter)
was held out of the number fold, so ``scoped_ordinal`` silently dropped the
weekday and landed on a bare next-weekday in the wrong month.  Low ordinals
(primo/secondo, not fraction homographs) always worked; the break started at
"terzo".  Expected dates are hand-derived from the calendar, anchor a Tuesday
2017-06-27.
"""
import pytest

from ._corpus import start, nomatch


@pytest.mark.parametrize("text,y,mo,d", [
    # low ordinals -- regression pins, must stay correct
    ("il primo lunedì di marzo", 2017, 3, 6),
    ("il secondo lunedì di marzo", 2017, 3, 13),
    # the previously-broken higher ordinals (fraction homographs)
    ("il terzo lunedì di marzo", 2017, 3, 20),
    ("il quarto lunedì di marzo", 2017, 3, 27),
    ("il quarto giovedì di novembre", 2017, 11, 23),
    ("il terzo giovedì di novembre", 2017, 11, 16),
    ("il quinto lunedì di maggio", 2017, 5, 29),
])
def test_nth_weekday_of_month(text, y, mo, d):
    s = start(text)
    assert (s.year, s.month, s.day) == (y, mo, d)


@pytest.mark.parametrize("text", [
    # March 2017 has only four Mondays -- no fifth exists
    "il quinto lunedì di marzo",
    # February 2017 has only four Thursdays -- no fifth exists
    "il quinto giovedì di febbraio",
])
def test_nonexistent_nth_is_none(text):
    nomatch(text)
