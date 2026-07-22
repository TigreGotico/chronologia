# -*- coding: utf-8 -*-
"""Fuzzy sub-spans (an): early/mid/late = first/middle/last arithmetic third
of the parent calendar period.  Aragonese period parts: primerías / prencipios
(early), meyanías / meitat (mid), zaguerías / zagueras (late).  Parents: mes
(month), anyo (year), and the next week (a semana que viene, Monday-based)."""
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


M = (AstroDate(2018, 6, 1), AstroDate(2018, 7, 1))
Y = (AstroDate(2018, 1, 1), AstroDate(2019, 1, 1))
NW = (AstroDate(2018, 6, 11), AstroDate(2018, 6, 18))  # next week (Mon-based)
_P = {"M": M, "Y": Y, "NW": NW}

_CASES = [
    ('primerías de mes', 'M', 'early'),
    ('meyanías de mes', 'M', 'mid'),
    ('zaguerías de mes', 'M', 'late'),
    ("primerías d'anyo", 'Y', 'early'),
    ("meyanías d'anyo", 'Y', 'mid'),
    ("zaguerías d'anyo", 'Y', 'late'),
    ("primerías d'a semana que viene", 'NW', 'early'),
    ("meyanías d'a semana que viene", 'NW', 'mid'),
    ('prencipios de mes', 'M', 'early'),
    ('zagueras de mes', 'M', 'late'),
]


@pytest.mark.parametrize("text,parent,part", _CASES)
def test_fuzzy_period(text, parent, part):
    want_s, want_e = _third(*_P[parent], part)
    s, e = start_end(text)
    assert s == want_s
    assert e == want_e


@pytest.mark.parametrize("text", ['o prencipio', 'luego'])
def test_not_a_fuzzy_period(text):
    nomatch(text)
