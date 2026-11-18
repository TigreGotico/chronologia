"""Russian numbers read through numtag.

numtag reads the numbers of every case form: the counts, the spelled years,
the day ordinals ("двадцать третьего") and the clock hours.  Every expected
value is written by hand or computed with ``timedelta`` from the anchor; a
lone clock hour takes the next twelve-hour reading after the anchor.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ANCHOR, ad, parse, start


@pytest.mark.parametrize("text,expected", [
    ("тысяча двести дней назад", ANCHOR - timedelta(days=1200)),
    ("через тысячу дней", ANCHOR + timedelta(days=1000)),
    ("двадцать третьего мая 2025", datetime(2025, 5, 23)),
    ("пятнадцатое апреля 2025", datetime(2025, 4, 15)),
    ("в половине девятого", datetime(2017, 6, 27, 20, 30)),
])
def test_numbers_read_through_numtag(text, expected):
    assert start(text) == ad(expected)


# The year of a spelled date is an ordinal that holds a scale word; the
# date keeps the year it names, whatever the anchor.
@pytest.mark.parametrize("anchor", [
    datetime(2026, 1, 10, 8, 0),
    datetime(2026, 12, 1, 8, 0),
    datetime(2028, 3, 1, 8, 0),
])
@pytest.mark.parametrize("text,month,day", [
    ("первого мая две тысячи двадцать шестого года", 5, 1),
    ("двадцатого марта две тысячи двадцать шестого года", 3, 20),
])
def test_spelled_date_with_a_year_from_2000(text, month, day, anchor):
    result = parse(text, anchor)
    assert result is not None
    assert result.span.start == ad(datetime(2026, month, day))
