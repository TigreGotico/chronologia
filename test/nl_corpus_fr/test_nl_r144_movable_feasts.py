# -*- coding: utf-8 -*-
"""Regression for R144: 'mercredi des cendres' (Ash Wednesday) was missing
from the French well-known-holiday alias table, so bare 'mercredi des
cendres' resolved to the next plain Wednesday with 'des cendres' stranded
in the remainder, and 'mercredi des cendres <year>' mis-parsed as well.

Gold dates are computed here by an independent Easter oracle (Anonymous
Gregorian algorithm), never read back from the parser. Ash Wednesday is
Easter - 46 days.
"""
from datetime import date, datetime, timedelta

import pytest

from chronologia import extract_timespan
from chronologia.extract import extract_recurrence
from chronologia.recurrence import HolidayRecurrence

LANG = "fr"
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


# Independently-verified anchors from the defect report / task brief.
def test_easter_oracle_sanity():
    assert _easter(2026) == date(2026, 4, 5)
    assert _easter(2027) == date(2027, 3, 28)
    assert _easter(2028) == date(2028, 4, 16)
    assert _ash_wednesday(2027) == date(2027, 2, 10)


@pytest.mark.parametrize("year", [2026, 2027, 2028])
def test_ash_wednesday_with_year(year):
    exp = _ash_wednesday(year)
    r = parse(f"mercredi des cendres {year}")
    assert r is not None, "mercredi des cendres <year> did not parse"
    span, remainder = r
    assert remainder == "", f"unexpected remainder: {remainder!r}"
    assert (span.start.year, span.start.month, span.start.day) == (exp.year, exp.month, exp.day)


def test_ash_wednesday_bare_rolls_to_next_occurrence():
    # anchor is 2026-08-13, well past Ash Wednesday 2026 (2026-02-18), so the
    # bare form must roll forward to the 2027 occurrence.
    exp = _ash_wednesday(2027)
    assert exp == date(2027, 2, 10)
    r = parse("mercredi des cendres")
    assert r is not None, "bare 'mercredi des cendres' did not parse"
    span, remainder = r
    assert remainder == "", f"'des cendres' must not be stranded, got remainder={remainder!r}"
    assert (span.start.year, span.start.month, span.start.day) == (exp.year, exp.month, exp.day)


def test_ash_wednesday_no_partial_strand():
    # Regression guard: the bug matched only 'mercredi' (any Wednesday) and
    # left 'des cendres' as remainder. Make sure the FULL span_start weekday
    # is Wednesday and remainder is empty (already covered above), plus
    # confirm it is NOT simply "next Wednesday" from the anchor.
    from datetime import timedelta as _td
    naive_next_wed = ANCHOR.date() + _td(days=(2 - ANCHOR.weekday()) % 7 or 7)
    r = parse("mercredi des cendres")
    span, remainder = r
    got = date(span.start.year, span.start.month, span.start.day)
    assert got != naive_next_wed
    assert got == _ash_wednesday(2027)


def test_control_non_holiday_wednesday_still_bare():
    # A plain "mercredi" (just Wednesday, no holiday qualifier) must still
    # resolve to the next plain Wednesday, proving we didn't break the
    # generic weekday matcher while fixing the holiday alias.
    r = parse("mercredi")
    assert r is not None
    span, remainder = r
    assert remainder == ""
    got = date(span.start.year, span.start.month, span.start.day)
    assert got.weekday() == 2  # Wednesday
    assert got != _ash_wednesday(2027)


def test_control_carnaval_and_paques_still_work():
    exp_carnival = _ash_wednesday(2026) - timedelta(days=1)
    r = parse("mardi gras")
    assert r is not None
    span, remainder = r
    assert remainder == ""
    # anchor past 2026 occurrence -> rolls to 2027
    exp_carnival_2027 = _ash_wednesday(2027) - timedelta(days=1)
    assert (span.start.year, span.start.month, span.start.day) == (
        exp_carnival_2027.year, exp_carnival_2027.month, exp_carnival_2027.day,
    )

    exp_e = _easter(2027)
    r2 = parse("pâques 2027")
    assert r2 is not None
    span2, remainder2 = r2
    assert remainder2 == ""
    assert (span2.start.year, span2.start.month, span2.start.day) == (exp_e.year, exp_e.month, exp_e.day)


def test_ash_wednesday_recurrence():
    got = extract_recurrence("chaque année à mercredi des cendres", LANG)
    assert got is not None
    assert got[0] == HolidayRecurrence("ash_wednesday")
    assert got[1] == ""
