"""Fuzzy sub-spans (hu): early/mid/late = first/middle/last arithmetic third
of the parent calendar period, marked by a postposed possessive noun
(hónap végén). Parent edges hand-derived; the third is pure timedelta
arithmetic."""
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

_CASES = [("hónap elején", "M", "early"), ("hónap közepén", "M", "mid"),
          ("hónap végén", "M", "late"), ("év elején", "Y", "early"),
          ("év közepén", "Y", "mid"), ("év végén", "Y", "late"),
          ("jövő hét elején", "NW", "early"), ("jövő hét végén", "NW", "late")]

@pytest.mark.parametrize("text,parent,part", _CASES)
def test_fuzzy_period(text, parent, part):
    want_s, want_e = _third(*_P[parent], part)
    s, e = start_end(text, A)
    assert s == want_s
    assert e == want_e

@pytest.mark.parametrize("text", ["eleje", "korai"])
def test_not_a_fuzzy_period(text):
    nomatch(text, A)
