# -*- coding: utf-8 -*-
"""Adversarial cases: strings written to BREAK the parser, plus the known
gaps documented as non-matches.  A parser is only as trustworthy as the
things it refuses to parse."""
import pytest

from ._corpus import nomatch, span, start_end, AstroDate


# -- must NOT parse ----------------------------------------------------------
@pytest.mark.parametrize("text", [
    "",                       # empty
    "مرحبا كيف حالك",         # greeting, no temporal content
    "قطة سوداء",              # "a black cat"
    "القاهرة مدينة كبيرة",     # a plain declarative sentence
    "بعد",                    # a lone direction marker, no count/unit
    "قبل",                    # lone past marker
    "خمسة",                   # a lone spelled number, no unit/marker
    "الساعة",                 # "the hour" with no reading
    "12345678",              # digit soup: too long to be a year
    "صباحا",                  # a bare meridiem word, no hour
])
def test_no_spurious_parse(text):
    nomatch(text)


# -- documented gaps: the dual noun is not a NUM UNIT pair -------------------
@pytest.mark.parametrize("text", [
    "بعد أسبوعين",            # "in a fortnight" (dual) -- known gap
    "قبل يومين",             # "two days ago" (dual) -- known gap
])
def test_dual_gap(text):
    nomatch(text)


# -- a bare weekday is not a construction here (needs a rel-marker) ----------
@pytest.mark.parametrize("text", ["الجمعة", "السبت", "الأحد"])
def test_bare_weekday_no_parse(text):
    nomatch(text)


# -- adversarial: real dates that MUST survive tricky context ---------------
def test_two_dates_first_wins_leftmost():
    # two dates; the leftmost span is returned, the rest is residue
    s, e = start_end("15 يناير 2020 أو مارس 2021")
    assert s == AstroDate(2020, 1, 15) and e == AstroDate(2020, 1, 16)


def test_year_not_swallowed_as_day():
    # "2020" is a year, not a day, when it stands with a month
    s, e = start_end("مارس 2020")
    assert s == AstroDate(2020, 3, 1) and e == AstroDate(2020, 4, 1)


def test_bc_beats_bare_year():
    # "44 ق.م" must read as 44 BC, not the bare number 44
    sp = span("44 ق.م")
    assert sp.start == AstroDate(-43, 1, 1)


def test_meridiem_does_not_leak_into_year():
    # "م" (AD marker) is also the pm abbreviation; with a 4-digit year it is AD
    s, e = start_end("1492 م")
    assert s == AstroDate(1492, 1, 1) and e == AstroDate(1493, 1, 1)
