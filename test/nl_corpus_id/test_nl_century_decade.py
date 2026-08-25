# -*- coding: utf-8 -*-
"""Century and decade vocabulary -- "abad" (KBBI: a period of 100 years) and
"dekade"/"dasawarsa" (KBBI: masa 10 tahun -- KBBI equates the two; dasawarsa
is the Sanskrit-derived synonym, dasa "ten" + warsa "year").

Indonesian postposes the ordinal after the noun ("abad ketiga" = the third
century), the same shape its own quarter_ref sibling already uses
("kuartal ketiga"), so this corpus's base_grammar.extend adds
"CMUNIT ordinal_prefix? ORD" to scoped_ordinal. Spelled ordinals fold through
ovos-number-parser (numbers_id, ordinals=True) only as single tokens, so of
the spelled forms only the one-word ordinals ("ketiga" etc, values 1..9ish)
are exercised here; the multi-word spelled compound ("kedua puluh") does not
fold and refuses. The digit ordinal is written with the ke- prefix and a
hyphen ("abad ke-20"), which the tokenizer splits, and that form does
resolve.

Gold for the ordinal form: the Nth century spans the 100 years opening in
year (N-1)*100, half-open, computed independently of the parser.

The relative-offset form ("N abad lalu" = N centuries ago) resolves through
the shared calendar-grain-offset machinery (resolver.py
``_calendar_grain_offset``/``_point_span``): it steps the anchor back by
exactly N*1200 (or, for decades, N*120) calendar months and returns the
one-unit-wide span starting there -- gold is computed by that same
independent month arithmetic, not read back from the parser.
"""
from dateutil.relativedelta import relativedelta

import pytest

from ._corpus import ANCHOR, parse, span, nomatch


@pytest.mark.parametrize("text,n", [
    ("abad kedua", 2), ("abad ketiga", 3),
    ("abad kelima", 5), ("abad kesembilan", 9),
])
def test_century_ordinal(text, n):
    s = span(text)
    assert s.start.year == (n - 1) * 100
    assert s.end.year == n * 100
    assert parse(text)[1] == ""


@pytest.mark.parametrize("text,years", [
    ("satu abad lalu", 100), ("dua abad lalu", 200),
])
def test_century_relative_offset(text, years):
    start = ANCHOR - relativedelta(years=years)
    end = start + relativedelta(years=100)
    s = span(text)
    assert (s.start.year, s.start.month, s.start.day) == (start.year, start.month, start.day)
    assert (s.end.year, s.end.month, s.end.day) == (end.year, end.month, end.day)
    assert parse(text)[1] == ""


@pytest.mark.parametrize("text,decades", [
    ("satu dekade lalu", 1), ("tiga dasawarsa lalu", 3),
])
def test_decade_relative_offset(text, decades):
    start = ANCHOR - relativedelta(years=10 * decades)
    end = start + relativedelta(years=10)
    s = span(text)
    assert (s.start.year, s.start.month, s.start.day) == (start.year, start.month, start.day)
    assert (s.end.year, s.end.month, s.end.day) == (end.year, end.month, end.day)
    assert parse(text)[1] == ""


@pytest.mark.parametrize("text", ["abad", "dekade", "dasawarsa"])
def test_bare_unit_word_no_match(text):
    nomatch(text)


def test_compound_spelled_ordinal_refuses():
    # "kedua puluh" (second + tens) means "twentieth", but the number fold
    # only reads spelled ordinals as single tokens: "kedua" folds to 2
    # alone, leaving "puluh" stranded beside it.  Composing multi-word
    # spelled ordinals is unsupported -- this refuses (None) rather than
    # silently answering "the 2nd century" for "the twentieth century".
    nomatch("abad kedua puluh")


@pytest.mark.parametrize("text,n", [
    ("abad ke-20", 20), ("abad ke-19", 19), ("abad ke-3", 3),
])
def test_century_with_the_ke_ordinal_prefix(text, n):
    """The digit ordinal Indonesian actually writes: ke- takes a hyphen
    before digits ("ke-20", "ke-100"), and the tokenizer splits the hyphen,
    so the prefix reaches the grammar as its own word.  This is the form the
    spelled compound ("kedua puluh") refuses, spelled the way it is written
    in practice."""
    s = span(text)
    assert (s.start.year, s.end.year) == ((n - 1) * 100, n * 100)
    assert parse(text)[1] == ""


@pytest.mark.parametrize("text,base", [
    ("dekade 1990", 1990), ("dasawarsa 1990", 1990), ("dekade 1980", 1980),
])
def test_the_decade_is_named_by_its_base_year(text, base):
    """Indonesian has no plural-suffix decade spelling, so there is no
    counterpart to "the 1990s": the decade head plus the base year is the
    whole construction.  Without it the year won on its own and the decade
    word was left in the remainder -- a single year answered for a decade."""
    s = span(text)
    assert (s.start.year, s.end.year) == (base, base + 10)
    assert parse(text)[1] == ""


def test_a_century_head_does_not_take_a_year():
    """The decade order binds decade heads only.  "abad 1990" is not the
    1990s -- there is no 1990th century either -- so it refuses."""
    nomatch("abad 1990")
