"""Turkish numbers read through numtag.

A count with "bin" (thousand) reads whole.  Every expected value is computed
with ``timedelta`` from the anchor.
"""
import pytest

from ._corpus import ANCHOR, ad, start, timedelta


@pytest.mark.parametrize("text,days", [
    ("bin gün sonra", 1000),
    ("iki bin gün önce", -2000),
    ("bin iki yüz gün sonra", 1200),
    ("iki bin yirmi beş gün önce", -2025),
])
def test_count(text, days):
    assert start(text) == ad(ANCHOR + timedelta(days=days))
