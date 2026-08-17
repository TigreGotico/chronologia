# -*- coding: utf-8 -*-
"""Century and decade vocabulary -- قرن (qarn, the standard Persian
dictionary word for "century") and دهه (dahe, derived from ده "ten", the
standard Persian dictionary word for a ten-year period).

Persian postposes the ordinal after the noun ("قرن سوم" = the third
century), the same shape its own quarter_ref sibling already uses
("ربع سوم" style orders), so this corpus's base_grammar.extend adds
"CMUNIT ORD" to scoped_ordinal. Ordinal words fold via
ovos-number-parser (numbers_fa, ordinals=True).

Gold for the ordinal form: the Nth century spans the 100 years opening in
year (N-1)*100, half-open, computed independently of the parser.

The relative-offset form ("N قرن پیش" = N centuries ago) resolves through
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
    ("قرن دوم", 2), ("قرن سوم", 3), ("قرن پنجم", 5),
])
def test_century_ordinal(text, n):
    s = span(text)
    assert s.start.year == (n - 1) * 100
    assert s.end.year == n * 100
    assert parse(text)[1] == ""


@pytest.mark.parametrize("text,years", [
    ("یک قرن پیش", 100), ("دو قرن پیش", 200),
])
def test_century_relative_offset(text, years):
    start = ANCHOR - relativedelta(years=years)
    end = start + relativedelta(years=100)
    s = span(text)
    assert (s.start.year, s.start.month, s.start.day) == (start.year, start.month, start.day)
    assert (s.end.year, s.end.month, s.end.day) == (end.year, end.month, end.day)
    assert parse(text)[1] == ""


@pytest.mark.parametrize("text,decades", [
    ("یک دهه پیش", 1), ("سه دهه پیش", 3),
])
def test_decade_relative_offset(text, decades):
    start = ANCHOR - relativedelta(years=10 * decades)
    end = start + relativedelta(years=10)
    s = span(text)
    assert (s.start.year, s.start.month, s.start.day) == (start.year, start.month, start.day)
    assert (s.end.year, s.end.month, s.end.day) == (end.year, end.month, end.day)
    assert parse(text)[1] == ""


@pytest.mark.parametrize("text", ["قرن", "دهه"])
def test_bare_unit_word_no_match(text):
    nomatch(text)


def test_compound_spelled_ordinal_refuses():
    # "بیست و یکم" (twenty + and + first) means "twenty-first", but
    # extract_number_fa reads only "بیست" (20) out of that run and stops --
    # it does not compose the "و یکم" continuation. The matcher's ORD slot
    # then binds 20 alone, stranding "و یکم" beside it. Composing multi-word
    # spelled ordinals is unsupported -- this refuses (None) rather than
    # silently answering "the 20th century" for "the twenty-first century".
    nomatch("قرن بیست و یکم")
