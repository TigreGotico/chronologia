# -*- coding: utf-8 -*-
"""Fuzzy sub-spans (sk): early/mid/late = first/middle/last arithmetic third of
the parent calendar period. Parent edges hand-derived (anchor 2017-06-27, a
Tuesday, week_start Monday); the expected third is pure timedelta arithmetic
that never touches the parser."""
from datetime import datetime
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end, nomatch


def _dt(a):
    return datetime(a.year, a.month, a.day, a.hour, a.minute, a.second, a.microsecond)


def _third(s, e, part):
    s, e = _dt(s), _dt(e)
    w = (e - s) / 3
    edges = {"early": (s, s + w), "mid": (s + w, s + 2 * w),
              "late": (s + 2 * w, e)}[part]
    return AstroDate.from_datetime(edges[0]), AstroDate.from_datetime(edges[1])


M = (AstroDate(2017, 6, 1), AstroDate(2017, 7, 1))
Y = (AstroDate(2017, 1, 1), AstroDate(2018, 1, 1))
W = (AstroDate(2017, 6, 26), AstroDate(2017, 7, 3))
_P = {"M": M, "Y": Y, "W": W}

_CASES = [
    ("začiatok mesiaca", "M", "early"),
    ("polovica mesiaca", "M", "mid"),
    ("koniec mesiaca", "M", "late"),
    ("začiatok roka", "Y", "early"),
    ("polovica roka", "Y", "mid"),
    ("koniec roka", "Y", "late"),
    ("začiatok týždňa", "W", "early"),
    ("koniec týždňa", "W", "late"),
]


@pytest.mark.parametrize("text,parent,part", _CASES)
def test_fuzzy_period(text, parent, part):
    want_s, want_e = _third(*_P[parent], part)
    s, e = start_end(text)
    assert s == want_s
    assert e == want_e


@pytest.mark.parametrize("text", ["začiatok", "stretnutie"])
def test_not_a_fuzzy_period(text):
    nomatch(text)
