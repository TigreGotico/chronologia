# -*- coding: utf-8 -*-
"""Spelled ordinal "décimo" (10th) folds to ORD for Galician -- R87.

Galician "décimo" is at once the ORDINAL_TENS surface for 10th and the
FRACTION denominator for a-tenth (``NumberVocabulary.FRACTION[10] ==
"décimo"``), the same homograph collision Spanish/Portuguese/Italian carry.
The shared Romance number-fold already resolved this class of homograph for
1st-9th UNIT ordinals but not for a TENS word, so "décimo" was silently
subtracted from the fold's word set: "o décimo mes de 2026" degraded to a
bare year_ref match on "2026" instead of resolving to October.

Galician's own 11th-19th ordinals ("undécimo", "duodécimo",
"decimoterceiro"..."decimonoveno") are each listed as a single complete
surface in ``NumberVocabulary.ORDINAL_TENS`` and do NOT collide with the
FRACTION table (Galician spells those fractions "onceavo"/"doceavo"/
"treceavo"/... instead), so they were already correctly folding before this
fix and are locked down here only as regression controls.

Source: ``ovos_number_parser`` ``numbers_gl.NumberVocabulary`` (ORDINAL_TENS
and FRACTION tables).

Golds are computed by independent calendar reasoning, never read back from
the parser.
"""
from ._corpus import start, nomatch, parse


def test_decimo_tens_homograph_valid_month():
    # the live regression: pre-fix this silently matched the bare year 2026
    s = start("o décimo mes de 2026")
    assert (s.year, s.month) == (2026, 10)


def test_no_silent_year_fallback_regression():
    r = parse("o décimo mes de 2026")
    assert r is not None and r.remainder == "", (
        f"'o décimo mes de 2026' must resolve to October 2026 with an "
        f"empty remainder; the pre-fix defect silently matched the bare "
        f"year 2026 with 'o décimo mes de' stranded, got {r!r}")


def test_already_working_teen_ordinals_regression_controls():
    # not a homograph in Galician -- these already worked; kept as controls
    assert (start("o undécimo mes de 2026").year,
            start("o undécimo mes de 2026").month) == (2026, 11)
    assert (start("o duodécimo mes de 2026").year,
            start("o duodécimo mes de 2026").month) == (2026, 12)


def test_impossible_ordinal_month_still_refuses():
    # 13th/14th month do not exist -- must refuse, not fabricate a span
    nomatch("o decimoterceiro mes de 2026")
    nomatch("o decimocuarto mes de 2026")
