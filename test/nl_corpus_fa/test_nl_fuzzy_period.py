# -*- coding: utf-8 -*-
"""Fuzzy sub-spans (fa): early/mid/late = first/middle/last arithmetic third
of the parent calendar period.  Persian period parts: اوایل / ابتدای (early),
اواسط / وسط (mid), اواخر / آخر / پایان (late).  Parent units: ماه (month),
سال (year), and a relative-marker week (هفته آینده -> next week, Sat-based)."""
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


M = (AstroDate(2017, 6, 1), AstroDate(2017, 7, 1))
Y = (AstroDate(2017, 1, 1), AstroDate(2018, 1, 1))
NW = (AstroDate(2017, 7, 1), AstroDate(2017, 7, 8))    # next week (Sat-based, fa)
_P = {"M": M, "Y": Y, "NW": NW}

_CASES = [
    ('اوایل ماه', 'M', 'early'),
    ('اواسط ماه', 'M', 'mid'),
    ('اواخر ماه', 'M', 'late'),
    ('ابتدای سال', 'Y', 'early'),
    ('اواسط سال', 'Y', 'mid'),
    ('اواخر سال', 'Y', 'late'),
    ('اوایل هفته آینده', 'NW', 'early'),
    ('اواسط هفته آینده', 'NW', 'mid'),
    ('پایان ماه', 'M', 'late'),
    ('وسط سال', 'Y', 'mid'),
]


@pytest.mark.parametrize("text,parent,part", _CASES)
def test_fuzzy_period(text, parent, part):
    want_s, want_e = _third(*_P[parent], part)
    s, e = start_end(text)
    assert s == want_s
    assert e == want_e


@pytest.mark.parametrize("text", ['شروع', 'زود'])
def test_not_a_fuzzy_period(text):
    nomatch(text)
