"""Fuzzy sub-spans (et): early/mid/late = first/middle/last arithmetic third
of the parent calendar period, marked by a postposed locative noun
(kuu lõpus). Parent edges hand-derived; the third is pure timedelta arithmetic.
The Estonian next-week genitive ("järgmise nädala") is not a REL_MARKER surface,
so only bare (this-period) forms are asserted here."""
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
W = (AstroDate(2017, 6, 26), AstroDate(2017, 7, 3))
_P = {"M": M, "Y": Y, "W": W}

_CASES = [("kuu alguses", "M", "early"), ("kuu keskel", "M", "mid"),
          ("kuu lõpus", "M", "late"), ("aasta alguses", "Y", "early"),
          ("aasta keskel", "Y", "mid"), ("aasta lõpus", "Y", "late"),
          ("nädala alguses", "W", "early"), ("nädala lõpus", "W", "late")]

@pytest.mark.parametrize("text,parent,part", _CASES)
def test_fuzzy_period(text, parent, part):
    want_s, want_e = _third(*_P[parent], part)
    s, e = start_end(text, A)
    assert s == want_s
    assert e == want_e

@pytest.mark.parametrize("text", ["algus", "varajane"])
def test_not_a_fuzzy_period(text):
    nomatch(text, A)
