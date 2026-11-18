"""Bulgarian numbers read through numtag.

numtag reads the numbers of every case form: the counts, the spelled years,
the day ordinals ("двадесет и трети") and the clock hours.  Every expected
value is written by hand or computed with ``timedelta`` from the anchor; a
lone clock hour takes the next twelve-hour reading after the anchor.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ANCHOR, ad, start


@pytest.mark.parametrize("text,expected", [
    ("след хиляда дни", ANCHOR + timedelta(days=1000)),
    ("преди хиляда и двеста дни", ANCHOR - timedelta(days=1200)),
    ("единадесети май 2025", datetime(2025, 5, 11)),
    ("двадесет и трети май 2025", datetime(2025, 5, 23)),
    ("в осем и половина", datetime(2017, 6, 27, 20, 30)),
])
def test_numbers_read_through_numtag(text, expected):
    assert start(text) == ad(expected)
