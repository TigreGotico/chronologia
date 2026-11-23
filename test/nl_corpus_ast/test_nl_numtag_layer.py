"""Asturian numbers read through numtag.

A count with "mil" (thousand) reads whole, and so does a spelled year. Every
expected value is computed with ``timedelta`` or ``datetime`` from the
anchor.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ANCHOR, ad, start


@pytest.mark.parametrize("text,days", [
    ("en mil díes", 1000),
    ("hai dos mil díes", -2000),
])
def test_count(text, days):
    assert start(text) == ad(ANCHOR + timedelta(days=days))


@pytest.mark.parametrize("text,year", [
    ("l'añu mil novecientos y cuarenta y dos", 1942),
    ("l'añu mil novecientos y noventa y un", 1991),
])
def test_spelled_year(text, year):
    assert start(text) == ad(datetime(year, 1, 1))
