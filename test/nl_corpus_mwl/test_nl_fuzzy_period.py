# -*- coding: utf-8 -*-
"""Fuzzy sub-spans (mwl): early/mid/late = first/middle/last arithmetic third
of the parent calendar period.  Mirandese period parts: ampeços / percípios
(early), meados / meio (mid), fin / final (late).  Parents: més (month),
anho (year), and the next week (la sumana que ben, Monday-based)."""
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
NW = (AstroDate(2017, 7, 3), AstroDate(2017, 7, 10))   # next week (Mon-based)
_P = {"M": M, "Y": Y, "NW": NW}

_CASES = [
    ('ampeços de més', 'M', 'early'),
    ('meados de més', 'M', 'mid'),
    ('fin de més', 'M', 'late'),
    ("ampeços de l anho", 'Y', 'early'),
    ("meados de l anho", 'Y', 'mid'),
    ("fin de l anho", 'Y', 'late'),
    ("ampeços de la sumana que ben", 'NW', 'early'),
    ("meados de la sumana que ben", 'NW', 'mid'),
    ('percípios de més', 'M', 'early'),
    ('final de més', 'M', 'late'),
]


@pytest.mark.parametrize("text,parent,part", _CASES)
def test_fuzzy_period(text, parent, part):
    want_s, want_e = _third(*_P[parent], part)
    s, e = start_end(text)
    assert s == want_s
    assert e == want_e


@pytest.mark.parametrize("text", ['l ampeço', 'lougo'])
def test_not_a_fuzzy_period(text):
    nomatch(text)
