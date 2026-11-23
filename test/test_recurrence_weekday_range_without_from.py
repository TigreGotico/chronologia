# -*- coding: utf-8 -*-
"""A weekday range after "every" with no "from" word reads every day in it."""
from datetime import datetime

import pytest

from chronologia import extract_recurrence

_A = datetime(2026, 11, 22, 9)  # a Sunday
_WORKWEEK = "BYDAY=MO,TU,WE,TH,FR"


@pytest.mark.parametrize("lang,text", [
    ("en", "every monday to friday"),
    ("de", "jeden Montag bis Freitag"),
    ("pt", "todas as segundas a sextas"),
    ("es", "cada lunes a viernes"),
    ("fr", "chaque lundi au vendredi"),
    ("it", "ogni lunedì a venerdì"),
    ("nl", "elke maandag tot vrijdag"),
    ("ca", "cada dilluns a divendres"),
    ("gl", "cada luns a venres"),
])
def test_weekday_range_without_from(lang, text):
    got = extract_recurrence(text, lang, _A)
    assert got.recurrence.to_string() == f"FREQ=WEEKLY;{_WORKWEEK}"
    assert got.remainder == ""


def test_weekday_range_wraps_the_week():
    got = extract_recurrence("every friday to monday", "en", _A)
    assert got.recurrence.to_string() == "FREQ=WEEKLY;BYDAY=FR,SA,SU,MO"


def test_weekday_list_after_range_keeps_both():
    got = extract_recurrence("every monday to wednesday and friday", "en", _A)
    assert got.recurrence.to_string() == "FREQ=WEEKLY;BYDAY=MO,TU,WE,FR"
