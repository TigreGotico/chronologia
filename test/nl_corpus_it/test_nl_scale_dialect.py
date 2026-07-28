# -*- coding: utf-8 -*-
"""Per-dialect short/long scale in Italian deep time.

Italy uses the LONG scale: "miliardo" = 10^9, "bilione" = 10^12.  Under the
short scale "bilione" would be 10^9.  Bare "it" / "it-IT" default to long; an
explicit ``scale=`` hard-overrides.

Sources: Wikipedia, "Long and short scales" (Italian section); ovos-number-
parser it vocabulary (miliardo 10^9, bilione 10^12).
"""
from datetime import datetime

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)


def _year(text, lang="it", scale=None):
    r = extract_timespan(text, lang, ANCHOR, scale=scale)
    assert r is not None, f"{text!r} ({lang}, scale={scale}) did not parse"
    return r[0].start.year


def _about(year, magnitude):
    assert abs(year - (-magnitude)) < magnitude * 0.001 + 10_000, \
        f"{year} is not ~ -{magnitude}"


def test_miliardo_is_1e9():
    _about(_year("un miliardo di anni fa"), 1_000_000_000)


def test_bilione_is_1e12_long_default():
    _about(_year("un bilione di anni fa"), 1_000_000_000_000)


def test_bilione_is_1e9_under_explicit_short():
    _about(_year("un bilione di anni fa", scale="short"), 1_000_000_000)
