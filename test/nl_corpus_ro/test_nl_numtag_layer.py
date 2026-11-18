"""Romanian numbers read through numtag.

A count with "sută" (hundred) reads whole, and so does a spelled year. Every
expected value is computed with ``timedelta`` or ``datetime`` from the
anchor.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ANCHOR, ad, start


@pytest.mark.parametrize("text,days", [
    ("peste o sută unu zile", 101),
    ("acum o mie nouă sute nouăzeci și nouă zile", -1999),
])
def test_count(text, days):
    assert start(text) == ad(ANCHOR + timedelta(days=days))


@pytest.mark.parametrize("text,year", [
    ("anul o mie nouă sute paisprezece", 1914),
    ("anul două mii doisprezece", 2012),
    ("anul două mii șaizeci și unu", 2061),
])
def test_spelled_year(text, year):
    assert start(text) == ad(datetime(year, 1, 1))
