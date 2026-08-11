# -*- coding: utf-8 -*-
"""R123: a time-of-day LIST in a recurrence used to keep only the first clock
and strand the rest -- "daily at 9am and 5pm" -> ``FREQ=DAILY;BYHOUR=9``,
remainder "and 5pm", silently dropping the 5pm occurrence.

RFC 5545's ``BYHOUR`` is multi-valued, so a list of full clocks (each with its
own meridiem, separated by commas/"and"/a repeated leading marker) must fold
onto ONE ``BYHOUR=h1,h2,...`` -- see :func:`chronologia.extract.nseries._apply_clock`.

``BYMINUTE`` has no per-hour variant in RFC 5545: when every list item names
the SAME minute, that minute is used; when items disagree, the rule cannot be
expressed honestly and the whole recurrence declines (``None``) rather than
silently keeping only one item's minute.
"""
from datetime import datetime

import pytest

from chronologia.extract import extract_recurrence

LANG = "en"
_A = datetime(2026, 8, 11, 10, 0)

# (text, expected RRULE string, expected remainder)
_CASES = [
    # two-item list, on-the-hour.
    ("daily at 9am and 5pm", "FREQ=DAILY;BYHOUR=9,17", ""),
    ("every day at 9am and 5pm", "FREQ=DAILY;BYHOUR=9,17", ""),
    # three-item list (comma between the first two, "and" before the last --
    # the tokenizer drops the comma, so nothing sits between "9am" and "12pm").
    ("every day at 9am, 12pm and 5pm", "FREQ=DAILY;BYHOUR=9,12,17", ""),
    ("daily at 9am, 12pm and 10pm", "FREQ=DAILY;BYHOUR=9,12,22", ""),
    # mixed meridiems within the list -- each item resolves its OWN am/pm,
    # not inherited from a neighbour.
    ("daily at 8am, 1pm and 11pm", "FREQ=DAILY;BYHOUR=8,13,23", ""),
    # minute-bearing items with an IDENTICAL minute across the whole list:
    # representable as one BYMINUTE.
    ("daily at 9:15 and 12:15", "FREQ=DAILY;BYHOUR=9,12;BYMINUTE=15", ""),
    ("daily at 9:15, 12:15 and 17:15", "FREQ=DAILY;BYHOUR=9,12,17;BYMINUTE=15", ""),
    # a weekday LIST plus an hour LIST together -- both multi-valued parts
    # fold independently onto the same rule.
    ("every monday and wednesday at 9am and 5pm",
     "FREQ=WEEKLY;BYDAY=MO,WE;BYHOUR=9,17", ""),
    # the list is embedded mid-sentence; trailing prose is left in the
    # remainder untouched.
    ("every friday at 9am and 5pm since it is a workday",
     "FREQ=WEEKLY;BYDAY=FR;BYHOUR=9,17", "since it is a workday"),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_byhour_list(text, rrule, remainder):
    got = extract_recurrence(text, LANG, anchor=_A)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", [
    # differing minutes across list items cannot be folded onto one
    # BYMINUTE -- refuse outright rather than silently keep only one item's
    # minute.
    "daily at 9:15 and 17:45",
    "every day at 9:00 and 17:30",
    "daily at 9:15, 12:30 and 17:45",
])
def test_byhour_list_differing_minutes_declines(text):
    assert extract_recurrence(text, LANG, anchor=_A) is None


# Controls: constructions this fix must NOT disturb.

@pytest.mark.parametrize("text,rrule,remainder", [
    # the "from 9 to 5" clock-RANGE convention keeps only the start hour --
    # untouched by the list fix (a range is not a list: no "and"-joined
    # sequence of full clocks here, just one start/end pair).
    ("every monday from 9 to 5", "FREQ=WEEKLY;BYDAY=MO;BYHOUR=9", ""),
    ("daily from 9am to 5pm", "FREQ=DAILY;BYHOUR=9", ""),
    # weekday lists alone (no hour clause) are unaffected.
    ("every monday and wednesday", "FREQ=WEEKLY;BYDAY=MO,WE", ""),
    ("every monday, wednesday and friday",
     "FREQ=WEEKLY;BYDAY=MO,WE,FR", ""),
    # a single clock pin (no list) is unaffected.
    ("daily at 9am", "FREQ=DAILY;BYHOUR=9", ""),
    ("every wednesday at 9:30", "FREQ=WEEKLY;BYDAY=WE;BYHOUR=9;BYMINUTE=30", ""),
])
def test_controls_unchanged(text, rrule, remainder):
    got = extract_recurrence(text, LANG, anchor=_A)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder
