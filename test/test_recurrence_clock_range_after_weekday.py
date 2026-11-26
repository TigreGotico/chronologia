# -*- coding: utf-8 -*-
"""A clock range after a weekday is a time of day, also where the range's "to"
word doubles as an "until" word (de "bis", nl "tot")."""
from datetime import datetime

import pytest

from chronologia import extract_event, extract_recurrence

_A = datetime(2026, 11, 22, 9)  # a Sunday


@pytest.mark.parametrize("lang,text", [
    ("en", "every monday from 9 to 5 pm"),
    ("de", "jeden Montag von 9 bis 17 Uhr"),
    ("nl", "elke maandag van 9 tot 17 uur"),
    ("fr", "chaque lundi de 9 à 17 heures"),
    ("it", "ogni lunedì dalle 9 fino alle 17"),
    ("ca", "cada dilluns de 9 a 17"),
])
def test_clock_range_after_weekday_is_a_time_of_day(lang, text):
    got = extract_recurrence(text, lang, _A)
    assert got.recurrence.to_string() == "FREQ=WEEKLY;BYDAY=MO;BYHOUR=9"
    assert got.remainder == ""
    event = extract_event(text, lang, _A)
    assert event.span.start == datetime(2026, 11, 23, 9)


@pytest.mark.parametrize("lang,text", [
    ("en", "every monday from 9am until 5 december"),
    ("de", "jeden Montag ab 9 Uhr bis 5. Dezember"),
    ("nl", "elke maandag vanaf 9 uur tot 5 december"),
    ("fr", "chaque lundi de 9 heures jusqu'au 5 décembre"),
    ("it", "ogni lunedì dalle 9 fino al 5 dicembre"),
    ("ca", "cada dilluns de 9 fins al 5 de desembre"),
    ("pt", "todas as segundas de 9 até 5 de dezembro"),
])
def test_end_date_after_a_start_clock_stays_an_until_bound(lang, text):
    rule = extract_recurrence(text, lang, _A).recurrence.to_string()
    assert "UNTIL=20261205T000000" in rule


@pytest.mark.parametrize("lang,text", [
    ("de", "jeden Montag vom 1. bis 5. Dezember"),
    ("fr", "chaque lundi du 1 au 5 décembre"),
    ("it", "ogni lunedì dal 1 al 5 dicembre"),
])
def test_date_range_after_a_weekday_is_not_a_clock(lang, text):
    rule = extract_recurrence(text, lang, _A).recurrence.to_string()
    assert "UNTIL=20261206T000000" in rule
    assert "BYHOUR" not in rule


def test_end_date_after_a_start_clock_keeps_the_end_clock():
    got = extract_recurrence("every monday from 9 until 5 december at 10", "en", _A)
    assert "UNTIL=20261205T100000" in got.recurrence.to_string()


@pytest.mark.parametrize("text,count", [
    ("every monday from 9 to 5 10 times", 10),
    ("every monday from 9 to 5, 10 times", 10),
    ("every monday from 9 to 11 3 times", 3),
])
def test_count_after_a_clock_range_is_kept(text, count):
    got = extract_recurrence(text, "en", _A)
    assert got.recurrence.to_string() == (
        f"FREQ=WEEKLY;COUNT={count};BYDAY=MO;BYHOUR=9")
    assert got.remainder == ""
