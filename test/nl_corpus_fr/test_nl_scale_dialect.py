# -*- coding: utf-8 -*-
"""Per-dialect short/long scale in French deep time.

France uses the LONG scale: "milliard" = 10^9, "billion" = 10^12.  Under the
short scale "billion" would be 10^9.  The bare code "fr" and the region code
"fr-FR" both default to long; an explicit ``scale=`` kwarg hard-overrides.

Sources: Wikipedia, "Long and short scales" (French section); the ovos-number-
parser French vocabulary (milliard = 10^9, billion = 10^12).
"""
from datetime import datetime

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)


def _year(text, lang="fr", scale=None):
    r = extract_timespan(text, lang, ANCHOR, scale=scale)
    assert r is not None, f"{text!r} ({lang}, scale={scale}) did not parse"
    return r[0].start.year


def _about(year, magnitude):
    # a deep-time offset is ~ (1950 - magnitude); allow a wide slop for the
    # radiocarbon-present epoch and month rounding.
    assert abs(year - (-magnitude)) < magnitude * 0.001 + 10_000, \
        f"{year} is not ~ -{magnitude}"


# -- milliard is 10^9 under every scale (unambiguous) ---------------------

def test_milliard_is_1e9():
    _about(_year("il y a un milliard d'années"), 1_000_000_000)


# -- billion is 10^12 under the long-scale default ------------------------

def test_billion_is_1e12_long_default():
    _about(_year("il y a un billion d'années"), 1_000_000_000_000)


def test_billion_1e12_under_region_code_fr_FR():
    _about(_year("il y a un billion d'années", lang="fr-FR"),
           1_000_000_000_000)


# -- explicit scale kwarg hard-overrides ----------------------------------

def test_billion_is_1e9_under_explicit_short():
    _about(_year("il y a un billion d'années", scale="short"), 1_000_000_000)


def test_billion_is_1e12_under_explicit_long():
    _about(_year("il y a un billion d'années", scale="long"),
           1_000_000_000_000)
