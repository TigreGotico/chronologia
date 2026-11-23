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
