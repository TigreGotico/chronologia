"""Higher-ordinal Nth-weekday-of-month for Spanish.

Regression for the cross-Romance silent-wrong where an ordinal spelled like
its fraction ("cuarto" = fourth *and* a-quarter, "quinto" = fifth *and* a
fifth) was held out of the number fold, so ``scoped_ordinal`` silently dropped
the weekday and landed on a bare next-weekday in the wrong month.  Spanish's
low ordinals (primer/segundo/tercer) always worked; the break started at
"cuarto".  Expected dates are hand-derived, anchor a Tuesday 2017-06-27.
"""
import pytest

from ._corpus import start, nomatch


@pytest.mark.parametrize("text,y,mo,d", [
    # low ordinals -- regression pins, must stay correct
    ("el tercer jueves de noviembre", 2017, 11, 16),
    ("el segundo lunes de mayo", 2017, 5, 8),
    # the previously-broken higher ordinals
    ("el cuarto jueves de noviembre", 2017, 11, 23),
    ("el cuarto lunes de mayo", 2017, 5, 22),
    ("el quinto lunes de mayo", 2017, 5, 29),
    # feminine ordinal + unit ("la cuarta semana") was broken the same way
    ("la cuarta semana de marzo", 2017, 3, 27),
])
def test_nth_weekday_of_month(text, y, mo, d):
    s = start(text)
    assert (s.year, s.month, s.day) == (y, mo, d)


@pytest.mark.parametrize("text", [
    # May 2017 has five Mondays but no sixth
    "el sexto lunes de mayo",
    # March 2017 has only four Mondays -- no fifth exists
    "el quinto lunes de marzo",
])
def test_nonexistent_nth_is_none(text):
    nomatch(text)
