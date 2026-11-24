"""Slovene numbers read through numtag.

numtag reads the numbers of every case form: the counts, the spelled years,
the day ordinals ("triindvajsetega") and the clock hours.  Every expected
value is written by hand or computed with ``timedelta`` from the anchor; a
lone clock hour takes the next twelve-hour reading after the anchor.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ANCHOR, ad, parse, start


@pytest.mark.parametrize("text,expected", [
    ("čez tisoč dni", ANCHOR + timedelta(days=1000)),
    ("triindvajsetega maja 2025", datetime(2025, 5, 23)),
    ("ob enih", datetime(2017, 6, 28, 1, 0)),
    ("pol devetih", datetime(2017, 6, 27, 20, 30)),
])
def test_numbers_read_through_numtag(text, expected):
    assert start(text) == ad(expected)


@pytest.mark.parametrize("text", ["ob drugem obisku", "ob tretjem poskusu"])
def test_ordinal_after_at_is_no_clock(text):
    assert parse(text) is None
