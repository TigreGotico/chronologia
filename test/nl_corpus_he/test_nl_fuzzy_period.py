# -*- coding: utf-8 -*-
"""Fuzzy sub-spans (he): early/mid/late = first/middle/last arithmetic third
of the parent calendar period.  Hebrew period parts: תחילת / ראשית (early),
אמצע (mid), סוף / שלהי (late).  Parent units: החודש (month), השנה (year),
and a relative-marker week (השבוע הבא -> next week, Sunday-based)."""
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
NW = (AstroDate(2017, 7, 2), AstroDate(2017, 7, 9))    # next week (Sun-based, he)
_P = {"M": M, "Y": Y, "NW": NW}

_CASES = [
    ('תחילת החודש', 'M', 'early'),
    ('אמצע החודש', 'M', 'mid'),
    ('סוף החודש', 'M', 'late'),
    ('ראשית השנה', 'Y', 'early'),
    ('אמצע השנה', 'Y', 'mid'),
    ('סוף השנה', 'Y', 'late'),
    ('תחילת השבוע הבא', 'NW', 'early'),
    ('אמצע השבוע הבא', 'NW', 'mid'),
    ('תחילת השנה', 'Y', 'early'),
    ('שלהי החודש', 'M', 'late'),
]


@pytest.mark.parametrize("text,parent,part", _CASES)
def test_fuzzy_period(text, parent, part):
    want_s, want_e = _third(*_P[parent], part)
    s, e = start_end(text)
    assert s == want_s
    assert e == want_e


@pytest.mark.parametrize("text", ['ההתחלה', 'מוקדם'])
def test_not_a_fuzzy_period(text):
    nomatch(text)
