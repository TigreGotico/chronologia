# -*- coding: utf-8 -*-
"""Recurrence in Portuguese: ``extract_recurrence(text, "pt")`` -> RRULE."""
import pytest

from chronologia.extract import extract_recurrence

LANG = "pt"

_CASES = [
    ("cada sexta-feira", "FREQ=WEEKLY;BYDAY=FR", ""),
    ("cada segunda-feira", "FREQ=WEEKLY;BYDAY=MO", ""),
    ("cada dia", "FREQ=DAILY", ""),
    ("cada mês", "FREQ=MONTHLY", ""),
    ("cada ano", "FREQ=YEARLY", ""),
    ("cada duas semanas", "FREQ=WEEKLY;INTERVAL=2", ""),
    ("semanalmente", "FREQ=WEEKLY", ""),
    ("mensalmente", "FREQ=MONTHLY", ""),
    ("anualmente", "FREQ=YEARLY", ""),
    ("diariamente", "FREQ=DAILY", ""),
    ("a primeira segunda-feira de cada mês", "FREQ=MONTHLY;BYDAY=1MO", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ["sexta-feira", "a segunda-feira"])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None


# Date-anchored recurrence + clock pin (BYHOUR/BYMINUTE) + fixed-holiday rule.
_ANCHORED_CASES = [
    ("todo 10 de maio", "FREQ=YEARLY;BYMONTH=5;BYMONTHDAY=10", ""),
    ("todos os anos em 10 de maio", "FREQ=YEARLY;BYMONTH=5;BYMONTHDAY=10", ""),
    ("todo 25 de dezembro", "FREQ=YEARLY;BYMONTH=12;BYMONTHDAY=25", ""),
    ("todos os meses no dia 10", "FREQ=MONTHLY;BYMONTHDAY=10", ""),
    ("todos os dias às 9", "FREQ=DAILY;BYHOUR=9", ""),
    ("diariamente às 9", "FREQ=DAILY;BYHOUR=9", ""),
    ("toda quarta às 9:30", "FREQ=WEEKLY;BYDAY=WE;BYHOUR=9;BYMINUTE=30", ""),
    ("todo domingo às 9", "FREQ=WEEKLY;BYDAY=SU;BYHOUR=9", ""),
    ("toda quinta-feira às 15", "FREQ=WEEKLY;BYDAY=TH;BYHOUR=15", ""),
    ("todos os dias ao meio-dia", "FREQ=DAILY;BYHOUR=12", ""),
    ("todo dia à meia-noite", "FREQ=DAILY;BYHOUR=0", ""),
    ("todo natal", "FREQ=YEARLY;BYMONTH=12;BYMONTHDAY=25", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _ANCHORED_CASES)
def test_anchored_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


from chronologia.recurrence import HolidayRecurrence   # noqa: E402


@pytest.mark.parametrize("text,key", [
    ("toda páscoa", "easter"),
    ("toda sexta-feira santa", "good_friday"),
])
def test_movable_holiday_recurrence(text, key):
    got = extract_recurrence(text, LANG)
    assert got is not None
    assert got[0] == HolidayRecurrence(key)
    assert got[1] == ""
    with pytest.raises(ValueError):
        got[0].to_string()
