# -*- coding: utf-8 -*-
"""R123 (es): a time-of-day LIST in a recurrence used to keep only the first
clock and strand the rest -- "todos los días a las 9am y a las 5pm" ->
``FREQ=DAILY;BYHOUR=9``, remainder "y a las 5pm".  See the English sibling
``test/nl_corpus_en/test_nl_r123_byhour_list.py`` for the full contract.

Spanish repeats the leading marker before each list item ("a las 9am y **a
las** 5pm"), not just the "and"/comma connector -- the fix must skip that
repeated marker between items too.
"""
from datetime import datetime

import pytest

from chronologia.extract import extract_recurrence

LANG = "es"
_A = datetime(2026, 8, 11, 10, 0)

_CASES = [
    ("todos los días a las 9am y a las 5pm", "FREQ=DAILY;BYHOUR=9,17", ""),
    ("diariamente a las 9am y a las 5pm", "FREQ=DAILY;BYHOUR=9,17", ""),
    # three-item list, repeated "a las" marker before each item.
    ("todos los días a las 9, a las 12 y a las 5pm",
     "FREQ=DAILY;BYHOUR=9,12,17", ""),
    # a weekday LIST plus an hour LIST together.
    ("cada lunes y miércoles a las 9 y a las 5pm",
     "FREQ=WEEKLY;BYDAY=MO,WE;BYHOUR=9,17", ""),
    # minute-bearing items with an IDENTICAL minute across the list.
    ("todos los días a las 9:15 y a las 12:15",
     "FREQ=DAILY;BYHOUR=9,12;BYMINUTE=15", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_byhour_list(text, rrule, remainder):
    got = extract_recurrence(text, LANG, anchor=_A)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", [
    # differing minutes across list items: refuse rather than mis-encode.
    "todos los días a las 9:15 y a las 17:45",
    "diariamente a las 9:00 y a las 17:30",
])
def test_byhour_list_differing_minutes_declines(text):
    assert extract_recurrence(text, LANG, anchor=_A) is None


# Controls: constructions this fix must NOT disturb.

@pytest.mark.parametrize("text,rrule,remainder", [
    ("cada lunes a las 9", "FREQ=WEEKLY;BYDAY=MO;BYHOUR=9", ""),
    ("cada miércoles a las 9:30", "FREQ=WEEKLY;BYDAY=WE;BYHOUR=9;BYMINUTE=30", ""),
    ("todos los días a las 9", "FREQ=DAILY;BYHOUR=9", ""),
])
def test_controls_unchanged(text, rrule, remainder):
    got = extract_recurrence(text, LANG, anchor=_A)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder
