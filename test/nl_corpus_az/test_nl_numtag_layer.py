"""Azerbaijani numbers read through numtag.

A count with "min" (thousand) reads whole, and "o biri gün" stays the day
after tomorrow.  Every expected value is computed with ``timedelta`` from the
anchor.
"""
import pytest

from ._corpus import ANCHOR, ad, datetime, start, start_end, timedelta


@pytest.mark.parametrize("text,days", [
    ("min gün sonra", 1000),
    ("iki min gün əvvəl", -2000),
    ("min iki yüz gün sonra", 1200),
])
def test_count(text, days):
    assert start(text) == ad(ANCHOR + timedelta(days=days))


def test_the_day_after_tomorrow():
    assert start_end("o biri gün") == (ad(datetime(2017, 6, 29)),
                                       ad(datetime(2017, 6, 30)))
