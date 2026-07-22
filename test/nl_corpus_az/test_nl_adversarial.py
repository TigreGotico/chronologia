# -*- coding: utf-8 -*-
"""Adversarial Azerbaijani."""
import pytest
from ._corpus import nomatch, start


@pytest.mark.parametrize("text", [
    "", "   ", "salam dünya", "beş", "gün", "ay", "əvvəl", "sonra",
    "25:00", "saat 25", "32:99",
    "besok", "kemarin", "yarın", "onte"])
def test_nomatch(text):
    nomatch(text)


def test_bare_offset_no_direction():
    nomatch("3 gün")


def test_marker_without_number():
    # "çoxdan əvvəl" -- əvvəl with no numeric offset must not fire
    nomatch("çoxdan əvvəl")


@pytest.mark.parametrize("text", ["!!! sabah !!!", "... bugün ..."])
def test_junk_around(text):
    assert start(text) is not None
