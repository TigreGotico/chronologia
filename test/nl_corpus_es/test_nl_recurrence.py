# -*- coding: utf-8 -*-
"""Recurrence in Spanish: ``extract_recurrence(text, "es")`` -> RRULE."""
import pytest

from chronologia.extract import extract_recurrence

LANG = "es"

_CASES = [
    ("cada viernes", "FREQ=WEEKLY;BYDAY=FR", ""),
    ("cada lunes", "FREQ=WEEKLY;BYDAY=MO", ""),
    ("cada dia", "FREQ=DAILY", ""),
    ("cada mes", "FREQ=MONTHLY", ""),
    ("cada año", "FREQ=YEARLY", ""),
    ("cada dos semanas", "FREQ=WEEKLY;INTERVAL=2", ""),
    ("semanalmente", "FREQ=WEEKLY", ""),
    ("mensualmente", "FREQ=MONTHLY", ""),
    ("anualmente", "FREQ=YEARLY", ""),
    ("diariamente", "FREQ=DAILY", ""),
    ("el segundo martes de cada mes", "FREQ=MONTHLY;BYDAY=2TU", ""),
    ("el 15 de cada mes", "FREQ=MONTHLY;BYMONTHDAY=15", ""),
    # a preposed day-of-month must survive a trailing number, even where the
    # locale has no "N times" count vocab: the preposed "15" wins over the
    # stray "3" from "3 veces" (which used to be read as the day, clobbering 15).
    ("el 15 de cada mes 3 veces", "FREQ=MONTHLY;BYMONTHDAY=15", "3 veces"),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ["viernes", "el lunes"])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None


# Date-anchored recurrence + clock pin (BYHOUR/BYMINUTE) + fixed-holiday rule.
_ANCHORED_CASES = [
    ("cada 10 de mayo", "FREQ=YEARLY;BYMONTH=5;BYMONTHDAY=10", ""),
    ("cada año el 10 de mayo", "FREQ=YEARLY;BYMONTH=5;BYMONTHDAY=10", ""),
    ("cada año el 1 de enero", "FREQ=YEARLY;BYMONTH=1;BYMONTHDAY=1", ""),
    ("cada 25 de diciembre", "FREQ=YEARLY;BYMONTH=12;BYMONTHDAY=25", ""),
    ("el 10 de cada mes", "FREQ=MONTHLY;BYMONTHDAY=10", ""),
    ("cada mes el 10", "FREQ=MONTHLY;BYMONTHDAY=10", ""),
    ("todos los días a las 9", "FREQ=DAILY;BYHOUR=9", ""),
    ("diariamente a las 9", "FREQ=DAILY;BYHOUR=9", ""),
    ("cada miércoles a las 9:30", "FREQ=WEEKLY;BYDAY=WE;BYHOUR=9;BYMINUTE=30", ""),
    ("cada lunes a las 8", "FREQ=WEEKLY;BYDAY=MO;BYHOUR=8", ""),
    ("cada día a mediodía", "FREQ=DAILY;BYHOUR=12", ""),
    ("cada navidad", "FREQ=YEARLY;BYMONTH=12;BYMONTHDAY=25", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _ANCHORED_CASES)
def test_anchored_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


from chronologia.recurrence import HolidayRecurrence   # noqa: E402


@pytest.mark.parametrize("text,key", [
    ("cada pascua", "easter"),
])
def test_movable_holiday_recurrence(text, key):
    got = extract_recurrence(text, LANG)
    assert got is not None
    assert got[0] == HolidayRecurrence(key)
    assert got[1] == ""
    with pytest.raises(ValueError):
        got[0].to_string()


import datetime as _dt_r41


@pytest.mark.parametrize("text,rrule", [('cada 2 semanas el martes', 'FREQ=WEEKLY;INTERVAL=2;BYDAY=TU')])
def test_every_n_unit_with_trailing_placement(text, rrule):
    # "every N <unit>" carrying a trailing "on <weekday>" / "on the <Nth>" that
    # pins the day. Regression: the units branch of _recur_every dropped the
    # placement in locales lacking a marker_on.voc, stranding the qualifier in
    # the remainder while occurrences() fell back to the anchor's own weekday.
    got = extract_recurrence(text, LANG, anchor=_dt_r41.datetime(2017, 6, 28, 13, 4))
    assert got is not None
    assert got[0].to_string() == rrule
    assert got[1] == ""
