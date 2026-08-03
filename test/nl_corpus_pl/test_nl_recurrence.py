# -*- coding: utf-8 -*-
"""Recurrence in pl: extract_recurrence -> RRULE."""
import pytest

from chronologia.extract import extract_recurrence

LANG = "pl"

_CASES = [
    ('każdy piątek', 'FREQ=WEEKLY;BYDAY=FR', ''),
    ('każdy poniedziałek', 'FREQ=WEEKLY;BYDAY=MO', ''),
    ('codziennie', 'FREQ=DAILY', ''),
    ('tygodniowo', 'FREQ=WEEKLY', ''),
    ('miesięcznie', 'FREQ=MONTHLY', ''),
    ('rocznie', 'FREQ=YEARLY', ''),
    ('co 2 tygodnie', 'FREQ=WEEKLY;INTERVAL=2', ''),
    ('co 3 dni', 'FREQ=DAILY;INTERVAL=3', ''),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ['piątek', 'dziś'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None


import datetime as _dt_r41


@pytest.mark.parametrize("text,rrule", [('co 2 tygodnie we wtorek', 'FREQ=WEEKLY;INTERVAL=2;BYDAY=TU')])
def test_every_n_unit_with_trailing_placement(text, rrule):
    # "every N <unit>" carrying a trailing "on <weekday>" / "on the <Nth>" that
    # pins the day. Regression: the units branch of _recur_every dropped the
    # placement in locales lacking a marker_on.voc, stranding the qualifier in
    # the remainder while occurrences() fell back to the anchor's own weekday.
    got = extract_recurrence(text, LANG, anchor=_dt_r41.datetime(2017, 6, 28, 13, 4))
    assert got is not None
    assert got[0].to_string() == rrule
    assert got[1] == ""
