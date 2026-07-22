# -*- coding: utf-8 -*-
"""One utterance -> a full :class:`~chronologia.events.Event`, in Spanish."""
from datetime import datetime, timedelta

import pytest

from chronologia import AstroDate
from chronologia.events import extract_event
from chronologia.recurrence import HolidayRecurrence, parse_rrule

LANG = "es"
ANCHOR = datetime(2026, 7, 22, 12, 0)   # a Wednesday


def _rec(x):
    return None if x is None else (x if isinstance(x, HolidayRecurrence)
                                   else parse_rrule(x))


_CASES = [
    ("mi reunión cada miércoles a las 9 por 30 minutos",
     "mi reunión", "FREQ=WEEKLY;BYDAY=WE;BYHOUR=9", 1800,
     AstroDate(2026, 7, 22, 9, 0), AstroDate(2026, 7, 22, 9, 30)),
    ("pagar alquiler el 1 de cada mes",
     "pagar alquiler", "FREQ=MONTHLY;BYMONTHDAY=1", None,
     AstroDate(2026, 8, 1), AstroDate(2026, 8, 2)),
    ("cena de navidad cada navidad",
     "cena de navidad", "FREQ=YEARLY;BYMONTH=12;BYMONTHDAY=25", None,
     AstroDate(2026, 12, 25), AstroDate(2026, 12, 26)),
    ("yoga cada pascua",
     "yoga", HolidayRecurrence("easter"), None,
     AstroDate(2027, 3, 28), AstroDate(2027, 3, 29)),
    ("almuerzo el 5 de junio",
     "almuerzo", None, None,
     AstroDate(2027, 6, 5), AstroDate(2027, 6, 6)),
    ("cita el viernes a las 15",
     "cita", None, None,
     AstroDate(2026, 7, 24, 15, 0), AstroDate(2026, 7, 24, 15, 1)),
    ("cumpleaños el 25 de diciembre",
     "cumpleaños", None, None,
     AstroDate(2026, 12, 25), AstroDate(2026, 12, 26)),
    ("sincronización cada miércoles a las 9",
     "sincronización", "FREQ=WEEKLY;BYDAY=WE;BYHOUR=9", None,
     AstroDate(2026, 7, 22, 9, 0), AstroDate(2026, 7, 22, 10, 0)),
    ("llamar a mamá cada domingo",
     "llamar a mamá", "FREQ=WEEKLY;BYDAY=SU", None,
     AstroDate(2026, 7, 26), AstroDate(2026, 7, 27)),
    ("desayuno todos los días a las 8",
     "desayuno", "FREQ=DAILY;BYHOUR=8", None,
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
