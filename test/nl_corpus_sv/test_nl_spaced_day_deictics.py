# -*- coding: utf-8 -*-
"""sv: the spaced day deictics CLDR gives as the standard surfaces.

Unicode CLDR 47 ``cldr-dates-full/main/sv/dateFields.json`` spells the
day deictics of Swedish with a space -- ``day.relative-type--2`` through
``day.relative-type-2`` -- so the whole phrase must bind as one named day and
leave nothing behind. The written-together spellings stay valid alongside it.

Anchor: Tuesday 2017-06-27 13:04, so the five days are 06-25 .. 06-29.
"""
import pytest

from chronologia.astrodate import AstroDate

from ._corpus import ANCHOR, parse, span  # noqa: F401

_DAY = {-2: 25, -1: 26, 0: 27, 1: 28, 2: 29}


def _whole_day(text, off):
    """The phrase covers exactly the calendar day at ``off`` and nothing is left."""
    r = parse(text)
    assert r is not None, f"{text!r} did not parse"
    assert r.remainder == "", f"{text!r} stranded {r.remainder!r}"
    assert (r.span.start, r.span.end) == (
        AstroDate(2017, 6, _DAY[off]), AstroDate(2017, 6, _DAY[off] + 1)
    ), f"{text!r} resolved to {r.span}"


@pytest.mark.parametrize("text,off", [('i förrgår', -2), ('i går', -1), ('i dag', 0), ('i morgon', 1), ('i övermorgon', 2)])
def test_spaced_day_deictic(text, off):
    _whole_day(text, off)


@pytest.mark.parametrize("text,off", [('förrgår', -2), ('igår', -1), ('idag', 0), ('imorgon', 1), ('övermorgon', 2)])
def test_written_together_day_deictic_still_binds(text, off):
    _whole_day(text, off)


def test_bare_morgon_is_the_morning_band():
    """A bare ``morgon`` is the noun "morning" and keeps its CLDR day-period band."""
    s = span("morgon")
    assert (s.start, s.end) == (AstroDate(2017, 6, 27, 5, 0),
                                AstroDate(2017, 6, 27, 10, 0))


def test_spaced_tomorrow_is_not_the_morning_band():
    """``i morgon`` is tomorrow, never today's morgon band read off ``morgon`` alone."""
    s = span("i morgon")
    assert s.start != AstroDate(2017, 6, 27, 5, 0)
    assert (s.start, s.end) == (AstroDate(2017, 6, 28), AstroDate(2017, 6, 29))


def test_spaced_tomorrow_composes_with_the_morning_band():
    """The deictic still takes a following daypart: tomorrow's morgon band."""
    s = span("i morgon morgon")
    assert (s.start, s.end) == (AstroDate(2017, 6, 28, 5, 0),
                                AstroDate(2017, 6, 28, 10, 0))
