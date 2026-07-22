# -*- coding: utf-8 -*-
"""Era references in Malay."""
import pytest
from ._corpus import start


@pytest.mark.parametrize("text,y", [
    ("44 sm", -43), ("753 sm", -752), ("323 sm", -322)])
def test_bc(text, y):
    assert start(text).year == y


@pytest.mark.parametrize("text,y", [
    ("1492 m", 1492), ("476 m", 476), ("1957 m", 1957)])
def test_ad(text, y):
    assert start(text).year == y
