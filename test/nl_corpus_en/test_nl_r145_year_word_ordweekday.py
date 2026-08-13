# -*- coding: utf-8 -*-
"""R145 (en) -- "the first/last <weekday> of the year"/"of this year" refused
to parse, and "every last <weekday> of the year" silently downgraded to a
MONTHLY rule with "of the year" stranded.

R142 (see ``test_nl_r142_ordweekday_year.py``) taught the engine to resolve
"the last monday of <bare YEAR>" WITHIN the named year. This defect is the
sibling gap it left behind: the "of the year"/"of this year" surfaces (naming
the ANCHOR's own year rather than an explicit ``GYEAR``) had no resolver path
at all and cleanly refused (returned ``None``), and the recurrence engine's
"every ... of [every] month" tail never recognised a trailing "year" unit,
so "every last monday of the year" fell through to a weaker finder that read
only "last monday" as a bare MONTHLY rule -- a SILENTLY WRONG frequency, not
a refusal.

Expected dates/rules below are computed by INDEPENDENT arithmetic -- a plain
``datetime.date`` weekday scan over the anchor's calendar year -- never read
back from the parser.
"""
from datetime import date, datetime, timedelta

import pytest

from chronologia import extract_recurrence, extract_timespan

LANG = "en"
ANCHOR = datetime(2026, 8, 13, 10, 0)


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


def _span(text, anchor=ANCHOR):
    r = extract_timespan(text, LANG, anchor)
    assert r is not None, f"{text!r} did not parse (expected a span)"
    return r[0]


MONDAY = 0


@pytest.mark.parametrize("text,expected", [
    ("the last monday of the year", _nth_weekday(2026, MONDAY, -1)),
    ("the last monday of this year", _nth_weekday(2026, MONDAY, -1)),
    ("the first monday of the year", _nth_weekday(2026, MONDAY, 1)),
    ("the first monday of this year", _nth_weekday(2026, MONDAY, 1)),
])
def test_ordinal_weekday_of_anchor_year(text, expected):
    span = _span(text)
    assert (span.start.year, span.start.month, span.start.day) == \
        (expected.year, expected.month, expected.day)
    assert (span.end - span.start).total_seconds() == 86400


def test_year_is_the_anchor_year_not_2027():
    # the literal shape of this defect's requirement: "of the year" resolves
    # against the ANCHOR's year (2026), consistent with R142's bare-GYEAR
    # reading resolving within the NAMED year.
    span = _span("the last monday of the year")
    assert span.start.year == 2026
    assert span.start == date(2026, 12, 28)


def test_no_remainder_stranded():
    r = extract_timespan("the last monday of the year", LANG, ANCHOR)
    assert r is not None
    assert r[1].strip() == ""


def test_control_ordinal_weekday_of_bare_gyear_still_works():
    # the R142 bare-GYEAR reading (unaffected by this fix) must keep
    # resolving exactly as before.
    expected = _nth_weekday(2027, MONDAY, -1)
    span = _span("last monday of 2027")
    assert (span.start.year, span.start.month, span.start.day) == \
        (expected.year, expected.month, expected.day)


def test_control_ordinal_weekday_of_this_month_still_works():
    span = _span("the first monday of this month")
    assert span.start == date(2026, 8, 3)


# -- recurrence: "every last <weekday> of the year" -----------------------

def test_recurrence_last_monday_of_the_year_is_yearly():
    r = extract_recurrence("every last monday of the year", LANG)
    assert r is not None
    assert r.recurrence.freq == "YEARLY"
    assert r.recurrence.byday == ((-1, MONDAY),)
    assert not r.recurrence.bymonth
    assert r.remainder.strip() == ""


def test_recurrence_first_tuesday_of_the_year_is_yearly():
    TUESDAY = 1
    r = extract_recurrence("every first tuesday of the year", LANG)
    assert r is not None
    assert r.recurrence.freq == "YEARLY"
    assert r.recurrence.byday == ((1, TUESDAY),)


def test_recurrence_control_last_monday_of_every_month_stays_monthly():
    # the pre-existing MONTHLY reading (unaffected by this fix) must not
    # regress into a yearly one.
    r = extract_recurrence("every last monday of every month", LANG)
    assert r is not None
    assert r.recurrence.freq == "MONTHLY"
    assert r.recurrence.byday == ((-1, MONDAY),)


def test_recurrence_control_last_monday_of_january_stays_yearly_bymonth():
    r = extract_recurrence("every last monday of january", LANG)
    assert r is not None
    assert r.recurrence.freq == "YEARLY"
    assert r.recurrence.bymonth == (1,)
    assert r.recurrence.byday == ((-1, MONDAY),)
