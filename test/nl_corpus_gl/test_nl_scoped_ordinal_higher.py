"""Higher-ordinal Nth-weekday-of-month for Galician.

Regression for the cross-Romance silent-wrong where an ordinal spelled like
its fraction ("cuarto" = fourth *and* a-quarter, "quinto" = fifth *and* a
fifth) was held out of the number fold, so ``scoped_ordinal`` silently dropped
the weekday.  Expected dates hand-derived, anchor a Tuesday 2017-06-27.
"""
import pytest

from ._corpus import start, nomatch


@pytest.mark.parametrize("text,y,mo,d", [
    ("o segundo xoves de novembro", 2017, 11, 9),
    ("o terceiro xoves de novembro", 2017, 11, 16),
    ("o cuarto xoves de novembro", 2017, 11, 23),
    # ruling 1 (changed on 26 November 2026): May has ended at the anchor, so
    # it is May 2018, which has no fifth Monday (7, 14, 21, 28); the fifth
    # Tuesday is 29 May 2018
    ("o quinto martes de maio", 2018, 5, 29),
])
def test_nth_weekday_of_month(text, y, mo, d):
    s = start(text)
    assert (s.year, s.month, s.day) == (y, mo, d)


def test_nonexistent_nth_is_none():
    # March 2017 has only four Mondays -- no fifth exists
    nomatch("o quinto luns de marzo")
