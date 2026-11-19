"""Arabic numbers read through numtag.

A count above ten, a compound count and a spelled year read whole.  Every
expected value is computed with ``timedelta`` or ``datetime`` from the
anchor.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ANCHOR, ad, start


@pytest.mark.parametrize("text,days", [
    ("بعد اثنا عشر يوم", 12),
    ("قبل اثنان وأربعون يوم", -42),
    ("بعد اثنان وتسعون يوم", 92),
    ("قبل ألف ومئتان يوم", -1200),
])
def test_count(text, days):
    assert start(text) == ad(ANCHOR + timedelta(days=days))


@pytest.mark.parametrize("text,year", [
    ("عام ألف وتسعمئة وأربعة عشر", 1914),
    ("عام ألفان وخمسة وعشرون", 2025),
])
def test_spelled_year(text, year):
    assert start(text) == ad(datetime(year, 1, 1))
