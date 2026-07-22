# -*- coding: utf-8 -*-
"""Open-ended ranges (an): ``dica`` (until -> open start, anchor to endpoint)
and ``dende`` (since -> open end, endpoint to anchor).  Anchor 2018-06-05 13:04."""
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import ANCHOR, start_end, ad, nomatch


def test_dica_friday_open_start():
    s, e = start_end("dica viernes")
    assert s == ad(ANCHOR)
    assert e == AstroDate(2018, 6, 9)      # end of next Friday (Jun 8)


def test_dica_2020_open_start():
    s, e = start_end("dica 2020")
    assert s == ad(ANCHOR)
    assert e == AstroDate(2021, 1, 1)


def test_dica_deciembre_open_start():
    s, e = start_end("dica deciembre")
    assert s == ad(ANCHOR)
    assert e == AstroDate(2019, 1, 1)      # end of December 2018


def test_dende_2010_open_end():
    s, e = start_end("dende 2010")
    assert s == AstroDate(2010, 1, 1)
    assert e == ad(ANCHOR)


def test_dende_2000_open_end():
    s, e = start_end("dende 2000")
    assert s == AstroDate(2000, 1, 1)
    assert e == ad(ANCHOR)


def test_desde_variant_open_end():
    s, e = start_end("desde 2015")
    assert s == AstroDate(2015, 1, 1)
    assert e == ad(ANCHOR)


@pytest.mark.parametrize("text", ["dica a reunión", "dende o mientgodía"])
def test_non_temporal_open_range_is_none(text):
    nomatch(text)
