# -*- coding: utf-8 -*-
"""Century and decade vocabulary -- "abad"/"kurun" (Kamus Dewan: both gloss
to "century" in Malay grammar) and "dekad"/"dasawarsa" (Kamus Dewan: "dekad"
an English loan, "10 dekad = 1 abad"; "dasawarsa" the Javanese-derived
alternative, dasa "ten" + warsa "year").

Malay postposes the ordinal after the noun ("abad ketiga" = the third
century), the same shape its own quarter_ref sibling already uses
("kuartal ketiga"), so this corpus's base_grammar.extend adds
"CMUNIT ORD" to scoped_ordinal. Spelled ordinals fold through
ovos-number-parser (numbers_id backend, ordinals=True) only as single
tokens, so only the ordinal words with a one-word spelling ("ketiga" etc,
values 1..9ish) are exercised here.

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


@pytest.mark.parametrize("text", ["kurun ketiga"])
def test_century_ordinal_kurun_synonym(text):
    s = span(text)
    assert s.start.year == 200
    assert s.end.year == 300
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
    ("satu dekad lalu", 1), ("dua dasawarsa lalu", 2),
])
def test_decade_relative_offset(text, decades):
    start = ANCHOR - relativedelta(years=10 * decades)
    end = start + relativedelta(years=10)
    s = span(text)
    assert (s.start.year, s.start.month, s.start.day) == (start.year, start.month, start.day)
    assert (s.end.year, s.end.month, s.end.day) == (end.year, end.month, end.day)
    assert parse(text)[1] == ""


@pytest.mark.parametrize("text", ["abad", "kurun", "dekad", "dasawarsa"])
def test_bare_unit_word_no_match(text):
    nomatch(text)
