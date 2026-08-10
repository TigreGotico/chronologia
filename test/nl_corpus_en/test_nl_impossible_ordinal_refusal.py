"""Impossible scoped-ordinal constructions refuse consistently -- R81.

Policy (owner-approved): "the Nth UNIT of SCOPE" where the Nth unit does not
exist inside that scope ("the 13th month of 2026", "the 0th week of may")
must return ``None`` -- an honest refusal -- never a silently-projected or
partially-bound result. There is no overflow projection: "the 13th month of
2026" is NOT January 2027.

Two independent defects produced the leak, both closed here:

1. ``scoped_ordinal``'s bare "ORD SCOPE_UNIT" absolute-period order (meant
   for "the 3rd century") also matched day/week/month/quarter scope words,
   but ``_ABSOLUTE`` (chronologia/extract/ranges.py) only has entries for
   decade/century/millennium -- so that reading ALWAYS failed to resolve
   (``KeyError``) for day/week/month, even for a perfectly valid ordinal
   ("the 12th month of 2026"). With no "of <bare year>" order for day/month
   (only "of the year <year>" existed), the doomed absolute-period reading
   was the only thing that matched "the 12th/13th month of 2026", stranding
   "the Nth month of" and letting a bare year_ref silently claim "2026".
   Fixed by a narrow new order (``DMUNIT``, day/month only -- week and
   quarter already resolve a bare trailing year through their own
   dedicated ``iso_week_ref``/``quarter_ref`` constructions) so
   "the 12th month of 2026" now resolves to December and "the 13th month
   of 2026" refuses outright (no fallback reading remains once the
   now-winning full-span match fails to resolve).
2. An ordinal that never binds at all -- 0, or any value below 1 -- never
   becomes a ``scoped_ordinal``/``weekend_of_month`` candidate in the first
   place (the ``ORD`` slot requires ``value >= 1``), so "the 0th week of
   may" / "the 0th weekend of june" never had a competing full-span match
   to lose to; only the bare "may"/"weekend" reading matched, stranding
   "the 0th week of"/"the 0th weekend of" as it would strand any other
   nonsense prefix. Fixed by extending the residue-veto machinery
   (``_impossible_date_veto_inner``) to recognise a stranded
   "<ordinal> <unit> of" run immediately before ANY recognised reference
   (the eventual composition winner or a same-position runner-up a weaker
   composition discarded) as proof of an incomplete parse, refusing the
   whole extraction rather than surfacing the truncated fallback.

Golds are computed by independent calendar arithmetic (Python's ``date``/
ISO calendar), never read back from the parser.
"""
from datetime import date, datetime

import pytest

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate

A = datetime(2026, 8, 10, 12, 0)


def _result(text, anchor=A):
    return extract_timespan(text, "en", anchor)


def _span(text, anchor=A):
    r = _result(text, anchor)
    return None if r is None else (r.span.start, r.span.end)


# ---------------------------------------------------------------------------
# Impossible constructions: must refuse (None), never a partial/wrong span.
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("text", [
    # verified live leaks (the bug reports this fix closes)
    "the 13th month of 2026",
    "the 0th week of may",
    # out-of-range day-of-year / week-of-year / month-of-year, bare year
    "the 0th day of january",
    "the 0th day of 2026",
    "the 0th month of 2026",
    "the 366th day of 2026",
    "the 100th month of 2026",
    # zero/negative-ordinal weekend-of-month (never binds ORD at all)
    "the 0th weekend of june",
    "0th weekend of june",
    # out-of-range weekend/week already covered by #639/#244 -- kept here as
    # same-defect-class controls so a future regression on the shared veto
    # machinery is caught by this file too
    "the 7th week of may",
    "the 6th weekend of june",
    "the 32nd of january",
    "february 30",
    # no article, still refuses
    "13th month of 2026",
    "0th week of may",
])
def test_impossible_ordinal_refuses(text):
    assert _result(text) is None, f"{text!r} should refuse (None), got {_result(text)!r}"


def test_no_overflow_projection_13th_month_is_not_january_next_year():
    """The exact regression the leak produced: "the 13th month of 2026" is
    NOT silently read as January 2027 (or any other projected date) -- it
    must be a flat refusal with nothing bound."""
    r = _result("the 13th month of 2026")
    assert r is None


def test_no_overflow_projection_53rd_day_of_a_short_year():
    # 2026 is not special here, but a day well past 366 has no valid mapping
    # in ANY year; make sure the resolver never wraps into a later year.
    assert _result("the 999th day of 2026") is None


# ---------------------------------------------------------------------------
# Positive controls: legitimate "Nth unit of scope" constructions must keep
# resolving exactly as before -- to an EXACT span, with an EMPTY remainder.
# ---------------------------------------------------------------------------
def test_twelfth_month_of_bare_year_is_december():
    r = _result("the 12th month of 2026")
    assert r is not None
    assert r.remainder == ""
    assert r.span.start == AstroDate(2026, 12, 1)
    assert r.span.end == AstroDate(2027, 1, 1)


def test_twelfth_month_of_bare_year_no_article():
    r = _result("12th month of 2026")
    assert r is not None
    assert r.remainder == ""
    assert r.span.start == AstroDate(2026, 12, 1)
    assert r.span.end == AstroDate(2027, 1, 1)


def test_first_day_of_bare_year_is_january_first():
    r = _result("the 1st day of 2026")
    assert r is not None
    assert r.remainder == ""
    assert r.span.start == AstroDate(2026, 1, 1)
    assert r.span.end == AstroDate(2026, 1, 2)


def test_hundredth_day_of_bare_year():
    # independently: Jan 1 + 99 days = Apr 10 2026 (2026 is not a leap year)
    expected = date(2026, 1, 1) + __import__("datetime").timedelta(days=99)
    assert expected == date(2026, 4, 10)
    r = _result("the 100th day of 2026")
    assert r is not None
    assert r.remainder == ""
    assert r.span.start == AstroDate(2026, 4, 10)
    assert r.span.end == AstroDate(2026, 4, 11)


def test_last_day_of_bare_year_is_december_31st():
    r = _result("the last day of 2026")
    assert r is not None
    assert r.remainder == ""
    assert r.span.start == AstroDate(2026, 12, 31)
    assert r.span.end == AstroDate(2027, 1, 1)


def test_fifty_third_week_of_2026_a_53_iso_week_year():
    # independently verified: date(2026, 12, 28).isocalendar()[1] == 53
    assert date(2026, 12, 28).isocalendar()[1] == 53
    r = _result("the 53rd week of 2026")
    assert r is not None
    assert r.remainder == ""
    assert r.span.start == AstroDate(2026, 12, 28)
    assert r.span.end == AstroDate(2027, 1, 4)


def test_fifty_third_week_of_2027_a_52_iso_week_year_refuses():
    # independently verified: date(2027, 12, 28).isocalendar()[1] == 52
    assert date(2027, 12, 28).isocalendar()[1] == 52
    assert _result("the 53rd week of 2027") is None


def test_fifth_week_of_march_2027():
    # independent arithmetic: month-week 5 = day1 + 5 weeks - 1 day, snapped
    # to that week's Monday -- Mar 1 2027 + 5w - 1d = Apr 4 2027 (Sunday),
    # Monday of that week is Mar 29 2027.
    from dateutil.relativedelta import relativedelta
    day = date(2027, 3, 1) + relativedelta(weeks=5) - __import__("datetime").timedelta(days=1)
    monday = day - __import__("datetime").timedelta(days=day.weekday())
    assert monday == date(2027, 3, 29)
    r = _result("the 5th week of march 2027")
    assert r is not None
    assert r.remainder == ""
    assert r.span.start == AstroDate(2027, 3, 29)
    assert r.span.end == AstroDate(2027, 4, 5)


def test_fifth_weekend_of_may_2026():
    # independent arithmetic: May 2026 Saturdays are 2/9/16/23/30 -- the 5th
    # weekend is Sat May 30 - Sun May 31.
    d = date(2026, 5, 1)
    saturdays = [d + __import__("datetime").timedelta(days=i) for i in range(31)
                if (d + __import__("datetime").timedelta(days=i)).weekday() == 5]
    assert saturdays[4] == date(2026, 5, 30)
    r = _result("the 5th weekend of may")
    assert r is not None
    assert r.remainder == ""
    assert r.span.start == AstroDate(2026, 5, 30)
    assert r.span.end == AstroDate(2026, 6, 1)


def test_twelfth_month_of_the_year_still_works():
    """The pre-existing "of the year" wording (year_word order) is
    untouched by the new bare-year order."""
    r = _result("the 12th month of the year")
    assert r is not None
    assert r.remainder == ""
    assert r.span.start == AstroDate(2026, 12, 1)
    assert r.span.end == AstroDate(2027, 1, 1)


def test_second_quarter_of_2026_still_works():
    r = _result("the 2nd quarter of 2026")
    assert r is not None
    assert r.remainder == ""
    assert r.span.start == AstroDate(2026, 4, 1)
    assert r.span.end == AstroDate(2026, 7, 1)


def test_thirteenth_quarter_of_2026_refuses():
    assert _result("the 13th quarter of 2026") is None


# ---------------------------------------------------------------------------
# Adversarial: sentences that only coincidentally SHAPE like a stranded
# scoped-ordinal (a plural count, or an unrelated clause) must not be
# refused by the extended residue-veto -- the veto targets the impossible
# ordinal-scope construction specifically, not any "number unit of X" run.
# ---------------------------------------------------------------------------
def test_plural_count_of_vacation_is_not_vetoed():
    r = _result("3 weeks of vacation in july")
    assert r is not None
    assert r.span.start == AstroDate(2026, 7, 1)
    assert r.span.end == AstroDate(2026, 8, 1)


def test_unrelated_later_clause_is_not_vetoed():
    r = _result("the first week of school starts in september")
    assert r is not None
    assert r.span.start == AstroDate(2026, 9, 1)
    assert r.span.end == AstroDate(2026, 10, 1)
