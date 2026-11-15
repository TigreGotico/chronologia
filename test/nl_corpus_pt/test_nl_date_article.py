# -*- coding: utf-8 -*-
"""The article that opens a date belongs to the date, pt.

"no sábado" and "na segunda" (em + o / em + a) name one coming day, and the
contraction carries the article of that day noun; leaving "no" in the
remainder strands half of the date expression (Svobodová, "Variabilidade
semântica e sintática dos nomes dos dias da semana", Acta Universitatis
Carolinae -- Philologica 3, Romanistica Pragensia, 2016, p. 25: "trabalhar
na sexta-feira" is singular).  The habitual "ao sábado" is in
test_nl_habitual_weekday.py.  Anchor 2017-06-27, a terça, 13:04; dates by hand.
"""
import pytest

from ._corpus import parse, start_end, AstroDate


@pytest.mark.parametrize("text,ymd,rest", [
    ("no sábado", (2017, 7, 1), ""),
    ("na segunda", (2017, 7, 3), ""),
    ("na sexta", (2017, 6, 30), ""),
    ("no domingo", (2017, 7, 2), ""),
    ("no dia 25 de dezembro", (2017, 12, 25), ""),
    ("na segunda-feira, 3 de julho", (2017, 7, 3), ""),
    ("no sábado o bebé faz um ano", (2017, 7, 1), "o bebé faz um ano"),
])
def test_contracted_article_is_part_of_the_date(text, ymd, rest):
    s, e = start_end(text)
    assert s == AstroDate(*ymd)
    assert (e - s).days == 1
    assert parse(text)[1] == rest
