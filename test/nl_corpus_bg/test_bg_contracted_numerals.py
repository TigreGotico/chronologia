# -*- coding: utf-8 -*-
"""Bulgarian's contracted everyday numerals, the register people speak in.

Every teen and the tens 20/30/60 carry two current spellings: the formal
"единадесет"/"двадесет" and the contracted "единайсет"/"двайсет".  Both are
attested cardinal lemmas on en.wiktionary.org -- единайсет and дванайсет are
labelled "colloquial but standard", тринайсет..деветнайсет and двайсет/трийсет
are contractions of their formal spellings, шейсет is the alternative form of
шестдесет -- and the contracted one is what the Wikibooks *Bulgarian/Time*
clock lesson writes ("Единайсет и половина = Half past eleven = 11:30").

Golds are computed by hand from the anchor, Tuesday 2017-06-27 13:04: an hour
already gone by rolls to the next morning, an hour still to come stays on the
anchor day.  Each contracted reading is pinned against an absolute literal
first, then against its formal twin, so the pair can never agree on a wrong
answer.
"""
from datetime import timedelta

import pytest

from chronologia.astrodate import AstroDate
from chronologia.extract import extract_duration

from ._corpus import parse

LANG = "bg"


@pytest.mark.parametrize("text,expect", [
    # hours 11 and 12 have passed at 13:04, so they land on the 28th
    ("единайсет часа", AstroDate(2017, 6, 28, 11, 0, 0, 0)),
    ("дванайсет часа", AstroDate(2017, 6, 28, 12, 0, 0, 0)),
    ("тринайсет часа", AstroDate(2017, 6, 28, 13, 0, 0, 0)),
    # 14:00 onward are still ahead of 13:04 and stay on the 27th
    ("четиринайсет часа", AstroDate(2017, 6, 27, 14, 0, 0, 0)),
    ("петнайсет часа", AstroDate(2017, 6, 27, 15, 0, 0, 0)),
    ("шестнайсет часа", AstroDate(2017, 6, 27, 16, 0, 0, 0)),
    ("седемнайсет часа", AstroDate(2017, 6, 27, 17, 0, 0, 0)),
    ("осемнайсет часа", AstroDate(2017, 6, 27, 18, 0, 0, 0)),
    ("деветнайсет часа", AstroDate(2017, 6, 27, 19, 0, 0, 0)),
    ("двайсет часа", AstroDate(2017, 6, 27, 20, 0, 0, 0)),
])
def test_contracted_hour_reads_its_clock_time(text, expect):
    r = parse(text)
    assert r is not None, f"{text!r} did not parse"
    assert r.span.start == expect
    assert r.span.width == timedelta(minutes=1)
    assert r.remainder == ""


@pytest.mark.parametrize("contracted,formal", [
    ("единайсет часа", "единадесет часа"),
    ("дванайсет часа", "дванадесет часа"),
    ("петнайсет часа", "петнадесет часа"),
    ("двайсет часа", "двадесет часа"),
])
def test_contracted_hour_matches_its_formal_spelling(contracted, formal):
    assert parse(contracted).span == parse(formal).span


@pytest.mark.parametrize("text,expect", [
    ("единайсет и половина", AstroDate(2017, 6, 28, 11, 30, 0, 0)),
    ("дванайсет и половина", AstroDate(2017, 6, 28, 12, 30, 0, 0)),
    ("петнайсет и половина", AstroDate(2017, 6, 27, 15, 30, 0, 0)),
])
def test_contracted_hour_takes_the_additive_half(text, expect):
    # The additive "и половина" the clock is built from must survive the
    # contracted hour word: "и" stays a joiner only before another numeral.
    r = parse(text)
    assert r is not None, f"{text!r} did not parse"
    assert r.span.start == expect
    assert r.remainder == ""


def test_contracted_tens_compose_a_compound_with_the_joiner():
    # 20 + 3 == 23; the compound folds through the internal "и" exactly as the
    # formal "двадесет и три часа" does, rather than reading a bare 3.
    r = parse("двайсет и три часа")
    assert r is not None
    assert r.span.start == AstroDate(2017, 6, 27, 23, 0, 0, 0)
    assert r.remainder == ""
    assert r.span == parse("двадесет и три часа").span


def test_contracted_compound_then_the_additive_half():
    r = parse("двайсет и три и половина")
    assert r is not None
    assert r.span.start == AstroDate(2017, 6, 27, 23, 30, 0, 0)
    assert r.remainder == ""


@pytest.mark.parametrize("text,seconds", [
    ("двайсет и пет минути", 25 * 60),
    ("трийсет минути", 30 * 60),
    ("шейсет минути", 60 * 60),
    ("петнайсет минути", 15 * 60),
])
def test_contracted_numerals_measure_a_duration(text, seconds):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got.duration == timedelta(seconds=seconds)
    assert got.remainder == ""
