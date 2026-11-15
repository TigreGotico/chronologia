# -*- coding: utf-8 -*-
"""A written date beside a count and a weekday keeps the count, es.

Anchor Saturday 2026-10-17 12:00: "dentro de una semana el viernes" is
Friday 23 October, the Friday of the week one week on.  A written date
("30 de octubre") outranks the count, so the count stays in the remainder.
"""
from datetime import datetime

from chronologia import extract_timespan

from ._corpus import ad

SATURDAY = datetime(2026, 10, 17, 12, 0)


def test_a_count_with_a_weekday():
    r = extract_timespan("dentro de una semana el viernes", "es", SATURDAY)
    assert r is not None
    assert r.span.start == ad(datetime(2026, 10, 23))
    assert r.remainder == ""


def test_a_written_date_keeps_the_count():
    r = extract_timespan("el viernes dentro de una semana, 30 de octubre",
                         "es", SATURDAY)
    assert r is not None
    assert (r.span.start, r.span.end) == (ad(datetime(2026, 10, 30)),
                                          ad(datetime(2026, 10, 31)))
    assert r.remainder == "dentro de una semana"
