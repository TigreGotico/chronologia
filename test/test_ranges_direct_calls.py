"""Direct calls of ``chronologia.extract.ranges`` keep their results."""
from datetime import date, datetime

from chronologia.extract.ranges import (
    Hemisphere, Season, current_season_date, date_to_season, get_date_ordinal,
    get_season_range, get_week_number, get_weekend_range, get_year_range,
    next_season_date, season_to_date)
from chronologia.resolution import DateTimeResolution


def _next_december_first(today: date) -> date:
    this_year = date(today.year, 12, 1)
    return this_year if this_year > today else date(today.year + 1, 12, 1)


def test_datetime_argument_gives_a_date():
    result = get_date_ordinal(2, datetime(2026, 11, 22, 9, 0),
                              DateTimeResolution.DAY_OF_MONTH)
    assert result == date(2026, 11, 2)
    assert type(result) is date


def test_current_season_accepts_a_datetime():
    assert current_season_date(Season.WINTER, datetime(2026, 1, 5, 3),
                               Hemisphere.NORTH) == date(2025, 12, 1)


def test_season_to_date_reads_an_int_season_and_a_date_year():
    assert season_to_date(1, 2020) == date(2020, 6, 1)
    assert season_to_date(Season.WINTER, date(2020, 5, 5)) == date(2020, 12, 1)


def test_season_functions_default_to_today():
    today = date.today()
    assert season_to_date(Season.WINTER) == date(today.year, 12, 1)
    assert next_season_date(Season.WINTER) == _next_december_first(today)


def test_week_and_year_ranges():
    sunday = date(2026, 11, 22)
    assert get_weekend_range(date(2026, 11, 25)) == (date(2026, 11, 28),
                                                     date(2026, 11, 29))
    assert get_weekend_range(sunday) == (date(2026, 11, 21), sunday)
    assert get_year_range(sunday) == (date(2026, 1, 1), date(2026, 12, 31))
    assert get_week_number(sunday) == 47


def test_season_lookup_and_range():
    assert date_to_season(date(2026, 7, 1)) is Season.SUMMER
    assert date_to_season(date(2026, 7, 1), Hemisphere.SOUTH) is Season.WINTER
    assert date_to_season(date(2026, 12, 15)) is Season.WINTER
    assert date_to_season(date(2026, 12, 15), Hemisphere.SOUTH) is Season.SUMMER
    assert get_season_range(date(2026, 4, 10)) == (date(2026, 3, 1),
                                                   date(2026, 5, 31))
    assert get_season_range(date(2026, 12, 15)) == (date(2026, 12, 1),
                                                    date(2027, 2, 28))
