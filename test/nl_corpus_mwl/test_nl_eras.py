# -*- coding: utf-8 -*-
"""Era and season references in Mirandese."""
import pytest
from ._corpus import start, start_end


@pytest.mark.parametrize("text,y", [
    ("44 ac", -43), ("753 ac", -752), ("218 ac", -217)])
def test_bc(text, y):
    assert start(text).year == y


@pytest.mark.parametrize("text,y", [("1492 dc", 1492), ("476 dc", 476)])
def test_ad(text, y):
    assert start(text).year == y


@pytest.mark.parametrize("text", ["berano", "ambierno", "primabera", "outonho"])
def test_bare_season(text):
    s, e = start_end(text)
    assert (e - s).days >= 80
