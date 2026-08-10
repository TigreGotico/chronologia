# -*- coding: utf-8 -*-
"""Spelled 11th-31st ordinals fold to ORD for Italian -- R87.

Italian spells its 11th-19th ordinals identically to the FRACTION
denominator of the same value ("tredicesimo" = thirteenth *and*
a-thirteenth), a homograph the shared Romance number-fold already resolves
positionally for units 1st-9th ("quarto"/"cuarto" = fourth vs. a-quarter) but
not for these -- ORDINAL_TENS only lists the round tens (10th/20th/.../90th),
so the collision was invisible to the existing mechanism and the words fell
out of the fold's vocabulary entirely. 21st-31st are absent from the
vocabulary outright: Italian fuses the cardinal's stem onto "-esimo"
("ventuno" -> "ventunesimo"), a spelling ``NumberVocabulary`` does not carry
at all (only the round tens do).  Without either, "il tredicesimo mese del
2026" silently degraded to a bare year_ref match on "2026" instead of
refusing (no 13th month exists), the same defect class R81/PR #640 closed
for the digit ordinal and English.

Source: Treccani / Accademia della Crusca, "numerali ordinali" -- 11th-19th
borrow the cardinal's stem + "-esimo" and are genuinely homographic with the
same-value fraction; 21st+ elide the cardinal's final vowel before
"-esimo" except where the cardinal itself ends in an accented vowel (23rd
"ventitré" keeps its final "e": "ventitreesimo").

Golds are computed by independent calendar reasoning, never read back from
the parser.
"""
import pytest

from ._corpus import start, nomatch, parse


@pytest.mark.parametrize("text,mo", [
    # only 11th and 12th are valid MONTH ordinals
    ("il undicesimo mese del 2026", 11),
    ("il dodicesimo mese del 2026", 12),
])
def test_teen_ordinal_valid_month(text, mo):
    s = start(text)
    assert (s.year, s.month) == (2026, mo)


@pytest.mark.parametrize("text", [
    # the live bug report: 13th month does not exist -- must refuse
    "il tredicesimo mese del 2026",
    # 14th-19th, 21st+: all impossible as a month
    "il quattordicesimo mese del 2026",
    "il quindicesimo mese del 2026",
    "il sedicesimo mese del 2026",
    "il diciassettesimo mese del 2026",
    "il diciottesimo mese del 2026",
    "il diciannovesimo mese del 2026",
    "il ventunesimo mese del 2026",
    "il ventiduesimo mese del 2026",
    "il trentunesimo mese del 2026",
])
def test_teen_or_compound_ordinal_impossible_month_refuses(text):
    nomatch(text)


def test_no_silent_year_fallback_regression():
    r = parse("il tredicesimo mese del 2026")
    assert r is None, (
        f"'il tredicesimo mese del 2026' must refuse (None); the pre-fix "
        f"defect silently matched the bare year 2026, got {r!r}")
