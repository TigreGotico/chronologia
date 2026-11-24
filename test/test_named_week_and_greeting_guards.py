# -*- coding: utf-8 -*-
"""Readings that a fix for #1004 or #1051 must keep.

#1004: a named week ("la semana pasada") is no length, but a week with an
article and no modifier, a week after a quantifier, a week before a "this"
word, and a week after a verb spelled like "last" or before the preposition
"next to" are lengths.  #1051: "good evening" greets, but a part of the day
after the adjective "good" keeps its band.  Every row reads right on dev.
"""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_duration, extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)
GREETING_ANCHOR = datetime(2026, 9, 25, 12, 0)


@pytest.mark.parametrize("text,lang,days", [
    ("la semana", "es", 7),
    ("una semana", "es", 7),
    ("a semana", "gl", 7),
    ("a week", "en", 7),
    ("a héten", "hu", 7),
    ("the last few months", "en", 92),
    ("in the next few weeks", "en", 21),
    ("die letzten paar Wochen", "de", 14),
    ("this couple of weeks", "en", 14),
    ("a week this summer", "en", 7),
    ("a fortnight this autumn", "en", 14),
    ("un mois cet été", "fr", 30),
    ("una settimana questa estate", "it", 7),
    ("a semana desta páscoa", "pt", 7),
    ("the week this summer", "en", 7),
    ("in the next 2 weeks", "en", 14),
    ("j'ai passé la semaine à Paris", "fr", 7),
    ("he pasado la semana en Madrid", "es", 7),
    ("tinha passado a semana em Lisboa", "pt", 7),
    ("ho passato la settimana a Roma", "it", 7),
    ("he passat la setmana a Barcelona", "ca", 7),
    ("pasado a semana na praia", "gl", 7),
    ("the milk will last the week", "en", 7),
    ("we spent the week next to the lake", "en", 7),
    ("we spent the fortnight next to the beach", "en", 14),
])
def test_a_week_that_names_no_calendar_week_is_a_length(text, lang, days):
    found = extract_duration(text, lang, anchor=ANCHOR)
    assert found is not None
    assert found.duration == timedelta(days=days)


@pytest.mark.parametrize("text,start,end,remainder", [
    ("tonight", datetime(2026, 9, 25, 21), datetime(2026, 9, 26, 6), ""),
    ("this evening", datetime(2026, 9, 25, 18), datetime(2026, 9, 25, 21), ""),
    ("the weather is good tonight", datetime(2026, 9, 25, 21),
     datetime(2026, 9, 26, 6), "the weather is good"),
    ("is it good tonight", datetime(2026, 9, 25, 21),
     datetime(2026, 9, 26, 6), "is it good"),
    ("good tonight", datetime(2026, 9, 25, 21), datetime(2026, 9, 26, 6),
     "good"),
])
def test_a_part_of_the_day_after_good_keeps_its_band(text, start, end,
                                                     remainder):
    found = extract_timespan(text, "en", GREETING_ANCHOR)
    assert found.span.start.datetime() == start
    assert found.span.end.datetime() == end
    assert found.remainder == remainder
