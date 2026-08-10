"""Ordinal-month weekend scopes refuse cleanly, and 'from' works as an
'after'-synonym anchoring an offset to an explicit date -- R84.

Two independent silent-wrong leaks, closed here:

1. "the weekend of the Nth month" ("the weekend of the 5th month", "the
   last weekend of the 13th month"): ``weekend_of_month`` only binds a NAMED
   month (its ``MONTH`` slot), not an ordinal month NUMBER -- there is no
   "the Nth month" scope wired into it, and building one would need new
   grammar (a second ordinal + a bare "month" noun slot), not a small
   extension of the existing ``scoped_ordinal`` machinery. Before the fix,
   the bare ``weekend_ref``/``rel_span_weekend`` reading won on "weekend"
   alone and stranded "of the Nth month" in the remainder -- an
   anchor-relative weekend with the scope silently dropped. Fixed by
   refusing (None) rather than surfacing the truncated span: see
   ``_stranded_ordinal_scope_veto`` in ``chronologia/extract/timespan.py``.

2. "N units from <date>" ("2 weeks from june 1st"): the offset-WITH-
   explicit-anchor construction (``apply_anchored_offset`` in
   ``chronologia/extract/anchored.py``) only recognised "after"/"before" as
   its directional marker, not "from" -- even though "from" is exactly
   synonymous with "after" here ("2 weeks from june 1st" == "2 weeks after
   june 1st" == june 15th the FOLLOWING year, since june 1st this year has
   already passed the anchor). Before the fix, the bare ``calendar_date``
   reference ("june 1st", rolled to next year since the anchor is past it)
   won alone and stranded "2 weeks from" -- a full YEAR off the intended
   answer. Fixed by adding "from" to the marker set used ONLY by this
   construction (never the recurrence "from X to Y" machinery in
   ``nseries.py``, and never the ``date_range`` "from ... to ..."
   construction -- both keep their own pinned behaviour, verified by the
   controls below).

   The sibling "the next N quarters from <date>" case ("the next 2 quarters
   from 500 BC") is NOT extended the same way: ``rel_span_quarter`` counts
   calendar-aligned quarters from the CALL anchor (today) and has no
   "from <explicit date>" order -- accepting one would mean rel_span/
   rel_period/rel_span_quarter counting from an arbitrary start date, a
   bigger change than the marker synonym fix above. Refused instead (see
   ``_stranded_explicit_anchor_veto``), never a present-day span with the
   500 BC anchor silently dropped.

Golds are computed by independent calendar arithmetic (Python's
``date``/``timedelta``), never read back from the parser.
"""
from datetime import date, datetime, timedelta

import pytest

from chronologia import extract_recurrence, extract_timespan
from chronologia.astrodate import AstroDate

A = datetime(2026, 8, 10, 12, 0)


def _result(text, anchor=A):
    return extract_timespan(text, "en", anchor)


def _span(text, anchor=A):
    r = _result(text, anchor)
    return None if r is None else (r.span.start, r.span.end)


# ---------------------------------------------------------------------------
# Defect A: "the weekend of the Nth month" -- refuses, never a stranded
# anchor-relative weekend.
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("text", [
    "the last weekend of the 13th month",
    "the weekend of the 5th month",
])
def test_weekend_of_ordinal_month_refuses(text):
    r = _result(text)
    assert r is None, f"{text!r} should refuse (None), got {r!r}"


# ---------------------------------------------------------------------------
# Defect A regression -- R93: the veto only fired when the stranded tail was
# EXACTLY "of? article? ORD SCOPE_UNIT"; any trailing text after the scope
# noun (a year, "next year", a trailing clause) evaded it and the
# anchor-relative weekend leak resurfaced. The veto must fire whenever the
# stranded tail STARTS WITH the ordinal-scope shape, regardless of what
# follows.
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("text", [
    "the last weekend of the 13th month of 2026",
    "the weekend of the 5th month of 2026",
    "the last weekend of the 13th month next year",
    "the last weekend of the 13th month, please",
    "the last weekend of the 13th month 13 2026",
])
def test_weekend_of_ordinal_month_with_trailing_text_refuses(text):
    r = _result(text)
    assert r is None, f"{text!r} should refuse (None), got {r!r}"


def test_weekend_of_ordinal_month_adjacency_control_unrelated_ordinal_later():
    """Control: a legitimate weekend reading with an UNRELATED later ordinal
    phrase in the remainder must still resolve -- the veto only considers a
    tail immediately adjacent (connected by "of") to the weekend
    construction's own match, not any ordinal-shaped text anywhere in the
    sentence."""
    r = _result("next weekend, then the 3rd month of the project kicks off")
    assert r is not None, "legitimate weekend reading must not be vetoed"
    assert "3rd month" in r.remainder or "month" in r.remainder


# ---------------------------------------------------------------------------
# Defect B: "N units from <date>" -- "from" doubles as "after".
# ---------------------------------------------------------------------------
def test_two_weeks_from_june_1st_matches_after():
    """"2 weeks from june 1st" must read identically to "2 weeks after june
    1st": the anchor (2026-08-10) is already past this year's june 1st, so
    the reference rolls to 2027-06-01, then shifts 2 weeks -> 2027-06-15."""
    got = _result("2 weeks from june 1st")
    want = _result("2 weeks after june 1st")
    assert got is not None and want is not None
    assert (got.span.start, got.span.end) == (want.span.start, want.span.end)
    assert got.remainder == ""
    expected = date(2027, 6, 1) + timedelta(weeks=2)
    assert (got.span.start.year, got.span.start.month, got.span.start.day) \
        == (expected.year, expected.month, expected.day)


def test_two_weeks_after_june_1st_control_unchanged():
    """Pin control: "after" itself is untouched by the "from" marker fix."""
    r = _result("2 weeks after june 1st")
    assert r is not None and r.remainder == ""
    expected = date(2027, 6, 1) + timedelta(weeks=2)
    assert (r.span.start.year, r.span.start.month, r.span.start.day) \
        == (expected.year, expected.month, expected.day)


def test_next_2_quarters_from_bc_refuses():
    """"the next 2 quarters from 500 BC" has no supported reading (rel_span_
    quarter cannot anchor to an explicit date) -- refuses rather than
    stranding "from 500 BC" against a present-day quarter span."""
    r = _result("the next 2 quarters from 500 BC")
    assert r is None, f"should refuse (None), got {r!r}"


def test_from_june_to_august_pinned_as_on_dev():
    """Control: the date_range "from X to Y" construction is UNCHANGED by
    the marker fix -- still the calendar-month span June 1 through Sept 1."""
    r = _result("from june to august")
    assert r is not None
    assert r.remainder == ""
    s, e = r.span.start, r.span.end
    assert (s.year, s.month, s.day) == (2026, 6, 1)
    assert (e.year, e.month, e.day) == (2026, 9, 1)


def test_extract_recurrence_every_monday_from_june_to_august_unchanged():
    """Control: the recurrence "from X to Y" machinery (nseries.py) is
    UNCHANGED -- weekly Monday recurrence bounded by an August 1st UNTIL."""
    r = extract_recurrence("every monday from june to august", "en", A)
    assert r is not None
    assert r.remainder == ""
    rec = r.recurrence
    assert rec.freq == "WEEKLY"
    assert rec.byday == ((None, 0),)
    u = rec.until
    assert (u.year, u.month, u.day) == (2026, 8, 1)


# ---------------------------------------------------------------------------
# Controls: unaffected sibling constructions.
# ---------------------------------------------------------------------------
def test_last_weekend_of_june_control_unchanged():
    r = _result("the last weekend of june")
    assert r is not None and r.remainder == ""
    s, e = r.span.start, r.span.end
    assert (s.year, s.month, s.day) == (2026, 6, 27)
    assert (e.year, e.month, e.day) == (2026, 6, 29)


def test_first_monday_of_october_control_unchanged():
    r = _result("the first monday of october")
    assert r is not None and r.remainder == ""
    s = r.span.start
    assert (s.year, s.month, s.day) == (2026, 10, 5)
