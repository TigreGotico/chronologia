"""Czech numbers read through numtag.

numtag reads the numbers of every case form: the counts, the spelled years,
the day ordinals ("dvacátého třetího") and the clock hours.  Every expected
value is written by hand or computed with ``timedelta`` from the anchor; a
lone clock hour takes the next twelve-hour reading after the anchor.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ANCHOR, ad, start


@pytest.mark.parametrize("text,expected", [
    ("za tisíc dní", ANCHOR + timedelta(days=1000)),
    ("v roce dva tisíce dvacet pět", datetime(2025, 1, 1)),
    ("dvacátého třetího května 2025", datetime(2025, 5, 23)),
    ("prvého května 2025", datetime(2025, 5, 1)),
    ("půl deváté", datetime(2017, 6, 27, 20, 30)),
    ("tři čtvrtě na sedm", datetime(2017, 6, 27, 18, 45)),
])
def test_numbers_read_through_numtag(text, expected):
    assert start(text) == ad(expected)
