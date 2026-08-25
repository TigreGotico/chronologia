"""Both Filipino numeral systems, read through the surfaces that carry them.

The two tables are exercised where each is actually spoken: the native set
through the day-of-month ordinal, the spelled year and the offset count, the
Spanish-derived set through the hour after ``alas``.  Every expected value is
the plain arithmetic meaning of the word, taken from its own dictionary
entry, not from the fold's output.
"""
import pytest

from chronologia.extract.numfold_filipino import (read_native_run,
                                                  read_spanish_run)

from ._corpus import ANCHOR, next_time, nomatch, span, start

NATIVE = [
    ("isa", 1), ("dalawa", 2), ("tatlo", 3), ("apat", 4), ("lima", 5),
    ("anim", 6), ("pito", 7), ("walo", 8), ("siyam", 9), ("sampu", 10),
    ("labing-isa", 11), ("labindalawa", 12), ("labintatlo", 13),
    ("labing-apat", 14), ("labinlima", 15), ("labing-anim", 16),
    ("labimpito", 17), ("labingwalo", 18), ("labinsiyam", 19),
    ("dalawampu", 20), ("tatlumpu", 30), ("apatnapu", 40), ("limampu", 50),
    ("animnapu", 60), ("pitumpu", 70), ("walumpu", 80), ("siyamnapu", 90),
    ("daan", 100), ("sandaan", 100), ("libo", 1000), ("sanlibo", 1000),
]

SPANISH = [
    ("uno", 1), ("dos", 2), ("tres", 3), ("kuwatro", 4), ("singko", 5),
    ("seis", 6), ("sais", 6), ("siyete", 7), ("otso", 8), ("nuwebe", 9),
    ("diyes", 10), ("onse", 11), ("dose", 12), ("trese", 13),
    ("katorse", 14), ("kinse", 15), ("disiseis", 16), ("disisiyete", 17),
    ("disiotso", 18), ("disinuwebe", 19), ("beynte", 20), ("treynta", 30),
    ("trenta", 30), ("kuwarenta", 40), ("singkuwenta", 50), ("setenta", 70),
    ("otsenta", 80), ("siyento", 100), ("mil", 1000),
]


@pytest.mark.parametrize("word,value", NATIVE)
def test_native_cardinal_word(word, value):
    assert read_native_run((word,)) == value


@pytest.mark.parametrize("word,value", SPANISH)
def test_spanish_cardinal_word(word, value):
    assert read_spanish_run((word,)) == value


def test_the_two_tables_share_no_surface():
    """Nothing has to disambiguate the systems because nothing is spelled the
    same in both -- which is why one run reader can be chosen by first word."""
    assert not {w for w, _ in NATIVE} & {w for w, _ in SPANISH}


@pytest.mark.parametrize("word,value", NATIVE)
def test_a_native_word_is_not_a_spanish_one(word, value):
    assert read_spanish_run((word,)) is None


@pytest.mark.parametrize("word,value", SPANISH)
def test_a_spanish_word_is_not_a_native_one(word, value):
    assert read_native_run((word,)) is None


@pytest.mark.parametrize("phrase,value", [
    ("dalawampu't isa", 21),
    ("dalawampu't dalawa", 22),
    ("tatlumpu't lima", 35),
    ("apatnapu't walo", 48),
    ("limampu't siyam", 59),
    ("pitumpu't tatlo", 73),
    ("siyamnapu't anim", 96),
])
def test_native_tens_join_their_unit_with_the_enclitic(phrase, value):
    assert read_native_run(tuple(phrase.split())) == value


@pytest.mark.parametrize("phrase,value", [
    ("dalawang libo", 2000),
    ("limang daan", 500),
    ("dalawang libo't dalawampu't dalawa", 2022),
    ("dalawang libo't dalawampu", 2020),
    ("tatlong libo", 3000),
])
def test_native_scale_words_multiply(phrase, value):
    assert read_native_run(tuple(phrase.split())) == value


@pytest.mark.parametrize("phrase,value", [
    ("beynte uno", 21),
    ("beynte dos", 22),
    ("beynte nuwebe", 29),
    ("kuwarenta y singko", 45),
    ("trenta y otso", 38),
    ("trenta y singko", 35),
    ("treynta y dos", 32),
    ("singkuwenta y nuwebe", 59),
    ("dos mil", 2000),
])
def test_spanish_compounds(phrase, value):
    assert read_spanish_run(tuple(phrase.split())) == value


def test_the_ligature_is_the_same_cardinal():
    """A modifying numeral takes -ng after a vowel and -g after n; both read
    back to the bare cardinal rather than being separate entries."""
    for bare, linked in [("dalawa", "dalawang"), ("lima", "limang"),
                         ("tatlumpu", "tatlumpung"), ("labinlima",
                                                      "labinlimang"),
                         ("labingwalo", "labingwalong"), ("daan", "daang")]:
        assert read_native_run((linked,)) == read_native_run((bare,))


@pytest.mark.parametrize("count,days", [
    ("isang", 1), ("dalawang", 2), ("tatlong", 3), ("limang", 5),
    ("sampung", 10), ("labinlimang", 15), ("dalawampu't limang", 25),
])
def test_native_count_drives_an_offset(count, days):
    from datetime import timedelta
    s = start(f"sa {count} araw")
    assert s.day == (ANCHOR + timedelta(days=days)).day


@pytest.mark.parametrize("count,unit,days", [
    ("dalawang", "araw", 2), ("apat na", "araw", 4), ("anim na", "araw", 6),
    ("siyam na", "araw", 9), ("labing-anim na", "araw", 16),
])
def test_the_free_standing_linker_after_a_consonant(count, unit, days):
    """The ligature is written onto a vowel-final numeral ("dalawang araw")
    and as a separate word after a consonant ("apat na araw"); both are the
    same morpheme and both count the same unit."""
    from datetime import timedelta
    s = start(f"sa {count} {unit}")
    assert s.day == (ANCHOR + timedelta(days=days)).day


@pytest.mark.parametrize("phrase,days", [
    ("labing-isang", 11), ("labing-apat na", 14), ("labing-anim na", 16),
])
def test_the_hyphenated_teens_survive_tokenization(phrase, days):
    """Eleven, fourteen and sixteen are the only teens spelled with an
    internal hyphen; the tokenizer shears it, so the fold rejoins the two
    pieces the way it does for the ``ika-`` prefix."""
    from datetime import timedelta
    assert start(f"sa {phrase} araw").day == (ANCHOR
                                              + timedelta(days=days)).day


@pytest.mark.parametrize("word,h", [
    ("uno", 1), ("dos", 2), ("tres", 3), ("kuwatro", 4), ("singko", 5),
    ("sais", 6), ("siyete", 7), ("otso", 8), ("nuwebe", 9), ("diyes", 10),
    ("onse", 11), ("dose", 12),
])
def test_spanish_count_drives_the_clock_hour(word, h):
    lead = "ala" if h == 1 else "alas"
    assert start(f"{lead} {word}").hour == h % 24


@pytest.mark.parametrize("phrase", [
    "sesenta", "nobenta", "kwatro", "dyes", "bente", "kwarenta", "nwebe",
])
def test_unattested_spanish_spellings_are_not_numerals(phrase):
    """Each has no numeral sense under that spelling in the dictionary the
    rest of the table was built from, so none of them folds -- an unfolded
    surface is a refusal, not a guess."""
    assert read_spanish_run((phrase,)) is None
    nomatch(f"alas {phrase}")


def test_a_run_of_unrelated_words_reads_as_nothing():
    assert read_native_run(("bukas", "kahapon")) is None
    assert read_spanish_run(("bukas", "kahapon")) is None
