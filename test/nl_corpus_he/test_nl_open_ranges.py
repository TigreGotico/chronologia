# -*- coding: utf-8 -*-
"""Open-ended ranges (he): ``עד`` (until -> open start, anchor to endpoint)
and ``מאז`` (since -> open end, endpoint to anchor).  Anchor 2017-06-27 13:04."""
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import ANCHOR, start_end, ad, nomatch


def test_until_friday_open_start():
    s, e = start_end("עד יום שישי")
    assert s == ad(ANCHOR)
    assert e == AstroDate(2017, 7, 1)      # next Friday (day-wide endpoint)


def test_until_2020_open_start():
    s, e = start_end("עד 2020")
    assert s == ad(ANCHOR)
    assert e == AstroDate(2021, 1, 1)


def test_since_2010_open_end():
    s, e = start_end("מאז 2010")
    assert s == AstroDate(2010, 1, 1)
    assert e == ad(ANCHOR)


def test_since_2000_open_end():
    s, e = start_end("מאז 2000")
    assert s == AstroDate(2000, 1, 1)
    assert e == ad(ANCHOR)


def test_since_january_open_end():
    s, e = start_end("מאז ינואר")
    assert s == AstroDate(2017, 1, 1)
    assert e == ad(ANCHOR)


def test_until_december_open_start():
    s, e = start_end("עד דצמבר")
    assert s == ad(ANCHOR)
    assert e == AstroDate(2018, 1, 1)      # end of December (endpoint span end)


@pytest.mark.parametrize("text", ["עד הפגישה", "מאז הארוחה"])
def test_non_temporal_open_range_is_none(text):
    nomatch(text)
