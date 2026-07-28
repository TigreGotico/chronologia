# -*- coding: utf-8 -*-
"""An explicit trailing year must bind across the fuzzy-month, range and
ordinal-weekday/holiday compositions -- it may never be silently dropped in
favour of the anchor (or prefer-future) year.

Two independent native reviewers (es, fr) found the same silent-wrong: an
explicit YEAR spoken alongside a fuzzy-month ("early March 2019"), a range with
one trailing year ("from January to March 2020"), an ordinal weekday ("the
second Tuesday of November 2019") or a holiday ("Christmas 2020") was ignored
and the span landed in the anchor year (2017) instead.  The resolvers are
shared across all 40 locales; en is the probe.

All expected spans are hand-derived against the anchor year 2017 so that a
regression to the anchor year is caught: none of the dated cases may land in
2017.  The no-year forms and the per-endpoint-year range are pinned to prove
the fix stays positional and does not disturb the un-yeared readings.
"""
import pytest

from ._corpus import AstroDate, parse, span, start_end


# -- (A) fuzzy month + explicit year -------------------------------------
# "early March" (anchor 2017) is the early third of March: Mar 1 00:00 .. Mar
# 11 08:00 (31 days / 3).  The trailing year must move that third into 2019,
# keeping the identical day-of-month boundaries.
@pytest.mark.parametrize("text,s,e", [
    ('early March 2019',
     AstroDate(2019, 3, 1, 0, 0), AstroDate(2019, 3, 11, 8, 0)),
    ('mid March 2020',
     AstroDate(2020, 3, 11, 8, 0), AstroDate(2020, 3, 21, 16, 0)),
    ('late March 2018',
     AstroDate(2018, 3, 21, 16, 0), AstroDate(2018, 4, 1, 0, 0)),
])
def test_fuzzy_month_binds_trailing_year(text, s, e):
    got_s, got_e = start_end(text)
    assert (got_s, got_e) == (s, e)
    assert parse(text)[1] == ""            # year consumed, no remainder


def test_fuzzy_month_no_year_stays_anchor_year():
    # byte-identical to the historic bare reading: anchor-year March.
    assert start_end('early March') == (
        AstroDate(2017, 3, 1, 0, 0), AstroDate(2017, 3, 11, 8, 0))


# -- (B) range with a single trailing year -------------------------------
# the trailing year lends to BOTH endpoints, exactly as #236 lent the shared
# month; "from January to March 2020" is entirely inside 2020.
@pytest.mark.parametrize("text,s,e", [
    ('from January to March 2020',
     AstroDate(2020, 1, 1), AstroDate(2020, 4, 1)),
    ('from June to August 2019',
     AstroDate(2019, 6, 1), AstroDate(2019, 9, 1)),
])
def test_range_trailing_year_lends_to_both_endpoints(text, s, e):
    got_s, got_e = start_end(text)
    assert (got_s, got_e) == (s, e)


def test_range_per_endpoint_years_stay_separate():
    # each endpoint carries its own year -- no lending.
    assert start_end('from December 2019 to March 2020') == (
        AstroDate(2019, 12, 1), AstroDate(2020, 4, 1))


def test_range_no_year_stays_anchor_year():
    assert start_end('from January to March') == (
        AstroDate(2017, 1, 1), AstroDate(2017, 4, 1))


# -- (C) ordinal weekday + year (en already binds; regression pin) -------
def test_ordinal_weekday_binds_trailing_year():
    assert start_end('the second Tuesday of November 2019') == (
        AstroDate(2019, 11, 12), AstroDate(2019, 11, 13))


def test_ordinal_weekday_no_year_stays_anchor_year():
    assert start_end('the second Tuesday of November') == (
        AstroDate(2017, 11, 14), AstroDate(2017, 11, 15))


# -- (D) holiday + year (en already binds; regression pin) ---------------
def test_holiday_binds_trailing_year():
    assert start_end('Christmas 2020') == (
        AstroDate(2020, 12, 25), AstroDate(2020, 12, 26))
