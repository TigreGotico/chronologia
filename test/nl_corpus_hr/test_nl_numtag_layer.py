"""Croatian numbers read through numtag.

numtag reads the numbers of every case form: the counts, the spelled years,
the day ordinals ("dvadeset i trećega") and the clock hours.  Every expected
value is written by hand or computed with ``timedelta`` from the anchor; a
lone clock hour takes the next twelve-hour reading after the anchor.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ANCHOR, ad, start


@pytest.mark.parametrize("text,expected", [
    ("za tisuću dana", ANCHOR + timedelta(days=1000)),
    ("tisuću devetsto devedeset pete godine", datetime(1995, 1, 1)),
    ("trećega prosinca 2025", datetime(2025, 12, 3)),
    ("dvadeset i trećega svibnja 2025", datetime(2025, 5, 23)),
    ("pola devet", datetime(2017, 6, 27, 20, 30)),
])
def test_numbers_read_through_numtag(text, expected):
    assert start(text) == ad(expected)
