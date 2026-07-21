"""Engine-level ``nongregorian_date`` resolution against the fixed anchor
datetime(2017, 6, 27, 13, 4).

Two surfaces are exercised: the synthetic ``zz`` locale (z-nonsense
Islamic-civil month surfaces, testing the construction in isolation) and
the real ``ar``/``he`` locales through the ``DateTimeEngine`` facade.
Every asserted Gregorian value is hand-checked against the downloaded
conversion tables cited in ``test/test_calendars.py`` (Dershowitz &
Reingold 1990 for the arithmetic; Hebrew/Hijri reference tables for the
gold dates).
"""
from datetime import datetime

import pytest
from engine_helpers import ANCHOR, zz_engine

from chronologia.astrodate import AstroDate
from chronologia.extract import DateTimeEngine, load_lang_spec
from chronologia.resolution import DateTimeResolution


def _one(engine, text):
    res = engine.resolve(text, ANCHOR)
    assert len(res) == 1, f"{text!r} -> {res}"
    return res[0]


# -- synthetic zz locale: the construction in isolation --------------------

def test_zz_cal_month_day_year():
    # 5 Ramadan (islamic_civil month 9) AH 1446 == 2025-03-05
    r = _one(zz_engine(), "zram 5 1446")
    assert r.value.start == AstroDate(2025, 3, 5)
    assert r.value.resolution == DateTimeResolution.DAY


def test_zz_day_of_cal_month_year():
    assert _one(zz_engine(), "5 zof zram 1446").value.start == AstroDate(2025, 3, 5)


def test_zz_cal_month_and_year_is_month_resolution():
    # 1 Ramadan AH 1446 == 2025-03-01; no day -> MONTH resolution
    r = _one(zz_engine(), "zram 1446")
    assert r.value.start == AstroDate(2025, 3, 1)
    assert r.value.resolution == DateTimeResolution.MONTH


def test_zz_muharram_epoch_year():
    # 1 Muharram AH 1446 == 2024-07-08
    assert _one(zz_engine(), "zmuh 1 1446").value.start == AstroDate(2024, 7, 8)


def test_zz_yearless_prefer_future_bumps_in_calendar_space():
    # anchor's Islamic year is 1438; 5 Ramadan 1438 == 2017-05-31, before
    # the anchor, so prefer_future bumps to AH 1439 == 2018-05-20 (a bump
    # of one *calendar* year, not one Gregorian year).
    assert _one(zz_engine(), "zram 5").value.start == AstroDate(2018, 5, 20)


def test_zz_yearless_month_only_no_bump():
    # month word alone -> day 1 of Ramadan in the anchor's Islamic year
    # (AH 1438); 1 Ramadan 1438 == 2017-05-27, MONTH resolution, no bump
    r = _one(zz_engine(), "zram")
    assert r.value.start == AstroDate(2017, 5, 27)
    assert r.value.resolution == DateTimeResolution.MONTH


def test_zz_explain_names_the_calendar():
    trace = zz_engine().explain("zram 5 1446", ANCHOR)
    (won,) = trace.winners
    assert won.match.calendar == "islamic_civil"
    assert "islamic_civil" in trace.report()


# -- adversarial: impossible days / garbage never raise --------------------

@pytest.mark.parametrize("text", [
    "zram 31 1446",     # Ramadan has 30 days
    "zdhu 31 1446",     # Dhu al-Hijjah has 29/30 days
    "zzz garbage 999",
    "",
    "31 zof zram",      # 31 Ramadan (no year) is impossible in any AH year
])
def test_zz_adversarial_never_raises(text):
    assert zz_engine().resolve(text, ANCHOR) == []


# -- real ar / he locales through the facade -------------------------------

@pytest.fixture(scope="module")
def ar():
    return DateTimeEngine(load_lang_spec("ar"))


@pytest.fixture(scope="module")
def he():
    return DateTimeEngine(load_lang_spec("he"))


def test_ar_ramadan(ar):
    # 15 Ramadan AH 1446 == 2025-03-15 (Hijri tabular reference table)
    assert _one(ar, "15 ramadan 1446").value.start == AstroDate(2025, 3, 15)


def test_ar_muharram_romanisation(ar):
    # 1 Muharram AH 1446 == 2024-07-08
    assert _one(ar, "1 muharram 1446").value.start == AstroDate(2024, 7, 8)


def test_ar_arabic_script(ar):
    # same as above via the Arabic-script surface رمضان
    assert _one(ar, "15 رمضان 1446").value.start == AstroDate(2025, 3, 15)


def test_he_tishrei(he):
    # 1 Tishrei (month 7, Rosh HaShanah) AM 5785 == 2024-10-03
    assert _one(he, "1 tishrei 5785").value.start == AstroDate(2024, 10, 3)


def test_he_nisan_is_month_one(he):
    # 15 Nisan (month 1) AM 5784 == 2024-04-23 (first day of Pesach)
    assert _one(he, "15 nisan 5784").value.start == AstroDate(2024, 4, 23)


def test_he_hebrew_script(he):
    # 1 Tishrei via the Hebrew-script surface תשרי
    assert _one(he, "1 תשרי 5785").value.start == AstroDate(2024, 10, 3)


@pytest.mark.parametrize("text", [
    "31 ramadan 1446", "31 tishrei 5785", "garbage", "ramadan tishrei"])
def test_facade_adversarial_never_raises(ar, text):
    # never raises; impossible days simply do not resolve
    ar.resolve(text, ANCHOR)


def test_he_impossible_day_does_not_resolve(he):
    # 31 Tishrei is impossible (Tishri has 30 days)
    assert all(r.value.start != AstroDate(2024, 10, 31)
               for r in he.resolve("31 tishrei 5785", ANCHOR))
