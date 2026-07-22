# -*- coding: utf-8 -*-
"""Adversarial Mirandese."""
import pytest
from ._corpus import nomatch, start


@pytest.mark.parametrize("text", [
    "", "   ", "buonos dies", "cinco", "die", "més",
    "25:00", "32:99",
    "besok", "yarın", "yesterday", "manyana"])
def test_nomatch(text):
    nomatch(text)


def test_bare_past_marker_without_number():
    # "hai" with no numeric offset must not fire
    nomatch("hai muito")


@pytest.mark.parametrize("text", ["... hoije ...", "!!! manhana !!!"])
def test_junk_around(text):
    assert start(text) is not None
