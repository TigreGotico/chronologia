"""Halves and quarters of a NAMED MONTH ("the first half of august" -> Aug
1..Aug 16 12:00, "the second quarter of august" -> Aug 8 18:00..Aug 16 12:00).

Before this construction existed, month NAMES were not ``SCOPE_UNIT``
tokens, so ``half_period`` never matched a month and the bare MONTH
construction won the shared span with its full-month width, stranding
"first half of"/"second half of"/"quarter of" in the remainder -- a
silent-wrong (too-wide) answer.  Halves/quarters are sliced by
:func:`chronologia.subdivide`'s exact elapsed-microsecond convention (the
same one ``month_fuzzy``'s early/mid/late thirds already use): a month is
short enough that no year/month rounding is needed, so a 31-day month's
half lands on a half-day boundary (Aug 16 12:00), while a 28-day February's
half lands exactly at midnight (Feb 15 00:00) and a 29-day (leap) February's
half lands at noon (Feb 15 12:00).  Edges hand-derived (anchor 2017-06-27).

Controls guard the three constructions this must never disturb: the
YEAR-scoped half ("the first half of 2027"), the calendar quarter of a YEAR
("the first quarter of 2027", pinned -- ``quarter_ref``, unrelated
construction), the bare month, and "the first weekend of august"
(``weekend_of_month``, a different slot shape entirely).
"""
import pytest

from chronologia.astrodate import AstroDate
from ._corpus import ANCHOR, start_end, parse


_HALF_CASES = [
    # 31-day month
    ("the first half of august", (2017, 8, 1), (2017, 8, 16, 12)),
    ("the second half of august", (2017, 8, 16, 12), (2017, 9, 1)),
    # 30-day month
    ("the first half of april", (2017, 4, 1), (2017, 4, 16)),
    ("the second half of april", (2017, 4, 16), (2017, 5, 1)),
    # February, non-leap anchor year (2017): 28 days, exact midnight split
    ("the first half of february", (2017, 2, 1), (2017, 2, 15)),
    ("the second half of february", (2017, 2, 15), (2017, 3, 1)),
    # February, leap year (2024, explicit): 29 days, noon split
    ("the first half of february 2024", (2024, 2, 1), (2024, 2, 15, 12)),
    ("the second half of february 2024", (2024, 2, 15, 12), (2024, 3, 1)),
    # explicit non-leap year overrides the anchor
    ("first half of august 2027", (2027, 8, 1), (2027, 8, 16, 12)),
    ("second half of august 2027", (2027, 8, 16, 12), (2027, 9, 1)),
]


@pytest.mark.parametrize("text,s,e", _HALF_CASES)
def test_half_of_month(text, s, e):
    assert start_end(text) == (AstroDate(*s), AstroDate(*e))


_QUARTER_CASES = [
    ("the first quarter of august", (2017, 8, 1), (2017, 8, 8, 18)),
    ("the second quarter of august", (2017, 8, 8, 18), (2017, 8, 16, 12)),
    ("the third quarter of august", (2017, 8, 16, 12), (2017, 8, 24, 6)),
    ("the fourth quarter of august", (2017, 8, 24, 6), (2017, 9, 1)),
]


@pytest.mark.parametrize("text,s,e", _QUARTER_CASES)
def test_quarter_of_month(text, s, e):
    assert start_end(text) == (AstroDate(*s), AstroDate(*e))


# -- controls: must stay exactly as before -----------------------------

def test_half_of_year_unchanged():
    assert start_end("the first half of 2027") == (
        AstroDate(2027, 1, 1), AstroDate(2027, 7, 1))
    assert start_end("the second half of 2027") == (
        AstroDate(2027, 7, 1), AstroDate(2028, 1, 1))


def test_quarter_of_year_unchanged():
    """"first quarter of 2027" is the CALENDAR quarter (``quarter_ref``,
    binding YEAR) -- pinned, unrelated to the new MONTH-binding
    ``quarter_of_month`` construction added here."""
    assert start_end("the first quarter of 2027") == (
        AstroDate(2027, 1, 1), AstroDate(2027, 4, 1))


def test_bare_month_unchanged():
    assert start_end("august") == (AstroDate(2017, 8, 1), AstroDate(2017, 9, 1))


def test_first_weekend_of_month_unchanged():
    """``weekend_of_month`` -- a different slot shape (WEEKEND, not
    half/quarter) -- must not be shadowed by the new orders."""
    s, e = start_end("the first weekend of august")
    assert s == AstroDate(2017, 8, 5)
    assert e == AstroDate(2017, 8, 7)


def test_half_of_the_month_still_refuses():
    """A KNOWN sibling gap, deliberately left unfixed by this change: "the
    first half of THE month" (a deictic reference to the anchor's own
    current month, no MONTH name) does not resolve -- ``half_period``'s new
    orders require a named MONTH slot, and the generic SCOPE_UNIT path
    (used for decade/century/millennium) does not cover "month" either."""
    assert parse("the first half of the month") is None


# -- #658 seam fixes (R101) ---------------------------------------------
#
# Three related defects around this construction's edges, all verified live
# against dev (anchor 2017-06-27) before being fixed here:
#
# (A) a trailing "until <year>" was double-bound -- the same year token both
#     filled the fraction construction's own optional YEAR slot (via the
#     range engine's year-lending) AND, independently, closed the range as a
#     whole calendar year, yielding a self-contradictory span (a half-month
#     start paired with a whole-year end). Fixed by refusing to compose the
#     range in exactly that shape (month-fraction left side, bare-year right
#     side, joined by an until-class marker); the sentence now falls back to
#     the single-span reading with "until <year>" honestly stranded in the
#     remainder, rather than surfacing the contradictory span.
# (B) an interposed word between "of" and the month name ("first half of
#     LEAP february 2028") reopened #658's stranding leak from a different
#     angle: neither half_period nor quarter_of_month tolerates a word there,
#     so the bare month construction won alone and stranded "first half of
#     leap" ahead of it. Fixed with a new leading stranded-fraction-prefix
#     veto (mirrors #651's prefix-tolerant trailing-tail shape, applied to
#     the LEADING side): refuses outright rather than surfacing the
#     too-wide bare-month span.
# (C) "last" was not recognised as a synonym for the final half/quarter
#     ("last half of august", "last quarter of august"), so it stranded and
#     the bare period won at full width. Fixed by adding the existing
#     ``ordlast`` connector ("last"/"final" -- already used by
#     scoped_ordinal/quarter_ref for the same "select the final unit" idea)
#     to half_period's GYEAR/MONTH orders and quarter_of_month's MONTH
#     order. Deliberately NOT added to quarter_of_month/quarter_ref's YEAR
#     case: quarter_ref already binds "last quarter" whole via its
#     ``REL_MARKER quarter_word`` order (the anchor-relative previous-quarter
#     reading) and a same-tokens ordlast order there would collide with it;
#     "last quarter of 2027" is pinned below to the existing relative
#     reading, unchanged.

def test_until_year_not_double_bound():
    """(A) "first half of august, until 2030" no longer resolves to the
    self-contradictory 2030-08-01..2031-01-01 (a half-month start closed by
    a whole-year end). It refuses to compose the range and falls back to
    the single-span half-of-august reading in the ANCHOR year, honestly
    stranding "until 2030"."""
    assert start_end("first half of august, until 2030") == (
        AstroDate(2017, 8, 1), AstroDate(2017, 8, 16, 12))
    assert parse("first half of august, until 2030")[1] == "until 2030"
    assert start_end("first half of august until 2030") == (
        AstroDate(2017, 8, 1), AstroDate(2017, 8, 16, 12))


def test_until_year_not_double_bound_quarter():
    """(A) same double-bind, on quarter_of_month: "third quarter of
    february, until 2030". February 2017 (28 days, anchor year) splits into
    four exact 7-day quarters (Feb1/8/15/22/Mar1); the third is Feb15..22."""
    assert start_end("third quarter of february, until 2030") == (
        AstroDate(2017, 2, 15), AstroDate(2017, 2, 22))
    assert parse("third quarter of february, until 2030")[1] == "until 2030"


def test_first_half_of_august_2030_unchanged():
    """Control (A): an explicit trailing year with NO until-marker is the
    ordinary half_period MONTH order and must resolve exactly as before --
    the double-bind veto only fires on the until-class connector."""
    assert start_end("first half of august 2030") == (
        AstroDate(2030, 8, 1), AstroDate(2030, 8, 16, 12))


def test_first_half_of_august_unchanged():
    """Control (A): the bare (yearless) form, anchor year, unchanged."""
    assert start_end("first half of august") == (
        AstroDate(2017, 8, 1), AstroDate(2017, 8, 16, 12))


def test_june_until_year_pinned_unchanged():
    """Control (A): a bare MONTH (not a half/quarter-of-month fraction) left
    of an until-class bare year is UNRELATED to this fix -- the veto is
    scoped to the fraction constructions only -- and keeps its pre-existing
    (year-lent-then-extended-to-year-end) reading."""
    assert start_end("june until 2030") == (
        AstroDate(2030, 6, 1), AstroDate(2031, 1, 1))


def test_interposed_word_strands_fraction_refuses():
    """(B) "first half of LEAP february 2028" -- an unsupported word wedged
    between "of" and the month -- refuses rather than silently surfacing
    the bare "february 2028" (with "first half of leap" dropped)."""
    assert parse("first half of leap february 2028") is None
    assert parse("first half of leap february") is None


def test_first_half_of_february_adjacent_still_works():
    """Control (B): the #658 adjacent case (no interposed word) is
    untouched by the new leading veto."""
    assert start_end("first half of february") == (
        AstroDate(2017, 2, 1), AstroDate(2017, 2, 15))


def test_bare_month_with_year_unchanged():
    """Control (B): a plain "MONTH YEAR" with no fraction prefix at all is
    untouched by the new leading veto."""
    assert start_end("february 2028") == (
        AstroDate(2028, 2, 1), AstroDate(2028, 3, 1))


_LAST_HALF_CASES = [
    ("last half of august", (2017, 8, 16, 12), (2017, 9, 1)),
    ("last half of 2027", (2027, 7, 1), (2028, 1, 1)),
]


@pytest.mark.parametrize("text,s,e", _LAST_HALF_CASES)
def test_last_half_is_final_half(text, s, e):
    """(C) "last" is a synonym for the final half (== "second")."""
    assert start_end(text) == (AstroDate(*s), AstroDate(*e))


def test_last_quarter_of_month_is_fourth():
    """(C) "last quarter of august" == "fourth quarter of august". August
    (31 days) splits into four exact 7d18h quarters (Aug1/8-18h/16-12h/
    24-6h/Sep1); the fourth is Aug24 06:00..Sep1."""
    assert start_end("last quarter of august") == (
        AstroDate(2017, 8, 24, 6), AstroDate(2017, 9, 1))


def test_last_quarter_of_year_pinned_relative_reading():
    """Control (C): "last quarter of 2027" deliberately keeps its
    pre-existing anchor-relative reading (quarter_ref's ``REL_MARKER
    quarter_word`` order, "the most recently ended calendar quarter") with
    "of 2027" stranded, rather than being redirected to "Q4 2027" -- adding
    an ordlast-of-YEAR order to quarter_of_month would collide with that
    established reading on the identical tokens "last quarter". Anchor
    2017-06-27 sits in Q2 2017, so the last (most recently ended) quarter is
    Q1 2017."""
    span_, remainder = parse("last quarter of 2027")
    assert (span_.start, span_.end) == (
        AstroDate(2017, 1, 1), AstroDate(2017, 4, 1))
    assert remainder == "of 2027"
