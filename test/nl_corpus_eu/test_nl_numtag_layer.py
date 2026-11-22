"""Basque numbers read through numtag.

A count above a hundred joins its parts with "eta" ("ehun eta hamar"), and
the count reads whole.  Every expected value is computed with ``timedelta``
from the anchor.
"""
import pytest

from ._corpus import ANCHOR, ad, start, timedelta


@pytest.mark.parametrize("text,days", [
    ("ehun eta hamar egun barru", 110),
    ("duela ehun eta hamar egun", -110),
    ("mila egun barru", 1000),
    ("duela bi mila eta hogeita bost egun", -2025),
])
def test_count(text, days):
    assert start(text) == ad(ANCHOR + timedelta(days=days))
