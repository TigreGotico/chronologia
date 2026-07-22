# -*- coding: utf-8 -*-
"""Open-ended ranges (ar): ``حتى`` / ``إلى`` (until -> open start, span runs
from the anchor to the endpoint) and ``منذ`` (since -> open end, span runs
from the endpoint to the anchor).  Anchor 2017-06-27 13:04 (Tuesday)."""
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import ANCHOR, start_end, ad, nomatch


def test_until_friday_open_start():
    s, e = start_end("حتى الجمعة")
    assert s == ad(ANCHOR)
    assert e == AstroDate(2017, 7, 1)      # next Friday (day-wide endpoint)


def test_until_2020_open_start():
    s, e = start_end("حتى 2020")
    assert s == ad(ANCHOR)
    assert e == AstroDate(2021, 1, 1)      # end of year 2020


def test_until_ela_variant():
    s, e = start_end("إلى 2020")
    assert s == ad(ANCHOR)
    assert e == AstroDate(2021, 1, 1)


def test_since_2010_open_end():
    s, e = start_end("منذ 2010")
    assert s == AstroDate(2010, 1, 1)
    assert e == ad(ANCHOR)


def test_since_2000_open_end():
    s, e = start_end("منذ 2000")
    assert s == AstroDate(2000, 1, 1)
    assert e == ad(ANCHOR)


def test_since_june_open_end():
    s, e = start_end("منذ يناير")
    assert s == AstroDate(2017, 1, 1)
    assert e == ad(ANCHOR)


@pytest.mark.parametrize("text", ["حتى الغداء", "منذ الاجتماع"])
def test_non_temporal_open_range_is_none(text):
    nomatch(text)
