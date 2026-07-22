# -*- coding: utf-8 -*-
"""Open-ended ranges (mwl): ``até`` (until -> open start, anchor to endpoint)
and ``zde`` / ``desde`` (since -> open end, endpoint to anchor).  Anchor
2017-06-27 13:04."""
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import ANCHOR, start_end, ad, nomatch


def test_ate_friday_open_start():
    s, e = start_end("até sesta feira")
    assert s == ad(ANCHOR)
    assert e == AstroDate(2017, 7, 1)      # end of next Friday (Jun 30)


def test_ate_2020_open_start():
    s, e = start_end("até 2020")
    assert s == ad(ANCHOR)
    assert e == AstroDate(2021, 1, 1)


def test_ate_dezembre_open_start():
    s, e = start_end("até dezembre")
    assert s == ad(ANCHOR)
    assert e == AstroDate(2018, 1, 1)      # end of December 2017


def test_zde_2010_open_end():
    s, e = start_end("zde 2010")
    assert s == AstroDate(2010, 1, 1)
    assert e == ad(ANCHOR)


def test_desde_2000_open_end():
    s, e = start_end("desde 2000")
    assert s == AstroDate(2000, 1, 1)
    assert e == ad(ANCHOR)


def test_zde_janeiro_open_end():
    s, e = start_end("zde janeiro")
    assert s == AstroDate(2017, 1, 1)
    assert e == ad(ANCHOR)


@pytest.mark.parametrize("text", ["até la reunion", "zde l almuorço"])
def test_non_temporal_open_range_is_none(text):
    nomatch(text)
