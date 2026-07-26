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


# -- a bare full weekday names its next strictly-future occurrence ----------
@pytest.mark.parametrize("text,idx", [("יום שישי", 4), ("שבת", 5), ("יום ראשון", 6)])
def test_bare_weekday_resolves_next(text, idx):
    from datetime import timedelta
    from ._corpus import ANCHOR, span
    ahead = (idx - ANCHOR.weekday()) % 7 or 7
    exp = (ANCHOR + timedelta(days=ahead)).date()
    s = span(text).start
    assert (s.year, s.month, s.day) == (exp.year, exp.month, exp.day)


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
