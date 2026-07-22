# -*- coding: utf-8 -*-
"""Adversarial Indonesian."""
import pytest
from ._corpus import nomatch, start


@pytest.mark.parametrize("text", [
    "", "   ", "halo dunia", "lima", "hari", "jam",
    "25:00", "pukul 30", "32:99",
    "yarın", "dün", "onte", "manyana"])
def test_nomatch(text):
    nomatch(text)


def test_bare_offset_no_direction():
    nomatch("3 hari")


@pytest.mark.parametrize("text", ["... besok ...", "!!! hari ini !!!"])
def test_junk_around(text):
    assert start(text) is not None
