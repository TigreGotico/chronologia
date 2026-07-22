# -*- coding: utf-8 -*-
"""Era and season references in Azerbaijani."""
import pytest
from ._corpus import start, start_end


@pytest.mark.parametrize("text,y", [
    ("44 eramızdan əvvəl", -43), ("753 eramızdan əvvəl", -752),
    ("323 eramızdan əvvəl", -322)])
def test_bc(text, y):
    assert start(text).year == y


@pytest.mark.parametrize("text,y", [
    ("1492 bizim eranın", 1492), ("476 bizim era", 476)])
def test_ad(text, y):
    assert start(text).year == y


@pytest.mark.parametrize("text", ["yay", "qış", "yaz", "payız"])
def test_bare_season(text):
    s, e = start_end(text)
    assert (e - s).days >= 80
