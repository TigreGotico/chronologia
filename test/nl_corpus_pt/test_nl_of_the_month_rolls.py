# -*- coding: utf-8 -*-
"""A day, weekday or week "do mês" that has passed is next month's, pt.

A named occurrence is the next one after the anchor, and a span that ended
before the anchor names the next such span.  So "o primeiro dia do mês"
said on 17 October is 1 November.  "deste mês" names the anchor's own month
("deste" is "Contracção da preposição de com o pronome este", Priberam s.v.
"deste") and never rolls; neither does a span that still contains or
follows the anchor ("o último dia do mês" is 31 October).

Anchor Saturday 2026-10-17 12:00.  October 2026 starts on a Thursday: its
first Tuesday is the 6th, its last Friday the 30th, its third week starts
on Monday the 19th.  November 2026 starts on a Sunday: its first Tuesday is
the 3rd and its first Monday the 2nd.  Counted on the calendar by hand.
"""
from datetime import datetime

import pytest

from ._corpus import ad, parse

SATURDAY = datetime(2026, 10, 17, 12, 0)


@pytest.mark.parametrize("text,ymd", [
    ("a primeira terça-feira do mês", (2026, 11, 3)),
    ("o primeiro domingo do mês", (2026, 11, 1)),
    ("o primeiro dia do mês", (2026, 11, 1)),
    ("a primeira semana do mês", (2026, 11, 2)),
    ("a última sexta-feira do mês", (2026, 10, 30)),
    ("o último dia do mês", (2026, 10, 31)),
    ("a terceira semana do mês", (2026, 10, 19)),
])
def test_of_the_month(text, ymd):
    r = parse(text, SATURDAY)
    assert r is not None, f"{text!r} did not parse"
    assert r.span.start == ad(datetime(*ymd))
    assert r.remainder == ""


# A weekday said on that day is the anchor's day: the first Tuesday of
# October 2026 is the 6th, so at noon on Tuesday 6 October it is today.  On
# Wednesday the 7th it has passed, and November's first Tuesday is the 3rd.
# The last Friday of October 2026 is the 30th.
@pytest.mark.parametrize("text,anchor,ymd", [
    ("a primeira terça-feira do mês", datetime(2026, 10, 6, 12),
     (2026, 10, 6)),
    ("a primeira terça-feira do mês", datetime(2026, 10, 7, 12),
     (2026, 11, 3)),
    ("a última sexta-feira do mês", datetime(2026, 10, 30, 12),
     (2026, 10, 30)),
])
def test_a_weekday_said_on_that_day_is_today(text, anchor, ymd):
    r = parse(text, anchor)
    assert r is not None, f"{text!r} did not parse"
    assert r.span.start == ad(datetime(*ymd))
    assert r.remainder == ""
