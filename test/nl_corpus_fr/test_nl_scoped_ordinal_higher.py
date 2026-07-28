"""Higher-ordinal Nth-weekday-of-month for French.

French spells most ordinals distinctly from their fractions ("quatrième" vs
"un quart"), so only the ordinals that *are* fraction homographs were broken:
"cinquième"/"sixième"/... doubling as the a-fifth/a-sixth fraction were held
out of the number fold, so ``scoped_ordinal`` silently dropped the weekday for
those.  "quatrième" (fourth) already worked and is pinned as a regression.
Anchor a Tuesday 2017-06-27.
"""
import pytest

from ._corpus import start, nomatch


@pytest.mark.parametrize("text,y,mo,d", [
    ("le quatrième jeudi de novembre", 2017, 11, 23),
    ("le cinquième lundi de mai", 2017, 5, 29),
])
def test_nth_weekday_of_month(text, y, mo, d):
    s = start(text)
    assert (s.year, s.month, s.day) == (y, mo, d)


def test_nonexistent_nth_is_none():
    # March 2017 has only four Mondays -- no fifth exists
    nomatch("le cinquième lundi de mars")
