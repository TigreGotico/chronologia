"""Finnish numbers read through numtag.

A spelled year is one compound word ("kaksituhattakaksikymmentäviisi"), and a
count with a thousand reads whole.  Every expected value is written by hand
or computed with ``timedelta`` from the anchor.
"""
import pytest

from ._corpus import ANCHOR, ad, datetime, start, start_end, timedelta


@pytest.mark.parametrize("text,year", [
    ("vuonna kaksituhattakaksikymmentäviisi", 2025),
    ("vuonna tuhatyhdeksänsataayhdeksänkymmentäyhdeksän", 1999),
    ("vuonna kaksituhattayksi", 2001),
])
def test_spelled_year(text, year):
    assert start_end(text) == (ad(datetime(year, 1, 1)),
                               ad(datetime(year + 1, 1, 1)))


@pytest.mark.parametrize("text,days", [
    ("tuhat päivää sitten", 1000),
    ("tuhatkaksisataa päivää sitten", 1200),
])
def test_count_with_a_thousand(text, days):
    assert start(text) == ad(ANCHOR - timedelta(days=days))
