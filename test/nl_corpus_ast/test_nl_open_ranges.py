# -*- coding: utf-8 -*-
"""Open-ended ranges (ast): an until-marker leaves the start open (-> anchor);
a since-marker leaves the end open (-> anchor)."""
from ._corpus import ANCHOR, ad, start_end
from chronologia.astrodate import AstroDate


def test_until_open_start():
    s, e = start_end('hasta vienres')
    assert s == ad(ANCHOR)
    assert e == AstroDate(2017, 7, 1)


def test_since_open_end():
    s, e = start_end('dende 2010')
    assert s == AstroDate(2010, 1, 1)
    assert e == ad(ANCHOR)
