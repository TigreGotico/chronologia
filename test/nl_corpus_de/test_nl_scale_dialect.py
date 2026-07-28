# -*- coding: utf-8 -*-
"""Per-dialect short/long scale in German deep time.

German uses the LONG scale: "Milliarde" = 10^9, "Billion" = 10^12.  Under the
short scale "Billion" would be 10^9.  Bare "de" / "de-DE" default to long; an
explicit ``scale=`` hard-overrides.

Source: Wikipedia, "Long and short scales" (German section).
"""
from datetime import datetime

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)


def _year(text, lang="de", scale=None):
    r = extract_timespan(text, lang, ANCHOR, scale=scale)
    assert r is not None, f"{text!r} ({lang}, scale={scale}) did not parse"
    return r[0].start.year


def _about(year, magnitude):
    assert abs(year - (-magnitude)) < magnitude * 0.001 + 10_000, \
        f"{year} is not ~ -{magnitude}"


def test_milliarde_is_1e9_unchanged():
    _about(_year("vor einer Milliarde Jahren"), 1_000_000_000)


def test_billion_is_1e12_long_default():
    _about(_year("vor einer Billion Jahren"), 1_000_000_000_000)


def test_billion_is_1e9_under_explicit_short():
    _about(_year("vor einer Billion Jahren", scale="short"), 1_000_000_000)
