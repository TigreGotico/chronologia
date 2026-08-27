# -*- coding: utf-8 -*-
"""nb: the spaced day deictics CLDR gives as the standard surfaces.

Unicode CLDR 47 ``cldr-dates-full/main/nb/dateFields.json`` spells the
day deictics of Norwegian Bokmål with a space -- ``day.relative-type--2`` through
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


@pytest.mark.parametrize("text,off", [('i forgårs', -2), ('i går', -1), ('i dag', 0), ('i morgen', 1), ('i overmorgen', 2)])
def test_spaced_day_deictic(text, off):
    _whole_day(text, off)


@pytest.mark.parametrize("text,off", [('iforgårs', -2), ('igår', -1), ('idag', 0), ('imorgen', 1), ('overmorgen', 2)])
def test_written_together_day_deictic_still_binds(text, off):
    _whole_day(text, off)


def test_bare_morgen_is_still_tomorrow():
    """Morgen carries no morning band in Norwegian Bokmål; bare, it is the day word."""
    s = span("morgen")
    assert (s.start, s.end) == (AstroDate(2017, 6, 28), AstroDate(2017, 6, 29))
