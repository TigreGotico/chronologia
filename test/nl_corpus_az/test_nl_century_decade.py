# -*- coding: utf-8 -*-
"""Century and decade vocabulary -- "esr" (Wiktionary: Azerbaijani for
"century", an Arabic loan) and "onillik" (Wiktionary, derived term of "il"
"year": on = ten, il = year, -lik nominal suffix, = "decade").

Azerbaijani is Ord-first ("Nth esr"), inheriting the shared scoped_ordinal
base order unchanged; ordinal words fold via ovos-number-parser
(numbers_az, ordinals=True).  Gold for the ordinal form: the Nth century
spans the 100 years opening in year (N-1)*100, half-open, computed
independently of the parser -- except the first century, which (no year
zero) spans [1, 101).

The relative-offset form ("N esr evvel" = N centuries ago) resolves through
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
    ("birinci əsr", 1), ("beşinci əsr", 5),
    ("onuncu əsr", 10), ("iyirminci əsr", 20),
])
def test_century_ordinal(text, n):
    s = span(text)
    assert s.start.year == (1 if n == 1 else (n - 1) * 100)
    assert s.end.year == (101 if n == 1 else n * 100)
    assert parse(text)[1] == ""


@pytest.mark.parametrize("text,years", [
    ("bir əsr əvvəl", 100), ("iki əsr əvvəl", 200),
])
def test_century_relative_offset(text, years):
    start = ANCHOR - relativedelta(years=years)
    end = start + relativedelta(years=100)
    s = span(text)
    assert (s.start.year, s.start.month, s.start.day) == (start.year, start.month, start.day)
    assert (s.end.year, s.end.month, s.end.day) == (end.year, end.month, end.day)
    assert parse(text)[1] == ""


@pytest.mark.parametrize("text,decades", [
    ("bir onillik əvvəl", 1), ("üç onillik əvvəl", 3),
])
def test_decade_relative_offset(text, decades):
    start = ANCHOR - relativedelta(years=10 * decades)
    end = start + relativedelta(years=10)
    s = span(text)
    assert (s.start.year, s.start.month, s.start.day) == (start.year, start.month, start.day)
    assert (s.end.year, s.end.month, s.end.day) == (end.year, end.month, end.day)
    assert parse(text)[1] == ""


@pytest.mark.parametrize("text", ["əsr", "onillik"])
def test_bare_unit_word_no_match(text):
    nomatch(text)
