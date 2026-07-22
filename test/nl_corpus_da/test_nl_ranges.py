# -*- coding: utf-8 -*-
"""Ranges (da). Dash-framed ranges parse language-agnostically; open-ended
ranges use the native until-marker (open start) and since-marker (open end)."""
import pytest
from ._corpus import AstroDate, start_end, ANCHOR, ad

def test_dash_range():
    s, e = start_end('juni - august')
    assert s == AstroDate(2017, 6, 1) and e == AstroDate(2017, 9, 1)

def test_until_open_start():
    s, e = start_end('indtil fredag')
    assert s == ad(ANCHOR)
    assert e == AstroDate(2017, 7, 1)

def test_since_open_end():
    s, e = start_end('siden 2010')
    assert s == AstroDate(2010, 1, 1)
    assert e == ad(ANCHOR)
