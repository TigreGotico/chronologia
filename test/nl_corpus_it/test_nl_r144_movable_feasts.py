# -*- coding: utf-8 -*-
"""Regression for R144: 'mercoledì delle ceneri' (Ash Wednesday) was missing
from the Italian well-known-holiday alias table, so bare 'mercoledì delle
ceneri' resolved to the next plain Wednesday with 'delle ceneri' stranded
in the remainder, and 'mercoledì delle ceneri <year>' mis-parsed as well.

Also covers 'martedì grasso' (Fat Tuesday / Carnival), which was likewise
missing as a carnival alias: it matched only 'martedì' (next Tuesday) and
stranded 'grasso'.

Gold dates are computed here by an independent Easter oracle (Anonymous
Gregorian algorithm), never read back from the parser. Ash Wednesday is
Easter - 46 days; Fat Tuesday (martedì grasso) is Ash Wednesday - 1 day.
"""
from datetime import date, datetime, timedelta

import pytest

from chronologia import extract_timespan

LANG = "it"
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


def _fat_tuesday(y):
    return _ash_wednesday(y) - timedelta(days=1)


def parse(text, anchor=ANCHOR):
    return extract_timespan(text, LANG, anchor)


def test_easter_oracle_sanity():
    assert _easter(2026) == date(2026, 4, 5)
    assert _easter(2027) == date(2027, 3, 28)
    assert _easter(2028) == date(2028, 4, 16)
    assert _ash_wednesday(2027) == date(2027, 2, 10)
    assert _fat_tuesday(2027) == date(2027, 2, 9)


@pytest.mark.parametrize("year", [2026, 2027, 2028])
def test_ash_wednesday_with_year(year):
    exp = _ash_wednesday(year)
    r = parse(f"mercoledì delle ceneri {year}")
    assert r is not None, "mercoledì delle ceneri <year> did not parse"
    span, remainder = r
    assert remainder == "", f"unexpected remainder: {remainder!r}"
    assert (span.start.year, span.start.month, span.start.day) == (exp.year, exp.month, exp.day)


def test_ash_wednesday_bare_rolls_to_next_occurrence():
    exp = _ash_wednesday(2027)
    assert exp == date(2027, 2, 10)
    r = parse("mercoledì delle ceneri")
    assert r is not None, "bare 'mercoledì delle ceneri' did not parse"
    span, remainder = r
    assert remainder == "", f"'delle ceneri' must not be stranded, got remainder={remainder!r}"
    assert (span.start.year, span.start.month, span.start.day) == (exp.year, exp.month, exp.day)


def test_ash_wednesday_no_partial_strand():
    from datetime import timedelta as _td
    naive_next_wed = ANCHOR.date() + _td(days=(2 - ANCHOR.weekday()) % 7 or 7)
    r = parse("mercoledì delle ceneri")
    span, remainder = r
    got = date(span.start.year, span.start.month, span.start.day)
    assert got != naive_next_wed
    assert got == _ash_wednesday(2027)


@pytest.mark.parametrize("year", [2026, 2027, 2028])
def test_fat_tuesday_with_year(year):
    exp = _fat_tuesday(year)
    r = parse(f"martedì grasso {year}")
    assert r is not None, "martedì grasso <year> did not parse"
    span, remainder = r
    assert remainder == "", f"unexpected remainder: {remainder!r}"
    assert (span.start.year, span.start.month, span.start.day) == (exp.year, exp.month, exp.day)


def test_fat_tuesday_bare_no_partial_strand():
    exp = _fat_tuesday(2027)
    r = parse("martedì grasso")
    assert r is not None, "bare 'martedì grasso' did not parse"
    span, remainder = r
    assert remainder == "", f"'grasso' must not be stranded, got remainder={remainder!r}"
    assert (span.start.year, span.start.month, span.start.day) == (exp.year, exp.month, exp.day)


def test_control_non_holiday_wednesday_still_bare():
    r = parse("mercoledì")
    assert r is not None
    span, remainder = r
    assert remainder == ""
    got = date(span.start.year, span.start.month, span.start.day)
    assert got.weekday() == 2  # Wednesday
    assert got != _ash_wednesday(2027)


def test_control_carnevale_and_pasqua_still_work():
    r = parse("carnevale")
    assert r is not None
    span, remainder = r
    assert remainder == ""
    exp_carnival_2027 = _fat_tuesday(2027)
    assert (span.start.year, span.start.month, span.start.day) == (
        exp_carnival_2027.year, exp_carnival_2027.month, exp_carnival_2027.day,
    )

    exp_e = _easter(2027)
    r2 = parse("pasqua 2027")
    assert r2 is not None
    span2, remainder2 = r2
    assert remainder2 == ""
    assert (span2.start.year, span2.start.month, span2.start.day) == (exp_e.year, exp_e.month, exp_e.day)
