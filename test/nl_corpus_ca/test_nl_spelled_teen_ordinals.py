# -*- coding: utf-8 -*-
"""Spelled 11th-19th ordinals fold to ORD for Catalan -- R87.

Catalan spells its 11th-19th ordinals identically to the FRACTION
denominator of the same value ("tretzè" = thirteenth *and* a-thirteenth,
"dotzè" = twelfth *and* a-twelfth -- unlike Spanish/Italian/Portuguese,
EVERY Catalan ordinal 11-19 is a homograph of its fraction, not just the
tens word itself).  The shared Romance number-fold already resolved this
family of homograph for the 1st-9th UNIT ordinals ("quart"/"cuarto" = fourth
vs. a-quarter) but the mechanism only scanned ORDINAL_UNITS, not
ORDINAL_TENS, so "tretzè"/"dotzè" and the rest of the Catalan 11-19 series
were silently subtracted from the fold's word set as fraction words and
never reached ``scoped_ordinal`` at all: "el tretzè mes de 2026" degraded to
a bare year_ref match on "2026" instead of refusing (no 13th month exists),
same defect class as R81/PR #640.

Source: standard Catalan ordinal-numeral vocabulary (``ovos_number_parser``
``numbers_ca.NumberVocabulary.ORDINAL_TENS``/``FRACTION``, both listing
identical surfaces for 11-19 -- "onzè".."dinovè").

Golds are computed by independent calendar reasoning, never read back from
the parser.
"""
import pytest

from ._corpus import start, nomatch, parse


@pytest.mark.parametrize("text,mo", [
    # only 11th and 12th are valid MONTH ordinals
    ("l'onzè mes de 2026", 11),
    ("el dotzè mes de 2026", 12),
])
def test_teen_ordinal_valid_month(text, mo):
    s = start(text)
    assert (s.year, s.month) == (2026, mo)


@pytest.mark.parametrize("text", [
    # the live bug report: 13th month does not exist -- must refuse
    "el tretzè mes de 2026",
    # 14th-19th: all impossible as a month
    "el catorzè mes de 2026",
    "el quinzè mes de 2026",
    "el setzè mes de 2026",
    "el dissetè mes de 2026",
    "el divuitè mes de 2026",
    "el dinovè mes de 2026",
])
def test_teen_ordinal_impossible_month_refuses(text):
    nomatch(text)


def test_no_silent_year_fallback_regression():
    r = parse("el tretzè mes de 2026")
    assert r is None, (
        f"'el tretzè mes de 2026' must refuse (None); the pre-fix defect "
        f"silently matched the bare year 2026, got {r!r}")
