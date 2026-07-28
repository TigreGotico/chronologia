# -*- coding: utf-8 -*-
"""Per-dialect short/long scale in Spanish deep time.

Spain (RAE) uses the LONG scale: 10^9 is "mil millones" (or "millardo"),
"billón" = 10^12.  Under the short scale "billón" would be 10^9.  Bare "es"
and "es-ES" default to long; an explicit ``scale=`` hard-overrides.

Sources: Real Academia Española, "billón"; Wikipedia, "Long and short scales"
(Spanish section).
"""
from datetime import datetime

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)


def _year(text, lang="es", scale=None):
    r = extract_timespan(text, lang, ANCHOR, scale=scale)
    assert r is not None, f"{text!r} ({lang}, scale={scale}) did not parse"
    return r[0].start.year


def _about(year, magnitude):
    assert abs(year - (-magnitude)) < magnitude * 0.001 + 10_000, \
        f"{year} is not ~ -{magnitude}"


def test_mil_millones_is_1e9():
    _about(_year("hace mil millones de años"), 1_000_000_000)


def test_billon_is_1e12_long_default():
    _about(_year("hace un billón de años"), 1_000_000_000_000)


def test_billon_1e12_under_region_code_es_ES():
    _about(_year("hace un billón de años", lang="es-ES"), 1_000_000_000_000)


def test_billon_is_1e9_under_explicit_short():
    _about(_year("hace un billón de años", scale="short"), 1_000_000_000)
