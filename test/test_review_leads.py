"""Readings that give a wrong value on dev, pinned until the issue is fixed."""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_duration, extract_recurrence, extract_timespan
from chronologia.extract.nseries import _timespan_engine

ANCHOR = datetime(2017, 6, 27, 13, 4)


def xfail(draft):
    return pytest.mark.xfail(strict=True, reason=f"#{draft}")


FR = xfail("20261124-175814-chronologia-1762870-17248")
NL_PT = xfail("20261124-175822-chronologia-1763333-31038")
SLOW = xfail("20261124-175824-chronologia-1763601-18381")
FA = xfail("20261124-175825-chronologia-1763993-3395")
SV = xfail("20261124-175827-chronologia-1764349-8234")
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


@SLOW
def test_duration_runs_the_matcher_once(monkeypatch):
    matcher = _timespan_engine("nl").matcher
    match, runs = matcher.match, []
    monkeypatch.setattr(matcher, "match",
                        lambda *args: runs.append(1) or match(*args))
    extract_duration(" en ".join(f"{k} uur" for k in range(2, 12)), "nl")
    assert len(runs) <= 1


@FA
@pytest.mark.parametrize("text", ["دو شب پیش", "سه شب پیش"])
def test_fa_nights_ago_is_not_a_future_clock(text):
    got = extract_timespan(text, "fa", ANCHOR)
    assert got is None or got.span.start.datetime() < ANCHOR


@FA
def test_fa_days_and_nights_is_no_clock():
    assert extract_timespan("سه روز و سه شب", "fa", ANCHOR) is None


@SV
@pytest.mark.parametrize("text", ["bitti", "väck mig bitti"])
def test_sv_bitti_alone_is_not_a_past_band(text):
    got = extract_timespan(text, "sv", ANCHOR)
    assert got is None or got.span.start.datetime() >= ANCHOR


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
