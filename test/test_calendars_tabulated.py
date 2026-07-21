"""Tabulated / reconstructed calendars: bounded event tables loaded from the
``chronologia/calendar_data/`` data files, the ``basis`` classification,
the out-of-range fallback contract, and the optional-ephemeris provider hook.

Each table carries its own provenance header (source URL, retrieval date,
coverage range) in its ``.tab`` file and an entry in
``~/AgentWorkspaces/papers/calendars/INDEX.md``; gold values below are
published, independently checkable dates stated with their meaning.
"""
import pytest

import chronologia.calendars as cal
from chronologia.calendars import (CALENDARS, CalendarRangeError,
                                        TabulatedCalendar, jdn_to_gregorian,
                                        gregorian_to_jdn,
                                        register_event_provider)


# -- mechanism: basis attribute across the registry -------------------------

def test_arithmetic_calendars_default_basis_exact():
    for key in ("islamic_civil", "hebrew", "julian", "bahai", "coptic"):
        assert CALENDARS[key].basis == "exact"


def test_umm_al_qura_is_a_tabulated_calendar():
    c = CALENDARS["umm_al_qura"]
    assert isinstance(c, TabulatedCalendar)
    assert c.basis == "tabulated"
    assert c.fallback == "islamic_civil"
    assert c.month_count == 12
    assert c.coverage                      # non-empty provenance range string


# -- Umm al-Qura: behaviour byte-identical to the pre-refactor embedded table.
# The unchanged assertions in test_calendars.py already prove full parity; these
# re-check the gold value and the fallback-carrying error through the new type.

def test_umm_al_qura_gold_ramadan_1445():
    c = CALENDARS["umm_al_qura"]
    # 1 Ramadan AH 1445 == 2024-03-11 Gregorian (Saudi-announced start)
    assert jdn_to_gregorian(c.to_jdn(1445, 9, 1)) == (2024, 3, 11)
    assert c.epoch_jdn == 2428607


def test_umm_al_qura_out_of_range_error_carries_fallback():
    c = CALENDARS["umm_al_qura"]
    with pytest.raises(CalendarRangeError) as ei:
        c.to_jdn(1501, 1, 1)               # terminal sentinel, not addressable
    assert ei.value.fallback == "islamic_civil"
    assert isinstance(ei.value, ValueError)
    with pytest.raises(CalendarRangeError) as ej:
        c.from_jdn(c.epoch_jdn - 1)
    assert ej.value.fallback == "islamic_civil"


def test_umm_al_qura_round_trip_through_tabulated_type():
    c = CALENDARS["umm_al_qura"]
    lo, hi = c.to_jdn(1356, 1, 1), c.to_jdn(1500, 12, 1)
    for jd in range(lo, hi, 13):
        y, m, d = c.from_jdn(jd)
        assert c.to_jdn(y, m, d) == jd


def test_umm_al_qura_invalid_day_raises_range_error():
    c = CALENDARS["umm_al_qura"]
    with pytest.raises(CalendarRangeError):
        c.to_jdn(1445, 9, 31)              # no Hijri month has 31 days


# -- generic tabulated invariants -------------------------------------------

def test_tabulated_epoch_is_day_one():
    for c in CALENDARS.values():
        if isinstance(c, TabulatedCalendar):
            y, m, d = c.from_jdn(c.epoch_jdn)
            assert c.to_jdn(y, m, d) == c.epoch_jdn


def test_tabulated_month_field_encoding_is_ordinary_for_umm_al_qura():
    # a 12-month lunar calendar never has a leap month, so no month-field > 100
    c = CALENDARS["umm_al_qura"]
    assert all(field <= 12 for _, field in c.labels)


# -- badi_2015: true-equinox Bahá'í (official Bahá'í World Centre table) -------
# Naw-Rúz = the Tehran day containing the vernal equinox; dates from the
# official "Badí' dates 172 to 221 BE" table
# (papers/calendars/bahai_dates_172-221_uhj.pdf).

def test_badi_2015_is_tabulated_with_bahai_fallback():
    c = CALENDARS["badi_2015"]
    assert isinstance(c, TabulatedCalendar)
    assert c.basis == "tabulated" and c.fallback == "bahai"
    assert c.month_count == 19


def test_badi_2015_gold_naw_ruz():
    c = CALENDARS["badi_2015"]
    assert jdn_to_gregorian(c.to_jdn(172, 1, 1)) == (2015, 3, 21)  # 1 Bahá 172
    assert jdn_to_gregorian(c.to_jdn(181, 1, 1)) == (2024, 3, 20)  # Naw-Rúz 181
    assert jdn_to_gregorian(c.to_jdn(183, 1, 1)) == (2026, 3, 21)


def test_badi_2015_differs_from_arithmetic_bahai():
    # the arithmetic bahai locks Naw-Rúz to 21 March; the true-equinox table
    # puts BE 181 (2024) on 20 March -- the two calendars genuinely diverge.
    tab = CALENDARS["badi_2015"]
    ari = CALENDARS["bahai"]
    assert jdn_to_gregorian(ari.to_jdn(181, 1, 1)) == (2024, 3, 21)
    assert jdn_to_gregorian(tab.to_jdn(181, 1, 1)) == (2024, 3, 20)


def test_badi_2015_ayyam_i_ha_is_month_zero_4_or_5_days():
    c = CALENDARS["badi_2015"]
    # BE 173 (2016->2017, 365 days) has a 4-day Ayyám-i-Há; BE 174 has 5.
    assert c.to_jdn(173, 19, 1) - c.to_jdn(173, 0, 1) == 4
    assert c.to_jdn(174, 19, 1) - c.to_jdn(174, 0, 1) == 5
    # month 0 round-trips as month 0
    assert c.from_jdn(c.to_jdn(174, 0, 3))[:2] == (174, 0)


def test_badi_2015_round_trip_and_bounds():
    c = CALENDARS["badi_2015"]
    for jd in range(c.epoch_jdn, c.starts[-1], 11):
        y, m, d = c.from_jdn(jd)
        assert c.to_jdn(y, m, d) == jd
        assert m in range(0, 20)
    for bad in ((171, 1, 1), (221, 1, 1)):     # before table / terminal sentinel
        with pytest.raises(CalendarRangeError) as ei:
            c.to_jdn(*bad)
        assert ei.value.fallback == "bahai"


# -- french_republican_equinox: true autumnal equinox at Paris, An I..An XIII --

def test_french_equinox_is_tabulated_with_arithmetic_fallback():
    c = CALENDARS["french_republican_equinox"]
    assert isinstance(c, TabulatedCalendar)
    assert c.basis == "tabulated" and c.fallback == "french_republican"


def test_french_equinox_gold_dates():
    c = CALENDARS["french_republican_equinox"]
    assert jdn_to_gregorian(c.to_jdn(1, 1, 1)) == (1792, 9, 22)   # An I Vendémiaire 1
    assert jdn_to_gregorian(c.to_jdn(8, 2, 18)) == (1799, 11, 9)  # 18 Brumaire An VIII
    assert jdn_to_gregorian(c.to_jdn(12, 1, 1)) == (1803, 9, 24)  # An XII begins


def test_french_equinox_sextile_years_have_six_complementary_days():
    c = CALENDARS["french_republican_equinox"]
    # An III, VII, XI are sextile (366-day) in this window: 6 complementary days
    for leap in (3, 7, 11):
        assert c.to_jdn(leap + 1, 1, 1) - c.to_jdn(leap, 13, 1) == 6
    for common in (1, 2, 4, 5):
        assert c.to_jdn(common + 1, 1, 1) - c.to_jdn(common, 13, 1) == 5


def test_french_equinox_arithmetic_variant_untouched():
    # the arithmetic Romme french_republican stays exact and Gregorian-derived;
    # in this window the two agree on An VIII's start, but the mechanisms differ.
    assert CALENDARS["french_republican"].basis == "exact"
    assert not isinstance(CALENDARS["french_republican"], TabulatedCalendar)


def test_french_equinox_round_trip_and_bounds():
    c = CALENDARS["french_republican_equinox"]
    for jd in range(c.epoch_jdn, c.starts[-1]):
        y, m, d = c.from_jdn(jd)
        assert c.to_jdn(y, m, d) == jd
        assert 1 <= m <= 13
    for bad in ((0, 1, 1), (14, 1, 1)):        # before table / terminal sentinel
        with pytest.raises(CalendarRangeError) as ei:
            c.to_jdn(*bad)
        assert ei.value.fallback == "french_republican"


# -- chinese: lunisolar, Hong Kong Observatory conversion tables 1901-2099 -----
# A leap month following ordinary month M is addressed as month M+100.

def test_chinese_is_tabulated_no_arithmetic_fallback():
    c = CALENDARS["chinese"]
    assert isinstance(c, TabulatedCalendar)
    assert c.basis == "tabulated"
    assert c.fallback is None            # lunisolar starts have no arithmetic rule
    assert c.month_count == 12


def test_chinese_new_year_gold():
    c = CALENDARS["chinese"]
    # CNY 2024 (jiachen, year of the Dragon) == 2024-02-10; CNY 2025 == 2025-01-29
    assert jdn_to_gregorian(c.to_jdn(2024, 1, 1)) == (2024, 2, 10)
    assert jdn_to_gregorian(c.to_jdn(2025, 1, 1)) == (2025, 1, 29)


def test_chinese_leap_months_2023_and_2025():
    c = CALENDARS["chinese"]
    # 2023 has leap month 2 (addressed as 102); 2025 has leap month 6 (106).
    assert jdn_to_gregorian(c.to_jdn(2023, 102, 1)) == (2023, 3, 22)
    assert jdn_to_gregorian(c.to_jdn(2025, 106, 1)) == (2025, 7, 25)
    # the leap month directly follows its ordinary namesake month
    assert c.to_jdn(2025, 106, 1) > c.to_jdn(2025, 6, 1)
    assert c.to_jdn(2025, 7, 1) > c.to_jdn(2025, 106, 1)
    # a non-leap year has no such leap month
    with pytest.raises(CalendarRangeError):
        c.to_jdn(2024, 102, 1)


def test_chinese_leap_month_encoding_round_trips():
    c = CALENDARS["chinese"]
    # a leap month start round-trips as month > 100 (leap flag preserved)
    jd = c.to_jdn(2025, 106, 3)
    assert c.from_jdn(jd) == (2025, 106, 3)


def test_chinese_months_are_29_or_30_days_and_12_or_13_per_year():
    c = CALENDARS["chinese"]
    from collections import Counter
    per_year = Counter(y for (y, _) in c.labels if y <= 2099)
    assert set(per_year.values()) <= {12, 13}
    assert per_year[2023] == 13 and per_year[2025] == 13   # leap years
    assert per_year[2024] == 12                            # common year
    for a, b in zip(c.starts, c.starts[1:]):
        assert b - a in (29, 30)


def test_chinese_full_range_round_trip():
    c = CALENDARS["chinese"]
    assert jdn_to_gregorian(c.epoch_jdn) == (1901, 2, 19)  # CNY 1901
    for jd in range(c.epoch_jdn, c.starts[-1], 17):
        y, m, d = c.from_jdn(jd)
        assert c.to_jdn(y, m, d) == jd


def test_chinese_out_of_range_raises():
    c = CALENDARS["chinese"]
    with pytest.raises(CalendarRangeError):
        c.to_jdn(1900, 12, 1)             # before the table
    with pytest.raises(CalendarRangeError):
        c.to_jdn(2100, 1, 1)             # terminal sentinel (CNY 2100)
    with pytest.raises(CalendarRangeError):
        c.from_jdn(c.epoch_jdn - 1)


# -- provider hook (item 7): a fake ephemeris extends a table past its end ---

def test_event_provider_extends_umm_al_qura_past_its_table():
    c = CALENDARS["umm_al_qura"]
    # Past the table (AH 1501+) the calendar raises; a registered provider can
    # supply month starts. Here a synthetic provider hands out fixed 30-day
    # months anchored at the terminal sentinel start.
    sentinel_start = c.starts[-1]          # JDN of AH 1501-01 (sentinel)

    def fake(year, month):
        # only serve AH 1501-01 as a 30-day month for this smoke test
        if (year, month) == (1501, 1):
            return sentinel_start, 30
        return None

    key = "umm_al_qura"
    try:
        with pytest.raises(CalendarRangeError):
            c.to_jdn(1501, 1, 1)           # not served before registration
        register_event_provider(key, fake)
        assert c.to_jdn(1501, 1, 1) == sentinel_start
        assert c.to_jdn(1501, 1, 30) == sentinel_start + 29
        # from_jdn also consults the provider past the table
        assert c.from_jdn(sentinel_start) == (1501, 1, 1)
        with pytest.raises(CalendarRangeError):
            c.to_jdn(1501, 1, 31)          # beyond provider month length
    finally:
        cal._EVENT_PROVIDERS.pop(key, None)
    # after cleanup the bounded contract is restored
    with pytest.raises(CalendarRangeError):
        c.to_jdn(1501, 1, 1)
