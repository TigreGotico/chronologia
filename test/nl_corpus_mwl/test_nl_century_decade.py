# -*- coding: utf-8 -*-
"""Century and decade vocabulary -- "seclo" and "decada"/"década", both
attested in native running text on the Mirandese Wikipedia (Biquipédia):
the article title "Seclo XX" (mwl.wikipedia.org/wiki/Seclo_XX) and the
category titles "Catadorie:Década de 1850" / "Catadorie:Década de 2000".

Roman-numeral centuries ("seclo XX", the Biquipédia spelling) are NOT
exercised here: Mirandese is not in the small set of locales the
Roman-numeral fold (``numfold_roman.py``) covers, so that surface
genuinely does not resolve regardless of this vocabulary addition -- out
of scope for this corpus. The dotted-ordinal digit form ("20. seclo")
works instead, since mwl's tokenizer already reads ordinal_dot notation.

Gold for the ordinal form: the Nth century spans the 100 years opening in
year (N-1)*100, half-open, computed independently of the parser.

The relative-offset form ("N seclo(s)/decada(s) hai" = N centuries/decades
ago, "hai" being this locale's one citable past marker -- see
papers/linguistics/mwl/INDEX.md) resolves through the shared
calendar-grain-offset machinery (resolver.py
``_calendar_grain_offset``/``_point_span``): it steps the anchor back by
exactly N*1200 (or, for decades, N*120) calendar months and returns the
one-unit-wide span starting there -- gold is computed by that same
independent month arithmetic, not read back from the parser.
"""
from dateutil.relativedelta import relativedelta

import pytest

from ._corpus import ANCHOR, parse, span, nomatch


@pytest.mark.parametrize("text,n", [
    ("3. seclo", 3), ("5. seclo", 5), ("20. seclo", 20),
])
def test_century_ordinal_dotted(text, n):
    s = span(text)
    assert s.start.year == (n - 1) * 100
    assert s.end.year == n * 100
    assert parse(text)[1] == ""


@pytest.mark.parametrize("text,years", [
    ("un seclo hai", 100), ("dous seclos hai", 200),
])
def test_century_relative_offset(text, years):
    start = ANCHOR - relativedelta(years=years)
    end = start + relativedelta(years=100)
    s = span(text)
    assert (s.start.year, s.start.month, s.start.day) == (start.year, start.month, start.day)
    assert (s.end.year, s.end.month, s.end.day) == (end.year, end.month, end.day)
    assert parse(text)[1] == ""


@pytest.mark.parametrize("text,decades", [
    ("un decada hai", 1), ("trés decadas hai", 3),
])
def test_decade_relative_offset(text, decades):
    start = ANCHOR - relativedelta(years=10 * decades)
    end = start + relativedelta(years=10)
    s = span(text)
    assert (s.start.year, s.start.month, s.start.day) == (start.year, start.month, start.day)
    assert (s.end.year, s.end.month, s.end.day) == (end.year, end.month, end.day)
    assert parse(text)[1] == ""


@pytest.mark.parametrize("text", ["seclo", "decada", "década"])
def test_bare_unit_word_no_match(text):
    nomatch(text)
