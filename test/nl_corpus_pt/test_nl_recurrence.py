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
    # Elliptical nth-weekday: the "do mês" tail is dropped in speech, exactly
    # as English drops "of the month".  The reading is engine-side and
    # language-agnostic -- it needs no pt vocabulary beyond the "último"
    # relative marker and the ordinal fold the locale already ships.
    ("toda última sexta-feira", "FREQ=MONTHLY;BYDAY=-1FR", ""),
    ("toda última sexta-feira do mês", "FREQ=MONTHLY;BYDAY=-1FR", ""),
    ("cada última sexta-feira", "FREQ=MONTHLY;BYDAY=-1FR", ""),
    ("toda última segunda-feira", "FREQ=MONTHLY;BYDAY=-1MO", ""),
    ("toda primeira segunda-feira", "FREQ=MONTHLY;BYDAY=1MO", ""),
    ("cada primeira sexta-feira", "FREQ=MONTHLY;BYDAY=1FR", ""),
    # as in English, an ordinal of two or upwards leaves the two readings
    # competing, so the month-of reading waits for the explicit tail.
    ("toda terceira quinta-feira do mês", "FREQ=MONTHLY;BYDAY=3TH", ""),
]


# adversarial: without the "todo/toda/cada" framing these are single past
# dates, not rules -- "última sexta-feira" is the friday just gone.
@pytest.mark.parametrize("text", [
    "última sexta-feira", "a última sexta-feira", "primeira sexta-feira",
])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None


# a cardinal before a unit stays an INTERVAL, never a day-of-month.
def test_cardinal_plus_unit_stays_an_interval():
    got = extract_recurrence("cada duas semanas", LANG)
    assert got is not None
    assert got[0].to_string() == "FREQ=WEEKLY;INTERVAL=2"


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


# --------------------------------------------------------------------------
# "uma vez ..." framing and the plural day-of-month form.
#
# Every surface below was confirmed natural by a native European Portuguese
# speaker; nothing here is a translation-by-analogy of the English forms.
# --------------------------------------------------------------------------
_ONCE_CASES = [
    # "uma vez por <unidade>" -- one occurrence per period *is* that period's
    # plain frequency, so the count word adds no RRULE part of its own.
    ("uma vez por dia", "FREQ=DAILY", ""),
    ("uma vez por semana", "FREQ=WEEKLY", ""),
    ("uma vez por mês", "FREQ=MONTHLY", ""),
    ("uma vez por ano", "FREQ=YEARLY", ""),
    # European Portuguese also contracts the preposition with the article:
    # "à semana", "ao mês".
    ("uma vez à semana", "FREQ=WEEKLY", ""),
    ("uma vez ao mês", "FREQ=MONTHLY", ""),
    ("uma vez ao dia", "FREQ=DAILY", ""),
    ("uma vez ao ano", "FREQ=YEARLY", ""),
    # a weekday pins the day, exactly as English "once a week on monday".
    ("uma vez por semana à segunda", "FREQ=WEEKLY;BYDAY=MO", ""),
    ("uma vez por semana à segunda-feira", "FREQ=WEEKLY;BYDAY=MO", ""),
    # ... and the clock pin still folds on top of it.
    ("uma vez por semana à segunda às 9", "FREQ=WEEKLY;BYDAY=MO;BYHOUR=9", ""),
]


_DAY_OF_MONTH_CASES = [
    # The plural is what a speaker uses here: the rule is not about one
    # specific day, so "todos os dias 1" reads as "the 1st of every month".
    ("todos os dias 1", "FREQ=MONTHLY;BYMONTHDAY=1", ""),
    ("todos os dias 15", "FREQ=MONTHLY;BYMONTHDAY=15", ""),
    ("todos os dias 1 do mês", "FREQ=MONTHLY;BYMONTHDAY=1", ""),
    ("todos os dias 15 do mês", "FREQ=MONTHLY;BYMONTHDAY=15", ""),
    ("no dia 1 de cada mês", "FREQ=MONTHLY;BYMONTHDAY=1", ""),
    ("no dia 15 de cada mês", "FREQ=MONTHLY;BYMONTHDAY=15", ""),
]


@pytest.mark.parametrize("text,rrule,remainder",
                         _ONCE_CASES + _DAY_OF_MONTH_CASES)
def test_once_and_day_of_month(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


def test_todos_os_dias_still_means_daily():
    """The collision guard: "todos os dias" on its own is DAILY.

    Only a *trailing day number* diverts it to a day-of-month rule, so the
    bare phrase must keep the reading it has always had."""
    got = extract_recurrence("todos os dias", LANG)
    assert got is not None
    assert got[0].to_string() == "FREQ=DAILY"
    assert got[1] == ""


def test_singular_day_number_is_not_a_day_of_month_rule():
    """"todo dia 1" is not the natural surface for this sense (a native
    speaker uses the plural), so the day number is *not* read as a
    BYMONTHDAY: the phrase keeps its plain DAILY reading and the stray
    number is left in the remainder."""
    got = extract_recurrence("todo dia 1", LANG)
    assert got is not None
    assert got[0].to_string() == "FREQ=DAILY"
    assert got[1] == "1"


@pytest.mark.parametrize("text", [
    # a per-period *count* above one needs a different RRULE shape
    # (BYSETPOS / per-period COUNT) than the plain frequency, so it is left
    # unread rather than forced into a wrong interval.
    "duas vezes por semana",
    "três vezes por mês",
    # the count phrase alone names no period at all
    "uma vez",
    "uma vez por",
    # a bare day number is a date, not a rule
    "dia 1",
    "no dia 1",
])
def test_once_adversarial_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None
