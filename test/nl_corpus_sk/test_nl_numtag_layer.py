"""Slovak numbers read through numtag.

numtag reads the numbers of every case form: the counts, the spelled years,
the day ordinals ("dvadsiateho tretieho") and the clock hours.  Every expected
value is written by hand or computed with ``timedelta`` from the anchor; a
lone clock hour takes the next twelve-hour reading after the anchor.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ANCHOR, ad, start


@pytest.mark.parametrize("text,expected", [
    ("o stodesať dní", ANCHOR + timedelta(days=110)),
    ("v roku dvetisícdvadsaťpäť", datetime(2025, 1, 1)),
    ("dvadsiateho tretieho mája 2025", datetime(2025, 5, 23)),
    ("pol deviatej", datetime(2017, 6, 27, 20, 30)),
    ("o druhej", datetime(2017, 6, 27, 14, 0)),
])
def test_numbers_read_through_numtag(text, expected):
    assert start(text) == ad(expected)
