"""Russian numbers read through numtag.

numtag reads the numbers of every case form: the counts, the spelled years,
the day ordinals ("двадцать третьего") and the clock hours.  Every expected
value is written by hand or computed with ``timedelta`` from the anchor; a
lone clock hour takes the next twelve-hour reading after the anchor.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ANCHOR, ad, start


@pytest.mark.parametrize("text,expected", [
    ("тысяча двести дней назад", ANCHOR - timedelta(days=1200)),
    ("через тысячу дней", ANCHOR + timedelta(days=1000)),
    ("двадцать третьего мая 2025", datetime(2025, 5, 23)),
    ("пятнадцатое апреля 2025", datetime(2025, 4, 15)),
    ("в половине девятого", datetime(2017, 6, 27, 20, 30)),
])
def test_numbers_read_through_numtag(text, expected):
    assert start(text) == ad(expected)
