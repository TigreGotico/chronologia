"""YEARANY must not bind a number that is really the start of a
duration/count phrase (R79 regression).

R74 (commit 49a81c19) added the YEARANY slot -- YEAR without the >=32
day-of-month lower bound -- so "new year 27" pivots to 2027 instead of
stranding "27" as a day/count value below the YEAR gate. But YEARANY's only
remaining guard is >=2 digits, so it also swallows the leading number of a
duration phrase: "new year 15 minutes" reads "15" as the year (-> 2015) and
stroods the sentence at "minutes", silently dropping the "15" that belongs to
the duration.

Fix: veto the YEARANY-bound ``new_year_ref`` order when the token right
after YEARANY is a known unit word (``spec.units`` / ``spec.singular_units``,
read from the locale voc, not hardcoded) -- the bare "new year_word" order
then wins at the same start, so the reading falls back to the un-dated
"coming new year" span and the whole "15 minutes" survives in the remainder.

Reference values are plain arithmetic against the fixed anchor below, or
the un-dated bare "new year_ref" span asserted only by remainder + no crash
(the exact prefer-future year is incidental to this guard and is already
pinned by test_nl_era_new_year_binding_fixes.py).
"""
from datetime import datetime

from chronologia import extract_timespan

from ._corpus import AstroDate

_ANCHOR = datetime(2026, 8, 5)


def _ts(text, anchor=_ANCHOR):
    return extract_timespan(text, "en", anchor)


# -- the reported regression -------------------------------------------
def test_new_year_minutes_leaves_duration_in_remainder():
    r = _ts("new year 15 minutes")
    assert r is not None
    # "15" must NOT be consumed as a year -- it stays with its unit.
    assert r[1] == "15 minutes"
    # falls back to the bare (undated) new-year reading, not year 2015.
    assert r[0].start.year != 2015


def test_new_year_days_leaves_duration_in_remainder():
    r = _ts("new year 30 days")
    assert r is not None
    assert r[1] == "30 days"
    assert r[0].start.year != 2030


def test_new_year_weeks_leaves_duration_in_remainder():
    r = _ts("new year 12 weeks")
    assert r is not None
    assert r[1] == "12 weeks"
    assert r[0].start.year != 2012


def test_new_year_months_leaves_duration_in_remainder():
    r = _ts("new year 18 months")
    assert r is not None
    assert r[1] == "18 months"
    assert r[0].start.year != 2018


def test_new_year_hours_leaves_duration_in_remainder():
    r = _ts("new year 48 hours")
    assert r is not None
    assert r[1] == "48 hours"
    assert r[0].start.year != 1948


def test_new_year_seconds_leaves_duration_in_remainder():
    r = _ts("new year 90 seconds")
    assert r is not None
    assert r[1] == "90 seconds"


def test_new_year_years_leaves_duration_in_remainder():
    # "years" itself is a unit word -- "new year 50 years" is "50 years
    # (from) new year", not the year 1950/2050.
    r = _ts("new year 50 years")
    assert r is not None
    assert r[1] == "50 years"
    assert r[0].start.year != 1950
    assert r[0].start.year != 2050


# -- controls: R74's intended behavior must survive unchanged ----------
def test_new_year_27_still_pivots_to_2027():
    r = extract_timespan("new year 27", "en", datetime(2020, 1, 1))
    assert r is not None and r[1] == ""
    assert r[0].start == AstroDate(2027, 1, 1)
    assert r[0].end == AstroDate(2027, 1, 2)


def test_new_year_99_still_pivots_to_1999():
    r = extract_timespan("new year 99", "en", datetime(2020, 1, 1))
    assert r is not None and r[1] == ""
    assert r[0].start == AstroDate(1999, 1, 1)
    assert r[0].end == AstroDate(1999, 1, 2)


def test_new_year_four_digit_year_still_dayweide():
    r = extract_timespan("new year 2027", "en", datetime(2020, 1, 1))
    assert r is not None and r[1] == ""
    assert r[0].start == AstroDate(2027, 1, 1)
    assert r[0].end == AstroDate(2027, 1, 2)


def test_new_year_27_followed_by_non_unit_word_still_pivots():
    # a trailing word that is NOT a unit must not trip the guard.
    r = extract_timespan("new year 27 party", "en", datetime(2020, 1, 1))
    assert r is not None and r[1] == "party"
    assert r[0].start == AstroDate(2027, 1, 1)
    assert r[0].end == AstroDate(2027, 1, 2)


def test_new_year_bare_single_digit_count_unchanged():
    # a single-digit count never bound YEARANY to begin with (n_digits>=2
    # gate) -- must stay exactly as before: bare new-year reading, count in
    # remainder.
    r = _ts("new year 5 minutes")
    assert r is not None
    assert r[1] == "5 minutes"
