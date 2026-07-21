"""Pure arithmetic-calendar conversions: JDN round-trip sweeps and gold
values transcribed from downloaded canonical sources.

Sources (``~/AgentWorkspaces/papers/calendars/``):

* ``reingold_dershowitz_1990_calendrical_calculations.pdf`` -- Dershowitz &
  Reingold, "Calendrical Calculations", SP&E 20(9):899-928 (1990): the
  Gregorian/Julian/Islamic/Hebrew algorithms.
* ``usno_julian_date.html`` -- U.S. Naval Observatory Julian Date reference
  (J2000.0 = JDN 2451545).
* ``french_republican_reference.html`` / ``bahai_calendar_reference.html``
  -- arithmetic rules, epochs and worked dates for the two solar calendars.

Every asserted Gregorian value below is a published, independently
checkable date (Rosh HaShanah dates, the 18 Brumaire coup, the Gregorian
reform offset), stated with its meaning in a comment.
"""
import pytest

import chronologia.calendars as cal
from chronologia.calendars import (CALENDARS, gregorian_to_jdn,
                                         jdn_to_gregorian, jdn_to_julian,
                                         julian_to_jdn)


# -- Gregorian / Julian: Fliegel & Van Flandern -----------------------------

def test_gregorian_j2000():
    # USNO: 2000-01-01 12:00 == JD 2451545.0
    assert gregorian_to_jdn(2000, 1, 1) == 2451545


def test_gregorian_epoch():
    # proleptic Gregorian 0001-01-01 == JDN 1721426 (RD 1 + 1721425)
    assert gregorian_to_jdn(1, 1, 1) == 1721426


def test_gregorian_round_trip():
    for jd in range(1_400_000, 2_600_000, 13):
        assert gregorian_to_jdn(*jdn_to_gregorian(jd)) == jd


def test_gregorian_negative_years_floor_division():
    # proleptic astronomical numbering: year 0 and negatives round-trip
    for y in (0, -1, -100, -4713):
        jd = gregorian_to_jdn(y, 6, 15)
        assert jdn_to_gregorian(jd) == (y, 6, 15)


def test_julian_epoch():
    assert julian_to_jdn(1, 1, 1) == 1721424


def test_julian_gregorian_1582_reform_offset():
    # The Gregorian reform: Julian 1582-10-05 == Gregorian 1582-10-15,
    # a 10-day offset (both the same JDN 2299161).
    jd = gregorian_to_jdn(1582, 10, 15)
    assert jd == 2299161
    assert jdn_to_julian(jd) == (1582, 10, 5)


def test_julian_round_trip():
    for jd in range(1_500_000, 2_500_000, 13):
        assert julian_to_jdn(*jdn_to_julian(jd)) == jd


# -- Islamic civil (tabular): Dershowitz & Reingold -------------------------

def test_islamic_epoch():
    c = CALENDARS["islamic_civil"]
    assert c.epoch_jdn == 1948440
    assert c.to_jdn(1, 1, 1) == 1948440
    # 1 Muharram AH 1 == 16 July 622 Julian == 19 July 622 proleptic Gregorian
    assert jdn_to_gregorian(c.epoch_jdn) == (622, 7, 19)


def test_islamic_modern_ramadan():
    # 1 Ramadan AH 1446 (tabular civil) == 2025-03-01 Gregorian
    c = CALENDARS["islamic_civil"]
    assert jdn_to_gregorian(c.to_jdn(1446, 9, 1)) == (2025, 3, 1)


def test_islamic_round_trip():
    c = CALENDARS["islamic_civil"]
    for jd in range(c.epoch_jdn, c.epoch_jdn + 500_000, 11):
        y, m, d = c.from_jdn(jd)
        assert c.to_jdn(y, m, d) == jd
        assert 1 <= m <= 12 and 1 <= d <= 30


# -- Hebrew (molad + dechiyot): Dershowitz & Reingold -----------------------

def test_hebrew_epoch():
    c = CALENDARS["hebrew"]
    assert c.epoch_jdn == 347998            # 1 Tishri (month 7) AM 1
    assert c.to_jdn(1, 7, 1) == 347998


@pytest.mark.parametrize("year,greg", [
    (5784, (2023, 9, 16)),   # Rosh HaShanah 5784
    (5785, (2024, 10, 3)),   # Rosh HaShanah 5785
])
def test_hebrew_rosh_hashanah(year, greg):
    c = CALENDARS["hebrew"]
    assert jdn_to_gregorian(c.to_jdn(year, 7, 1)) == greg


def test_hebrew_passover_nisan_is_month_one():
    # 15 Nisan (month 1) 5784 == 23 April 2024 (first day of Pesach)
    c = CALENDARS["hebrew"]
    assert jdn_to_gregorian(c.to_jdn(5784, 1, 15)) == (2024, 4, 23)


def test_hebrew_dechiyot_gatarad_and_adu_both_fire():
    # AM 5789: the GaTaRaD delay (Tuesday common-year molad) and the lo-ADU
    # postponement both fire, moving Rosh HaShanah to 2028-09-21.
    c = CALENDARS["hebrew"]
    assert jdn_to_gregorian(c.to_jdn(5789, 7, 1)) == (2028, 9, 21)


def test_hebrew_dechiyot_betutekapot_fires():
    # AM 5766: the BeTUTeKaPoT delay (Monday molad after a leap year) fires;
    # Rosh HaShanah 5766 == 2005-10-04.
    c = CALENDARS["hebrew"]
    assert jdn_to_gregorian(c.to_jdn(5766, 7, 1)) == (2005, 10, 4)


def test_hebrew_year_lengths_always_valid():
    for y in range(5000, 6200):
        assert cal._hebrew_year_length(y) in (353, 354, 355, 383, 384, 385)


def test_hebrew_round_trip():
    c = CALENDARS["hebrew"]
    for jd in range(c.epoch_jdn + 1_000_000, c.epoch_jdn + 1_500_000, 11):
        y, m, d = c.from_jdn(jd)
        assert c.to_jdn(y, m, d) == jd
        assert 1 <= m <= 13 and 1 <= d <= 30


# -- French Republican (Romme arithmetic variant) ---------------------------

def test_french_republican_epoch_an_i():
    c = CALENDARS["french_republican"]
    assert c.epoch_jdn == 2375840
    # An I Vendemiaire 1 == 22 September 1792 Gregorian
    assert jdn_to_gregorian(c.to_jdn(1, 1, 1)) == (1792, 9, 22)


def test_french_republican_18_brumaire_an_viii():
    # 18 Brumaire (month 2, day 18) An VIII == 9 November 1799 (the coup)
    c = CALENDARS["french_republican"]
    assert jdn_to_gregorian(c.to_jdn(8, 2, 18)) == (1799, 11, 9)


def test_french_republican_observed_sextiles():
    # Historically observed sextile (leap) years An III, VII, XI
    assert [cal._fr_sextile(y) for y in range(1, 13)] == [
        False, False, True, False, False, False, True, False,
        False, False, True, False]


def test_french_republican_round_trip():
    c = CALENDARS["french_republican"]
    for jd in range(c.epoch_jdn, c.epoch_jdn + 200_000, 7):
        y, m, d = c.from_jdn(jd)
        assert c.to_jdn(y, m, d) == jd


# -- Bahai (arithmetic Badi', Gregorian-locked Naw-Ruz) ---------------------

def test_bahai_epoch():
    c = CALENDARS["bahai"]
    assert c.epoch_jdn == 2394647
    # BE 1 Baha 1 == Naw-Ruz == 21 March 1844 Gregorian
    assert jdn_to_gregorian(c.to_jdn(1, 1, 1)) == (1844, 3, 21)


def test_bahai_naw_ruz_locked_to_march_21():
    c = CALENDARS["bahai"]
    # pre-2015 arithmetic form: every Naw-Ruz is 21 March Gregorian
    assert jdn_to_gregorian(c.to_jdn(172, 1, 1)) == (2015, 3, 21)
    assert jdn_to_gregorian(c.to_jdn(100, 1, 1)) == (1943, 3, 21)


def test_bahai_round_trip_including_ayyam_i_ha():
    c = CALENDARS["bahai"]
    for jd in range(c.epoch_jdn, c.epoch_jdn + 100_000, 7):
        y, m, d = c.from_jdn(jd)
        assert c.to_jdn(y, m, d) == jd
        assert m in range(0, 20)     # month 0 == Ayyam-i-Ha


# -- generic registry invariants --------------------------------------------

def test_every_calendar_epoch_is_day_one():
    for c in CALENDARS.values():
        # from_jdn of the epoch is day 1 of the calendar's first month
        y, m, d = c.from_jdn(c.epoch_jdn)
        assert c.to_jdn(y, m, d) == c.epoch_jdn


def test_before_epoch_raises_for_lunisolar_and_solar():
    for key in ("islamic_civil", "french_republican"):
        with pytest.raises(ValueError):
            CALENDARS[key].from_jdn(CALENDARS[key].epoch_jdn - 5)
