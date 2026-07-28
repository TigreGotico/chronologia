"""Higher-ordinal Nth-weekday-of-month for Portuguese.

Regression for the cross-Romance silent-wrong where an ordinal spelled like
its fraction ("quarto" = fourth *and* a-quarter, "quinto" = fifth *and* a
fifth) was held out of the number fold, so ``scoped_ordinal`` silently dropped
the weekday.  Masculine "domingo" (Sunday) is used to stay clear of the
separate feminine-ordinal/weekday homograph ("quarta" = fourth *and*
Wednesday), which is deliberately left untouched here.  Anchor 2017-06-27.
"""
import pytest

from ._corpus import start, nomatch


@pytest.mark.parametrize("text,y,mo,d", [
    ("o segundo domingo de novembro", 2017, 11, 12),
    ("o terceiro domingo de novembro", 2017, 11, 19),
    ("o quarto domingo de novembro", 2017, 11, 26),
    ("o quinto domingo de outubro", 2017, 10, 29),
])
def test_nth_weekday_of_month(text, y, mo, d):
    s = start(text)
    assert (s.year, s.month, s.day) == (y, mo, d)


def test_nonexistent_nth_is_none():
    # November 2017 has only four Sundays -- no fifth exists
    nomatch("o quinto domingo de novembro")
