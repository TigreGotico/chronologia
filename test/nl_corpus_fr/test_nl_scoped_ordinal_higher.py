"""Higher-ordinal Nth-weekday-of-month for French.

French spells most ordinals distinctly from their fractions ("quatrième" vs
"un quart"), so only the ordinals that *are* fraction homographs were broken:
"cinquième"/"sixième"/... doubling as the a-fifth/a-sixth fraction were held
out of the number fold, so ``scoped_ordinal`` silently dropped the weekday for
those.  "quatrième" (fourth) already worked and is pinned as a regression.
Anchor a Tuesday 2017-06-27.

Ruling 1 (changed on 26 November 2026): a part of a month with no year takes
the year the month alone takes, so May (ended at the anchor) is May 2018.  May
2018 has only four Mondays (7, 14, 21, 28), so the fifth-ordinal case uses the
fifth Tuesday (1, 8, 15, 22, 29) instead of the fifth Monday.
"""
import pytest

from ._corpus import start, nomatch


@pytest.mark.parametrize("text,y,mo,d", [
    ("le quatrième jeudi de novembre", 2017, 11, 23),
    # ruling 1: May has ended at the anchor, so it is May 2018 (no fifth Monday
    # there; the fifth Tuesday is May 29)
    ("le cinquième mardi de mai", 2018, 5, 29),
])
def test_nth_weekday_of_month(text, y, mo, d):
    s = start(text)
    assert (s.year, s.month, s.day) == (y, mo, d)


def test_nonexistent_nth_is_none():
    # March 2017 has only four Mondays -- no fifth exists
    nomatch("le cinquième lundi de mars")
