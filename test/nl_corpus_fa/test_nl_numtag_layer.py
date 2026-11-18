"""Persian numbers read through numtag.

A compound count ("بیست و یک", twenty-one) reads whole, not as its last
word.  Every expected value is computed with ``timedelta`` or ``datetime``
from the anchor.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ANCHOR, ad, start


@pytest.mark.parametrize("text,days", [
    ("بیست و یک روز دیگه", 21),
    ("بیست و پنج روز پیش", -25),
    ("سی و یک روز دیگه", 31),
    ("چهل و پنج روز پیش", -45),
])
def test_count(text, days):
    assert start(text) == ad(ANCHOR + timedelta(days=days))


@pytest.mark.parametrize("text,year", [
    ("سال هزار و نهصد و نود و نه", 1999),
    ("سال دو هزار و بیست و پنج", 2025),
])
def test_spelled_year(text, year):
    assert start(text) == ad(datetime(year, 1, 1))
