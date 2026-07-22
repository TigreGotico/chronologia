# -*- coding: utf-8 -*-
"""One utterance -> a full :class:`~chronologia.events.Event`, in Portuguese."""
from datetime import datetime, timedelta

import pytest

from chronologia import AstroDate
from chronologia.events import extract_event
from chronologia.recurrence import HolidayRecurrence, parse_rrule

LANG = "pt"
ANCHOR = datetime(2026, 7, 22, 12, 0)   # a Wednesday


def _rec(x):
    return None if x is None else (x if isinstance(x, HolidayRecurrence)
                                   else parse_rrule(x))


_CASES = [
    ("minha reunião toda quarta às 9 por 30 minutos",
     "minha reunião", "FREQ=WEEKLY;BYDAY=WE;BYHOUR=9", 1800,
     AstroDate(2026, 7, 22, 9, 0), AstroDate(2026, 7, 22, 9, 30)),
    ("pagar aluguel todos os meses no dia 1",
     "pagar aluguel", "FREQ=MONTHLY;BYMONTHDAY=1", None,
     AstroDate(2026, 8, 1), AstroDate(2026, 8, 2)),
    ("jantar de natal todo natal",
     "jantar de natal", "FREQ=YEARLY;BYMONTH=12;BYMONTHDAY=25", None,
     AstroDate(2026, 12, 25), AstroDate(2026, 12, 26)),
    ("ioga toda páscoa",
     "ioga", HolidayRecurrence("easter"), None,
     AstroDate(2027, 3, 28), AstroDate(2027, 3, 29)),
    ("consulta na sexta-feira às 15",
     "consulta", None, None,
     AstroDate(2026, 7, 24, 15, 0), AstroDate(2026, 7, 24, 15, 1)),
    ("aniversário em 25 de dezembro",
     "aniversário", None, None,
     AstroDate(2026, 12, 25), AstroDate(2026, 12, 26)),
    ("sincronização toda quarta às 9",
     "sincronização", "FREQ=WEEKLY;BYDAY=WE;BYHOUR=9", None,
     AstroDate(2026, 7, 22, 9, 0), AstroDate(2026, 7, 22, 10, 0)),
    ("ligar para mãe todo domingo",
     "ligar para mãe", "FREQ=WEEKLY;BYDAY=SU", None,
     AstroDate(2026, 7, 26), AstroDate(2026, 7, 27)),
    ("café da manhã todos os dias às 8",
     "café da manhã", "FREQ=DAILY;BYHOUR=8", None,
     AstroDate(2026, 7, 22, 8, 0), AstroDate(2026, 7, 22, 9, 0)),
    ("festa em 5 de junho",
     "festa", None, None,
     AstroDate(2027, 6, 5), AstroDate(2027, 6, 6)),
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
