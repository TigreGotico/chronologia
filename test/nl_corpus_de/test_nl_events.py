# -*- coding: utf-8 -*-
"""One utterance -> a full :class:`~chronologia.events.Event`, in German."""
from datetime import datetime, timedelta

import pytest

from chronologia import AstroDate
from chronologia.events import extract_event
from chronologia.recurrence import HolidayRecurrence, parse_rrule

LANG = "de"
ANCHOR = datetime(2026, 7, 22, 12, 0)   # a Wednesday


def _rec(x):
    return None if x is None else (x if isinstance(x, HolidayRecurrence)
                                   else parse_rrule(x))


_CASES = [
    ("mein meeting jeden mittwoch um 9 für 30 minuten",
     "mein meeting", "FREQ=WEEKLY;BYDAY=WE;BYHOUR=9", 1800,
     AstroDate(2026, 7, 22, 9, 0), AstroDate(2026, 7, 22, 9, 30)),
    ("miete zahlen am 1. jeden monat",
     "miete zahlen", "FREQ=MONTHLY;BYMONTHDAY=1", None,
     AstroDate(2026, 8, 1), AstroDate(2026, 8, 2)),
    ("weihnachtsessen jedes weihnachten",
     "weihnachtsessen", "FREQ=YEARLY;BYMONTH=12;BYMONTHDAY=25", None,
     AstroDate(2026, 12, 25), AstroDate(2026, 12, 26)),
    ("yoga jedes ostern",
     "yoga", HolidayRecurrence("easter"), None,
     AstroDate(2027, 3, 28), AstroDate(2027, 3, 29)),
    ("mittagessen am 5. juni",
     "mittagessen", None, None,
     AstroDate(2027, 6, 5), AstroDate(2027, 6, 6)),
    ("termin am freitag um 15",
     "termin", None, None,
     AstroDate(2026, 7, 24, 15, 0), AstroDate(2026, 7, 24, 15, 1)),
    ("geburtstag am 25. dezember",
     "geburtstag", None, None,
     AstroDate(2026, 12, 25), AstroDate(2026, 12, 26)),
    ("sync jeden mittwoch um 9",
     "sync", "FREQ=WEEKLY;BYDAY=WE;BYHOUR=9", None,
     AstroDate(2026, 7, 22, 9, 0), AstroDate(2026, 7, 22, 10, 0)),
    ("mama anrufen jeden sonntag",
     "mama anrufen", "FREQ=WEEKLY;BYDAY=SU", None,
     AstroDate(2026, 7, 26), AstroDate(2026, 7, 27)),
    ("frühstück täglich um 8",
     "frühstück", "FREQ=DAILY;BYHOUR=8", None,
     AstroDate(2026, 7, 22, 8, 0), AstroDate(2026, 7, 22, 9, 0)),
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
