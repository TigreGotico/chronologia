"""Fuzzy sub-spans (ms): awal/pertengahan/akhir (early/mid/late) of a parent
calendar period. Parent edges hand-derived; the third is pure timedelta
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
NM = (AstroDate(2017, 7, 1), AstroDate(2017, 8, 1))
_P = {"M": M, "Y": Y, "NM": NM}

_CASES = [("awal bulan", "M", "early"), ("pertengahan bulan", "M", "mid"),
          ("akhir bulan", "M", "late"), ("awal tahun", "Y", "early"),
          ("pertengahan tahun", "Y", "mid"), ("akhir tahun", "Y", "late"),
          ("awal bulan depan", "NM", "early"), ("akhir bulan depan", "NM", "late")]

@pytest.mark.parametrize("text,parent,part", _CASES)
def test_fuzzy_period(text, parent, part):
    want_s, want_e = _third(*_P[parent], part)
    s, e = start_end(text, A)
    assert s == want_s
    assert e == want_e

@pytest.mark.parametrize("text", ["awal", "dini"])
def test_not_a_fuzzy_period(text):
    nomatch(text, A)
