# -*- coding: utf-8 -*-
"""Second-pass sweep (fy): "N bp" (before present) year spans -- the
era_bp construction, not previously covered for this locale (only bc/ad
were, in test_fy_eras_deep.py). The BP epoch is 1950 by convention (the
radiocarbon-dating standard present), so year N BP resolves to the
Gregorian year (1950 - N), a year-wide span. Gold by independent
arithmetic against that fixed epoch -- never pinned from the parser.
"""
import pytest

from ._corpus import AstroDate, start, span, nomatch

_EPOCH = 1950


@pytest.mark.parametrize("text,n", [
    ('100 bp', 100),
    ('500 bp', 500),
    ('2000 bp', 2000),
    ('5000 bp', 5000),
])
def test_years_before_present(text, n):
    assert start(text) == AstroDate(_EPOCH - n, 1, 1)
    assert span(text).start.year == _EPOCH - n


@pytest.mark.parametrize("text", ['bp', '100 jier bp'])
def test_bp_needs_bare_number(text):
    # the fy grammar binds the era_bp construction as "NUM bp" (no unit
    # word) -- a bare marker or a number-plus-unit-word phrasing does not
    # resolve as a BP year.
    nomatch(text)
