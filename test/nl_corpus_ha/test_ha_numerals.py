"""Spelled numerals, and the composition rule they are built by.

Hausa Wikipedia habitually glosses a spelled number with the digits it means,
which makes it its own worked-example oracle.  The values asserted here are
those glosses -- "goma sha biyar (15)", "ashirin da shida (26)", "dubu ɗaya da
ɗari tara da goma sha huɗu (1914)" -- never a reading taken off the fold.
"""
import pytest

from chronologia.extract.numfold_chadic import read_run

from ._corpus import nomatch, start_end, year_span


def value(text):
    return read_run(tuple(text.split()))


@pytest.mark.parametrize("text,n", [
    ("sifiri", 0), ("ɗaya", 1), ("biyu", 2), ("uku", 3), ("huɗu", 4),
    ("biyar", 5), ("shida", 6), ("bakwai", 7), ("takwas", 8), ("tara", 9),
    ("goma", 10),
])
def test_the_base_numerals(text, n):
    """en.wiktionary.org, Module:number_list/data/ha, each cross-checked
    against its own lemma entry."""
    assert value(text) == n


@pytest.mark.parametrize("text,n", [
    ("daya", 1), ("hudu", 4), ("fuɗu", 4), ("fudu", 4),
])
def test_the_spelling_variants(text, n):
    """Written Hausa drops the hooks about as often as it keeps them, and
    fuɗu is Wiktionary's Western Hausa form of huɗu."""
    assert value(text) == n


@pytest.mark.parametrize("text,n", [
    ("ashirin", 20), ("talatin", 30), ("arba'in", 40), ("hamsin", 50),
    ("sittin", 60), ("saba'in", 70), ("tamanin", 80), ("casa'in", 90),
    ("tis'in", 90),
])
def test_the_arabic_tens(text, n):
    assert value(text) == n


@pytest.mark.parametrize("text,n", [
    ("gomiya biyu", 20), ("gomiya uku", 30), ("gomiya tara", 90),
])
def test_the_inherited_tens_multiply_ten(text, n):
    """gomiya is glossed "used to form multiples of ten"."""
    assert value(text) == n


@pytest.mark.parametrize("text,n", [
    ("goma sha ɗaya", 11), ("goma sha biyu", 12), ("goma sha uku", 13),
    ("goma sha huɗu", 14), ("goma sha biyar", 15), ("goma sha shida", 16),
    ("goma sha tara", 19),
])
def test_the_teens_are_ten_plus_a_unit(text, n):
    assert value(text) == n


@pytest.mark.parametrize("text,n", [
    ("sha ɗaya", 11), ("sha biyar", 15), ("sha bakwai", 17),
])
def test_the_goma_may_be_dropped(text, n):
    """"ranar sha ɗaya" is the eleventh day; "dubu biyu da sha biyar" is 2015."""
    assert value(text) == n


@pytest.mark.parametrize("text,n", [
    ("ashirin da shida", 26),
    ("ashirin da bakwai", 27),
    ("ashirin da takwas", 28),
    ("ashirin da hudu", 24),
    ("arba'in da biyar", 45),
    ("casa'in da ɗaya", 91),
])
def test_da_joins_a_tens_word_to_its_unit(text, n):
    assert value(text) == n


@pytest.mark.parametrize("text,n", [
    ("ɗari", 100), ("ɗari tara", 900), ("ɗari biyar", 500),
    ("ɗari takwas", 800), ("dubu", 1000), ("dubu biyu", 2000),
    ("dubu ɗaya", 1000),
])
def test_a_scale_word_leads_its_multiplier(text, n):
    assert value(text) == n


@pytest.mark.parametrize("text,n", [
    ("dubu ɗaya da ɗari tara da goma sha huɗu", 1914),
    ("dubu ɗaya da ɗari biyar da biyar", 1505),
    ("dubu ɗaya da ɗari takwas da ashirin da biyu", 1822),
    ("dubu ɗaya da ɗari tara da casa'in da ɗaya", 1991),
    ("dubu ɗaya da ɗari tara da sittin", 1960),
    ("dubu biyu da sha biyar", 2015),
])
def test_the_worked_examples_the_encyclopedia_glosses_itself(text, n):
    assert value(text) == n


@pytest.mark.parametrize("text", [
    "biyu da uku",          # ascending: not one number
    "tara ashirin",         # a unit before a tens word
    "goma goma",            # a repeat cannot be one number
    "sha",                  # the linker with nothing to link
    "da biyu",              # a connector cannot open a number
    "ɗari da dubu",         # a scale rising instead of falling
])
def test_a_run_that_cannot_be_one_number_reads_none(text):
    assert value(text) is None


def test_da_between_two_weekdays_is_not_a_numeral():
    """The connector is also the ordinary "and"; it bridges numbers only."""
    assert start_end("tsakanin Litinin da Jumaʼa") is not None


@pytest.mark.parametrize("text", ["biyar", "ashirin da biyar", "ɗari tara",
                                  "goma sha bakwai"])
def test_a_bare_numeral_is_not_a_date(text):
    """A count with nothing counted names no time."""
    nomatch(text)


def test_a_spelled_four_figure_numeral_reads_as_a_year():
    """The library reads a four-figure number as a year in every language."""
    assert start_end("dubu biyu da sha biyar") == year_span(2015)
