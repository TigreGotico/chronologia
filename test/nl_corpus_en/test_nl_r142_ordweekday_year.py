# -*- coding: utf-8 -*-
"""R142 -- "first/last <weekday> of <bare YEAR>" silently ignored the year and
answered relative to the anchor.

Before the fix, no grammar order bound WEEKDAY together with a bare trailing
GYEAR (a YEAR slot only ever bound alongside a MONTH, in "ORD WEEKDAY of
MONTH of? YEAR?"). "last monday of 2026" therefore fell through to the
anchor-relative ``weekday_ref`` reading ("last monday"), silently stranding
"of 2026" in the remainder and answering next to the anchor date instead of
inside the named year.

The fix adds an ordinal-weekday-of-YEAR construction to the shared
``base_grammar`` ``scoped_ordinal`` orders (``ORD/ordlast WEEKDAY of?|in
GYEAR``) and a resolver branch (``_nth_weekday_of_year``) that scans the
named year (never the anchor) for the Nth/last occurrence of that weekday.

Expected dates below are computed by INDEPENDENT arithmetic -- a plain
``datetime.date`` weekday scan over the named year -- never by reading back
the parser's own output.
"""
from datetime import date, datetime, timedelta

import pytest

from chronologia import extract_timespan

LANG = "en"
ANCHOR = datetime(2026, 8, 12)
_A = ANCHOR


def _nth_weekday(year, weekday, n):
    """Independent reference implementation: Mon=0 .. Sun=6."""
    jan1 = date(year, 1, 1)
    first = jan1 + timedelta(days=(weekday - jan1.weekday()) % 7)
    days = []
    d = first
    while d.year == year:
        days.append(d)
        d += timedelta(days=7)
    return days[n - 1] if n > 0 else days[n]


def _span(text, anchor=_A):
    r = extract_timespan(text, LANG, anchor)
    assert r is not None, f"{text!r} did not parse (expected a span)"
    return r[0]


def _nomatch(text, anchor=_A):
    r = extract_timespan(text, LANG, anchor)
    assert r is None, f"{text!r} unexpectedly parsed to {r!r}"


MONDAY = 0
TUESDAY = 1
FRIDAY = 4


@pytest.mark.parametrize("text,expected", [
    ("last monday of 2026", _nth_weekday(2026, MONDAY, -1)),
    ("first monday in 2027", _nth_weekday(2027, MONDAY, 1)),
    ("second tuesday of 2027", _nth_weekday(2027, TUESDAY, 2)),
    ("last friday of 2026", _nth_weekday(2026, FRIDAY, -1)),
    ("first monday of 2027", _nth_weekday(2027, MONDAY, 1)),
])
def test_ordinal_weekday_of_bare_year(text, expected):
    span = _span(text)
    assert span.start.year == expected.year
    assert span.start.month == expected.month
    assert span.start.day == expected.day
    assert (span.end - span.start).total_seconds() == 86400


def test_year_is_not_the_anchor_year():
    # the literal shape of the defect: the answer must fall inside the named
    # year, never the anchor's year (2026 in a phrase naming 2027).
    span = _span("first monday of 2027")
    assert span.start.year == 2027


def test_control_ordinal_weekday_of_named_month_still_works():
    # the "ORD WEEKDAY of MONTH of? YEAR?" path (unaffected by this fix) must
    # keep resolving exactly as before -- pinned so the new bare-year order
    # cannot regress the named-month reading it sits alongside.
    expected = _nth_weekday(2027, MONDAY, 1)
    assert expected == date(2027, 1, 4)
    span = _span("first monday of january 2027")
    assert (span.start.year, span.start.month, span.start.day) == (2027, 1, 4)


def test_out_of_range_ordinal_refuses_whole_extraction():
    # a year only ever has 52 or 53 of any given weekday -- a 54th refuses
    # the WHOLE extraction (impossible-ordinal policy), never falls back to
    # some other partial reading.
    _nomatch("54th monday of 2027")


def test_embedded_in_sentence():
    span = _span("let's meet on the last monday of 2026 for review")
    expected = _nth_weekday(2026, MONDAY, -1)
    assert (span.start.year, span.start.month, span.start.day) == \
        (expected.year, expected.month, expected.day)
