"""Hebrew numbers read through numtag.

A teen and a compound count read whole, and so does a spelled year.  Every
expected value is computed with ``timedelta`` or ``datetime`` from the
anchor.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ANCHOR, ad, start


@pytest.mark.parametrize("text,days", [
    ("בעוד שתים עשרה ימים", 12),
    ("לפני עשרים וארבע ימים", -24),
    ("בעוד שלושים ותשע ימים", 39),
    ("לפני ארבעים וארבע ימים", -44),
])
def test_count(text, days):
    assert start(text) == ad(ANCHOR + timedelta(days=days))


@pytest.mark.parametrize("text,year", [
    ("בשנת אלף תשע מאות תשעים ותשע", 1999),
    ("בשנת אלפיים עשרים וחמש", 2025),
])
def test_spelled_year(text, year):
    assert start(text) == ad(datetime(year, 1, 1))
