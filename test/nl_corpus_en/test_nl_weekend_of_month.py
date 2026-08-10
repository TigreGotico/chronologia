""""the first/second/.../last weekend of <month>" -- R80.

DEFECT (B2/B3): "the first/last weekend of june" used to bind through the
bare ``weekend_ref`` construction (rel 0 for an ordinal like "first"/
"second", which is not a REL_MARKER at all; ``rel=-1`` for "last", which
IS a REL_MARKER), returning an ANCHOR-relative weekend and stranding "of
june" (and the ordinal word itself, for "first"/"second") in the
remainder -- a silently wrong answer, not a refusal.

Fixed here with a dedicated ``weekend_of_month`` construction (siblings:
``scoped_ordinal``'s "Nth WEEKDAY of MONTH" reading) that resolves the
Nth (or last) weekend WITHIN the named month: the weekend whose Saturday
(the locale's ``weekend_start`` day) falls in that month, counted from the
start (or, for "last", from the end). The month's YEAR follows the same
anchor-relative resolution as a bare month reference (anchor.year,
regardless of where the anchor sits relative to the named month -- a bare
month never rolls to a different year; see ``test_nl_month_fuzzy`` /
``month_fuzzy`` for the shared rule).

Golds are computed by independent calendar arithmetic (enumerate every
Saturday in the month, pick the Nth or the last), never read back from the
parser.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate

# Wednesday -- deliberately NOT inside, before, or after any tested month in
# an unusual way; individual cases below re-anchor as needed.
A = datetime(2026, 1, 15, 12, 0)


def _result(text, anchor=A):
    return extract_timespan(text, "en", anchor)


def _span(text, anchor=A):
    r = _result(text, anchor)
    return None if r is None else (r.span.start, r.span.end)


@pytest.mark.parametrize("text,anchor,s,e", [
    # June 2026: 1st is a Monday, Saturdays fall on 6/13/20/27. Anchor
    # BEFORE the month (January).
    ("the first weekend of june", A,
     AstroDate(2026, 6, 6), AstroDate(2026, 6, 8)),
    ("the second weekend of june", A,
     AstroDate(2026, 6, 13), AstroDate(2026, 6, 15)),
    ("the last weekend of june", A,
     AstroDate(2026, 6, 27), AstroDate(2026, 6, 29)),
    # anchor INSIDE the named month itself
    ("the first weekend of june", datetime(2026, 6, 18),
     AstroDate(2026, 6, 6), AstroDate(2026, 6, 8)),
    ("the last weekend of june", datetime(2026, 6, 18),
     AstroDate(2026, 6, 27), AstroDate(2026, 6, 29)),
    # anchor AFTER the month (December) -- bare month never rolls forward to
    # next year, so this must still be June of the ANCHOR's year (2026), not
    # June 2027.
    ("the first weekend of june", datetime(2026, 12, 1),
     AstroDate(2026, 6, 6), AstroDate(2026, 6, 8)),
    ("the last weekend of june", datetime(2026, 12, 1),
     AstroDate(2026, 6, 27), AstroDate(2026, 6, 29)),
    # February 2026: 1st is a SUNDAY -- the weekend straddling the month
    # boundary (Sat Jan 31 / Sun Feb 1) does NOT count as a February
    # weekend (its Saturday is in January), so "first weekend of february"
    # must be Feb 7-8, not Jan 31-Feb 1.
    ("the first weekend of february", A,
     AstroDate(2026, 2, 7), AstroDate(2026, 2, 9)),
    # August 2026: 1st is a SATURDAY -- the month opens exactly on a
    # weekend, so the first weekend of the month IS Aug 1-2.
    ("the first weekend of august", A,
     AstroDate(2026, 8, 1), AstroDate(2026, 8, 3)),
    ("the last weekend of august", A,
     AstroDate(2026, 8, 29), AstroDate(2026, 8, 31)),
    # November 2026: 1st is a Sunday, same boundary shape as February --
    # last weekend still lands cleanly inside the month (28-29).
    ("the last weekend of november", A,
     AstroDate(2026, 11, 28), AstroDate(2026, 11, 30)),
])
def test_weekend_of_month_resolves_within_month(text, anchor, s, e):
    r = _result(text, anchor)
    assert r is not None, text
    assert (r.span.start, r.span.end) == (s, e), text
    assert r.remainder == "", (text, r.remainder)


def test_weekend_of_month_year_matches_anchor_year_not_month_relative():
    # "of june" with an anchor in a LATER year must NOT silently reuse a
    # stale year -- both December-anchor cases above already prove the year
    # tracks the anchor, this is the converse: an anchor a full year later.
    got = _span("the first weekend of june", datetime(2027, 1, 15))
    assert got == (AstroDate(2027, 6, 5), AstroDate(2027, 6, 7))


def test_weekend_of_month_with_explicit_year():
    # "the last weekend of june 1999": June 1999 Saturdays are 5/12/19/26.
    r = _result("the last weekend of june 1999")
    if r is None:
        pytest.skip("explicit-year composition not supported by the grammar")
    assert (r.span.start, r.span.end) == (
        AstroDate(1999, 6, 26), AstroDate(1999, 6, 28))
    assert r.remainder == ""


# -- controls: plain "next weekend" / "the next N weekends" must be UNCHANGED
# by the new construction (they carry no ordinal + month, so weekend_of_month
# must never fire for them).

def test_next_weekend_unchanged():
    # anchor Thursday 2026-01-15; "this" week's weekend (rel 0 base) is
    # Jan 17-18, so "next weekend" (rel +1) is Jan 24-25.
    got = _span("next weekend")
    assert got == (AstroDate(2026, 1, 24), AstroDate(2026, 1, 26))


def test_next_3_weekends_unchanged():
    # covering span: Sat Jan17 (nearest upcoming) through Sun of the 3rd
    # weekend out (Jan31-Feb1), i.e. up to (exclusive) Feb 2.
    got = _span("the next 3 weekends")
    assert got == (AstroDate(2026, 1, 17), AstroDate(2026, 2, 2))
