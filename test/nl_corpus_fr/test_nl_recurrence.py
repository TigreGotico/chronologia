# -*- coding: utf-8 -*-
"""Recurrence in French: ``extract_recurrence(text, "fr")`` -> RRULE."""
import pytest

from chronologia.extract import extract_recurrence

LANG = "fr"

_CASES = [
    ("chaque vendredi", "FREQ=WEEKLY;BYDAY=FR", ""),
    ("chaque lundi", "FREQ=WEEKLY;BYDAY=MO", ""),
    ("chaque samedi", "FREQ=WEEKLY;BYDAY=SA", ""),
    ("chaque jour", "FREQ=DAILY", ""),
    ("chaque mois", "FREQ=MONTHLY", ""),
    ("chaque année", "FREQ=YEARLY", ""),
    ("toutes les deux semaines", "FREQ=WEEKLY;INTERVAL=2", ""),
    ("tous les jours", "FREQ=DAILY", ""),
    ("mensuellement", "FREQ=MONTHLY", ""),
    ("annuellement", "FREQ=YEARLY", ""),
    ("quotidiennement", "FREQ=DAILY", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ["vendredi", "le lundi"])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None


# Date-anchored recurrence + clock pin (BYHOUR/BYMINUTE) + fixed-holiday rule.
_ANCHORED_CASES = [
    ("tous les 10 mai", "FREQ=YEARLY;BYMONTH=5;BYMONTHDAY=10", ""),
    ("chaque année le 10 mai", "FREQ=YEARLY;BYMONTH=5;BYMONTHDAY=10", ""),
    ("chaque 1 janvier", "FREQ=YEARLY;BYMONTH=1;BYMONTHDAY=1", ""),
    ("chaque 25 décembre", "FREQ=YEARLY;BYMONTH=12;BYMONTHDAY=25", ""),
    ("le 10 de chaque mois", "FREQ=MONTHLY;BYMONTHDAY=10", ""),
    ("tous les mois le 10", "FREQ=MONTHLY;BYMONTHDAY=10", ""),
    ("tous les jours à 9h", "FREQ=DAILY;BYHOUR=9", ""),
    ("chaque mercredi à 9h30", "FREQ=WEEKLY;BYDAY=WE;BYHOUR=9;BYMINUTE=30", ""),
    ("chaque dimanche à 9h", "FREQ=WEEKLY;BYDAY=SU;BYHOUR=9", ""),
    ("chaque lundi à 8h", "FREQ=WEEKLY;BYDAY=MO;BYHOUR=8", ""),
    ("tous les jours à midi", "FREQ=DAILY;BYHOUR=12", ""),
    ("chaque noël", "FREQ=YEARLY;BYMONTH=12;BYMONTHDAY=25", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _ANCHORED_CASES)
def test_anchored_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


from chronologia.recurrence import HolidayRecurrence   # noqa: E402


@pytest.mark.parametrize("text,key", [
    ("chaque pâques", "easter"),
    ("chaque vendredi saint", "good_friday"),
])
def test_movable_holiday_recurrence(text, key):
    got = extract_recurrence(text, LANG)
    assert got is not None
    assert got[0] == HolidayRecurrence(key)
    assert got[1] == ""
    with pytest.raises(ValueError):
        got[0].to_string()


import datetime as _dt_r41


@pytest.mark.parametrize("text,rrule", [('toutes les 2 semaines le mardi', 'FREQ=WEEKLY;INTERVAL=2;BYDAY=TU')])
def test_every_n_unit_with_trailing_placement(text, rrule):
    # "every N <unit>" carrying a trailing "on <weekday>" / "on the <Nth>" that
    # pins the day. Regression: the units branch of _recur_every dropped the
    # placement in locales lacking a marker_on.voc, stranding the qualifier in
    # the remainder while occurrences() fell back to the anchor's own weekday.
    got = extract_recurrence(text, LANG, anchor=_dt_r41.datetime(2017, 6, 28, 13, 4))
    assert got is not None
    assert got[0].to_string() == rrule
    assert got[1] == ""
