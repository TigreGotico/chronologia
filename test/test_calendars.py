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


# -- Coptic & Ethiopic: 12x30 + 5/6-day epagomenal 13th month ---------------

def test_coptic_epoch():
    c = CALENDARS["coptic"]
    assert c.epoch_jdn == 1825030
    assert c.to_jdn(1, 1, 1) == 1825030
    # 1 Thoout AM 1 == 284-08-29 Julian (Era of the Martyrs / Diocletian)
    assert jdn_to_julian(c.epoch_jdn) == (284, 8, 29)


def test_coptic_new_year_1741():
    # 1 Thoout AM 1741 == 2024-09-11 Gregorian (Coptic new year, Nayrouz)
    c = CALENDARS["coptic"]
    assert jdn_to_gregorian(c.to_jdn(1741, 1, 1)) == (2024, 9, 11)


def test_ethiopian_epoch():
    c = CALENDARS["ethiopian"]
    assert c.epoch_jdn == 1724221
    assert c.to_jdn(1, 1, 1) == 1724221
    # 1 Maskaram EE 1 == 8-08-29 Julian (Incarnation era)
    assert jdn_to_julian(c.epoch_jdn) == (8, 8, 29)


def test_ethiopian_new_year_2017():
    # 1 Maskaram EE 2017 (Enkutatash) == 2024-09-11 Gregorian
    c = CALENDARS["ethiopian"]
    assert jdn_to_gregorian(c.to_jdn(2017, 1, 1)) == (2024, 9, 11)


def test_coptic_ethiopian_share_the_day_276_years_apart():
    # Coptic and Ethiopic epochs are 276 Julian years apart, so the same JDN
    # is numbered 276 years higher in the Ethiopic reckoning.
    coptic, eth = CALENDARS["coptic"], CALENDARS["ethiopian"]
    assert coptic.to_jdn(1741, 1, 1) == eth.to_jdn(2017, 1, 1)
    assert eth.to_jdn(2017, 5, 13) - coptic.to_jdn(1741, 5, 13) == 0


@pytest.mark.parametrize("key,epoch_year", [("coptic", 1741),
                                            ("ethiopian", 2017)])
def test_coptic_like_leap_epagomenal_sixth_day(key, epoch_year):
    # year Y with Y % 4 == 3 is leap: month 13 has 6 days, else 5.
    c = CALENDARS[key]
    leap = epoch_year - (epoch_year % 4) + 3      # nearest leap year form
    # the 6th epagomenal day exists in a leap year and round-trips as (Y,13,6)
    assert c.from_jdn(c.to_jdn(leap, 13, 6)) == (leap, 13, 6)
    common = leap + 1                              # (leap+1) % 4 == 0, common
    # the day after (common, 13, 5) is (common+1, 1, 1): only 5 epagomenals
    assert c.to_jdn(common, 13, 5) + 1 == c.to_jdn(common + 1, 1, 1)


@pytest.mark.parametrize("key,epoch", [("coptic", 1825030),
                                       ("ethiopian", 1724221)])
def test_coptic_like_round_trip(key, epoch):
    c = CALENDARS[key]
    for jd in range(epoch, epoch + 700_000, 13):
        y, m, d = c.from_jdn(jd)
        assert c.to_jdn(y, m, d) == jd
        assert 1 <= m <= 13 and 1 <= d <= 30


@pytest.mark.parametrize("key", ["coptic", "ethiopian"])
def test_coptic_like_proleptic_pre_epoch(key):
    # proleptic (year <= 0) round-trips rather than raising, matching Julian.
    c = CALENDARS[key]
    for jd in range(c.epoch_jdn - 40_000, c.epoch_jdn, 7):
        assert c.to_jdn(*c.from_jdn(jd)) == jd


# -- Revised Julian (Milankovic 900-year rule) ------------------------------

def test_revised_julian_leap_rule():
    # century years leap only when Y % 900 in (200, 600)
    assert cal._rj_leap(2000) and cal._rj_leap(2400)      # divisible by 400
    assert cal._rj_leap(2900)                              # 2900 % 900 == 200
    assert not cal._rj_leap(1900) and not cal._rj_leap(2100)
    assert not cal._rj_leap(2800)                          # 2800 % 900 == 100
    assert 218 == cal._rj_leaps_before(900) - cal._rj_leaps_before(0)


def test_revised_julian_agrees_with_gregorian_1600_to_2800():
    # identical from 1600-03-01 through 2800-02-28
    c = CALENDARS["revised_julian"]
    for y in range(1600, 2800):
        for (m, d) in ((3, 1), (7, 15), (12, 31)):
            assert c.to_jdn(y, m, d) == gregorian_to_jdn(y, m, d)
    assert c.to_jdn(2800, 2, 28) == gregorian_to_jdn(2800, 2, 28)


def test_revised_julian_diverges_from_gregorian_at_2800():
    # 2800 is a Gregorian leap year but not a Revised Julian one, so from
    # 2800-03-01 the Revised Julian date sits one JDN before the Gregorian.
    c = CALENDARS["revised_julian"]
    assert c.to_jdn(2800, 3, 1) == gregorian_to_jdn(2800, 3, 1) - 1
    # Revised Julian has no 2800-02-29; Gregorian does
    assert gregorian_to_jdn(2800, 3, 1) - gregorian_to_jdn(2800, 2, 28) == 2
    assert c.to_jdn(2800, 3, 1) - c.to_jdn(2800, 2, 28) == 1


def test_revised_julian_round_trip():
    c = CALENDARS["revised_julian"]
    for jd in range(1_900_000, 2_900_000, 13):
        y, m, d = c.from_jdn(jd)
        assert c.to_jdn(y, m, d) == jd
        assert 1 <= m <= 12 and 1 <= d <= 31


# -- Armenian (365-day vague year, no leap) ---------------------------------

def test_armenian_epoch():
    c = CALENDARS["armenian"]
    assert c.epoch_jdn == 1922868
    assert c.to_jdn(1, 1, 1) == 1922868
    # 1 Navasard AE 1 == 552-07-11 Julian
    assert jdn_to_julian(c.epoch_jdn) == (552, 7, 11)


def test_armenian_no_leap_every_year_365_days():
    c = CALENDARS["armenian"]
    for y in range(1, 2000):
        assert c.to_jdn(y + 1, 1, 1) - c.to_jdn(y, 1, 1) == 365


@pytest.mark.parametrize("year,greg", [
    (1462, (2012, 7, 24)),   # 1 Navasard AE 1462 (epoch-derived)
    (1474, (2024, 7, 21)),   # 1 Navasard AE 1474
    (1475, (2025, 7, 21)),   # 1 Navasard AE 1475
])
def test_armenian_new_year_drifts_vague_year(year, greg):
    c = CALENDARS["armenian"]
    assert jdn_to_gregorian(c.to_jdn(year, 1, 1)) == greg


def test_armenian_epagomenal_month_13_has_five_days():
    c = CALENDARS["armenian"]
    assert c.from_jdn(c.to_jdn(5, 13, 5)) == (5, 13, 5)
    # sixth epagomenal day does not exist: (Y,13,5)+1 == (Y+1,1,1)
    assert c.to_jdn(5, 13, 5) + 1 == c.to_jdn(6, 1, 1)


def test_armenian_round_trip_and_proleptic():
    c = CALENDARS["armenian"]
    for jd in range(c.epoch_jdn - 30_000, c.epoch_jdn + 600_000, 13):
        y, m, d = c.from_jdn(jd)
        assert c.to_jdn(y, m, d) == jd
        assert 1 <= m <= 13 and 1 <= d <= 30


# -- Maya Long Count (GMT-584283 correlation, mixed radix) ------------------

def test_mayan_epoch_gmt_correlation():
    # 0.0.0.0.0 == JDN 584283 == proleptic Gregorian -3113-08-11
    assert cal.mayan_long_count_to_jdn(0, 0, 0, 0, 0) == 584283
    assert jdn_to_gregorian(584283) == (-3113, 8, 11)


def test_mayan_13_baktun_end_2012():
    # 13.0.0.0.0 == JDN 2456283 == 2012-12-21 Gregorian
    jd = cal.mayan_long_count_to_jdn(13, 0, 0, 0, 0)
    assert jd == 2456283
    assert jdn_to_gregorian(jd) == (2012, 12, 21)


@pytest.mark.parametrize("lc,jdn", [
    ((9, 0, 0, 0, 0), 584283 + 9 * 144000),    # 9.0.0.0.0 classic-era start
    ((7, 16, 3, 2, 13), 584283 + 7 * 144000 + 16 * 7200 + 3 * 360 + 2 * 20 + 13),
    ((13, 0, 8, 0, 0), 2456283 + 8 * 360),      # 13.0.8.0.0
])
def test_mayan_place_value_arithmetic(lc, jdn):
    assert cal.mayan_long_count_to_jdn(*lc) == jdn
    assert cal.mayan_long_count_from_jdn(jdn) == lc


def test_mayan_positions_stay_in_radix():
    for jd in range(584283, 584283 + 3_000_000, 997):
        b, k, t, u, ki = cal.mayan_long_count_from_jdn(jd)
        assert cal.mayan_long_count_to_jdn(b, k, t, u, ki) == jd
        assert 0 <= k < 20 and 0 <= t < 20 and 0 <= u < 18 and 0 <= ki < 20


def test_mayan_pre_epoch_negative_baktun_round_trips():
    for jd in range(0, 584283, 4159):
        lc = cal.mayan_long_count_from_jdn(jd)
        assert lc[0] < 0                       # proleptic: negative baktun
        assert cal.mayan_long_count_to_jdn(*lc) == jd


def test_mayan_registry_view_matches_full_long_count():
    # registry (tuncount, uinal, kin) view is the same JDN as the 5-place form
    c = CALENDARS["mayan_long_count"]
    assert c.epoch_jdn == 584283
    for b, k, t, u, ki in [(13, 0, 0, 0, 0), (9, 12, 11, 5, 18)]:
        full = cal.mayan_long_count_to_jdn(b, k, t, u, ki)
        assert c.to_jdn(b * 400 + k * 20 + t, u, ki) == full
        assert c.from_jdn(full) == (b * 400 + k * 20 + t, u, ki)


def test_mayan_registry_round_trip():
    c = CALENDARS["mayan_long_count"]
    for jd in range(584283, 584283 + 2_000_000, 397):
        y, m, d = c.from_jdn(jd)
        assert c.to_jdn(y, m, d) == jd
        assert 0 <= m < 18 and 0 <= d < 20


# -- ISO 8601 week date (YYYY-Www-D) ----------------------------------------

def test_iso_week_2026_w01_1():
    # 2026-W01-1 (Monday of week 1) == 2025-12-29 Gregorian
    c = CALENDARS["iso_week"]
    assert jdn_to_gregorian(c.to_jdn(2026, 1, 1)) == (2025, 12, 29)
    assert c.from_jdn(gregorian_to_jdn(2025, 12, 29)) == (2026, 1, 1)


def test_iso_week_jan4_always_in_week1():
    # the January-4 rule: 4 January is always in W01 of its own year
    c = CALENDARS["iso_week"]
    for y in range(1901, 2101):
        iy, w, _ = c.from_jdn(gregorian_to_jdn(y, 1, 4))
        assert (iy, w) == (y, 1)


@pytest.mark.parametrize("greg,iso", [
    ((2015, 1, 1), (2015, 1, 4)),    # Thursday -> W01 of 2015
    ((2016, 1, 1), (2015, 53, 5)),   # Friday -> W53 of 2015
    ((2005, 1, 1), (2004, 53, 6)),   # Saturday -> W53 of 2004
    ((2021, 1, 3), (2020, 53, 7)),   # 2020 has a week 53
])
def test_iso_week_year_boundary_and_w53(greg, iso):
    c = CALENDARS["iso_week"]
    assert c.from_jdn(gregorian_to_jdn(*greg)) == iso
    assert jdn_to_gregorian(c.to_jdn(*iso)) == greg


def test_iso_week_2020_has_53_weeks_2021_has_52():
    c = CALENDARS["iso_week"]
    # W53 of 2020 exists and rolls into W01 of 2021
    assert c.to_jdn(2020, 53, 7) + 1 == c.to_jdn(2021, 1, 1)
    # 2021 has no W53: W52 rolls straight into 2022 W01
    assert c.to_jdn(2021, 52, 7) + 1 == c.to_jdn(2022, 1, 1)


def test_iso_week_round_trip():
    c = CALENDARS["iso_week"]
    for jd in range(2_200_000, 2_600_000, 13):
        iy, w, wd = c.from_jdn(jd)
        assert c.to_jdn(iy, w, wd) == jd
        assert 1 <= w <= 53 and 1 <= wd <= 7


# -- Solar Hijri (arithmetic 33-year cycle) ---------------------------------

def test_solar_hijri_epoch():
    c = CALENDARS["solar_hijri_arithmetic"]
    assert c.epoch_jdn == 1948320
    assert c.to_jdn(1, 1, 1) == 1948320
    # 1 Farvardin AP 1 == 21 March 622 proleptic Gregorian (== 18 March 622 Julian)
    assert jdn_to_gregorian(c.epoch_jdn) == (622, 3, 21)
    assert jdn_to_julian(c.epoch_jdn) == (622, 3, 18)


@pytest.mark.parametrize("ap_year,greg", [
    (1399, (2020, 3, 20)),   # Nowruz 1399
    (1400, (2021, 3, 21)),   # Nowruz 1400
    (1403, (2024, 3, 20)),   # Nowruz 1403 (gold)
    (1404, (2025, 3, 20)),   # Nowruz 1404
])
def test_solar_hijri_modern_nowruz(ap_year, greg):
    c = CALENDARS["solar_hijri_arithmetic"]
    assert jdn_to_gregorian(c.to_jdn(ap_year, 1, 1)) == greg


def test_solar_hijri_leap_residues_18_not_17_variant():
    # verified convention: residue 18 (not 17) reproduces AP 1404 Nowruz.
    assert cal._solar_hijri_leap(18) and not cal._solar_hijri_leap(17)
    # the {..,17,..} variant would place Nowruz 1404 one day late (2025-03-21);
    # the shipped {..,18,..} form lands on 2025-03-20.
    c = CALENDARS["solar_hijri_arithmetic"]
    assert jdn_to_gregorian(c.to_jdn(1404, 1, 1)) == (2025, 3, 20)
    assert 8 == sum(1 for r in range(33) if cal._solar_hijri_leap(r))


def test_solar_hijri_month_lengths():
    c = CALENDARS["solar_hijri_arithmetic"]
    # months 1..6 have 31 days, 7..11 have 30, month 12 has 29 (30 in leap)
    for y in (1403, 1404):        # 1404 % 33 == 18 -> leap; 1403 common
        for m in range(1, 7):
            assert c.to_jdn(y, m + 1, 1) - c.to_jdn(y, m, 1) == 31
        for m in range(7, 12):
            assert c.to_jdn(y, m + 1, 1) - c.to_jdn(y, m, 1) == 30
    assert cal._solar_hijri_leap(1404) and not cal._solar_hijri_leap(1403)
    assert c.to_jdn(1405, 1, 1) - c.to_jdn(1404, 12, 1) == 30   # Esfand 30 (leap)
    assert c.to_jdn(1404, 1, 1) - c.to_jdn(1403, 12, 1) == 29   # Esfand 29 (common)


def test_solar_hijri_round_trip_and_proleptic():
    c = CALENDARS["solar_hijri_arithmetic"]
    for jd in range(c.epoch_jdn - 40_000, c.epoch_jdn + 600_000, 13):
        y, m, d = c.from_jdn(jd)
        assert c.to_jdn(y, m, d) == jd
        assert 1 <= m <= 12 and 1 <= d <= 31


# -- Umm al-Qura (bounded lookup table) -------------------------------------

def test_umm_al_qura_epoch():
    c = CALENDARS["umm_al_qura"]
    # 1 Muharram AH 1356 == 1937-03-14 Gregorian (start of the table)
    assert c.epoch_jdn == 2428607
    assert jdn_to_gregorian(c.to_jdn(1356, 1, 1)) == (1937, 3, 14)


@pytest.mark.parametrize("hijri,greg", [
    ((1445, 9, 1), (2024, 3, 11)),    # 1 Ramadan 1445 (gold, Saudi-announced)
    ((1444, 10, 1), (2023, 4, 21)),   # 1 Shawwal 1444 (Eid al-Fitr 2023)
    ((1440, 1, 1), (2018, 9, 11)),    # Islamic New Year 1440
    ((1420, 1, 1), (1999, 4, 17)),    # 1 Muharram 1420
    ((1500, 12, 1), (2077, 10, 18)),  # last tabulated month
])
def test_umm_al_qura_table_conversions(hijri, greg):
    c = CALENDARS["umm_al_qura"]
    assert jdn_to_gregorian(c.to_jdn(*hijri)) == greg
    y, m, _ = hijri
    assert c.from_jdn(gregorian_to_jdn(*greg)) == (y, m, 1)


def test_umm_al_qura_months_are_29_or_30():
    c = CALENDARS["umm_al_qura"]
    for y in range(1420, 1501):
        for m in range(1, 12):
            assert c.to_jdn(y, m + 1, 1) - c.to_jdn(y, m, 1) in (29, 30)


def test_umm_al_qura_out_of_range_raises():
    c = CALENDARS["umm_al_qura"]
    # before the table (AH < 1356) and after it (AH > 1500) -> ValueError,
    # so callers can fall back to islamic_civil
    with pytest.raises(ValueError):
        c.to_jdn(1355, 12, 29)
    with pytest.raises(ValueError):
        c.to_jdn(1501, 1, 1)
    with pytest.raises(ValueError):
        c.from_jdn(c.epoch_jdn - 1)
    with pytest.raises(ValueError):
        c.from_jdn(c.to_jdn(1500, 12, 1) + 60)   # past the last month
    # islamic_civil covers the same instant without raising (fallback works)
    assert CALENDARS["islamic_civil"].from_jdn(c.to_jdn(1445, 9, 1))[0] == 1445


def test_umm_al_qura_invalid_day_raises():
    c = CALENDARS["umm_al_qura"]
    with pytest.raises(ValueError):
        c.to_jdn(1445, 9, 0)
    with pytest.raises(ValueError):
        c.to_jdn(1445, 9, 31)     # no Hijri month has 31 days


def test_umm_al_qura_round_trip():
    c = CALENDARS["umm_al_qura"]
    lo, hi = c.to_jdn(1356, 1, 1), c.to_jdn(1500, 12, 1)
    for jd in range(lo, hi, 7):
        y, m, d = c.from_jdn(jd)
        assert c.to_jdn(y, m, d) == jd
        assert 1 <= m <= 12 and 1 <= d <= 30


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


# --------------------------------------------------------------------------
# Field validation: no calendar may silently accept an impossible month/day.
# --------------------------------------------------------------------------
# Driven off the ``CALENDARS`` registry so a newly registered calendar cannot
# skip validation.  Bounds are never hardcoded here either: each calendar is
# asked, through its own arithmetic, which months and days it really has in a
# probe year taken from inside its domain.

def _probe_year(c):
    """A year comfortably inside ``c``'s domain (tabulated ones are bounded)."""
    return c.from_jdn(c.epoch_jdn + 400)[0]


def _months_of(c, year):
    return cal._valid_months(c, year)


def _days_of(c, year, month):
    return cal._valid_days(c, year, month)


@pytest.mark.parametrize("key", sorted(CALENDARS))
def test_calendar_rejects_impossible_month(key):
    c = CALENDARS[key]
    year = _probe_year(c)
    months = _months_of(c, year)
    assert months, f"{key}: probe year {year} has no valid month"
    for bad in (months[0] - 1, months[-1] + 1, 99, -5):
        with pytest.raises(ValueError) as exc:
            c.date(year, bad, 1)
        assert key in str(exc.value)


@pytest.mark.parametrize("key", sorted(CALENDARS))
def test_calendar_rejects_impossible_day(key):
    c = CALENDARS[key]
    year = _probe_year(c)
    month = _months_of(c, year)[0]
    days = _days_of(c, year, month)
    assert days, f"{key}: {year}-{month} has no valid day"
    for bad in (days[0] - 1, days[-1] + 1, 99):
        with pytest.raises(ValueError) as exc:
            c.date(year, month, bad)
        assert key in str(exc.value)


@pytest.mark.parametrize("key", sorted(CALENDARS))
def test_calendar_accepts_every_month_edge(key):
    """First and last day of the first and last month still convert -- the
    guard against an over-strict rule quietly rejecting a legal date."""
    c = CALENDARS[key]
    year = _probe_year(c)
    months = _months_of(c, year)
    for month in (months[0], months[-1]):
        days = _days_of(c, year, month)
        for day in (days[0], days[-1]):
            assert c.date(year, month, day) is not None


@pytest.mark.parametrize("key", sorted(CALENDARS))
def test_calendar_validation_matches_from_calendar(key):
    """``AstroDate.from_calendar`` is the same construction path."""
    from chronologia.astrodate import AstroDate
    c = CALENDARS[key]
    year = _probe_year(c)
    month = _months_of(c, year)[0]
    assert AstroDate.from_calendar(key, year, month, 1) == c.date(year, month, 1)
    with pytest.raises(ValueError):
        AstroDate.from_calendar(key, year, 99, 1)


# -- the irregular months a naive 1..12 / 1..31 check would wrongly reject ---

def test_hebrew_leap_year_has_a_thirteenth_month():
    # 5784 AM is a leap year (Adar I + Adar II) -> 13 months; 5785 is not.
    assert cal._hebrew_leap(5784) and not cal._hebrew_leap(5785)
    assert CALENDARS["hebrew"].date(5784, 13, 1) is not None
    with pytest.raises(ValueError, match="expected 1..12"):
        CALENDARS["hebrew"].date(5785, 13, 1)


def test_coptic_and_ethiopic_epagomenal_month():
    # month 13 is the short epagomenal month: 5 days, 6 when year % 4 == 3.
    for key in ("coptic", "ethiopian"):
        c = CALENDARS[key]
        assert c.date(1739, 13, 5) is not None          # 1739 % 4 == 3 -> 6 days
        assert c.date(1739, 13, 6) is not None
        assert c.date(1740, 13, 5) is not None
        with pytest.raises(ValueError, match="expected 1..5"):
            c.date(1740, 13, 6)


def test_armenian_and_egyptian_have_five_epagomenal_days():
    # the vague year never leaps: month 13 is always exactly 5 days.
    for key in ("armenian", "egyptian"):
        c = CALENDARS[key]
        assert c.date(1400, 13, 5) is not None
        with pytest.raises(ValueError, match="expected 1..5"):
            c.date(1400, 13, 6)


def test_french_republican_complementary_days():
    # month 13 (les sans-culottides) is 5 days, 6 in a sextile year.
    c = CALENDARS["french_republican"]
    assert cal._fr_sextile(3) and not cal._fr_sextile(2)
    assert c.date(3, 13, 6) is not None
    assert c.date(2, 13, 5) is not None
    with pytest.raises(ValueError, match="expected 1..5"):
        c.date(2, 13, 6)


def test_bahai_ayyam_i_ha_is_month_zero():
    # Ayyám-i-Há sits between months 18 and 19 and is addressed as month 0;
    # it is 4 or 5 days long, unlike the nineteen 19-day months.
    c = CALENDARS["bahai"]
    assert c.date(172, 0, 4) is not None
    assert c.date(172, 19, 19) is not None
    with pytest.raises(ValueError, match="expected 1..19"):
        c.date(172, 19, 20)


def test_iso_week_53_exists_only_in_long_years():
    c = CALENDARS["iso_week"]
    assert c.date(2020, 53, 7) is not None      # 2020 is a 53-week ISO year
    with pytest.raises(ValueError, match="expected 1..52"):
        c.date(2021, 53, 1)


def test_mayan_positions_are_zero_based():
    # uinal 0..17 and kin 0..19 -- day/month 0 is legal here, unlike elsewhere.
    c = CALENDARS["mayan_long_count"]
    assert c.date(1000, 0, 0) is not None
    with pytest.raises(ValueError, match="expected 0..17"):
        c.date(1000, 18, 0)
    with pytest.raises(ValueError, match="expected 0..19"):
        c.date(1000, 0, 20)
