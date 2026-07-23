# -*- coding: utf-8 -*-
"""Catalan *sistema de campanar* -- the traditional bell-tower clock.

Catalan runs two numerically incompatible clock systems side by side:

* the **sistema de rellotge** (modern, additive, like Spanish) --
  "les nou i quart" 09:15, "les nou i mitja" 09:30, "les deu menys quart" 09:45;
* the **sistema de campanar** (traditional, counting quarters already struck
  *toward* the named hour) -- "un quart de deu" 09:15, "dos quarts de deu"
  09:30, "tres quarts de deu" 09:45.

The named hour is the one being approached, so a campanar reading is
(hour - 1) + N*15 minutes.  "un quart de deu" is 9:15, never 10:15 -- reading
it additively would silently produce an hour-wrong time, so the two shapes are
kept strictly apart and both readings must coexist.

Sources (normative):

* Optimot / Nova gramatica (Institut d'Estudis Catalans), "Les hores en
  catala: sistema de campanar i sistema de rellotge",
  https://aplicacions.llengua.gencat.cat/llc/AppJava/index.html?action=Principal&method=detall&input_cercar=hores&numPagina=1&database=FITXES_PUB&idFont=12802&idHit=12802&tipusFont=Fitxes+de+l%27Optimot
  -- "Es un quart de nou" (8.15 h), "Son dos quarts de nou" (8.30 h),
  "Son tres quarts de nou" (8.45 h), "Son les nou" (9.00 h).
* Diputacio de Barcelona, Servei de Llengua, "Sistema tradicional o de
  campanar", https://llengua.diba.cat/sistema-tradicional-o-de-campanar
  -- "un quart de vuit", "dos quarts de vuit", "tres quarts de vuit".
* Viquipedia, "Sistema horari catala",
  https://ca.wikipedia.org/wiki/Sistema_horari_catala -- 1:15 "un quart de
  dues"; and: "quatre quarts" is not an expression, one says "una hora".
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, start, span, nomatch


def clk(h, mi, s=0):
    dt = ANCHOR.replace(hour=h, minute=mi, second=s, microsecond=0)
    if dt < ANCHOR:
        dt += timedelta(days=1)
    return ad(dt)


# -- the three quantities, across the whole 12-hour dial --------------------

@pytest.mark.parametrize("text,h,mi", [
    # un quart -> :15 of the previous hour
    ("un quart de dues", 1, 15),
    ("un quart de tres", 2, 15),
    ("un quart de quatre", 3, 15),
    ("un quart de cinc", 4, 15),
    ("un quart de sis", 5, 15),
    ("un quart de set", 6, 15),
    ("un quart de vuit", 7, 15),
    ("un quart de nou", 8, 15),
    ("un quart de deu", 9, 15),
    ("un quart de dotze", 11, 15),
    # dos quarts -> :30 of the previous hour
    ("dos quarts de dues", 1, 30),
    ("dos quarts de quatre", 3, 30),
    ("dos quarts de nou", 8, 30),
    ("dos quarts de deu", 9, 30),
    ("dos quarts de dotze", 11, 30),
    # tres quarts -> :45 of the previous hour
    ("tres quarts de dues", 1, 45),
    ("tres quarts de sis", 5, 45),
    ("tres quarts de nou", 8, 45),
    ("tres quarts de deu", 9, 45),
    ("tres quarts de dotze", 11, 45),
])
def test_campanar_quarters(text, h, mi):
    assert start(text) == clk(h, mi)
    assert span(text).width == timedelta(minutes=1)


# -- the elided "de" -> "d'" before a vowel-initial hour name ---------------
# Only "una" and "onze" begin with a vowel among the twelve hour names, so
# only those two take the apostrophe; "vuit" is consonantal (de vuit).

@pytest.mark.parametrize("text,h,mi", [
    ("un quart d'onze", 10, 15),
    ("dos quarts d'onze", 10, 30),
    ("tres quarts d'onze", 10, 45),
])
def test_campanar_elision_onze(text, h, mi):
    assert start(text) == clk(h, mi)


# -- the 1 o'clock wrap: the hour before one is spoken as twelve ------------

@pytest.mark.parametrize("text,mi", [
    ("un quart d'una", 15),
    ("dos quarts d'una", 30),
    ("tres quarts d'una", 45),
])
def test_campanar_one_oclock_wraps_to_twelve(text, mi):
    """A quarter *of one* is 12:15 -- not 00:15, and never a negative hour."""
    assert start(text) == clk(12, mi)


# -- meridiem still composes -----------------------------------------------

def test_campanar_with_meridiem():
    assert start("un quart de deu de la nit") == clk(21, 15)
    assert start("dos quarts de vuit del mati") == clk(7, 30)


# -- regression: the modern rellotge system is untouched --------------------

@pytest.mark.parametrize("text,h,mi", [
    ("les nou i quart", 9, 15),
    ("les nou i mitja", 9, 30),
    ("les deu menys quart", 9, 45),
])
def test_rellotge_unchanged(text, h, mi):
    assert start(text) == clk(h, mi)


# -- no collision: the two systems coexist and never capture each other -----

def test_both_systems_coexist_at_the_same_instant():
    """09:15 has one name in each system; each keeps its own arithmetic."""
    assert start("les nou i quart") == clk(9, 15)
    assert start("un quart de deu") == clk(9, 15)
    assert start("les nou i mitja") == clk(9, 30)
    assert start("dos quarts de deu") == clk(9, 30)
    assert start("les deu menys quart") == clk(9, 45)
    assert start("tres quarts de deu") == clk(9, 45)


def test_campanar_is_not_read_additively():
    """The trap: additive logic would make "un quart de deu" 10:15."""
    assert start("un quart de deu") != clk(10, 15)
    assert start("dos quarts de deu") != clk(10, 30)
    assert start("tres quarts de deu") != clk(10, 45)


def test_rellotge_hour_is_the_stated_hour():
    """Conversely, the rellotge hour is *not* shifted back a step."""
    assert start("les nou i quart") != clk(8, 15)


# -- out-of-range quantities refuse rather than guess -----------------------

@pytest.mark.parametrize("text", [
    "quatre quarts de deu",   # no fourth quarter -- that is "una hora"
    "zero quarts de deu",
    "cinc quarts de deu",
    "set quarts d'una",
])
def test_campanar_out_of_range_refuses(text):
    nomatch(text)
