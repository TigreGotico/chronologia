# -*- coding: utf-8 -*-
"""Recurrence in German: ``extract_recurrence(text, "de")`` -> RRULE."""
import pytest

from chronologia.extract import extract_recurrence

LANG = "de"

_CASES = [
    ("jeden freitag", "FREQ=WEEKLY;BYDAY=FR", ""),
    ("jeden montag", "FREQ=WEEKLY;BYDAY=MO", ""),
    ("jeden tag", "FREQ=DAILY", ""),
    ("jeden monat", "FREQ=MONTHLY", ""),
    ("jedes jahr", "FREQ=YEARLY", ""),
    ("alle zwei wochen", "FREQ=WEEKLY;INTERVAL=2", ""),
    ("wöchentlich", "FREQ=WEEKLY", ""),
    ("monatlich", "FREQ=MONTHLY", ""),
    ("jährlich", "FREQ=YEARLY", ""),
    ("täglich", "FREQ=DAILY", ""),
    ("jeden wochentag", "FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR", ""),
    ("jeden ersten montag im monat", "FREQ=MONTHLY;BYDAY=1MO", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ["freitag", "nächste woche"])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None


# Date-anchored recurrence + clock pin (BYHOUR/BYMINUTE) + fixed-holiday rule.
_ANCHORED_CASES = [
    ("jeden 10. mai", "FREQ=YEARLY;BYMONTH=5;BYMONTHDAY=10", ""),
    ("jedes jahr am 10. mai", "FREQ=YEARLY;BYMONTH=5;BYMONTHDAY=10", ""),
    ("jeden 1. januar", "FREQ=YEARLY;BYMONTH=1;BYMONTHDAY=1", ""),
    ("jeden 25. dezember", "FREQ=YEARLY;BYMONTH=12;BYMONTHDAY=25", ""),
    ("jeden monat am 10.", "FREQ=MONTHLY;BYMONTHDAY=10", ""),
    ("täglich um 9", "FREQ=DAILY;BYHOUR=9", ""),
    ("jeden tag um 9", "FREQ=DAILY;BYHOUR=9", ""),
    ("jeden mittwoch um 9:30", "FREQ=WEEKLY;BYDAY=WE;BYHOUR=9;BYMINUTE=30", ""),
    ("jeden sonntag um 9", "FREQ=WEEKLY;BYDAY=SU;BYHOUR=9", ""),
    ("jeden montag um 8", "FREQ=WEEKLY;BYDAY=MO;BYHOUR=8", ""),
    ("täglich um mitternacht", "FREQ=DAILY;BYHOUR=0", ""),
    ("jedes weihnachten", "FREQ=YEARLY;BYMONTH=12;BYMONTHDAY=25", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _ANCHORED_CASES)
def test_anchored_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


from chronologia.recurrence import HolidayRecurrence   # noqa: E402


@pytest.mark.parametrize("text,key", [
    ("jedes ostern", "easter"),
])
def test_movable_holiday_recurrence(text, key):
    got = extract_recurrence(text, LANG)
    assert got is not None
    assert got[0] == HolidayRecurrence(key)
    assert got[1] == ""
    with pytest.raises(ValueError):
        got[0].to_string()


import datetime as _dt_r41


@pytest.mark.parametrize("text,rrule", [('alle 2 Wochen am Dienstag', 'FREQ=WEEKLY;INTERVAL=2;BYDAY=TU'), ('alle 3 Monate am 5.', 'FREQ=MONTHLY;INTERVAL=3;BYMONTHDAY=5')])
def test_every_n_unit_with_trailing_placement(text, rrule):
    # "every N <unit>" carrying a trailing "on <weekday>" / "on the <Nth>" that
    # pins the day. Regression: the units branch of _recur_every dropped the
    # placement in locales lacking a marker_on.voc, stranding the qualifier in
    # the remainder while occurrences() fell back to the anchor's own weekday.
    got = extract_recurrence(text, LANG, anchor=_dt_r41.datetime(2017, 6, 28, 13, 4))
    assert got is not None
    assert got[0].to_string() == rrule
    assert got[1] == ""
