# -*- coding: utf-8 -*-
"""Portuguese "faz" as the verb "fazer" with the weather or an age.

"faz N <unit>" counts back like "há" ("faz dois dias que não como").
Impersonal "fazer" also names the weather (Priberam s.v. "fazer", 26:
"Haver determinada condição atmosférica"), so "faz um dia lindo" names no
date.  "fazer" with a subject names an age (Priberam s.v. "fazer", 13:
"Atingir determinado tempo ou determinada quantidade"), so "o bebé faz dois
meses" names no date either; a bare length is not a date.  After a verb, an
object or a place, or before "que", the count still counts back.

Gold values are hand arithmetic from the anchor, Tuesday 2017-06-27 13:04:
today is 2017-06-27, tomorrow 2017-06-28; one day back is 2017-06-26 13:04,
one week back 2017-06-20 13:04, one month back 2017-05-27 13:04, two
months back 2017-04-27 13:04 and three months back 2017-03-27 13:04.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ad, nomatch, parse, start, start_end

#: Saturday 2026-10-17 12:00, the anchor of the ovos-date-parser pt grid.
SATURDAY = datetime(2026, 10, 17, 12, 0)


@pytest.mark.parametrize("anchor", [datetime(2017, 6, 27, 13, 4), SATURDAY])
@pytest.mark.parametrize("text", [
    "faz um dia lindo",
    "faz um dia bonito",
    "faz um dia quente",
    "faz um dia frio",
    "faz um dia chuvoso",
    "faz um dia soalheiro",
    "faz um dia nublado",
    "faz um dia de sol",
    "faz um dia de chuva",
    "o bebé faz dois meses",
    "o bebê faz dois meses",
    "a bebé faz três meses",
    "ela faz seis meses",
    "ele faz dois meses",
    "o meu filho faz onze meses",
    "a minha filha faz dez meses",
    "este bebé faz dois meses",
    "esta gata faz três meses",
    "está ótimo. o bebé faz dois meses",
])
def test_weather_or_age_names_no_date(text, anchor):
    nomatch(text, anchor)


@pytest.mark.parametrize("text,day,rest", [
    ("faz um dia bonito hoje", datetime(2017, 6, 27), "faz um dia bonito"),
    ("hoje faz um dia de sol", datetime(2017, 6, 27), "faz um dia de sol"),
    ("o bebé faz dois meses amanhã", datetime(2017, 6, 28),
     "o bebé faz dois meses"),
])
def test_the_day_word_gives_the_date(text, day, rest):
    assert start_end(text) == (ad(day), ad(day + timedelta(days=1)))
    assert parse(text).remainder == rest


def test_weather_on_the_grid_anchor_is_that_saturday():
    assert start_end("faz um dia bonito hoje", SATURDAY) == (
        ad(datetime(2026, 10, 17)), ad(datetime(2026, 10, 18)))


@pytest.mark.parametrize("text,begin", [
    ("faz um dia", datetime(2017, 6, 26, 13, 4)),
    ("faz um dia que não como", datetime(2017, 6, 26, 13, 4)),
    ("faz um dia inteiro que não como", datetime(2017, 6, 26, 13, 4)),
    ("faz um dia desde que ela partiu", datetime(2017, 6, 26, 13, 4)),
    ("faz um dia sem dormir", datetime(2017, 6, 26, 13, 4)),
    ("faz um dia ela partiu", datetime(2017, 6, 26, 13, 4)),
    ("faz um dia hoje", datetime(2017, 6, 26, 13, 4)),
    ("faz um dia de viagem", datetime(2017, 6, 26, 13, 4)),
    ("isso foi faz uma semana", datetime(2017, 6, 20, 13, 4)),
    ("isso foi faz um mês", datetime(2017, 5, 27, 13, 4)),
    ("o bebé nasceu faz dois meses", datetime(2017, 4, 27, 13, 4)),
    ("ele trabalha cá faz dois meses", datetime(2017, 4, 27, 13, 4)),
    ("comprei o carro faz dois meses", datetime(2017, 4, 27, 13, 4)),
    ("vendi a casa faz dois meses", datetime(2017, 4, 27, 13, 4)),
    ("eu a vi faz dois meses", datetime(2017, 4, 27, 13, 4)),
    ("fui a Lisboa faz dois meses", datetime(2017, 4, 27, 13, 4)),
    ("conheci a minha mulher faz três meses", datetime(2017, 3, 27, 13, 4)),
    ("a minha mãe faz dois meses que está internada",
     datetime(2017, 4, 27, 13, 4)),
    ("ela faz dois meses que não me liga", datetime(2017, 4, 27, 13, 4)),
])
def test_elapsed_time_still_counts_back(text, begin):
    assert start(text) == ad(begin)
