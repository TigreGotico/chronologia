# -*- coding: utf-8 -*-
"""Adversarial Persian."""
import pytest
from ._corpus import nomatch, start


@pytest.mark.parametrize("text", [
    "", "   ", "سلام دنیا", "روز", "ماه",
    "25:00", "ساعت 25", "32:99",
    "besok", "yarın", "onte", "manyana"])
def test_nomatch(text):
    nomatch(text)


def test_bare_offset_no_direction():
    nomatch("3 روز")


@pytest.mark.parametrize("text", ["... فردا ...", "!!! امروز !!!"])
def test_junk_around(text):
    assert start(text) is not None
