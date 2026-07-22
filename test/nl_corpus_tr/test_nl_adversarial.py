# -*- coding: utf-8 -*-
"""Adversarial Turkish: things that must NOT parse (or parse cleanly)."""
import pytest
from ._corpus import nomatch, parse, start


@pytest.mark.parametrize("text", [
    "", "   ", "merhaba dünya", "beş", "gün", "ay",
    "önce", "sonra",
    "25:00", "saat 25", "32:99",
    "besok", "lusa", "kemarin",  # Indonesian/Malay must not leak
    "manyana", "demán",           # Aragonese must not leak
    "xoves", "onte"])             # Galician must not leak
def test_nomatch(text):
    nomatch(text)


def test_bare_offset_no_direction():
    # "3 gün" with no önce/sonra is a bare span, not a date
    nomatch("3 gün")


@pytest.mark.parametrize("text", [
    "!!! yarın !!!", "... bugün ..."])
def test_junk_around(text):
    assert start(text) is not None
