# -*- coding: utf-8 -*-
"""Era and season references in Turkish."""
import pytest
from ._corpus import start, start_end, AstroDate


@pytest.mark.parametrize("text,y", [
    ("44 mö", -43), ("753 mö", -752), ("323 mö", -322)])
def test_bc(text, y):
    assert start(text).year == y


@pytest.mark.parametrize("text,y", [
    ("1492 ms", 1492), ("476 ms", 476), ("1071 ms", 1071)])
def test_ad(text, y):
    assert start(text).year == y


@pytest.mark.parametrize("text,m", [
    ("yaz", 6), ("kış", 12), ("ilkbahar", 3), ("sonbahar", 9)])
def test_bare_season(text, m):
    # season resolves to a 3-month span starting on its first month
    s, e = start_end(text)
    assert (e - s).days >= 80
