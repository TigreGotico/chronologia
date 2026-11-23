"""Estonian numbers read through numtag.

A count with a thousand reads whole.  Every expected value is computed with
``timedelta`` from the anchor.
"""
import pytest

from ._corpus import ANCHOR, ad, start, timedelta


@pytest.mark.parametrize("text,days", [
    ("tuhat päeva tagasi", 1000),
    ("tuhat kakssada päeva tagasi", 1200),
    ("kaks tuhat kakskümmend viis päeva tagasi", 2025),
])
def test_count_with_a_thousand(text, days):
    assert start(text) == ad(ANCHOR - timedelta(days=days))
