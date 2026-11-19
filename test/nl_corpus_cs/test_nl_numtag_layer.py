"""Czech numbers read through numtag.

numtag reads the numbers of every case form: the counts, the spelled years,
the day ordinals ("dvacátého třetího") and the clock hours.  Every expected
value is written by hand or computed with ``timedelta`` from the anchor; a
lone clock hour takes the next twelve-hour reading after the anchor.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ANCHOR, ad, parse, start


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


# An ordinal after a preposition names a thing, not an hour: the hour of
# this language is a cardinal.
def test_ordinal_after_a_locative_preposition_is_no_clock():
    assert parse("ve druhém patře") is None


@pytest.mark.xfail(strict=True, reason="https://github.com/TigreGotico/chronologia/issues/1193")
def test_known_gap_hour_and_minute_clock():
    assert start("v devět třicet") == ad(datetime(2017, 6, 27, 21, 30))


@pytest.mark.parametrize("text", ["mluvili jsme o druhém díle", "o třetím pokusu"])
def test_ordinal_after_about_is_no_clock(text):
    assert parse(text) is None
