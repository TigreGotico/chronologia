# -*- coding: utf-8 -*-
"""Spelled ordinal "décimo" (10th) folds to ORD for Galician -- R87.

The numtag Galician lexicon lists "décimo" both as the ordinal of value 10
and as the denominator of a tenth, the same homograph Spanish, Portuguese
and Italian carry.  "o décimo mes de 2026" must resolve to October instead
of degrading to a bare year_ref match on "2026".

The lexicon lists "undécimo" and "duodécimo" as the ordinals of 11 and 12.
Its 11-19 fractions are the "-avo" forms ("onceavo", "doceavo", "treceavo"
and so on), which do not collide with them.  It has no ordinal entry for
13-19, so the two-word forms stay impossible months.

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


def test_impossible_two_word_ordinal_month_refuses():
    nomatch("o décimo terceiro mes de 2026")
    nomatch("o décimo cuarto mes de 2026")
