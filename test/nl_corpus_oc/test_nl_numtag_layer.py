"""Occitan numbers read through numtag.

A count with "cents" (hundreds) or "mila" (thousand) reads whole. Every
expected value is computed with ``timedelta`` from the anchor.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, start


@pytest.mark.parametrize("text,days", [
    ("dins tres cents jorns", 300),
    ("fa mila dos cents jorns", -1200),
    ("fa vint e un jorns", -21),
])
def test_count(text, days):
    assert start(text) == ad(ANCHOR + timedelta(days=days))

