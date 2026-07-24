# -*- coding: utf-8 -*-
"""The "nth week of a month" reading for Aragonese, "a tercer semana de marzo".

Aragonese folds its feminine ordinals to a digit like the rest of Romance, but
the construction that reads "the nth week of a month" was never declared for
the locale, so "a tercera semana de marzo" was left with only the clock reading
of its leading "a tercera" -- a nonsensical one-minute span at hour three.  The
grammar attests the construction directly: "La tercer semana de chiner no feba
que nevar" (Gramatica Basica de l'Aragonés, Academia Aragonesa de la Lengua,
2020, section 8.1.2 "Los numerals ordinals", p. 77), where the feminine article
"a" precedes an ordinal apocopated before the feminine noun.  Anchor
2018-06-05.
"""
from datetime import timedelta

import pytest

from ._corpus import span, start_end, parse, nomatch


@pytest.mark.parametrize("text,start,end", [
    ("a primera semana de marzo", (2018, 3, 5), (2018, 3, 12)),
    ("a segunda semana de marzo", (2018, 3, 12), (2018, 3, 19)),
    ("a tercer semana de marzo", (2018, 3, 19), (2018, 3, 26)),
    ("a tercera semana de marzo", (2018, 3, 19), (2018, 3, 26)),
    ("a cuatrena semana de marzo", (2018, 3, 26), (2018, 4, 2)),
    ("a segunda semana de chinero", (2018, 1, 8), (2018, 1, 15)),
])
def test_nth_week_of_month(text, start, end):
    s, e = start_end(text)
    assert (s.year, s.month, s.day) == start
    assert (e.year, e.month, e.day) == end
    assert span(text).width.days == 7
    assert parse(text)[1] == ""


@pytest.mark.parametrize("text,hour", [
    ("a las tres", 3),
    ("a tres", 3),
])
def test_bare_hour_still_a_clock(text, hour):
    """No week noun follows, so "a tres" keeps its clock reading."""
    s = span(text)
    assert s.start.hour == hour
    assert s.width == timedelta(minutes=1)


def test_weekday_is_still_a_weekday():
    s = span("martes")
    assert (s.start.year, s.start.month, s.start.day) == (2018, 6, 12)
    assert s.width == timedelta(days=1)


@pytest.mark.parametrize("text", [
    "a tercer semana de",              # dangling scope, no month
    "semana de marzo",                 # the marker alone
])
def test_garbage_never_raises(text):
    parse(text)
