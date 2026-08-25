"""The spelled-numeral fold, swept over every value a source attests.

Gold comes from en.wiktionary.org's Albanian number data -- the units, teens
and tens below are transcribed from it here, and the compound is spelled by
this module's own ``TENS e UNIT`` rule rather than by asking the fold what it
thinks.  Each value is exercised through a real phrase ("<numeral> ditë më
parë"), so a numeral that folds to the wrong number lands on the wrong day.
"""
from datetime import timedelta

import pytest

from chronologia.extract.numfold_albanian import read_run

from ._corpus import ANCHOR, nomatch, parse, start

#: 1..10, transcribed from the entries një, dy, tre/tri, katër, pesë,
#: gjashtë, shtatë, tetë, nëntë, dhjetë.
UNITS = {1: "një", 2: "dy", 3: "tre", 4: "katër", 5: "pesë", 6: "gjashtë",
         7: "shtatë", 8: "tetë", 9: "nëntë", 10: "dhjetë"}

#: 11..19, each a single word ending in -mbëdhjetë.
TEENS = {11: "njëmbëdhjetë", 12: "dymbëdhjetë", 13: "trembëdhjetë",
         14: "katërmbëdhjetë", 15: "pesëmbëdhjetë", 16: "gjashtëmbëdhjetë",
         17: "shtatëmbëdhjetë", 18: "tetëmbëdhjetë", 19: "nëntëmbëdhjetë"}

#: the round tens.  Twenty and forty are lexical (njëzet, dyzet); thirty is
#: tridhjetë and the rest are unit + dhjetë.
TENS = {20: "njëzet", 30: "tridhjetë", 40: "dyzet", 50: "pesëdhjetë",
        60: "gjashtëdhjetë", 70: "shtatëdhjetë", 80: "tetëdhjetë",
        90: "nëntëdhjetë"}


def _spell(n):
    """Spell 1..99 by the attested rule, independently of the fold."""
    if n in UNITS:
        return UNITS[n]
    if n in TEENS:
        return TEENS[n]
    if n in TENS:
        return TENS[n]
    tens, unit = divmod(n, 10)
    return f"{TENS[tens * 10]} e {UNITS[unit]}"


def _days_ago(word):
    return (ANCHOR - start(f"{word} ditë më parë").datetime()).days


@pytest.mark.parametrize("n", sorted(UNITS))
def test_units(n):
    assert _days_ago(UNITS[n]) == n


@pytest.mark.parametrize("n", sorted(TEENS))
def test_teens(n):
    assert _days_ago(TEENS[n]) == n


@pytest.mark.parametrize("n", sorted(TENS))
def test_round_tens(n):
    assert _days_ago(TENS[n]) == n


@pytest.mark.parametrize("n", list(range(21, 100)))
def test_every_compound_below_a_hundred(n):
    """The whole 21..99 range, spelled by the ``TENS e UNIT`` rule."""
    if n % 10 == 0:
        pytest.skip("round tens are covered by their own case")
    assert _days_ago(_spell(n)) == n


def test_the_feminine_three_counts_the_same_as_the_masculine():
    """``tri`` and ``tre`` are one value in two genders, not two values."""
    assert _days_ago("tri") == _days_ago("tre") == 3


@pytest.mark.parametrize("word,years", [
    ("njëqind", 100), ("qind", 100), ("dyqind", 200), ("treqind", 300),
    ("katërqind", 400), ("pesëqind", 500), ("gjashtëqind", 600),
    ("shtatëqind", 700), ("tetëqind", 800), ("nëntëqind", 900),
    ("mijë", 1000), ("njëmijë", 1000),
])
def test_the_round_hundreds_and_the_thousand(word, years):
    assert start(f"{word} vjet më parë").year == ANCHOR.year - years


def test_zero_is_a_number():
    """``zero`` is the attested cardinal, and the fold reads it as one.  It has
    no phrase of its own to be exercised through -- a bare hour needs the hour
    word in front of it -- so the fold's reader is asked directly."""
    assert read_run("zero") == 0


# -- what the fold refuses, because nothing attests it ----------------------

@pytest.mark.parametrize("text", [
    "njëqind e njëzet ditë më parë",
    "njëqind e njëzet",
    "dyqind e pesëdhjetë ditë më parë",
    "dy mijë e njëzet e gjashtë",
    "një mijë e nëntëqind ditë më parë",
    "dy mijë",
])
def test_a_hundred_or_thousand_joined_to_a_remainder_refuses(text):
    """No source spells how Albanian joins a hundreds or thousands word to the
    rest of the number.  Reading one group and stopping is not enough: it would
    fold the TAIL and answer a smaller number -- "njëqind e njëzet" would come
    back as twenty, "dy mijë e njëzet e gjashtë" as the year 1000 -- with the
    unread words merely sitting in the remainder.  A visible remainder is a
    hint, not a refusal, so the whole run refuses and nothing resolves."""
    assert parse(text) is None


def test_a_compound_without_its_connective_is_not_a_number():
    """The connective ``e`` is obligatory: "njëzet pesë" is not 25."""
    r = parse("njëzet pesë ditë më parë")
    assert r is None or (ANCHOR - r[0].start.datetime()) != timedelta(days=25)


@pytest.mark.parametrize("text,years", [
    ("njëqind vjet më parë", 100), ("dyqind vjet më parë", 200),
    ("mijë vjet më parë", 1000),
])
def test_a_round_word_standing_alone_still_reads(text, years):
    """The refusal is scoped to a round word sitting BESIDE another number; one
    on its own is a plain, attested count."""
    assert start(text).year == ANCHOR.year - years


@pytest.mark.parametrize("text,expected", [
    ("shtatë e njëzet e pesë", (7, 25)), ("tetë e dyzet", (8, 40)),
])
def test_a_run_without_a_round_word_still_composes(text, expected):
    """The clock's hour-and-minutes run has the same shape as the refused one
    -- number, connective, number -- and must keep composing."""
    s = start(text)
    assert (s.hour, s.minute) == expected


@pytest.mark.parametrize("text", [
    "dhjetë e një ditë më parë", "gjashtë e dy ditë më parë",
])
def test_a_unit_word_does_not_open_a_compound(text):
    """Only a TENS word may lead a compound; "dhjetë e një" is not eleven."""
    r = parse(text)
    assert r is None or (ANCHOR - r[0].start.datetime()) != timedelta(days=11)


def test_a_number_word_inside_another_word_is_not_a_number():
    nomatch("dygjuhësh")
