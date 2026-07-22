# -*- coding: utf-8 -*-
"""Fuzzy sub-spans (ar): early/mid/late = first/middle/last arithmetic third
of the parent calendar period.  Parent edges hand-derived; the expected third
is the same timedelta arithmetic the engine's ``subdivide`` applies.

Arabic period parts: أوائل / مطلع / بداية (early), منتصف / أواسط / وسط (mid),
أواخر / نهاية (late).  Parent units: الشهر (month), العام / السنة (year), and
a relative-marker week (الأسبوع القادم -> next week)."""
from datetime import datetime
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end, nomatch


def _dt(a):
    return datetime(a.year, a.month, a.day, a.hour, a.minute, a.second,
                    a.microsecond)


def _third(s, e, part):
    s, e = _dt(s), _dt(e)
    w = (e - s) / 3
    edges = {"early": (s, s + w), "mid": (s + w, s + 2 * w),
             "late": (s + 2 * w, e)}[part]
    return AstroDate.from_datetime(edges[0]), AstroDate.from_datetime(edges[1])


M = (AstroDate(2017, 6, 1), AstroDate(2017, 7, 1))     # current month (June)
Y = (AstroDate(2017, 1, 1), AstroDate(2018, 1, 1))     # current year
NW = (AstroDate(2017, 7, 1), AstroDate(2017, 7, 8))    # next week (Sat-based, ar)
_P = {"M": M, "Y": Y, "NW": NW}

_CASES = [
    ('أوائل الشهر', 'M', 'early'),
    ('منتصف الشهر', 'M', 'mid'),
    ('أواخر الشهر', 'M', 'late'),
    ('مطلع العام', 'Y', 'early'),
    ('منتصف العام', 'Y', 'mid'),
    ('أواخر العام', 'Y', 'late'),
    ('أوائل الأسبوع القادم', 'NW', 'early'),
    ('أواخر الأسبوع القادم', 'NW', 'late'),
    ('نهاية الشهر', 'M', 'late'),
    ('بداية العام', 'Y', 'early'),
]


@pytest.mark.parametrize("text,parent,part", _CASES)
def test_fuzzy_period(text, parent, part):
    want_s, want_e = _third(*_P[parent], part)
    s, e = start_end(text)
    assert s == want_s
    assert e == want_e


@pytest.mark.parametrize("text", ['البداية', 'مبكرا'])
def test_not_a_fuzzy_period(text):
    nomatch(text)
