# -*- coding: utf-8 -*-
"""Regression for R143: 'środa popielcowa' (Ash Wednesday) was missing from
the Polish well-known-holiday alias table. Because 'środa' (Wednesday) alone
IS a recognised weekday word, the parser silently matched the bare weekday
and stranded 'popielcowa' in the remainder -- a silent misread that happened
even WITHOUT a trailing year.

Gold dates are computed here by an independent Easter oracle (Anonymous
Gregorian algorithm), never read back from the parser. Ash Wednesday is
Easter - 46 days.
"""
from datetime import date, datetime, timedelta

import pytest

from chronologia import extract_timespan
from chronologia.extract import extract_recurrence
from chronologia.recurrence import HolidayRecurrence

LANG = "pl"
ANCHOR = datetime(2026, 8, 12)


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


@pytest.mark.parametrize("year", [2026, 2027, 2028])
def test_ash_wednesday_with_year(year):
    exp = _ash_wednesday(year)
    r = parse(f"środa popielcowa {year}")
    assert r is not None, "'środa popielcowa <year>' did not parse"
    span, remainder = r
    assert remainder == "", f"unexpected remainder: {remainder!r}"
    assert (span.start.year, span.start.month, span.start.day) == (exp.year, exp.month, exp.day)


def test_ash_wednesday_bare_no_year_must_not_be_a_bare_wednesday():
    # This is the silent-misread case from the defect report: without the
    # fix, 'środa popielcowa' matches bare 'środa' (next Wednesday from the
    # anchor) with 'popielcowa' stranded in the remainder.
    exp = _ash_wednesday(2027)  # anchor 2026-08-12 is past Ash Wed 2026
    r = parse("środa popielcowa")
    assert r is not None, "'środa popielcowa' did not parse"
    span, remainder = r
    assert remainder == "", f"unexpected remainder (partial match): {remainder!r}"
    assert (span.start.year, span.start.month, span.start.day) == (exp.year, exp.month, exp.day)
    # explicitly must NOT be the next-Wednesday misread (2026-08-19)
    assert (span.start.year, span.start.month, span.start.day) != (2026, 8, 19)


def test_ash_wednesday_2026_is_feb_18():
    assert _ash_wednesday(2026) == date(2026, 2, 18)
    r = parse("środa popielcowa 2026")
    span, remainder = r
    assert (span.start.year, span.start.month, span.start.day) == (2026, 2, 18)
    assert remainder == ""


def test_control_bare_wednesday_still_resolves_to_next_wednesday():
    # 'środa' alone (no 'popielcowa') is an ordinary weekday reference and
    # must keep working: anchor is Wednesday 2026-08-12, so the next
    # Wednesday is 2026-08-19.
    r = parse("środa")
    assert r is not None
    span, remainder = r
    assert remainder == ""
    assert (span.start.year, span.start.month, span.start.day) == (2026, 8, 19)


def test_control_wielki_piatek_still_works():
    # Good Friday alias ('wielki piątek') was already present and multiword;
    # confirm the fix did not disturb it.
    exp_gf = _easter(2026) - timedelta(days=2)
    r = parse("wielki piątek 2026")
    assert r is not None
    span, remainder = r
    assert remainder == ""
    assert (span.start.year, span.start.month, span.start.day) == (exp_gf.year, exp_gf.month, exp_gf.day)


def test_ash_wednesday_recurrence():
    # probed: pl holiday recurrence path supports "co roku <holiday>"
    got = extract_recurrence("co roku środa popielcowa", LANG)
    assert got is not None
    assert got[0] == HolidayRecurrence("ash_wednesday")
    assert got[1] == ""
