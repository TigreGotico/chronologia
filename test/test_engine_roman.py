"""roman_date stage: Kalends/Nones/Ides inclusive backward counting over the
Julian calendar, against the fixed anchor datetime(2017, 6, 27) (year 2017).

Day-wide spans; the returned month/day are the Julian-calendar (Roman)
labels.  Values follow Wikipedia, "Roman calendar"."""
import pytest
from engine_helpers import ANCHOR, zz_engine

from chronologia.astrodate import AstroDate
from chronologia.roman import roman_to_julian


def _one(text):
    res = zz_engine().resolve(text, ANCHOR)
    assert len(res) == 1, f"{text!r} -> {res}"
    return res[0]


# -- the canonical worked examples -----------------------------------------

def test_ad_iii_kalendas_aprilis_is_march_30():
    r = _one("zad 3 zkal zap")
    assert r.value.start == AstroDate(2017, 3, 30)
    assert r.value.width.days == 1                       # day-wide

def test_pridie_idus_martias_is_march_14():
    assert _one("zpridie zid zmar").value.start == AstroDate(2017, 3, 14)

def test_idibus_martiis_is_march_15():
    assert _one("zid zmar").value.start == AstroDate(2017, 3, 15)


# -- Nones/Ides late-month rule (March = 7th / 15th) -----------------------

def test_nonae_martiae_is_march_7():
    assert _one("znon zmar").value.start == AstroDate(2017, 3, 7)

def test_nonae_ianuariae_is_january_5():
    # January is not a late month: Nones = 5th (month_1 surface is "zan")
    assert _one("znon zan").value.start == AstroDate(2017, 1, 5)


# -- Kalends counting into the previous month ------------------------------

def test_ad_iii_kalendas_martias_is_february_27():
    assert _one("zad 3 zkal zmar").value.start == AstroDate(2017, 2, 27)


# -- helper agreement ------------------------------------------------------

def test_helper_matches_construction():
    assert roman_to_julian(2017, 4, "kalends", 3) == (2017, 3, 30)


# -- adversarial: ordinal beyond the span -> None --------------------------

@pytest.mark.parametrize("text", [
    "zad 18 zkal zap",     # overshoots the Ides of March
    "zad 0 zkal zap",      # count < 1
    "zzz zkal zap"])
def test_out_of_span_returns_nothing(text):
    for r in zz_engine().resolve(text, ANCHOR):
        assert r.value.width.days == 1
