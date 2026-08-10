# -*- coding: utf-8 -*-
"""Fused compound spelled ordinals (11th-31st) fold to ORD for Spanish -- R87.

Spanish spells its 11th-19th/21st-29th/31st ordinals as ONE fused word
("decimotercero" = thirteenth, "vigesimoprimero" = twenty-first) rather than
the two-word compound ("décimo tercero") the shared Romance number-fold
already composed through ``extract_number_es``.  The fused spelling was
absent from the fold's word set entirely, so a sentence built on one never
tokenized an ordinal at all: "el decimotercer mes de 2026" silently degraded
to a bare year_ref match on "2026" (span = all of 2026, remainder =
"el decimotercer mes de") instead of refusing outright the way the digit
ordinal ("el 13.º mes de 2026") and English ("the thirteenth month of 2026")
already do (R81, PR #640) -- a silent-wrong, not a mere gap.

Forms and their citation: Real Academia Española, Diccionario panhispánico
de dudas (2005), s.v. "numerales, 2.2" -- the fused compound loses the
tens-word's own written accent ("décimo" -> "decimo-", "vigésimo" ->
"vigesimo-") while the unit component keeps its own ("séptimo" stays
accented in "decimoséptimo"); "undécimo"/"duodécimo" are the classical
11th/12th alternatives RAE lists alongside the productive fused form.
Apocopated forms ("decimotercer", "vigesimoprimer") are used directly
before a masculine singular noun, exactly like "primer"/"tercer" alone.

Golds are computed by independent calendar reasoning (month 1-12 mapped by
hand from the cited ordinal value), never read back from the parser.
"""
import pytest

from ._corpus import start, nomatch


@pytest.mark.parametrize("text,mo", [
    # only 11th and 12th are valid MONTH ordinals; masculine/apocopated/
    # classical-alternative forms
    ("el decimoprimer mes de 2026", 11),
    ("el decimoprimero mes de 2026", 11),
    ("el undécimo mes de 2026", 11),
    ("el decimosegundo mes de 2026", 12),
    ("el duodécimo mes de 2026", 12),
])
def test_compound_ordinal_valid_month(text, mo):
    s = start(text)
    assert (s.year, s.month) == (2026, mo)


@pytest.mark.parametrize("text", [
    # the exact live bug report: 13th month does not exist -- must refuse,
    # never silently fall back to the bare year
    "el decimotercer mes de 2026",
    "el decimotercero mes de 2026",
    "el decimotercera mes de 2026",
    # every other fused form 14th-19th, 21st-31st: all impossible as a month
    "el decimocuarto mes de 2026",
    "el decimoquinto mes de 2026",
    "el decimosexto mes de 2026",
    "el decimoséptimo mes de 2026",
    "el decimoctavo mes de 2026",
    "el decimonoveno mes de 2026",
    "el decimonono mes de 2026",
    "el vigesimoprimer mes de 2026",
    "el vigesimoprimero mes de 2026",
    "el vigesimosegundo mes de 2026",
    "el vigesimotercer mes de 2026",
    "el trigesimoprimer mes de 2026",
])
def test_compound_ordinal_impossible_month_refuses(text):
    nomatch(text)


def test_no_silent_year_fallback_regression():
    """The exact regression this fix closes: a spelled teen ordinal must not
    leave the parser matching only the bare trailing year with the ordinal
    phrase stranded in the remainder."""
    from ._corpus import parse
    r = parse("el decimotercer mes de 2026")
    assert r is None, (
        f"'el decimotercer mes de 2026' must refuse (None); the pre-fix "
        f"defect silently matched the bare year 2026, got {r!r}")
