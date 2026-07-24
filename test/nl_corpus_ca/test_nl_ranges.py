# -*- coding: utf-8 -*-
"""Ranges.  Dash-framed ranges parse language-agnostically; the word-framed
Romance forms ("de juny a agost", "entre ... i ...") parse too -- the "from"
lead ("de"/"des de") and "to"/"between" connectors ship per-locale, so range
framing is not English-only.  Because Catalan "a" is a hyper-common preposition
("a les tres", "anem a Barcelona"), a bare "A a B" is only trusted as a range
when a "from" lead disambiguates it -- the adversarial cases below pin that down."""
import pytest

from ._corpus import AstroDate, start_end, nomatch


@pytest.mark.parametrize("text,s,e", [
    ("juny - agost", (2017, 6, 1), (2017, 9, 1)),
    ("gener - març", (2017, 1, 1), (2017, 4, 1)),
    ("5 de juny - 12 de juny", (2018, 6, 5), (2018, 6, 13)),
])
def test_dash_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)


@pytest.mark.parametrize("text,s,e", [
    ("de juny a agost", (2017, 6, 1), (2017, 9, 1)),
    ("de juny fins a agost", (2017, 6, 1), (2017, 9, 1)),
    ("entre juny i agost", (2017, 6, 1), (2017, 9, 1)),
    ("de 5 de juny a 12 de juny", (2018, 6, 5), (2018, 6, 13)),
])
def test_word_framed_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)


# -- adversarial: the "a" trap.  "a" is also the clock preposition ("a les 3"),
# so a bare "<month> a <time>" / "a les tres" must NEVER become a bounded range;
# without a "from" lead the "a"-connector is untrusted and the normal single-span
# path runs (a minute-wide clock span), while a non-temporal endpoint is nomatch.
def test_a_trap_bare_month_plus_time_is_single_span():
    # "juny a les tres" folds month+clock into ONE minute-wide span, not a range
    ss, ee = start_end("juny a les tres")
    assert ss == AstroDate(2017, 6, 1, 3, 0) and ee == AstroDate(2017, 6, 1, 3, 1)


def test_a_trap_non_temporal_place_is_nomatch():
    nomatch("anem a Barcelona")


# -- open-ended ranges: "fins" (open start) / "des de" (open end) -----------
from ._corpus import ANCHOR, ad  # noqa: E402


def test_fins_open_start():
    s, e = start_end("fins divendres")
    assert s == ad(ANCHOR)
    assert e == AstroDate(2017, 7, 1)


def test_desde_open_end():
    s, e = start_end("des de 2010")
    assert s == AstroDate(2010, 1, 1)
    assert e == ad(ANCHOR)


# -- the shared-month range: the month named ONCE for the pair ---------------
# Naming the month once is the default written form of a date range in the
# Romance languages (RAE, Ortografia de la lengua espanola 5.2.5.1, and its
# counterparts), and the endpoint carrying only the bare day used to be thrown
# away -- the span collapsed onto the dated endpoint alone.  The bare day is
# read through its partner's own words, so both forms now agree.

@pytest.mark.parametrize("text", [
    "del 5 al 12 de juny",
    "del 5 de juny al 12 de juny",
    "de 5 a 12 de juny",
])
def test_shared_month_range_reads_both_days(text):
    ss, ee = start_end(text)
    assert ss == AstroDate(2018, 6, 5) and ee == AstroDate(2018, 6, 13)


def test_del_al_crosses_the_year():
    ss, ee = start_end("del 28 de desembre al 3 de gener")
    assert ss == AstroDate(2017, 12, 28) and ee == AstroDate(2018, 1, 4)


def test_al_without_a_from_lead_is_not_a_range():
    ss, ee = start_end("el concert és a les tres")
    assert ss == AstroDate(2017, 6, 28, 3, 0)
    assert ee == AstroDate(2017, 6, 28, 3, 1)


@pytest.mark.parametrize("text", ["del al", "del 5 al", "anem del pa al vi"])
def test_del_al_garbage_never_raises(text):
    from ._corpus import parse
    parse(text)
