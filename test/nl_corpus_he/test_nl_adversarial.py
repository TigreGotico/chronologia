# -*- coding: utf-8 -*-
"""Adversarial cases: strings written to BREAK the parser, plus the known
gaps documented as non-matches."""
import pytest

from ._corpus import nomatch, span, start_end, AstroDate


# -- must NOT parse ----------------------------------------------------------
@pytest.mark.parametrize("text", [
    "",                       # empty
    "שלום מה שלומך",          # greeting, no temporal content
    "חתול שחור",              # "a black cat"
    "ירושלים עיר עתיקה",       # a plain declarative sentence
    "לפני",                   # a lone past marker, no count/unit
    "בעוד",                   # a lone future marker
    "בשעה",                   # "at hour" with no reading
    "12345678",              # digit soup: too long to be a year
    "בבוקר",                  # a bare day-part word, no hour
    "חמש",                    # a lone spelled number, no unit/marker
])
def test_no_spurious_parse(text):
    nomatch(text)


# -- documented gap: the dual noun is not a NUM UNIT pair -------------------
@pytest.mark.parametrize("text", [
    "בעוד שבועיים",           # "in a fortnight" (dual) -- known gap
    "לפני יומיים",           # "two days ago" (dual) -- known gap
])
def test_dual_gap(text):
    nomatch(text)


# -- a bare weekday is not a construction here (needs a rel-marker) ----------
@pytest.mark.parametrize("text", ["יום שישי", "שבת", "יום ראשון"])
def test_bare_weekday_no_parse(text):
    nomatch(text)


# -- real dates that MUST survive tricky context ----------------------------
def test_two_dates_leftmost_wins():
    s, e = start_end("15 בינואר 2020 או מרץ 2021")
    assert s == AstroDate(2020, 1, 15) and e == AstroDate(2020, 1, 16)


def test_year_not_swallowed_as_day():
    s, e = start_end("מרץ 2020")
    assert s == AstroDate(2020, 3, 1) and e == AstroDate(2020, 4, 1)


def test_bc_beats_bare_year():
    sp = span("44 לפנה״ס")
    assert sp.start == AstroDate(-43, 1, 1)
