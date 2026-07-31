"""Regression locks for the second adversarial-audit round.

Correctness-only (no timing assertions): the DoS fixes are verified here by the
behaviour they preserve/repair, and the data fixes by their resulting dates.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate
from chronologia.calendars import (french_republican_from_jdn,
                                   french_republican_to_jdn)
from chronologia.recurrence import every, occurrences, parse_rrule


# --- SEC-002: French Republican conversion is closed-form (O(1)) and exact ---
@pytest.mark.parametrize("year", [1, 3, 100, 2000, 2_000_000, 10_000_000])
def test_french_republican_roundtrips_at_large_years(year):
    for month, day in [(1, 1), (7, 15), (13, 1)]:
        jdn = french_republican_to_jdn(year, month, day)
        assert french_republican_from_jdn(jdn) == (year, month, day)


def test_french_republican_epoch_is_1792_09_22():
    from chronologia import jdn_to_gregorian
    assert jdn_to_gregorian(french_republican_to_jdn(1, 1, 1)) == (1792, 9, 22)


# --- SEC-003: statically-impossible recurrence rejected up front ---
def test_impossible_bymonthday_is_rejected():
    with pytest.raises(ValueError, match="can never occur"):
        parse_rrule("FREQ=YEARLY;BYMONTH=2;BYMONTHDAY=30")


def test_valid_leap_day_recurrence_still_works():
    rec = parse_rrule("FREQ=YEARLY;BYMONTH=2;BYMONTHDAY=29")
    got = [s.start for s in occurrences(rec, AstroDate(2020, 1, 1), count=3)]
    assert [d.year for d in got] == [2020, 2024, 2028]


# --- E1: Bulgarian/Ukrainian Christmas is Revised-Julian (Dec 25), not Jan 7 ---
@pytest.mark.parametrize("lang,phrase,expected", [
    ("bg", "Коледа", "2024-12-25"),
    ("bg", "Бъдни вечер", "2024-12-24"),
    ("uk", "Різдво", "2024-12-25"),
    ("ru", "Рождество", "2025-01-07"),   # Russia stays on the Julian calendar
])
def test_orthodox_christmas_calendar_classification(lang, phrase, expected):
    r = extract_timespan(phrase, lang, datetime(2024, 6, 27, 13, 4))
    assert r is not None
    assert r[0].start_datetime.date().isoformat() == expected
