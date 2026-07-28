# -*- coding: utf-8 -*-
"""Per-dialect short/long scale in English deep time.

English uses the SHORT scale everywhere today: "billion" = 10^9 (en-GB since
the 1974 UK Treasury switch, en-US always).  This pins the PR #312 behaviour --
"a billion years ago" stays 10^9 -- and checks the explicit long override.
"""
from datetime import datetime

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)


def _year(text, lang="en", scale=None):
    r = extract_timespan(text, lang, ANCHOR, scale=scale)
    assert r is not None, f"{text!r} ({lang}, scale={scale}) did not parse"
    return r[0].start.year


def test_a_billion_years_ago_is_1e9_unchanged():
    # the indefinite-article count-from-now form (PR #312): anchor.year - 1e9
    assert _year("a billion years ago") == -999_997_983


def test_billion_short_default_en_GB():
    assert _year("a billion years ago", lang="en-GB") == -999_997_983


def test_billion_short_default_en_US():
    assert _year("a billion years ago", lang="en-US") == -999_997_983


def test_66_million_years_ago_unchanged():
    assert _year("66 million years ago") == -65_998_050


def test_billion_becomes_1e12_under_explicit_long():
    y = _year("a billion years ago", scale="long")
    assert abs(y - (-1_000_000_000_000)) < 10_000
