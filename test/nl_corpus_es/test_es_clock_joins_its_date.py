# -*- coding: utf-8 -*-
"""A clock beside the date it names reads as one moment, es.

The quarter or half after the hour stays in the clock when "el día" or "del día"
follows, so the clock and the date compose into one moment.  Anchor
2017-06-27 13:04: the next 14 March is in 2018 and 14 June has passed, so
"dia 14" is 14 July.
"""
import pytest

from chronologia.extract import extract_recurrence

from ._corpus import ANCHOR, span


def _fields(s):
    return (s.start.year, s.start.month, s.start.day, s.start.hour, s.start.minute)


@pytest.mark.parametrize("text,gold", [
    ("a las diez y cuarto el día 14 de marzo", (2018,3,14,10,15)),
    ("a las diez y cuarto del día 14 de marzo", (2018,3,14,10,15)),
    ("a las diez el día 14 de marzo", (2018,3,14,10,0)),
    ("a las diez y media el día 14 de marzo", (2018,3,14,10,30)),
    ("el día 14 de marzo a las diez y cuarto", (2018,3,14,10,15)),
])
def test_clock_joins_the_date(text, gold):
    s = span(text)
    assert _fields(s) == gold


@pytest.mark.parametrize("text,gold", [
    ("a las diez y cuarto", (2017,6,27,22,15)),
    ("el día 14 de marzo", (2018,3,14,0,0)),
])
def test_alone_keeps_its_reading(text, gold):
    assert _fields(span(text)) == gold


@pytest.mark.parametrize("text,rule", [("a las ocho de todos los días", "FREQ=DAILY;BYHOUR=8"), ("a las diez de cada sábado", "FREQ=WEEKLY;BYDAY=SA;BYHOUR=10")])
def test_recurrence_takes_the_de_after_its_clock(text, rule):
    r = extract_recurrence(text, "es", ANCHOR)
    assert (r.recurrence.to_string(), r.remainder) == (rule, "")


@pytest.mark.parametrize("text,rule,remainder", [
    ("a las diez de cada sábado por favor", "FREQ=WEEKLY;BYDAY=SA;BYHOUR=10", "por favor"),
])
def test_recurrence_de_leaves_the_words_after_it(text, rule, remainder):
    r = extract_recurrence(text, "es", ANCHOR)
    assert (r.recurrence.to_string(), r.remainder) == (rule, remainder)
