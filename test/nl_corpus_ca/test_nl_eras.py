# -*- coding: utf-8 -*-
"""Eras and deep time: BC/BCE, AD/CE, before-present, numeric deep time."""
import pytest

from ._corpus import AstroDate, start, span


@pytest.mark.parametrize("text,n", [("44 a.c.", 44), ("753 a.c.", 753), ("300 a.c.", 300), ("1 a.c.", 1), ("3000 a.c.", 3000)])
def test_bc(text, n):
    assert start(text) == AstroDate(1 - n, 1, 1)
    assert span(text).width.days >= 365


@pytest.mark.parametrize("text,n", [("1492 d.c.", 1492), ("800 d.c.", 800), ("79 d.c.", 79), ("2000 d.c.", 2000)])
def test_ad(text, n):
    assert start(text) == AstroDate(n, 1, 1)


@pytest.mark.parametrize("text,n", [("2000 ap", 2000), ("5000 ap", 5000), ("500 ap", 500)])
def test_before_present(text, n):
    assert start(text) == AstroDate(1950 - n, 1, 1)


@pytest.mark.parametrize("text,val", [
    ("fa 66 milions d'anys", 66_000_000),
    ("66 milions d'anys enrere", 66_000_000),
    ("fa 2 milions d'anys", 2_000_000),
])
def test_deep_time(text, val):
    assert start(text).year == 1950 - val
