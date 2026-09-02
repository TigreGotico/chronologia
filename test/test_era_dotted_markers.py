# -*- coding: utf-8 -*-
"""Era markers written with dots -- "1500 b.c.", "44 B.C.".

The tokenizer shatters a dotted abbreviation on its dots, so "b.c." arrives as
the two tokens ``b`` and ``c``.  Unless something glues them back the era
marker binds nothing: the number reads as a plain Gregorian year and the marker
strands in the remainder.  For BC that is not a stranded token but a sign flip
-- "1500 b.c." answered 1500 instead of -1499, three millennia the wrong way,
at full confidence.

Golds are plain arithmetic, not read back from the extractor: the
astronomical year of *n* BC is ``1 - n`` (1 BC is year 0), so 1500 BC is -1499
and 44 BC is -43.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

_A = datetime(2026, 9, 2)


@pytest.mark.parametrize("lang, text, year", [
    ("en", "1500 b.c.", -1499),
    ("en", "1500 B.C.", -1499),
    ("en", "44 b.c.", -43),
    ("en", "44 B.C.", -43),
    ("en", "the year 1500 b.c.", -1499),
    ("en", "in 300 b.c.", -299),
    ("en", "1500 b.c.e.", -1499),
    ("en", "march 15th, 44 b.c.", -43),
    ("ast", "1500 enantes de la nuesa era", -1499),
])
def test_before_christ_marker_flips_the_sign(lang, text, year):
    r = extract_timespan(text, lang, _A)
    assert r is not None
    assert r.span.start.year == year
    assert r.remainder == ""


@pytest.mark.parametrize("lang, text, year", [
    ("en", "1500 a.d.", 1500),
    ("en", "a.d. 1500", 1500),
    ("en", "2000 c.e.", 2000),
    ("en", "1500 anno domini", 1500),
    ("en", "1500 common era", 1500),
    ("ast", "1500 de la nuesa era", 1500),
])
def test_common_era_marker_is_consumed_not_stranded(lang, text, year):
    r = extract_timespan(text, lang, _A)
    assert r is not None
    assert r.span.start.year == year
    assert r.remainder == ""


@pytest.mark.parametrize("lang, text, year", [
    ("en", "1500 bc", -1499),
    ("en", "1500 bce", -1499),
    ("en", "1500 ad", 1500),
    ("en", "2000 ce", 2000),
    ("en", "march 15th, 44 bc", -43),
    ("en", "in 300 bc", -299),
    ("en", "the year 999", 999),
    ("en", "january 1st, 99", 1999),
    ("en", "'99", 1999),
    ("it", "1500 a.c.", -1499),
    ("it", "1500 avanti cristo", -1499),
    ("it", "1500 dopo cristo", 1500),
    ("ast", "1500 enantes de cristu", -1499),
    ("ast", "1500 dempués de cristu", 1500),
])
def test_undotted_and_bare_year_readings_are_unchanged(lang, text, year):
    r = extract_timespan(text, lang, _A)
    assert r is not None
    assert r.span.start.year == year
    assert r.remainder == ""


@pytest.mark.parametrize("lang, text, year, remainder", [
    ("en", "in 1999 b/c of y2k", 1999, "b/c of y2k"),
    ("en", "route 1500 b-c", 1500, "route b-c"),
    ("en", "1500 b, c", 1500, "b, c"),
    ("en", "2020 a/d converter", 2020, "a/d converter"),
    ("en", "grade a, d 2020", 2020, "grade a, d"),
    ("en", "answer a. d. 1500", 1500, "answer a. d"),
    ("en", "1500: b. c.", 1500, "b. c"),
])
def test_letters_parted_by_other_punctuation_are_not_an_era(
        lang, text, year, remainder):
    """Only a full stop abbreviates: "b/c" is "because", "e V" is "and V".

    The tokenizer drops every separator, so the fragments of an era marker are
    adjacent in the token stream no matter what stood between them.  Reading
    that adjacency alone turns the informal "b/c" into BC -- the number keeps
    its Gregorian reading, three millennia off, and the word that carried the
    real meaning is swallowed.  The year stays Gregorian here and the letters
    stay in the remainder for the caller to see.
    """
    r = extract_timespan(text, lang, _A)
    assert r is not None
    assert r.span.start.year == year
    assert r.remainder == remainder


@pytest.mark.parametrize("lang, text, year, remainder", [
    ("it", "1500 a.e.v.", 1500, "a.e.v"),
    ("it", "1500 a.e.v", 1500, "a.e.v"),
    ("it", "1500 a e v", 1500, "a e v"),
    ("it", "1500 a e V", 1500, "a e V"),
    ("it", "1500 a, e, v", 1500, "a, e, v"),
    ("it", "1500 a/e/v", 1500, "a/e/v"),
    ("it", "1500: a) e) v)", 1500, "a) e) v"),
    ("it", "nel 1500 a. e v", 1500, "a. e v"),
    ("it", "dal 1500 a e V compresi", 1500, "a e V compresi"),
    ("it", "1500 e V", 1500, "V"),
    ("it", "1500 e v", 1500, "v"),
    ("it", "il 3 e V maggio", 2026, "il 3 e V"),
])
def test_italian_areligious_era_abbreviation_is_not_read(
        lang, text, year, remainder):
    """Italian reads no abbreviation of the "era volgare" formula.

    "a.e.v."/"e.v." would have to be matched by the Romance phrase table,
    which sees token text only -- and the tokenizer has already dropped the
    dots by then, so the same rows match the letters written apart.  "a", "e"
    and "v" are an ordinary preposition, the conjunction "and" and a Roman
    numeral, so a row would turn "1500 a e V" into 1499 BC: a three-millennia
    sign flip on ordinary Italian, with an empty remainder to hide it.  The
    year stays Gregorian and the letters stay in the remainder; the
    spelled-out "avanti l'era volgare" reads correctly and is unambiguous.
    """
    r = extract_timespan(text, lang, _A)
    assert r is not None
    assert r.span.start.year == year
    assert r.remainder == remainder


@pytest.mark.parametrize("text, year, remainder", [
    ("3 b.c", -2, ""),
    ("1500 b.c", -1499, ""),
    ("fig 3 b.c", -2, "fig"),
    ("clause 44 a.d", 44, "clause"),
    ("1500 b.c.e", -1499, ""),
])
def test_unterminated_abbreviation_still_reads_as_an_era(text, year, remainder):
    """The closing full stop is optional -- only the inner ones are required.

    "in 3 b.c" is ordinary written English, so the dot between the letters is
    what marks the abbreviation, not the one after the last of them.
    """
    r = extract_timespan(text, "en", _A)
    assert r is not None
    assert r.span.start.year == year
    assert r.remainder == remainder


def test_a_letter_trailing_a_complete_marker_stays_in_the_remainder():
    """"1500 b.c.e.e" is garbage, and the remainder says so.

    The glue takes the longest era spelling it can ("b.c.e.") and leaves what
    follows alone rather than guessing, so the stray letter reaches the caller
    as an unconsumed remainder instead of being silently swallowed.
    """
    r = extract_timespan("1500 b.c.e.e", "en", _A)
    assert r is not None
    assert r.span.start.year == -1499
    assert r.remainder == "e"
