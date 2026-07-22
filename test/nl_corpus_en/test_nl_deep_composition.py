# -*- coding: utf-8 -*-
"""Deep composition: an offset / business-day count taken over a reference
that is *itself* a composed construction.

Two things had to be true for these to resolve:

* an **nth-weekday-of-month** reference ("the last friday of november", "the
  first monday of march") must resolve as a single span in its own right --
  the scoped-ordinal grammar was extended with ``ORD WEEKDAY of MONTH`` so it
  does;
* a post-pass (anchored offset, business-day count) taking a *reference* must
  bind one that is itself composed -- an offset ("the monday after christmas")
  or an nth-weekday -- not only a matcher-native one.  The business-day pass
  recurses the reference slice through the single-span core when the flat scan
  sees only a shorter, partial reference ("monday" inside "monday after
  christmas").

Every expected value is derived here by independent ``datetime`` arithmetic
(and, for business days, the civil-holiday calendar -- not the extract
parser), then asserted against the parser's span.
"""
import calendar
from datetime import datetime, timedelta

import pytest

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate
from chronologia.civil_holidays import is_civil_holiday

from ._corpus import ANCHOR, parse, span

MON, FRI = 0, 4


# -- independent oracles (no parser) --------------------------------------

def nth_weekday(year, month, weekday, n):
    last = calendar.monthrange(year, month)[1]
    days = [d for d in range(1, last + 1)
            if datetime(year, month, d).weekday() == weekday]
    return datetime(year, month, days[n if n < 0 else n - 1])


def roll_weekday(base, weekday, sign):
    if sign > 0:
        ahead = (weekday - base.weekday()) % 7 or 7
        return base + timedelta(days=ahead)
    back = (base.weekday() - weekday) % 7 or 7
    return base - timedelta(days=back)


def nth_business_day(base, n, sign, weekend_start, jurisdiction):
    day = datetime(base.year, base.month, base.day)
    step = timedelta(days=1 if sign > 0 else -1)
    seen = 0
    while seen < n:
        day += step
        wd = day.weekday()
        if wd == weekend_start or wd == (weekend_start + 1) % 7:
            continue
        if jurisdiction and is_civil_holiday(day, jurisdiction,
                                             categories=("public",)):
            continue
        seen += 1
    return day


def us(text):
    r = extract_timespan(text, "en", ANCHOR, jurisdiction="US")
    assert r is not None, f"{text!r} did not parse"
    return r


# -- nth-weekday-of-month standalone --------------------------------------

@pytest.mark.parametrize("text,month,wd,n", [
    ('the last friday of november', 11, FRI, -1),
    ('the first monday of march', 3, MON, 1),
    ('the third monday of march', 3, MON, 3),
    ('the last monday of may', 5, MON, -1),
])
def test_nth_weekday_of_month_standalone(text, month, wd, n):
    ref = nth_weekday(ANCHOR.year, month, wd, n)
    s = span(text)
    assert s.start == AstroDate(ref.year, ref.month, ref.day)
    assert s.end == s.start + timedelta(days=1)
    assert parse(text)[1] == ""


# -- an anchored offset over an nth-weekday reference ---------------------

@pytest.mark.parametrize("text,month,wd,n,off_days", [
    ('the day before the last friday of november', 11, FRI, -1, -1),
    ('the day after the last friday of november', 11, FRI, -1, 1),
    ('the day before the first monday of march', 3, MON, 1, -1),
])
def test_day_offset_of_nth_weekday(text, month, wd, n, off_days):
    ref = nth_weekday(ANCHOR.year, month, wd, n)
    expect = ref + timedelta(days=off_days)
    s = span(text)
    assert s.start == AstroDate(expect.year, expect.month, expect.day)
    assert s.end == s.start + timedelta(days=1)
    assert parse(text)[1] == ""


def test_two_weeks_after_first_monday_of_march():
    text = 'two weeks after the first monday of march'
    ref = nth_weekday(ANCHOR.year, 3, MON, 1)
    expect = ref + timedelta(weeks=2)
    assert span(text).start == AstroDate(expect.year, expect.month, expect.day)
    assert parse(text)[1] == ""


# -- business-day count over a composed reference (offset-of-offset) ------

def test_working_days_after_monday_after_christmas():
    text = '3 working days after the monday after christmas'
    ref = roll_weekday(datetime(ANCHOR.year, 12, 25), MON, 1)  # Mon after xmas
    expect = nth_business_day(ref, 3, 1, 5, "US")              # Sat+Sun rest
    s, rem = us(text)
    assert s.start == AstroDate(expect.year, expect.month, expect.day)
    assert s.end == s.start + timedelta(days=1)
    assert rem == ""


def test_business_days_before_first_monday_of_march():
    text = '2 business days before the first monday of march'
    ref = nth_weekday(ANCHOR.year, 3, MON, 1)
    expect = nth_business_day(ref, 2, -1, 5, None)
    r = extract_timespan(text, "en", ANCHOR)
    assert r is not None
    assert r[0].start == AstroDate(expect.year, expect.month, expect.day)
    assert r[1] == ""


def test_working_days_after_plain_christmas_unchanged():
    # a NON-composed reference (bare holiday) keeps its exact prior binding
    expect = nth_business_day(datetime(ANCHOR.year, 12, 25), 3, 1, 5, "US")
    s, _ = us('3 working days after christmas')
    assert s.start == AstroDate(expect.year, expect.month, expect.day)


# -- negatives: a nonsense reference must not fabricate -------------------

def test_nonsense_reference_after_offset_does_not_fabricate():
    r = parse('the day before the last friday of blursday')
    if r is not None:
        assert 'blursday' in r[1] or 'friday' in r[1]


def test_working_days_after_nonsense_is_not_composed():
    r = extract_timespan('3 working days after the frobnitz of march',
                         "en", ANCHOR, jurisdiction="US")
    if r is not None:
        assert 'frobnitz' in r[1] or 'march' in r[1] or 'working' in r[1]
