"""Mirandese numbers read through numtag.

A count with "mil" (thousand) reads whole, and so does a spelled year. Every
expected value is computed with ``timedelta`` or ``datetime`` from the
anchor.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ANCHOR, ad, start


@pytest.mark.parametrize("text,days", [
    ("déntro de mil dies", 1000),
    ("hai dous mil dies", -2000),
])
def test_count(text, days):
    assert start(text) == ad(ANCHOR + timedelta(days=days))


@pytest.mark.parametrize("text,year", [
    ("l anho mil nuobe cientos i setenta i siete", 1977),
    ("l anho dous mil i bint'i seis", 2026),
])
def test_spelled_year(text, year):
    assert start(text) == ad(datetime(year, 1, 1))
