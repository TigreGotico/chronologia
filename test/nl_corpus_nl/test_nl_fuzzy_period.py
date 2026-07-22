"""Fuzzy sub-spans (nl): early/mid/late = first/middle/last arithmetic
third of the parent calendar period. Parent edges hand-derived; the expected
third is pure timedelta arithmetic."""
from datetime import datetime
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end, nomatch

def _dt(a):
    return datetime(a.year, a.month, a.day, a.hour, a.minute, a.second, a.microsecond)

def _third(s, e, part):
    s, e = _dt(s), _dt(e)
    wd = (e - s) / 3
    edges = {"early": (s, s + wd), "mid": (s + wd, s + 2 * wd), "late": (s + 2 * wd, e)}[part]
    return AstroDate.from_datetime(edges[0]), AstroDate.from_datetime(edges[1])

M = (AstroDate(2017, 6, 1), AstroDate(2017, 7, 1))
Y = (AstroDate(2017, 1, 1), AstroDate(2018, 1, 1))
_P = {"M": M, "Y": Y}

_CASES = [('begin van de maand', 'M', 'early'), ('midden van de maand', 'M', 'mid'), ('eind van de maand', 'M', 'late'), ('begin van het jaar', 'Y', 'early'), ('eind van het jaar', 'Y', 'late')]

@pytest.mark.parametrize("text,parent,part", _CASES)
def test_fuzzy_period(text, parent, part):
    want_s, want_e = _third(*_P[parent], part)
    s, e = start_end(text)
    assert s == want_s
    assert e == want_e

@pytest.mark.parametrize("text", ['begin', 'vroeg'])
def test_not_a_fuzzy_period(text):
    nomatch(text)
