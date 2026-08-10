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
