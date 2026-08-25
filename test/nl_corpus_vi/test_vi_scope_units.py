# -*- coding: utf-8 -*-
"""The century and the decade, both of which Vietnamese frames head-first.

The scope noun leads and the numeral follows it: ``thế kỷ 20`` is the
twentieth century, optionally with the ordinal marker spelled out
(``thế kỷ thứ 20``) and equally with the numeral written out
(``thế kỷ hai mươi``).  There is no English "20th century" order here -- the
number never precedes the noun.

The decade works the same way and is the only spelling Vietnamese has for it:
nothing pluralises, so "the 1990s" has no counterpart, and ``thập kỷ 1990``
(or ``thập niên 1990``) is what a speaker says.  ``thập niên`` is collective
and appears only in this compound, which is why it is a decade head and not a
duration noun.

Gold is arithmetic, computed here rather than read back from the parser: the
Nth century opens in year (N-1)*100 and is 100 years wide, and a decade named
by its base year opens there and is 10 years wide, both half-open.

Source for the surfaces: en.wiktionary.org, thế kỷ / thập niên / thập kỷ; the
decade phrase is attested in the thập niên entry's own example, "thập niên 80
(của thế kỉ 20)".
"""
import pytest

from ._corpus import nomatch, parse, span


@pytest.mark.parametrize("text,n", [
    ("thế kỷ 20", 20),
    ("thế kỉ 20", 20),
    ("thế kỷ thứ 20", 20),
    ("thế kỷ hai mươi", 20),
    ("thế kỷ thứ hai mươi", 20),
    ("thế kỷ 2", 2),
    ("thế kỷ thứ hai mươi mốt", 21),
])
def test_the_century_reads_head_first(text, n):
    s = span(text)
    assert (s.start.year, s.end.year) == ((n - 1) * 100, n * 100)
    assert parse(text)[1] == ""


@pytest.mark.parametrize("text,base", [
    ("thập kỷ 1990", 1990),
    ("thập kỉ 1990", 1990),
    ("thập niên 1990", 1990),
    ("thập kỷ 1980", 1980),
])
def test_the_decade_is_named_by_its_base_year(text, base):
    s = span(text)
    assert (s.start.year, s.end.year) == (base, base + 10)
    assert parse(text)[1] == ""


@pytest.mark.parametrize("text", ["thế kỷ", "thế kỉ", "thập kỷ", "thập niên"])
def test_a_bare_scope_noun_names_no_period(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["thế kỷ 1990", "thế kỉ 1990"])
def test_a_year_is_not_a_century_number(text):
    """There is no 1990th century.  Answering the bare year and leaving the
    century word in the remainder would drop the only word that said what
    kind of period was meant, so the whole phrase refuses."""
    nomatch(text)


@pytest.mark.parametrize("text,n", [
    ("thế kỷ 21", 21),
    ("thế kỷ thứ 21", 21),
])
def test_the_century_we_are_in(text, n):
    s = span(text)
    assert (s.start.year, s.end.year) == ((n - 1) * 100, n * 100)
    assert parse(text)[1] == ""


def test_a_bare_tens_names_the_most_recent_such_decade():
    """A two-digit decade is written without its century ("thập kỷ 90"), and
    the one meant is the most recent already begun -- from a 2017 anchor the
    1990s, not the 2090s."""
    s = span("thập kỷ 90")
    assert (s.start.year, s.end.year) == (1990, 2000)
    assert parse("thập kỷ 90")[1] == ""
