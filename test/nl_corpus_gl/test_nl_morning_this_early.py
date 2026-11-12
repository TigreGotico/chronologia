# -*- coding: utf-8 -*-
"""This morning with the contracted demonstrative, and "cedo" after a day, gl.

RAG s.v. "neste": "Contracción da preposición en co demostrativo este, esta,
estes, estas", so "nesta mañá" is "esta mañá".  RAG s.v. "cedo", 1: "Ao
principio do día, nas primeiras horas do día. [...] Volveron do mar pola mañá
cedo", so "mañá cedo" is the morning of tomorrow.  Without a day word "cedo"
is "early" and names no date.  Anchor 2017-06-27 13:04, a Tuesday; the gl
morning band is [06:00, 12:00) (CLDR 47, locale gl).
"""
import pytest

from ._corpus import parse, start_end, nomatch, AstroDate


@pytest.mark.parametrize("text,day", [
    ("nesta mañá", 27),
    ("esta mañá", 27),
    ("mañá cedo", 28),
    ("hoxe cedo", 27),
    ("mañá pola mañá cedo", 28),
])
def test_the_morning_band(text, day):
    s, e = start_end(text)
    assert (s, e) == (AstroDate(2017, 6, day, 6), AstroDate(2017, 6, day, 12))
    assert parse(text)[1] == ""


@pytest.mark.parametrize("text", ["cedo", "chegou cedo", "érguome moi cedo"])
def test_cedo_without_a_day_names_no_date(text):
    nomatch(text)


def test_neste_before_a_weekday_reads_forward():
    """Said on Tuesday 27 June, "neste luns" is the next Monday, 3 July, as
    the bare "luns" reads; never the Monday that has gone."""
    s, e = start_end("neste luns")
    assert (s, e) == (AstroDate(2017, 7, 3), AstroDate(2017, 7, 4))


@pytest.mark.parametrize("text,start,end", [
    ("nesta semana", (2017, 6, 26), (2017, 7, 3)),
    ("neste mes", (2017, 6, 1), (2017, 7, 1)),
])
def test_neste_before_a_period_is_this_period(text, start, end):
    """gl weeks start on Monday, so the anchor's week is 26 June to 3 July."""
    assert start_end(text) == (AstroDate(*start), AstroDate(*end))
