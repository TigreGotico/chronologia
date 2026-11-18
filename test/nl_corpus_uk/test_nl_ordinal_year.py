"""Ukrainian years spoken as ordinals.

Ukrainian reads a year as an ordinal numeral, and only its last word
declines: "у дві тисячі другому році" is "у 2002 році" (Український правопис,
відмінювання складених порядкових числівників).  The year word after it is a
unit of time, so the number must not read as a count.  Every expected span is
the calendar year, written by hand.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ANCHOR, ad, start, start_end


@pytest.mark.parametrize("text,year", [
    ("у дві тисячі другому році", 2002),
    ("у дві тисячі двадцять п'ятому році", 2025),
    ("тисяча дев'ятсот дев'яносто четвертий рік", 1994),
    ("у тисяча дев'ятсот сорок п'ятому році", 1945),
])
def test_ordinal_year(text, year):
    assert start_end(text) == (ad(datetime(year, 1, 1)),
                               ad(datetime(year + 1, 1, 1)))


def test_cardinal_count_of_days_stays_a_count():
    assert start("через дві тисячі днів") == ad(ANCHOR + timedelta(days=2000))
