"""Aragonese numbers read through numtag.

A count with "mil" (thousand) reads whole, and so does a spelled year. Every
expected value is computed with ``timedelta`` or ``datetime`` from the
anchor.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ANCHOR, ad, start


@pytest.mark.parametrize("text,days", [
    ("dentro de mil diyas", 1000),
    ("fa dos mil diyas", -2000),
])
def test_count(text, days):
    assert start(text) == ad(ANCHOR + timedelta(days=days))


@pytest.mark.parametrize("text,year", [
    ("l'anyo mil noucientos y cuaranta y dos", 1942),
    ("l'anyo mil noucientos y novanta y un", 1991),
])
def test_spelled_year(text, year):
    assert start(text) == ad(datetime(year, 1, 1))
