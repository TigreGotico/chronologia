"""Slovene names noon and midnight with an adverb as well as a noun.

Beside the bare nouns "poldne" and "polnoč", running prose uses "opoldne"
(at noon) and "opolnoči" (at midnight), and "dopoldne" (before noon) is the
ante-meridiem mirror of the "popoldne" this locale already reads.

Anchor 2017-06-27 13:04, which is past noon, so the next noon and the next
midnight are both on the 28th.
"""
import pytest

from ._corpus import AstroDate, parse, start


@pytest.mark.parametrize("text,hour", [
    ("opoldne", 12),
    ("poldne", 12),
])
def test_noon(text, hour):
    assert start(text) == AstroDate(2017, 6, 28, hour, 0)
    assert parse(text).remainder == ""


@pytest.mark.parametrize("text", ["opolnoči", "polnoč"])
def test_midnight(text):
    assert start(text) == AstroDate(2017, 6, 28, 0, 0)
    assert parse(text).remainder == ""


def test_before_noon_binds_the_hour():
    assert start("ob deseti uri dopoldne") == AstroDate(2017, 6, 28, 10, 0)
    assert parse("ob deseti uri dopoldne").remainder == ""


@pytest.mark.parametrize("text,day,hour", [
    # the afternoon adverb keeps both its readings
    ("popoldne", 27, 12),
    ("ob štirih popoldne", 27, 16),
])
def test_the_afternoon_adverb_is_unchanged(text, day, hour):
    assert start(text) == AstroDate(2017, 6, day, hour, 0)
