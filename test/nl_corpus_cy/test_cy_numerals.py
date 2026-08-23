"""The two Welsh numeral systems, and the gender the numeral agrees in.

Welsh counts twice over.  The traditional VIGESIMAL series counts in twenties
-- "pymtheg" 15, "deunaw" 18, "un ar hugain" 21 ("one on twenty"), "hanner
cant" 50 ("half a hundred"), "pedwar ugain" 80 ("four twenties") -- and the
modern DECIMAL series spells the same values as tens plus units ("un deg
wyth" 18, "dau ddeg un" 21).  Both are read, because the vigesimal one is the
series a date or an age actually uses.

Two, three and four agree in gender with the noun they count, so "dwy flynedd"
(feminine year) stands beside "dau fis" (masculine month) for the same count.

The expected surfaces below are transcribed from the numeral appendix, not
read back from the fold: each pair is a surface and the value that appendix
row gives it.
"""
import pytest

from chronologia.extract.numfold_welsh import (CARDINALS, ORDINALS,
                                               counted_phrase,
                                               decimal_surface,
                                               numeral_surface, soft_mutate)

#: (surface, value) transcribed from en.wiktionary.org "Appendix:Welsh
#: numbers", cardinal column, vigesimal readings.
VIGESIMAL = [
    ("sero", 0), ("un", 1), ("dau", 2), ("dwy", 2), ("tri", 3), ("tair", 3),
    ("pedwar", 4), ("pedair", 4), ("pump", 5), ("pum", 5), ("chwech", 6),
    ("chwe", 6), ("saith", 7), ("wyth", 8), ("naw", 9), ("deg", 10),
    ("un ar ddeg", 11), ("deuddeg", 12), ("tri ar ddeg", 13),
    ("tair ar ddeg", 13), ("pedwar ar ddeg", 14), ("pedair ar ddeg", 14),
    ("pymtheg", 15), ("un ar bymtheg", 16), ("dau ar bymtheg", 17),
    ("dwy ar bymtheg", 17), ("deunaw", 18), ("tair ar bymtheg", 18),
    ("pedwar ar bymtheg", 19), ("ugain", 20), ("un ar hugain", 21),
    ("dau ar hugain", 22), ("tri ar hugain", 23), ("pedwar ar hugain", 24),
    ("pump ar hugain", 25), ("chwech ar hugain", 26), ("saith ar hugain", 27),
    ("wyth ar hugain", 28), ("naw ar hugain", 29), ("deg ar hugain", 30),
    ("un ar ddeg ar hugain", 31), ("deuddeg ar hugain", 32),
    ("pymtheg ar hugain", 35), ("deunaw ar hugain", 38),
    ("deugain", 40), ("hanner cant", 50), ("trigain", 60),
    ("deg a thrigain", 70), ("pedwar ugain", 80), ("cant", 100),
]

#: the same values in the modern decimal series, same source.
DECIMAL = [
    ("un deg un", 11), ("un deg dau", 12), ("un deg tri", 13),
    ("un deg pedwar", 14), ("un deg pump", 15), ("un deg chwech", 16),
    ("un deg saith", 17), ("un deg wyth", 18), ("un deg naw", 19),
    ("dau ddeg", 20), ("dau ddeg un", 21), ("dau ddeg dau", 22),
    ("dau ddeg naw", 29), ("tri deg", 30), ("tri deg un", 31),
    ("pedwar deg", 40), ("pum deg", 50), ("chwe deg", 60),
    ("saith deg", 70), ("wyth deg", 80), ("naw deg", 90),
    ("naw deg naw", 99),
]

#: (surface, value) from the same appendix, ordinal column.
ORDINAL_ROWS = [
    ("cyntaf", 1), ("ail", 2), ("eilfed", 2), ("trydydd", 3),
    ("trydedd", 3), ("pedwerydd", 4), ("pedwaredd", 4), ("pumed", 5),
    ("chweched", 6), ("seithfed", 7), ("wythfed", 8), ("nawfed", 9),
    ("degfed", 10), ("unfed ar ddeg", 11), ("deuddegfed", 12),
    ("trydydd ar ddeg", 13), ("pedwerydd ar ddeg", 14), ("pymthegfed", 15),
    ("unfed ar bymtheg", 16), ("ail ar bymtheg", 17), ("deunawfed", 18),
    ("pedwerydd ar bymtheg", 19), ("ugeinfed", 20), ("unfed ar hugain", 21),
    ("pumed ar hugain", 25), ("degfed ar hugain", 30),
    ("unfed ar ddeg ar hugain", 31),
]


@pytest.mark.parametrize("surface,value", VIGESIMAL)
def test_vigesimal_surface_reads_its_value(surface, value):
    assert CARDINALS[surface] == value


@pytest.mark.parametrize("surface,value", DECIMAL)
def test_decimal_surface_reads_its_value(surface, value):
    assert CARDINALS[surface] == value


@pytest.mark.parametrize("surface,value", ORDINAL_ROWS)
def test_ordinal_surface_reads_its_value(surface, value):
    assert ORDINALS[surface] == value


@pytest.mark.parametrize("surface,value", VIGESIMAL + DECIMAL)
def test_every_cardinal_also_reads_soft_mutated(surface, value):
    """A numeral after "am" or "i" carries its mutated surface, so the
    mutated spelling must read the same value.  Mutation touches the first
    word of a compound and nothing else."""
    head, _, tail = surface.partition(" ")
    mutated = " ".join(filter(None, (soft_mutate(head), tail)))
    assert CARDINALS[mutated] == value


@pytest.mark.parametrize("value,masculine,feminine", [
    (2, "dau", "dwy"), (3, "tri", "tair"), (4, "pedwar", "pedair"),
])
def test_two_three_and_four_agree_in_gender(value, masculine, feminine):
    assert numeral_surface(value, "m") == masculine
    assert numeral_surface(value, "f") == feminine
    assert CARDINALS[masculine] == CARDINALS[feminine] == value


@pytest.mark.parametrize("value", [1, 5, 6, 7, 8, 9, 10, 15, 18, 20])
def test_everything_else_is_invariant(value):
    assert numeral_surface(value, "m") == numeral_surface(value, "f")


@pytest.mark.parametrize("value,expected", [
    (5, "pum"), (6, "chwe"), (10, "deng"), (100, "can"),
])
def test_the_before_a_noun_short_forms(value, expected):
    assert numeral_surface(value, "m", before_noun=True) == expected


@pytest.mark.parametrize("n,kind,expected", [
    (2, "year", "dwy flynedd"),      # feminine two, soft mutation
    (3, "year", "tair blynedd"),     # feminine three, radical
    (5, "year", "pum mlynedd"),      # nasal mutation
    (2, "month", "dau fis"),         # masculine two, soft mutation
    (3, "month", "tri mis"),
    (3, "day", "tri diwrnod"),
    (2, "hour", "dwy awr"),          # feminine, opens on a vowel
    (3, "week", "tair wythnos"),     # feminine, never mutates
    (5, "minute", "pum munud"),
])
def test_counted_phrase_agrees_and_mutates(n, kind, expected):
    assert counted_phrase(n, kind) == expected


@pytest.mark.parametrize("n,expected", [
    (11, "un deg un"), (18, "un deg wyth"), (20, "dau ddeg"),
    (21, "dau ddeg un"), (30, "tri deg"), (99, "naw deg naw"),
])
def test_decimal_surface_is_built_regularly(n, expected):
    assert decimal_surface(n) == expected


@pytest.mark.parametrize("n", [41, 55, 63, 77, 88, 95])
def test_unattested_vigesimal_compounds_are_refused(n):
    """The appendix joins these with a coordinator its own entry contradicts,
    so no vigesimal spelling ships for them and none is invented."""
    with pytest.raises(ValueError):
        numeral_surface(n)


@pytest.mark.parametrize("word,expected", [
    ("pedwar", "bedwar"), ("tri", "dri"), ("cant", "gant"), ("blynedd",
                                                             "flynedd"),
    ("dydd", "ddydd"), ("gorffennaf", "orffennaf"), ("mis", "fis"),
    ("llun", "lun"), ("rhagfyr", "ragfyr"),
])
def test_soft_mutation_table(word, expected):
    assert soft_mutate(word) == expected


@pytest.mark.parametrize("word", [
    "awst", "ebrill", "ionawr", "chwefror", "hydref", "saith", "wyth", "naw",
])
def test_words_that_cannot_soft_mutate(word):
    """A vowel, an "h", an "s" and the digraph "ch" have no soft-mutation
    cell, so the word is its own mutated form."""
    assert soft_mutate(word) == word
