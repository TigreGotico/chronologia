"""Wave 1 -- Japanese regnal years (nengo) and the Roman calendar.

Regnal years resolve to the Gregorian year the nengo year occupies inside
its reign segment (Reiwa 1 opens at the 2019-05-01 accession; a closed
era's final year ends at the successor's accession).  Roman dates count
inclusively back from the monthly Kalends/Nones/Ides anchor over the
Julian calendar (Ides of March == the 15th; Nones of March == the 7th).
"""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, start, start_end, span


def _d(s):
    y, m, dd = (int(x) for x in s.split("-"))
    return AstroDate(y, m, dd)


# -- regnal: "<nengo> N" -> the Gregorian year of that regnal year --------

@pytest.mark.parametrize("text,y", [
    ("reiwa 7", 2025), ("reiwa 3", 2021), ("meiji 6", 1873),
    ("meiji 45", 1912), ("showa 20", 1945), ("showa 64", 1989),
    ("taisho 5", 1916), ("heisei 31", 2019),
])
def test_regnal_bare(text, y):
    assert start(text).year == y


# -- regnal: "the Nth year of <nengo>" ------------------------------------

@pytest.mark.parametrize("text,y", [
    ("the third year of reiwa", 2021),
    ("the fifth year of heisei", 1993),
    ("the tenth year of meiji", 1877),
    ("the first year of showa", 1926),
])
def test_regnal_ordinal(text, y):
    assert start(text).year == y


# -- regnal accession-year edges (segment clamping) -----------------------

def test_reiwa_1_starts_at_accession():
    assert start("reiwa 1") == AstroDate(2019, 5, 1)


def test_heisei_1_starts_at_accession():
    assert start("heisei 1") == AstroDate(1989, 1, 8)


# -- Roman calendar: Kalends / Nones / Ides -------------------------------

@pytest.mark.parametrize("text,iso", [
    ("the ides of march", "2017-3-15"), ("ides of march", "2017-3-15"),
    ("the ides of october", "2017-10-15"), ("the ides of may", "2017-5-15"),
    ("the ides of january", "2017-1-13"), ("the ides of july", "2017-7-15"),
    ("the kalends of april", "2017-4-1"), ("kalends of may", "2017-5-1"),
    ("the kalends of january", "2017-1-1"),
    ("the kalends of december", "2017-12-1"),
    ("the nones of march", "2017-3-7"), ("the nones of january", "2017-1-5"),
    ("the nones of april", "2017-4-5"), ("the nones of july", "2017-7-7"),
])
def test_roman_anchor(text, iso):
    assert start(text) == _d(iso)
    assert span(text).width == timedelta(days=1)


# -- Roman: pridie (the day before) and a.d. counted days -----------------

@pytest.mark.parametrize("text,iso", [
    ("pridie ides of march", "2017-3-14"),
    ("pridie kalends of april", "2017-3-31"),
    ("pridie nones of march", "2017-3-6"),
    ("ad 3 kalends of april", "2017-3-30"),
    ("ad 4 ides of march", "2017-3-12"),
    ("ad 6 ides of march", "2017-3-10"),
])
def test_roman_counted(text, iso):
    assert start(text) == _d(iso)


# -- Latin ablative "on the Ides/Kalends/Nones of <month>" ----------------

@pytest.mark.parametrize("text,iso", [
    ("idibus martiis", "2017-3-15"),      # the Ides of March
    ("kalendis ianuariis", "2017-1-1"),   # the Kalends of January
    ("nonis martiis", "2017-3-7"),        # the Nones of March
])
def test_latin_ablative(text, iso):
    assert start(text) == _d(iso)
