# -*- coding: utf-8 -*-
"""One utterance -> a full :class:`~chronologia.events.Event`, in English.

The contract is ``extract_event(text, "en", anchor=...)`` -> an Event whose
summary, recurrence, duration and first-occurrence span are all asserted by
hand.  The anchor is a fixed Wednesday (2026-07-22 12:00) so every span is
deterministic.
"""
from datetime import datetime, timedelta

import pytest

from chronologia import AstroDate
from chronologia.events import extract_event
from chronologia.recurrence import HolidayRecurrence, parse_rrule

LANG = "en"
ANCHOR = datetime(2026, 7, 22, 12, 0)   # a Wednesday


def _rec(x):
    return None if x is None else (x if isinstance(x, HolidayRecurrence)
                                   else parse_rrule(x))


# (text, summary, recurrence-or-None, duration-seconds-or-None, start, end)
_CASES = [
    ("my weekly meeting every wednesday at 9 for 30 minutes",
     "my weekly meeting", "FREQ=WEEKLY;BYDAY=WE;BYHOUR=9", 1800,
     AstroDate(2026, 7, 22, 9, 0), AstroDate(2026, 7, 22, 9, 30)),
    ("standup every day at 9am for 15 minutes",
     "standup", "FREQ=DAILY;BYHOUR=9", 900,
     AstroDate(2026, 7, 22, 9, 0), AstroDate(2026, 7, 22, 9, 15)),
    ("call mom every sunday",
     "call mom", "FREQ=WEEKLY;BYDAY=SU", None,
     AstroDate(2026, 7, 26), AstroDate(2026, 7, 27)),
    ("team sync every wednesday at 9",
     "team sync", "FREQ=WEEKLY;BYDAY=WE;BYHOUR=9", None,
     AstroDate(2026, 7, 22, 9, 0), AstroDate(2026, 7, 22, 10, 0)),
    ("pay rent on the 1st of every month",
     "pay rent", "FREQ=MONTHLY;BYMONTHDAY=1", None,
     AstroDate(2026, 8, 1), AstroDate(2026, 8, 2)),
    ("christmas dinner every christmas",
     "christmas dinner", "FREQ=YEARLY;BYMONTH=12;BYMONTHDAY=25", None,
     AstroDate(2026, 12, 25), AstroDate(2026, 12, 26)),
    ("yoga class every easter",
     "yoga class", HolidayRecurrence("easter"), None,
     AstroDate(2027, 3, 28), AstroDate(2027, 3, 29)),
    ("dentist next friday at 3pm",
     "dentist", None, None,
     AstroDate(2026, 7, 24, 15, 0), AstroDate(2026, 7, 24, 15, 1)),
    ("lunch june 5th at noon for 1 hour",
     "lunch", None, 3600,
     AstroDate(2027, 6, 5, 12, 0), AstroDate(2027, 6, 5, 13, 0)),
    ("my birthday party on december 25th",
     "my birthday party", None, None,
     AstroDate(2026, 12, 25), AstroDate(2026, 12, 26)),
]


@pytest.mark.parametrize("text,summary,rec,dur,start,end", _CASES)
def test_extract_event(text, summary, rec, dur, start, end):
    ev = extract_event(text, LANG, anchor=ANCHOR)
    assert ev is not None, f"{text!r} produced no event"
    assert ev.summary == summary
    assert ev.recurrence == _rec(rec)
    assert ev.duration == (None if dur is None else timedelta(seconds=dur))
    assert ev.span.start == start
    assert ev.span.end == end
