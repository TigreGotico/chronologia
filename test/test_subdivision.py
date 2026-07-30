"""French Republican decimal time: exact day-fraction arithmetic on the
``DaySubdivision`` registry, ported from the reckoning-core assertions the
parser exercised through its ``subdivision_time`` engine stage.

The day divides into 10 decimal hours / 100 decimal minutes / 100 decimal
seconds; rescaling to civil time is exact to the microsecond
(Wikipedia, "French Republican calendar").  The parser's start/width AstroDate
spans are engine composition; the exact ``units_to_us`` / ``unit_width_us``
values they rest on are the core, asserted directly here.
"""
from chronologia.cycles import DAY_SUBDIVISIONS

FR = DAY_SUBDIVISIONS["french_decimal"]

US_PER_DAY = 86_400_000_000


# -- exact rescaling to civil microseconds -------------------------------

def test_five_decimal_hours_is_noon_exactly():
    # 5 decimal hours == 1/2 day == 43_200_000_000 us == 12:00:00
    assert FR.units_to_us(5, 0, 0) == 43_200_000_000
    assert FR.units_to_us(5, 0, 0) == US_PER_DAY // 2


def test_two_and_a_half_decimal_hours_is_six_am():
    # 2 dh + 50 dm == 0.2 + 0.05 == 0.25 day == 06:00:00
    assert FR.units_to_us(2, 50, 0) == US_PER_DAY // 4
    assert FR.units_to_us(2, 50, 0) == 21_600_000_000


def test_full_decimal_reading_to_the_microsecond():
    # 7 dh + 50 dm + 0 ds == 0.75 day == 18:00:00
    assert FR.units_to_us(7, 50, 0) == US_PER_DAY * 3 // 4
    assert FR.units_to_us(7, 50, 0) == 64_800_000_000


def test_midnight_zero_reading():
    assert FR.units_to_us(0, 0, 0) == 0


# -- referential unit widths ---------------------------------------------

def test_decimal_hour_width_is_two_hours_twenty_four_minutes():
    # one decimal hour == 1/10 day == 2h24m == 8_640_000_000 us
    assert FR.unit_width_us("hour") == 8_640_000_000


def test_decimal_minute_width_is_eighty_six_point_four_seconds():
    # one decimal minute == 1/1000 day == 86.4 civil seconds
    assert FR.unit_width_us("minute") == 86_400_000


def test_decimal_second_width_is_point_eight_six_four_seconds():
    # one decimal second == 1/100000 day == 0.864 civil seconds
    assert FR.unit_width_us("second") == 864_000
