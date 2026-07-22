# -*- coding: utf-8 -*-
"""Adversarial Kabyle."""
import pytest
from ._corpus import nomatch, start


@pytest.mark.parametrize("text", [
    "", "   ", "azul fell-awen", "amek tellam",
    "25:00", "32:99",
    "besok", "yarın", "onte", "manyana"])
def test_nomatch(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["... azekka ...", "!!! assa !!!"])
def test_junk_around(text):
    assert start(text) is not None
