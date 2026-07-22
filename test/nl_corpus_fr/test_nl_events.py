# -*- coding: utf-8 -*-
"""One utterance -> a full :class:`~chronologia.events.Event`, in French."""
from datetime import datetime, timedelta

import pytest

from chronologia import AstroDate
from chronologia.events import extract_event
from chronologia.recurrence import HolidayRecurrence, parse_rrule

LANG = "fr"
ANCHOR = datetime(2026, 7, 22, 12, 0)   # a Wednesday


def _rec(x):
    return None if x is None else (x if isinstance(x, HolidayRecurrence)
                                   else parse_rrule(x))


_CASES = [
    ("ma réunion chaque mercredi à 9h pendant 30 minutes",
     "ma réunion", "FREQ=WEEKLY;BYDAY=WE;BYHOUR=9", 1800,
     AstroDate(2026, 7, 22, 9, 0), AstroDate(2026, 7, 22, 9, 30)),
    ("payer le loyer le 1 de chaque mois",
     "payer le loyer", "FREQ=MONTHLY;BYMONTHDAY=1", None,
     AstroDate(2026, 8, 1), AstroDate(2026, 8, 2)),
    ("dîner de noël chaque noël",
     "dîner de noël", "FREQ=YEARLY;BYMONTH=12;BYMONTHDAY=25", None,
     AstroDate(2026, 12, 25), AstroDate(2026, 12, 26)),
    ("yoga chaque pâques",
     "yoga", HolidayRecurrence("easter"), None,
     AstroDate(2027, 3, 28), AstroDate(2027, 3, 29)),
    ("déjeuner le 5 juin",
     "déjeuner", None, None,
     AstroDate(2027, 6, 5), AstroDate(2027, 6, 6)),
    ("anniversaire le 25 décembre",
     "anniversaire", None, None,
     AstroDate(2026, 12, 25), AstroDate(2026, 12, 26)),
    ("sync chaque mercredi à 9h",
     "sync", "FREQ=WEEKLY;BYDAY=WE;BYHOUR=9", None,
     AstroDate(2026, 7, 22, 9, 0), AstroDate(2026, 7, 22, 10, 0)),
    ("appeler maman chaque dimanche",
     "appeler maman", "FREQ=WEEKLY;BYDAY=SU", None,
     AstroDate(2026, 7, 26), AstroDate(2026, 7, 27)),
    ("petit déjeuner tous les jours à 8h",
     "petit déjeuner", "FREQ=DAILY;BYHOUR=8", None,
     AstroDate(2026, 7, 22, 8, 0), AstroDate(2026, 7, 22, 9, 0)),
    ("réunion chaque vendredi à 17h",
     "réunion", "FREQ=WEEKLY;BYDAY=FR;BYHOUR=17", None,
     AstroDate(2026, 7, 24, 17, 0), AstroDate(2026, 7, 24, 18, 0)),
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
