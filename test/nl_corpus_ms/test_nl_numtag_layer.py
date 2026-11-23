"""Malay numbers read through numtag.

A count or a year with "ribu" (thousand) reads whole, and "delapan" (eight)
counts days.  Every expected value is computed with ``timedelta``,
``relativedelta`` or ``datetime`` from the anchor.
"""
from datetime import datetime, timedelta

import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, start


@pytest.mark.parametrize("text,days", [
    ("delapan hari lagi", 8),
    ("dua ribu hari lagi", 2000),
])
def test_count(text, days):
    assert start(text) == ad(ANCHOR + timedelta(days=days))


def test_thousand_years_ago():
    assert start("dua ribu tahun lalu") == ad(ANCHOR - relativedelta(years=2000))


@pytest.mark.parametrize("text,year", [
    ("tahun dua ribu dua puluh", 2020),
    ("dua ribu dua puluh lima", 2025),
])
def test_spelled_year(text, year):
    assert start(text) == ad(datetime(year, 1, 1))
