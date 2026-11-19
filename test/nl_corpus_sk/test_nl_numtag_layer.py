"""Slovak numbers read through numtag.

numtag reads the numbers of every case form: the counts, the spelled years,
the day ordinals ("dvadsiateho tretieho") and the clock hours.  Every expected
value is written by hand or computed with ``timedelta`` from the anchor; a
lone clock hour takes the next twelve-hour reading after the anchor.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ANCHOR, ad, parse, start


@pytest.mark.parametrize("text,expected", [
    ("o stodesať dní", ANCHOR + timedelta(days=110)),
    ("v roku dvetisícdvadsaťpäť", datetime(2025, 1, 1)),
    ("dvadsiateho tretieho mája 2025", datetime(2025, 5, 23)),
    ("pol deviatej", datetime(2017, 6, 27, 20, 30)),
    ("o druhej", datetime(2017, 6, 27, 14, 0)),
])
def test_numbers_read_through_numtag(text, expected):
    assert start(text) == ad(expected)


# An ordinal hour after the clock preposition keeps its clock when a word
# outside the vocabulary follows; the clock reads the same without it.
@pytest.mark.parametrize("text,expected", [
    ("o deviatej zavolaj mame", datetime(2017, 6, 27, 21, 0)),
    ("zajtra o ôsmej stretnutie s lekárom", datetime(2017, 6, 28, 8, 0)),
])
def test_ordinal_hour_before_another_word(text, expected):
    assert start(text) == ad(expected)


def test_masculine_ordinal_after_o_is_no_clock():
    assert parse("o druhom etape") is None
