# -*- coding: utf-8 -*-
"""Two Portuguese words that read as a date inside a sentence about
something else.

"segunda", "quarta", "quinta" and "sexta" are weekday names and also the
feminine ordinals, so "a segunda dose da vacina" and "pela segunda vez" name
no day.  "faz" counts back like "há" ("faz dois dias") at the start of a
clause, but after a subject it is the verb "to turn" ("a minha filha faz dez
anos"), which names an age.

Gold values are hand arithmetic from the anchor, Tuesday 2017-06-27 13:04:
the coming Monday is 2017-07-03, the coming Wednesday 2017-06-28, and two
days back is 2017-06-25 13:04.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ad, nomatch, start, start_end


@pytest.mark.parametrize("text", [
    "a segunda dose da vacina",
    "a segunda opção",
    "pela segunda vez",
    "a quarta vez que ele chegou atrasado",
    "a sexta sinfonia de Beethoven",
    "a quinta edição do festival",
    "a segunda opinião do médico",
    "a minha filha faz dez anos",
    "o meu filho faz oito anos",
    "a Maria faz trinta anos",
])
def test_sentence_without_a_date_gives_none(text):
    nomatch(text)


@pytest.mark.parametrize("text,day", [
    ("na segunda", datetime(2017, 7, 3)),
    ("na quarta", datetime(2017, 6, 28)),
    ("vemo-nos na segunda", datetime(2017, 7, 3)),
    ("na sexta", datetime(2017, 6, 30)),
    ("segunda-feira", datetime(2017, 7, 3)),
])
def test_weekday_reading_survives(text, day):
    assert start_end(text) == (ad(day), ad(day + timedelta(days=1)))


@pytest.mark.parametrize("text", [
    "faz dois dias",
    "já faz dois dias",
    "faz dois dias que não o vejo",
])
def test_clause_initial_faz_counts_back(text):
    assert start_end(text) == (ad(datetime(2017, 6, 25, 13, 4)),
                               ad(datetime(2017, 6, 26, 13, 4)))


def test_faz_dois_anos_counts_back():
    assert start("faz dois anos") == ad(datetime(2015, 6, 27, 13, 4))


@pytest.mark.parametrize("text,begin", [
    ("eu o vi faz dois dias", datetime(2017, 6, 25, 13, 4)),
    ("cheguei faz três dias", datetime(2017, 6, 24, 13, 4)),
    ("isso aconteceu faz uma semana", datetime(2017, 6, 20, 13, 4)),
    ("ele saiu faz dez dias", datetime(2017, 6, 17, 13, 4)),
    ("ele trabalha cá faz dois meses", datetime(2017, 4, 27, 13, 4)),
    ("e faz dois dias que não como", datetime(2017, 6, 25, 13, 4)),
    ("mas faz três dias que chove", datetime(2017, 6, 24, 13, 4)),
])
def test_faz_after_a_verb_counts_back_unless_the_unit_is_years(text, begin):
    assert start(text) == ad(begin)


@pytest.mark.parametrize("text,begin", [
    ("sexta, visita ao médico", datetime(2017, 6, 30)),
    ("segunda, entrada no novo emprego", datetime(2017, 7, 3)),
    ("segunda, aula de piano às 9", datetime(2017, 7, 3)),
    ("quinta, sessão de cinema às 21h", datetime(2017, 6, 29)),
])
def test_weekday_opening_a_calendar_note_is_a_weekday(text, begin):
    # The day is the contract here.  The trailing clock time is a separate
    # matter that these rows do not assert.
    assert (start(text).year, start(text).month, start(text).day) == (
        begin.year, begin.month, begin.day)
