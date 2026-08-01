"""Regression test: Tokyo 2020 Olympic/Paralympic special-measures relocation.

海の日 (Marine Day), スポーツの日 (Sports Day) and 山の日 (Mountain Day) were
statutorily relocated for 2020 and 2021 by the Act on Special Measures for the
Tokyo 2020 Olympic and Paralympic Games (東京オリンピック・パラリンピック競技
大会特別措置法) to open/close the Games (held in 2021 due to COVID-19). Cross-
checked against vacanza/holidays 0.101 `country_holidays("JP")`.
"""
import datetime

from chronologia import AstroDate, holidays_for

MARINE = "海の日"
SPORTS = "スポーツの日"
MOUNTAIN = "山の日"
FURIKAE_SUFFIX = " (振替休日)"


def _dates_by_name(year):
    return {h.name: h.span.start for h in holidays_for("JP", year)}


def test_2020_olympic_relocated_dates():
    dates = _dates_by_name(2020)
    assert dates[MARINE] == AstroDate(2020, 7, 23)
    assert dates[SPORTS] == AstroDate(2020, 7, 24)
    assert dates[MOUNTAIN] == AstroDate(2020, 8, 10)


def test_2021_olympic_relocated_dates():
    dates = _dates_by_name(2021)
    assert dates[MARINE] == AstroDate(2021, 7, 22)
    assert dates[SPORTS] == AstroDate(2021, 7, 23)
    assert dates[MOUNTAIN] == AstroDate(2021, 8, 8)


def test_2021_mountain_day_furikae_substitute():
    # 2021-08-08 山の日 falls on a Sunday -> 振替休日 substitute the next day.
    dates = _dates_by_name(2021)
    assert dates[MOUNTAIN].weekday() == 6  # Sunday
    assert dates[MOUNTAIN + FURIKAE_SUFFIX] == AstroDate(2021, 8, 9)


def test_2019_uses_standing_rule_dates():
    # Standing rules: 3rd Monday of July, 2nd Monday of October, fixed Aug 11.
    dates = _dates_by_name(2019)
    assert dates[MARINE] == AstroDate(2019, 7, 15)
    assert dates[SPORTS] == AstroDate(2019, 10, 14)
    assert dates[MOUNTAIN] == AstroDate(2019, 8, 11)


def test_2022_reverts_to_standing_rule_dates():
    dates = _dates_by_name(2022)
    assert dates[MARINE] == AstroDate(2022, 7, 18)
    assert dates[SPORTS] == AstroDate(2022, 10, 10)
    assert dates[MOUNTAIN] == AstroDate(2022, 8, 11)


def test_no_duplicate_entries_2020_and_2021():
    for year in (2020, 2021):
        holidays = holidays_for("JP", year)
        names = [h.name for h in holidays if h.name in (MARINE, SPORTS, MOUNTAIN)]
        assert sorted(names) == sorted(set(names)), (
            f"duplicate holiday rows in {year}: {names}")
