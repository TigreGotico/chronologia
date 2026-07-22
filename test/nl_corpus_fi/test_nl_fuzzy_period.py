"""Fuzzy sub-spans (fi): early/mid/late = first/middle/last arithmetic third
of the parent calendar period. Finnish marks the part with a postposed locative
noun (kuukauden alussa/lopussa); parent edges hand-derived, the third is pure
timedelta arithmetic."""
from datetime import datetime
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end, nomatch

A = datetime(2017, 6, 27, 13, 4)

def _dt(a):
    return datetime(a.year, a.month, a.day, a.hour, a.minute, a.second, a.microsecond)

def _third(s, e, part):
    s, e = _dt(s), _dt(e)
    w = (e - s) / 3
    edges = {"early": (s, s + w), "mid": (s + w, s + 2 * w), "late": (s + 2 * w, e)}[part]
    return AstroDate.from_datetime(edges[0]), AstroDate.from_datetime(edges[1])

M = (AstroDate(2017, 6, 1), AstroDate(2017, 7, 1))
Y = (AstroDate(2017, 1, 1), AstroDate(2018, 1, 1))
NW = (AstroDate(2017, 7, 3), AstroDate(2017, 7, 10))
_P = {"M": M, "Y": Y, "NW": NW}

_CASES = [('kuukauden alussa', 'M', 'early'), ('kuukauden puolivälissä', 'M', 'mid'),
          ('kuukauden lopussa', 'M', 'late'), ('vuoden alussa', 'Y', 'early'),
          ('vuoden puolivälissä', 'Y', 'mid'), ('vuoden lopussa', 'Y', 'late'),
          ('ensi viikon alussa', 'NW', 'early'), ('ensi viikon lopussa', 'NW', 'late')]

@pytest.mark.parametrize("text,parent,part", _CASES)
def test_fuzzy_period(text, parent, part):
    want_s, want_e = _third(*_P[parent], part)
    s, e = start_end(text, A)
    assert s == want_s
    assert e == want_e

@pytest.mark.parametrize("text", ['alku', 'aikainen'])
def test_not_a_fuzzy_period(text):
    nomatch(text, A)
