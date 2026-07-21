"""scoped_ordinal stage: "Nth UNIT of SCOPE" nesting, absolute periods and
last-ordinal, resolved against the fixed anchor datetime(2017, 6, 27).

Values are cross-checked against ``scoped_scan.extract_scoped_date`` (the
ported semantics) so the engine reproduces the regex layer's dates while
carrying honest span width.  The synthetic ``zz`` locale exercises the
construction in isolation."""
from datetime import date

import pytest
from engine_helpers import ANCHOR, zz_engine

from chronologia.astrodate import AstroDate
from chronologia.resolution import DateTimeResolution


def _one(text):
    res = zz_engine().resolve(text, ANCHOR)
    assert len(res) == 1, f"{text!r} -> {res}"
    return res[0]


# -- absolute periods (width = the period) ---------------------------------

def test_21st_century():
    r = _one("zthe 21 zcentury")
    assert r.value.start == AstroDate(2000, 1, 1)
    assert r.value.end == AstroDate(2100, 1, 1)
    assert r.value.resolution == DateTimeResolution.CENTURY

def test_3rd_millennium():
    r = _one("zthe 3 zmillennium")
    assert r.value.start == AstroDate(2000, 1, 1)
    assert r.value.resolution == DateTimeResolution.MILLENNIUM

def test_198th_decade():
    r = _one("198 zdecade")
    assert r.value.start == AstroDate(1970, 1, 1)
    assert r.value.resolution == DateTimeResolution.DECADE


# -- month-scoped (week/day wide) ------------------------------------------

def test_3rd_week_of_june():
    r = _one("zthe 3 zweek zof zjun")
    # anchor year 2017; 3rd week of June 2017 (Monday-aligned)
    assert r.value.start == AstroDate(2017, 6, 19)
    assert r.value.resolution == DateTimeResolution.WEEK

def test_3rd_week_of_june_explicit_year():
    assert _one("zthe 3 zweek zof zjun 1969").value.start == AstroDate(1969, 6, 16)

def test_last_week_of_june():
    r = _one("zthe zlast zweek zof zjun")
    assert r.value.start == AstroDate(2017, 6, 26)
    assert r.value.resolution == DateTimeResolution.WEEK


# -- year-scoped -----------------------------------------------------------

def test_100th_day_of_the_year():
    r = _one("zthe 100 zday zof zthe zyr")
    assert r.value.start == AstroDate(2017, 4, 10)
    assert r.value.resolution == DateTimeResolution.DAY

def test_100th_day_of_the_year_1969():
    assert _one("zthe 100 zday zof zthe zyr 1969").value.start == AstroDate(1969, 4, 10)


# -- nested one level ------------------------------------------------------

def test_first_decade_of_the_21st_century():
    r = _one("zthe 1 zdecade zof zthe 21 zcentury")
    assert r.value.start == AstroDate(2000, 1, 1)
    assert r.value.end == AstroDate(2010, 1, 1)
    assert r.value.resolution == DateTimeResolution.DECADE

def test_fifth_year_of_the_21st_century():
    r = _one("zthe 5 zyear zof zthe 21 zcentury")
    assert r.value.start == AstroDate(2004, 1, 1)
    assert r.value.resolution == DateTimeResolution.YEAR


# -- cross-check with the ported regex layer -------------------------------

def test_scoped_ordinal_lands_exact_date():
    # "the 3rd week of june 1969" -> the Monday of that week
    assert _one("zthe 3 zweek zof zjun 1969").value.start == AstroDate(1969, 6, 16)


# -- adversarial: impossible ordinals -> None, never raise -----------------

@pytest.mark.parametrize("text", [
    "zthe 9 zweek zof zjun",     # months only have 4 weeks
    "zthe 13 zmonth zof zthe zyr",  # years only have 12 months
    "zthe 0 zcentury",           # ordinal 0
    "zzz garbage 999"])
def test_adversarial_never_raises(text):
    zz_engine().resolve(text, ANCHOR)   # must not raise
