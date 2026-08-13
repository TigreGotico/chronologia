# -*- coding: utf-8 -*-
"""Regression for R144: 'aswoensdag' (Ash Wednesday) was missing from the
Dutch well-known-holiday alias table. Bare 'aswoensdag' did not parse at
all (returned None), and 'aswoensdag <year>' mis-parsed as the WHOLE-YEAR
span with 'aswoensdag' stranded in the remainder.

Gold dates are computed here by an independent Easter oracle (Anonymous
Gregorian algorithm), never read back from the parser. Ash Wednesday is
Easter - 46 days.
"""
from datetime import date, datetime, timedelta

import pytest

from chronologia import extract_timespan
from chronologia.extract import extract_recurrence
from chronologia.recurrence import HolidayRecurrence

LANG = "nl"
ANCHOR = datetime(2026, 8, 13, 10, 0)


def _easter(y):
    a = y % 19
    b, c = y // 100, y % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    ll = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * ll) // 451
    mo = (h + ll - 7 * m + 114) // 31
    da = ((h + ll - 7 * m + 114) % 31) + 1
    return date(y, mo, da)


def _ash_wednesday(y):
    return _easter(y) - timedelta(days=46)


def parse(text, anchor=ANCHOR):
    return extract_timespan(text, LANG, anchor)


def test_easter_oracle_sanity():
    assert _easter(2026) == date(2026, 4, 5)
    assert _easter(2027) == date(2027, 3, 28)
    assert _easter(2028) == date(2028, 4, 16)
    assert _ash_wednesday(2027) == date(2027, 2, 10)


@pytest.mark.parametrize("year", [2026, 2027, 2028])
def test_ash_wednesday_with_year(year):
    exp = _ash_wednesday(year)
    r = parse(f"aswoensdag {year}")
    assert r is not None, "aswoensdag <year> did not parse"
    span, remainder = r
    assert remainder == "", f"unexpected remainder: {remainder!r}"
    assert (span.start.year, span.start.month, span.start.day) == (exp.year, exp.month, exp.day)
    # regression: must NOT be the whole-year span
    assert not (span.start.month == 1 and span.start.day == 1)


def test_ash_wednesday_bare_parses():
    # previously returned None entirely
    exp = _ash_wednesday(2027)
    assert exp == date(2027, 2, 10)
    r = parse("aswoensdag")
    assert r is not None, "bare 'aswoensdag' did not parse"
    span, remainder = r
    assert remainder == ""
    assert (span.start.year, span.start.month, span.start.day) == (exp.year, exp.month, exp.day)


def test_ash_wednesday_2027_with_year_not_whole_year_span():
    r = parse("aswoensdag 2027")
    assert r is not None
    span, remainder = r
    assert remainder == "", f"'aswoensdag' must not be stranded, got remainder={remainder!r}"
    exp = _ash_wednesday(2027)
    assert (span.start.year, span.start.month, span.start.day) == (exp.year, exp.month, exp.day)
    assert (span.end.year, span.end.month, span.end.day) == (exp.year, exp.month, exp.day + 1)


def test_control_non_holiday_wednesday_still_bare():
    r = parse("woensdag")
    assert r is not None
    span, remainder = r
    assert remainder == ""
    got = date(span.start.year, span.start.month, span.start.day)
    assert got.weekday() == 2  # Wednesday
    assert got != _ash_wednesday(2027)


def test_control_carnaval_and_pasen_still_work():
    r = parse("carnaval")
    assert r is not None
    span, remainder = r
    assert remainder == ""
    exp_carnival_2027 = _ash_wednesday(2027) - timedelta(days=1)
    assert (span.start.year, span.start.month, span.start.day) == (
        exp_carnival_2027.year, exp_carnival_2027.month, exp_carnival_2027.day,
    )

    exp_e = _easter(2027)
    r2 = parse("pasen 2027")
    assert r2 is not None
    span2, remainder2 = r2
    assert remainder2 == ""
    assert (span2.start.year, span2.start.month, span2.start.day) == (exp_e.year, exp_e.month, exp_e.day)


def test_ash_wednesday_recurrence():
    got = extract_recurrence("elk jaar op aswoensdag", LANG)
    assert got is not None
    assert got[0] == HolidayRecurrence("ash_wednesday")
    assert got[1] == ""
