"""Readings that give a wrong value on dev, pinned until the issue is fixed."""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_duration, extract_recurrence, extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)


def xfail(issue):
    return pytest.mark.xfail(raises=AssertionError, strict=True, reason=f"#{issue}")


FR = xfail("1379")
NL_PT = xfail("1380")
FA = xfail("1382")
HOLIDAY_BOUNDS = xfail("1373")


@FR
@pytest.mark.parametrize("text", ["à 8 heures de route", "à 8 heures de Paris"])
def test_fr_hours_of_travel_are_no_clock(text):
    assert extract_timespan(text, "fr", ANCHOR) is None


@FR
def test_fr_hours_of_route_are_a_length():
    got = extract_duration("à 8 heures de route", "fr", anchor=ANCHOR)
    assert got is not None and got.duration == timedelta(hours=8)


@NL_PT
@pytest.mark.parametrize("lang, text", [
    ("nl", "om 8 uur en 30 minuten"),
    ("pt", "às 8 horas e 30 minutos"),
])
def test_clock_with_minutes_in_words(lang, text):
    got = extract_timespan(text, lang, ANCHOR)
    assert got is not None
    assert got.span.start.datetime() == datetime(2017, 6, 27, 20, 30)
    assert got.remainder == ""
    assert extract_duration(text, lang, anchor=ANCHOR) is None


@FA
@pytest.mark.parametrize("text", ["دو شب پیش", "سه شب پیش"])
def test_fa_nights_ago_is_not_a_future_clock(text):
    got = extract_timespan(text, "fa", ANCHOR)
    assert got is None or got.span.start.datetime() < ANCHOR


@FA
def test_fa_days_and_nights_is_no_clock():
    assert extract_timespan("سه روز و سه شب", "fa", ANCHOR) is None


@HOLIDAY_BOUNDS
def test_holiday_second_bound_is_not_dropped_silently():
    got = extract_recurrence("every easter until 2030 for 2 times", "en",
                             datetime(2026, 11, 24, 9))
    assert "2 times" in got.remainder


@HOLIDAY_BOUNDS
def test_weekly_second_bound_is_not_dropped_silently():
    got = extract_recurrence("every monday until 2030 for 2 times", "en",
                             datetime(2026, 11, 24, 9))
    assert got.recurrence.count == 2 or "2 times" in got.remainder
