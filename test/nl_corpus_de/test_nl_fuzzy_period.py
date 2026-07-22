"""Fuzzy sub-spans (de): early/mid/late = first/middle/last arithmetic
third of the parent calendar period (same rule as month_fuzzy / decade_ref).
Parent edges hand-derived; the expected third is pure timedelta arithmetic."""
from datetime import datetime
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end, nomatch

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
TW = (AstroDate(2017, 6, 26), AstroDate(2017, 7, 3))
_P = {"M": M, "Y": Y, "NW": NW, "TW": TW}

_CASES = [('anfang des monats', 'M', 'early'), ('mitte des monats', 'M', 'mid'), ('ende des monats', 'M', 'late'), ('anfang des jahres', 'Y', 'early'), ('mitte des jahres', 'Y', 'mid'), ('ende des jahres', 'Y', 'late'), ('anfang nächster woche', 'NW', 'early'), ('ende nächster woche', 'NW', 'late'), ('mitte nächster woche', 'NW', 'mid'), ('anfang dieses monats', 'M', 'early')]

@pytest.mark.parametrize("text,parent,part", _CASES)
def test_fuzzy_period(text, parent, part):
    want_s, want_e = _third(*_P[parent], part)
    s, e = start_end(text)
    assert s == want_s
    assert e == want_e

@pytest.mark.parametrize("text", ['der anfang', 'frühaufsteher'])
def test_not_a_fuzzy_period(text):
    nomatch(text)
