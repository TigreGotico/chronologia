# -*- coding: utf-8 -*-
"""Bounded recurrence (an): a base rule plus an until-date (``dica`` -> UNTIL)
or a for-duration (``durante`` -> COUNT).  UNTIL resolved against a fixed
anchor (2018-06-05)."""
from datetime import datetime
import pytest
from chronologia.extract import extract_recurrence

ANCHOR = datetime(2018, 6, 5, 13, 4)
_CASES = [
    ('cada viernes', 'FREQ=WEEKLY;BYDAY=FR', ''),
    ('cada semana', 'FREQ=WEEKLY', ''),
    ('cada viernes dica abril', 'FREQ=WEEKLY;UNTIL=20180401T000000;BYDAY=FR', ''),
    ('cada luns dica setiembre', 'FREQ=WEEKLY;UNTIL=20180901T000000;BYDAY=MO', ''),
    ('cada luns durante 6 semanas', 'FREQ=WEEKLY;COUNT=6;BYDAY=MO', ''),
    ('cada viernes durante 3 semanas', 'FREQ=WEEKLY;COUNT=3;BYDAY=FR', ''),
    ('cada semana durante 4 semanas', 'FREQ=WEEKLY;COUNT=4', ''),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_bounded_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, "an", anchor=ANCHOR)
    assert got is not None, f"{text!r} did not parse"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ['viernes', "o 5 de chinero"])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, "an", anchor=ANCHOR) is None
