"""Russian years spoken as ordinals.

Russian reads a year as an ordinal numeral, and only its last word declines:
"в две тысячи втором году" is "в 2002 году" (Д. Э. Розенталь, "Справочник по
правописанию и литературной правке", склонение составных порядковых
числительных).  The year word after it is a unit of time, so the number must
not read as a count.  Every expected span is the calendar year, written by
hand.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ANCHOR, ad, start, start_end


@pytest.mark.parametrize("text,year", [
    ("в две тысячи втором году", 2002),
    ("в две тысячи двадцать пятом году", 2025),
    ("в тысяча девятьсот девяносто пятом году", 1995),
    ("две тысячи двадцать пятый год", 2025),
    ("в тысяча девятьсот сорок пятом году", 1945),
])
def test_ordinal_year(text, year):
    assert start_end(text) == (ad(datetime(year, 1, 1)),
                               ad(datetime(year + 1, 1, 1)))


def test_cardinal_count_of_years_stays_a_count():
    assert start("через две тысячи дней") == ad(ANCHOR + timedelta(days=2000))
