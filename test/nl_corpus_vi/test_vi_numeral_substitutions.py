"""The positional numeral substitutions, exercised across their boundaries.

Vietnamese spells the same digit differently depending on where it sits, and
each substitution has a boundary the fold has to get right:

    mười -> mươi   at twenty:  mười chín 19, hai mươi 20
    năm  -> lăm    above ten:  năm 5, mười lăm 15, hai mươi lăm 25
    một  -> mốt    after mươi: mười một 11, hai mươi mốt 21
    bốn  -> tư     after mươi: mười bốn 14, hai mươi tư 24

Each family below straddles its boundary, so a fold that applied the rule one
step too early or too late fails rather than passing on the easy side.  The
gold values are the arithmetic of the phrase, computed here; the numbers are
carried into a date offset because that is the public edge the corpus tests.

Sources: en.wikipedia.org, "Vietnamese numerals" for every substitution and
for the linh/lẻ and nghìn/ngàn regional pairs.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, start
from chronologia.extract.numfold_vietnamese import read_run, surface


@pytest.mark.parametrize("phrase,value", [
    ("không", 0), ("một", 1), ("hai", 2), ("ba", 3), ("bốn", 4),
    ("sáu", 6), ("bảy", 7), ("tám", 8), ("chín", 9), ("mười", 10),
])
def test_units(phrase, value):
    assert read_run(phrase) == value


@pytest.mark.parametrize("phrase,value", [
    ("mười một", 11),
    ("mười hai", 12),
    ("mười bốn", 14),
    ("mười tư", 14),
    ("mười lăm", 15),
    ("mười nhăm", 15),
    ("mười chín", 19),
])
def test_teens_keep_the_free_form_muoi(phrase, value):
    assert read_run(phrase) == value


@pytest.mark.parametrize("phrase,value", [
    ("hai mươi", 20),
    ("ba mươi", 30),
    ("bốn mươi", 40),
    ("năm mươi", 50),
    ("sáu mươi", 60),
    ("chín mươi", 90),
])
def test_tens_above_nineteen_take_the_reduced_muoi(phrase, value):
    assert read_run(phrase) == value


@pytest.mark.parametrize("phrase", ["hai mười", "ba mười", "chín mười"])
def test_the_free_form_never_multiplies(phrase):
    """mười is the free ten, not a multiplier; only mươi multiplies.  Reading
    "hai mười" as twenty would erase the distinction the language draws."""
    assert read_run(phrase) is None


@pytest.mark.parametrize("phrase,value", [
    ("mười một", 11),
    ("hai mươi mốt", 21),
    ("ba mươi mốt", 31),
    ("chín mươi mốt", 91),
])
def test_one_becomes_mot_only_after_muoi(phrase, value):
    assert read_run(phrase) == value


@pytest.mark.parametrize("phrase,value", [
    ("hai mươi một", 21),
    ("ba mươi một", 31),
])
def test_the_citation_one_is_still_read_where_it_appears(phrase, value):
    """mốt is what a speaker says; một in the same slot is still unambiguously
    the same digit, so it is read rather than refused.  The pair matches
    tư/bốn, where the source names one form as the common one without ruling
    the other out."""
    assert read_run(phrase) == value


@pytest.mark.parametrize("phrase,value", [
    ("mười lăm", 15),
    ("hai mươi lăm", 25),
    ("năm mươi lăm", 55),
    ("chín mươi lăm", 95),
    ("một trăm mười lăm", 115),
])
def test_five_becomes_lam_above_ten(phrase, value):
    assert read_run(phrase) == value


@pytest.mark.parametrize("phrase", ["mười năm", "hai mươi năm", "năm mươi năm"])
def test_the_citation_five_never_closes_a_compound(phrase):
    """This is the collision the lăm substitution exists to prevent: mười năm
    is ten YEARS, not fifteen, and reading it as a numeral would hand back a
    number where the speaker said a duration."""
    assert read_run(phrase) is None


@pytest.mark.parametrize("phrase,value", [
    ("mười tư", 14),
    ("hai mươi tư", 24),
    ("ba mươi tư", 34),
    ("chín mươi tư", 94),
])
def test_four_becomes_tu_in_the_compound_final_position(phrase, value):
    assert read_run(phrase) == value


@pytest.mark.parametrize("phrase,value", [
    ("hai mươi bốn", 24),
    ("ba mươi bốn", 34),
])
def test_the_native_four_is_still_read_where_it_appears(phrase, value):
    assert read_run(phrase) == value


@pytest.mark.parametrize("phrase", ["tư", "tư ngày", "tư tháng"])
def test_tu_alone_is_not_a_cardinal(phrase):
    """tư is positional -- it names the fourth thing, not four things.  A
    duration of four months is bốn tháng; tư tháng is not Vietnamese, and a
    fold that treated tư as a spelling variant of bốn would accept it."""
    assert read_run(phrase.split()[0]) is None


@pytest.mark.parametrize("phrase,value", [
    ("một trăm", 100),
    ("hai trăm", 200),
    ("một trăm hai mươi ba", 123),
    ("một trăm linh một", 101),
    ("một trăm lẻ một", 101),
    ("sáu trăm linh năm", 605),
    ("sáu trăm lẻ năm", 605),
])
def test_hundreds_and_the_regional_zero_filler(phrase, value):
    assert read_run(phrase) == value


@pytest.mark.parametrize("phrase,value", [
    ("một nghìn", 1000),
    ("một ngàn", 1000),
    ("hai nghìn", 2000),
    ("hai nghìn không trăm hai mươi tư", 2024),
    ("hai ngàn không trăm hai mươi tư", 2024),
    ("mười nghìn không trăm năm mươi lăm", 10055),
    ("một nghìn không trăm linh một", 1001),
])
def test_thousands_north_and_south(phrase, value):
    assert read_run(phrase) == value


@pytest.mark.parametrize("value", [
    0, 1, 4, 9, 10, 11, 14, 15, 19, 20, 21, 24, 25, 30, 31, 50, 55, 91,
    95, 99, 100, 101, 115, 123, 605, 1000, 2024,
])
def test_surface_and_reader_agree(value):
    assert read_run(surface(value)) == value


def test_the_bare_five_is_the_one_value_that_does_not_round_trip():
    """surface(5) is năm, and năm alone is refused a numeral reading because
    it is equally the noun "year".  The asymmetry is deliberate and pinned
    here so it cannot be "fixed" into a silent misreading; every compound
    containing five round-trips normally."""
    assert surface(5) == "năm"
    assert read_run("năm") is None
    assert read_run(surface(55)) == 55
    assert read_run(surface(605)) == 605


@pytest.mark.parametrize("text,days", [
    ("mười chín ngày trước", 19),
    ("hai mươi ngày trước", 20),
    ("hai mươi mốt ngày trước", 21),
    ("hai mươi tư ngày trước", 24),
    ("hai mươi lăm ngày trước", 25),
    ("chín mươi mốt ngày trước", 91),
])
def test_the_substitutions_survive_into_a_real_offset(text, days):
    assert start(text) == ad(ANCHOR - timedelta(days=days))
