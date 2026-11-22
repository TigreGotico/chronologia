# -*- coding: utf-8 -*-
"""A clock beside the date it names reads as one moment, pt.

The quarter or half after the hour stays in the clock when "no dia" or "do dia"
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
    ("às dez e quarto no dia 14 de março", (2018,3,14,10,15)),
    ("às dez e quarto do dia 14 de março", (2018,3,14,10,15)),
    ("às dez no dia 14 de março", (2018,3,14,10,0)),
    ("às dez e meia no dia 14", (2017,7,14,10,30)),
    ("às 10h15 no dia 14 de março", (2018,3,14,10,15)),
    ("no dia 14 de março às dez e quarto", (2018,3,14,10,15)),
])
def test_clock_joins_the_date(text, gold):
    s = span(text)
    assert _fields(s) == gold


@pytest.mark.parametrize("text,gold", [
    ("às dez e quarto", (2017,6,27,22,15)),
    ("dez e quarto", (2017,6,27,22,15)),
    ("no dia 14 de março", (2018,3,14,0,0)),
])
def test_alone_keeps_its_reading(text, gold):
    assert _fields(span(text)) == gold


@pytest.mark.parametrize("text,gold", [
    ("às dez e quarto no décimo quarto dia de março", (3, 14, 10, 15)),
    ("às dez no décimo quarto dia de março", (3, 14, 10, 0)),
])
def test_ordinal_day_takes_the_clock(text, gold):
    s = span(text)
    assert (s.start.month, s.start.day, s.start.hour, s.start.minute) == gold


@pytest.mark.parametrize("text,gold", [
    ("às dez horas de sábado", (2017, 7, 1, 10, 0)),
    ("às dez horas do sábado", (2017, 7, 1, 10, 0)),
    ("às 10 horas de sábado", (2017, 7, 1, 10, 0)),
    ("às 21 horas de sexta-feira", (2017, 6, 30, 21, 0)),
    ("às oito horas de domingo", (2017, 7, 2, 8, 0)),
    ("lembra-me de ligar ao João às dez horas de sábado", (2017, 7, 1, 10, 0)),
])
def test_clock_with_horas_keeps_the_day_after_de(text, gold):
    assert _fields(span(text)) == gold


@pytest.mark.parametrize("text,rule", [
    ("às dez de cada sábado", "FREQ=WEEKLY;BYDAY=SA;BYHOUR=10"),
    ("às dez de todos os sábados", "FREQ=WEEKLY;BYDAY=SA;BYHOUR=10"),
    ("às oito e meia de todos os dias", "FREQ=DAILY;BYHOUR=8;BYMINUTE=30"),
    ("às dez e meia do dia 15 de cada mês", "FREQ=MONTHLY;BYMONTHDAY=15;BYHOUR=10;BYMINUTE=30"),
])
def test_recurrence_takes_the_de_after_its_clock(text, rule):
    r = extract_recurrence(text, "pt", ANCHOR)
    assert (r.recurrence.to_string(), r.remainder) == (rule, "")
