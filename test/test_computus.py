"""Computus: Easter, movable feasts, and the fixed liturgical feasts.

Golden dates are cited historical/liturgical facts (Western Easter 2024-03-31,
Orthodox 2024-05-05, the 2025 coincidence, the 1818/1943 calendar extremes) and
the day-offsets from ``moveable_feast_wikipedia.html`` /
``liturgical_year_wikipedia.html``.  The suite includes a 500-year bounds sweep,
the Sunday invariant, method divergence/coincidence checks, and adversarial
inputs written to break the API.
"""
from datetime import timedelta

import pytest

from chronologia import (AstroDate, EASTER_METHODS, FIXED_FEASTS,
                         MOVABLE_FEAST_OFFSETS, advent_sunday, easter,
                         fixed_feast, movable_feast)


# --------------------------------------------------------------------------
# Easter golds
# --------------------------------------------------------------------------

def test_gregorian_easter_2024_is_march_31():
    assert easter(2024, "gregorian") == AstroDate(2024, 3, 31)


def test_gregorian_easter_default_method_is_gregorian():
    assert easter(2024) == easter(2024, "gregorian")


def test_orthodox_easter_2024_civil_is_may_5():
    # Julian Easter rendered on the Gregorian civil calendar.
    assert easter(2024, "julian_gregorian_date") == AstroDate(2024, 5, 5)


def test_julian_easter_2024_own_label_is_april_22():
    # The raw Julian-calendar label (22 April Julian), carried as AstroDate
    # fields -- a label, not the civil instant.
    assert easter(2024, "julian") == AstroDate(2024, 4, 22)


def test_julian_label_renders_to_civil_instant():
    # Feeding the Julian label back through the Julian calendar reproduces the
    # civil (Gregorian) instant, tying the two Orthodox renderings together.
    label = easter(2024, "julian")
    civil = AstroDate.from_calendar("julian", label.year,
                                    label.month, label.day)
    assert civil == easter(2024, "julian_gregorian_date")


def test_orthodox_easter_2023_civil_is_april_16():
    assert easter(2023, "julian_gregorian_date") == AstroDate(2023, 4, 16)


def test_gregorian_easter_2025_is_april_20():
    assert easter(2025, "gregorian") == AstroDate(2025, 4, 20)


# --------------------------------------------------------------------------
# Method divergence and the rare coincidence
# --------------------------------------------------------------------------

def test_2025_both_easters_coincide():
    # Rare alignment: Western and Orthodox Easter both fall on 2025-04-20.
    assert (easter(2025, "gregorian")
            == easter(2025, "julian_gregorian_date")
            == AstroDate(2025, 4, 20))


def test_2024_methods_diverge():
    # Usual case: the two civil Easters differ (2024 by five weeks).
    assert (easter(2024, "gregorian")
            != easter(2024, "julian_gregorian_date"))
    delta = (easter(2024, "julian_gregorian_date")
             - easter(2024, "gregorian"))
    assert delta == timedelta(days=35)


def test_orthodox_never_before_gregorian_over_a_century():
    # The Orthodox civil Easter is always on or after the Western one.
    for year in range(1950, 2050):
        assert (easter(year, "julian_gregorian_date")
                >= easter(year, "gregorian"))


def test_coincidence_years_are_rare_but_recur():
    coincide = [y for y in range(2000, 2100)
                if easter(y, "gregorian")
                == easter(y, "julian_gregorian_date")]
    assert 2025 in coincide
    assert 2010 in coincide  # both 2010-04-04
    # rare: far fewer than half the century
    assert 0 < len(coincide) < 40


# --------------------------------------------------------------------------
# The Sunday invariant
# --------------------------------------------------------------------------

def test_gregorian_easter_is_always_sunday():
    # datetime convention: Sunday == weekday() 6.
    for year in range(1583, 2583):
        assert easter(year, "gregorian").weekday() == 6


def test_orthodox_civil_easter_is_always_sunday():
    for year in range(1583, 2583):
        assert easter(year, "julian_gregorian_date").weekday() == 6


def test_julian_label_is_sunday_in_the_julian_calendar():
    # The raw label's own weekday is not a civil Sunday, but the instant it
    # denotes (via the Julian calendar) is.
    for year in range(1900, 2100):
        label = easter(year, "julian")
        instant = AstroDate.from_calendar("julian", label.year,
                                          label.month, label.day)
        assert instant.weekday() == 6


# --------------------------------------------------------------------------
# 500-year bounds sweep and the historical extremes
# --------------------------------------------------------------------------

def test_gregorian_easter_bounds_over_500_years():
    # Easter can never fall before 22 March nor after 25 April.
    earliest = (12, 31)
    latest = (1, 1)
    for year in range(1583, 2083):
        e = easter(year, "gregorian")
        assert (3, 22) <= (e.month, e.day) <= (4, 25), (year, e)
        earliest = min(earliest, (e.month, e.day))
        latest = max(latest, (e.month, e.day))
    # both extremes are actually attained within the window
    assert earliest == (3, 22)
    assert latest == (4, 25)


def test_earliest_possible_easter_1818():
    # 1818 is the cited earliest-possible date, 22 March.
    assert easter(1818, "gregorian") == AstroDate(1818, 3, 22)


def test_latest_possible_easter_1943():
    # 1943 is the cited latest-possible date, 25 April.
    assert easter(1943, "gregorian") == AstroDate(1943, 4, 25)


def test_pre_gregorian_year_is_proleptic_but_computed():
    # year < 1583: the Gregorian method is proleptic (the calendar did not yet
    # exist), yet the arithmetic still yields a valid in-bounds Sunday.
    e = easter(1500, "gregorian")
    assert e.weekday() == 6
    assert (3, 22) <= (e.month, e.day) <= (4, 25)


# --------------------------------------------------------------------------
# Movable feasts
# --------------------------------------------------------------------------

def test_ash_wednesday_2024_is_feb_14():
    assert movable_feast("ash_wednesday", 2024) == AstroDate(2024, 2, 14)


def test_good_friday_2024_is_march_29():
    assert movable_feast("good_friday", 2024) == AstroDate(2024, 3, 29)


def test_pentecost_2024_is_may_19():
    assert movable_feast("pentecost", 2024) == AstroDate(2024, 5, 19)


def test_palm_sunday_2024_is_march_24():
    assert movable_feast("palm_sunday", 2024) == AstroDate(2024, 3, 24)


def test_ascension_2024_is_may_9():
    assert movable_feast("ascension", 2024) == AstroDate(2024, 5, 9)


def test_movable_feasts_honour_their_offsets():
    e = easter(2024, "gregorian")
    for name, offset in MOVABLE_FEAST_OFFSETS.items():
        assert movable_feast(name, 2024) == e + timedelta(days=offset)


def test_ash_wednesday_and_good_friday_are_correct_weekdays():
    for year in range(1990, 2060):
        assert movable_feast("ash_wednesday", year).weekday() == 2  # Wed
        assert movable_feast("good_friday", year).weekday() == 4    # Fri
        assert movable_feast("palm_sunday", year).weekday() == 6    # Sun


def test_orthodox_movable_feast_uses_civil_instant():
    # Orthodox Good Friday 2024 = Orthodox Easter (2024-05-05) minus 2 days.
    assert (movable_feast("good_friday", 2024, "julian_gregorian_date")
            == AstroDate(2024, 5, 3))
    # 'julian' resolves to the same civil instant (never the raw label).
    assert (movable_feast("good_friday", 2024, "julian")
            == movable_feast("good_friday", 2024, "julian_gregorian_date"))


# --------------------------------------------------------------------------
# Fixed feasts and Advent
# --------------------------------------------------------------------------

def test_fixed_feasts_stamp_their_dates():
    assert fixed_feast("christmas", 2024) == AstroDate(2024, 12, 25)
    assert fixed_feast("epiphany", 2024) == AstroDate(2024, 1, 6)
    assert fixed_feast("assumption", 2024) == AstroDate(2024, 8, 15)
    assert fixed_feast("all_saints", 2024) == AstroDate(2024, 11, 1)


def test_fixed_feasts_dont_move_with_year():
    for year in (1000, 1583, 2024, 5000):
        assert fixed_feast("christmas", year) == AstroDate(year, 12, 25)


def test_advent_sunday_2024_is_dec_1():
    assert advent_sunday(2024) == AstroDate(2024, 12, 1)


def test_advent_sunday_2023_and_2025():
    assert advent_sunday(2023) == AstroDate(2023, 12, 3)
    assert advent_sunday(2025) == AstroDate(2025, 11, 30)


def test_advent_sunday_is_always_sunday_in_late_november_window():
    for year in range(1900, 2100):
        a = advent_sunday(year)
        assert a.weekday() == 6
        assert (a.month, a.day) >= (11, 27)
        assert (a.month, a.day) <= (12, 3)


# --------------------------------------------------------------------------
# Adversarial: bad methods and names must raise, not silently misbehave
# --------------------------------------------------------------------------

def test_bad_easter_method_raises():
    with pytest.raises(ValueError):
        easter(2024, "byzantine")


def test_bad_movable_feast_name_raises():
    with pytest.raises(ValueError):
        movable_feast("groundhog_day", 2024)


def test_movable_feast_bad_method_raises():
    with pytest.raises(ValueError):
        movable_feast("pentecost", 2024, "coptic")


def test_bad_fixed_feast_name_raises():
    with pytest.raises(ValueError):
        fixed_feast("halloween", 2024)


def test_method_names_match_registry():
    assert set(EASTER_METHODS) == {
        "gregorian", "julian", "julian_gregorian_date"}
    assert set(MOVABLE_FEAST_OFFSETS) >= {
        "ash_wednesday", "palm_sunday", "good_friday", "ascension",
        "pentecost", "trinity_sunday", "corpus_christi"}
    assert set(FIXED_FEASTS) == {
        "christmas", "epiphany", "assumption", "all_saints"}
