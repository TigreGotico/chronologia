# -*- coding: utf-8 -*-
"""Regression for R143: 'Aschermittwoch' (Ash Wednesday) was missing from the
German well-known-holiday alias table, so 'aschermittwoch 2026' silently
mis-parsed as the WHOLE-YEAR span 2026 with 'aschermittwoch' stranded in the
remainder, and bare 'aschermittwoch' did not parse at all.

Gold dates are computed here by an independent Easter oracle (Anonymous
Gregorian algorithm), never read back from the parser. Ash Wednesday is
Easter - 46 days.
"""
from datetime import date, datetime

import pytest

from chronologia import extract_timespan
from chronologia.extract import extract_recurrence
from chronologia.recurrence import HolidayRecurrence

LANG = "de"
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
    from datetime import timedelta
    return _easter(y) - timedelta(days=46)


def parse(text, anchor=ANCHOR):
    return extract_timespan(text, LANG, anchor)


@pytest.mark.parametrize("year", [2026, 2027, 2028])
def test_ash_wednesday_with_year(year):
    exp = _ash_wednesday(year)
    r = parse(f"aschermittwoch {year}")
    assert r is not None, "aschermittwoch <year> did not parse"
    span, remainder = r
    assert remainder == "", f"unexpected remainder: {remainder!r}"
    assert (span.start.year, span.start.month, span.start.day) == (exp.year, exp.month, exp.day)


def test_ash_wednesday_bare_rolls_to_next_occurrence():
    # anchor is 2026-08-12, well past Ash Wednesday 2026 (2026-02-18), so the
    # bare form must roll forward to the 2027 occurrence.
    exp = _ash_wednesday(2027)
    r = parse("aschermittwoch")
    assert r is not None, "bare 'aschermittwoch' did not parse"
    span, remainder = r
    assert remainder == ""
    assert (span.start.year, span.start.month, span.start.day) == (exp.year, exp.month, exp.day)


def test_ash_wednesday_2026_is_feb_18():
    # Explicit independently-verified anchor value from the defect report.
    assert _ash_wednesday(2026) == date(2026, 2, 18)
    r = parse("aschermittwoch 2026")
    span, remainder = r
    assert (span.start.year, span.start.month, span.start.day) == (2026, 2, 18)
    assert remainder == ""


def test_control_karfreitag_and_ostern_still_work():
    exp_gf = _easter(2026) - __import__("datetime").timedelta(days=2)
    r = parse("karfreitag 2026")
    assert r is not None
    assert (r.span.start.year, r.span.start.month, r.span.start.day) == (exp_gf.year, exp_gf.month, exp_gf.day)

    exp_e = _easter(2026)
    r2 = parse("ostern 2026")
    assert r2 is not None
    assert (r2.span.start.year, r2.span.start.month, r2.span.start.day) == (exp_e.year, exp_e.month, exp_e.day)


def test_ash_wednesday_recurrence():
    # probed: "jedes jahr am aschermittwoch" resolves as a holiday recurrence
    got = extract_recurrence("jedes jahr am aschermittwoch", LANG)
    assert got is not None
    assert got[0] == HolidayRecurrence("ash_wednesday")
    assert got[1] == ""
