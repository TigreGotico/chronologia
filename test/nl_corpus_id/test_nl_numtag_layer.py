"""Indonesian numbers read through numtag.

A count and a year with "ribu" (thousand) read whole.  Every expected value
is computed with ``timedelta`` or ``datetime`` from the anchor.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ANCHOR, ad, start


@pytest.mark.parametrize("text,days", [
    ("dua ribu hari lagi", 2000),
    ("seribu dua ratus hari lalu", -1200),
])
def test_count(text, days):
    assert start(text) == ad(ANCHOR + timedelta(days=days))


@pytest.mark.parametrize("text,year", [
    ("tahun dua ribu", 2000),
    ("tahun dua ribu empat puluh", 2040),
])
def test_spelled_year(text, year):
    assert start(text) == ad(datetime(year, 1, 1))
