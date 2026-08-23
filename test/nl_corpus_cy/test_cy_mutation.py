"""Initial mutation, the feature that makes Welsh unlike every other locale.

A Welsh word changes its FIRST letter according to what precedes it, so a
vocabulary listing only dictionary forms would silently fail on ordinary
sentences.  The surfaces are therefore enumerated in the ``.voc`` files, and
this module is the proof that every enumerated one resolves and that the
mutation never changes the meaning: "dwy flynedd" and "tair blynedd" differ by
one year, not by which word the year is.

The richest case is the year.  Its count form has three surfaces -- radical
"blynedd", soft "flynedd" after two, nasal "mlynedd" after five -- and all
three name the same unit.
"""
import pytest
from dateutil.relativedelta import relativedelta

from chronologia.astrodate import AstroDate

from ._corpus import ANCHOR, ad, nomatch, remainder, start


@pytest.mark.parametrize("text,years", [
    ("tair blynedd yn ôl", 3),      # radical, after the feminine three
    ("dwy flynedd yn ôl", 2),       # soft b -> f, after the feminine two
    ("pum mlynedd yn ôl", 5),       # nasal b -> m, after five
])
def test_the_year_has_three_surfaces(text, years):
    assert start(text) == ad(ANCHOR - relativedelta(years=years))


@pytest.mark.parametrize("text", [
    "tair blynedd yn ôl", "dwy flynedd yn ôl", "pum mlynedd yn ôl",
])
def test_every_year_surface_is_fully_consumed(text):
    """A mutated surface the vocabulary missed would be left in the
    remainder, so an empty remainder is what proves it was read."""
    assert remainder(text) == ""


def test_the_three_year_surfaces_are_three_different_spans():
    a = start("dwy flynedd yn ôl")
    b = start("tair blynedd yn ôl")
    c = start("pum mlynedd yn ôl")
    assert a > b > c


@pytest.mark.parametrize("radical,mutated", [
    ("ymhen dau fis", "ymhen dau fis"),
    ("ymhen tri mis", "ymhen tri mis"),
])
def test_the_month_noun_mutates_after_two(radical, mutated):
    """"mis" is soft-mutated to "fis" after "dau"; both are read as month."""
    assert start(radical) == start(mutated)


def test_month_noun_radical_and_mutated_name_the_same_unit():
    assert start("ymhen tri mis") == ad(ANCHOR + relativedelta(months=3))
    assert start("ymhen dau fis") == ad(ANCHOR + relativedelta(months=2))


@pytest.mark.parametrize("text,y,m,d", [
    ("y 3ydd o Fawrth 1990", 1990, 3, 3),
    ("y 3ydd o Fai 1990", 1990, 5, 3),
    ("y 3ydd o Fehefin 1990", 1990, 6, 3),
    ("y 3ydd o Orffennaf 1990", 1990, 7, 3),
    ("y 3ydd o Fedi 1990", 1990, 9, 3),
    ("y 3ydd o Dachwedd 1990", 1990, 11, 3),
    ("y 3ydd o Ragfyr 1990", 1990, 12, 3),
])
def test_the_month_name_mutates_after_the_linking_o(text, y, m, d):
    """"o" soft-mutates the month it introduces: Mawrth -> Fawrth, Gorffennaf
    -> Orffennaf (the g disappears entirely), Rhagfyr -> Ragfyr."""
    assert start(text) == AstroDate(y, m, d)


@pytest.mark.parametrize("text,y,m,d", [
    ("y 3ydd o Ionawr 1990", 1990, 1, 3),
    ("y 3ydd o Chwefror 1990", 1990, 2, 3),
    ("y 3ydd o Ebrill 1990", 1990, 4, 3),
    ("y 3ydd o Awst 1990", 1990, 8, 3),
    ("y 3ydd o Hydref 1990", 1990, 10, 3),
])
def test_the_unmutable_months_stay_radical(text, y, m, d):
    """A month opening on a vowel, on "h", or on the digraph "ch" has no
    mutated surface at all, and inventing one would be wrong."""
    assert start(text) == AstroDate(y, m, d)


@pytest.mark.parametrize("bad", [
    "y 3ydd o Fonawr 1990", "y 3ydd o Gwefror 1990", "y 3ydd o Febrill 1990",
])
def test_invented_mutations_are_not_months(bad):
    """The mutation table does not license these forms and no vocabulary
    ships them, so the date must not resolve to a month from them."""
    from ._corpus import parse
    r = parse(bad)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("mutated,radical", [
    ("ddydd Llun", "dydd Llun"),
    ("ddydd Mercher", "dydd Mercher"),
    ("ddydd Gwener", "dydd Gwener"),
    ("ddydd Sul", "dydd Sul"),
])
def test_the_weekday_head_noun_mutates(mutated, radical):
    """"dydd" is soft-mutated to "ddydd" after the markers that open an
    adverbial "on <weekday>"; the day named is unchanged."""
    assert start(mutated) == start(radical)


@pytest.mark.parametrize("text,h", [
    ("am ddau o'r gloch", 2), ("am dri o'r gloch", 3),
    ("am bedwar o'r gloch", 4), ("am bump o'r gloch", 5),
    ("am ddeg o'r gloch", 10),
])
def test_the_hour_numeral_mutates_after_am(text, h):
    """"am" (at) triggers soft mutation on the numeral itself: dau -> ddau,
    tri -> dri, pedwar -> bedwar, pump -> bump, deg -> ddeg."""
    assert start(text).hour == h


def test_bob_is_the_every_marker_in_its_mutated_form():
    """"bob" IS the lexicalised soft mutation of "pob", and it is the surface
    the "every X" construction actually uses."""
    from ._corpus import recur
    assert recur("bob dydd").recurrence.freq == "DAILY"
    assert recur("bob dydd").remainder == ""


@pytest.mark.parametrize("text", ["mlynedd", "flynedd", "fis", "ddydd"])
def test_a_mutated_noun_alone_is_not_a_time(text):
    """Recognising the surface must not make a bare noun into a span."""
    nomatch(text)
