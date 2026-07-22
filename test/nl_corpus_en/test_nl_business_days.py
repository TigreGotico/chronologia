"""Business-day counting: "in N business days", "the next working day",
"N working days after christmas".

A business day is a non-weekend weekday that is also not a public holiday of
the ``jurisdiction`` passed to ``extract_timespan``.  With ``jurisdiction=None``
the count is holiday-blind (weekend-aware only).

Anchor is Wednesday 2026-12-23.  December 2026 (Dec 1 is a Tuesday)::

    Mon  7 14 21 28      Thu  3 10 17 24 31
    Tue  1  8 15 22 29   Fri  4 11 18 25
    Wed  2  9 16 23 30   Sat  5 12 19 26
                         Sun  6 13 20 27

Public holidays in range (US/PT calendars): Fri 2026-12-25 (Christmas) and
Fri 2027-01-01 (New Year).  Every gold below is counted by hand off that grid.

Holiday-blind (jurisdiction=None), Mon-Fri only, strictly after Wed 12-23:
    Thu24(1) Fri25(2) Mon28(3) Tue29(4) Wed30(5) Thu31(6)
With a jurisdiction (skip Christmas + New Year):
    Thu24(1) Mon28(2) Tue29(3) Wed30(4) Thu31(5) Mon Jan4(6)
"""
from datetime import date, datetime

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate

import pytest

ANCHOR = datetime(2026, 12, 23, 9, 0)   # Wednesday


def start(text, jurisdiction=None):
    r = extract_timespan(text, "en", ANCHOR, jurisdiction=jurisdiction)
    assert r is not None, f"{text!r} did not parse"
    return r[0].start


def nomatch(text, jurisdiction=None):
    r = extract_timespan(text, "en", ANCHOR, jurisdiction=jurisdiction)
    assert r is None, f"{text!r} unexpectedly parsed to {r!r}"


def _ad(d):
    return AstroDate(d.year, d.month, d.day)


# -- holiday-aware count (jurisdiction=US): skips Christmas + New Year -----

@pytest.mark.parametrize("text,expected", [
    ("in 1 business day", date(2026, 12, 24)),
    ("in 2 business days", date(2026, 12, 28)),   # skips Fri Christmas + w/e
    ("in 3 business days", date(2026, 12, 29)),
    ("in 4 business days", date(2026, 12, 30)),
    ("in 5 business days", date(2026, 12, 31)),
    ("in 6 business days", date(2027, 1, 4)),      # skips New Year + w/e
    ("in 5 working days", date(2026, 12, 31)),
])
def test_count_us(text, expected):
    assert start(text, "US") == _ad(expected)


# -- holiday-blind default (no jurisdiction): weekday-only ------------------

@pytest.mark.parametrize("text,expected", [
    ("in 1 business day", date(2026, 12, 24)),
    ("in 2 business days", date(2026, 12, 25)),    # Christmas counts, blind
    ("in 3 business days", date(2026, 12, 28)),
    ("in 5 business days", date(2026, 12, 30)),
    ("in 6 business days", date(2026, 12, 31)),
])
def test_count_holiday_blind(text, expected):
    assert start(text) == _ad(expected)


# -- "the next" == N=1 -----------------------------------------------------

def test_next_working_day_us():
    assert start("the next working day", "US") == _ad(date(2026, 12, 24))


def test_next_business_day_blind():
    assert start("the next business day") == _ad(date(2026, 12, 24))


# -- composition on a resolved reference ("... after christmas") -----------
# christmas is Fri 2026-12-25; after it: Mon28(1) Tue29(2) Wed30(3).

@pytest.mark.parametrize("text,expected,juris", [
    ("3 working days after christmas", date(2026, 12, 30), "US"),
    ("3 working days after christmas", date(2026, 12, 30), None),
    ("one working day after christmas", date(2026, 12, 28), "US"),
    ("2 business days before christmas", date(2026, 12, 23), "US"),
    ("2 business days before christmas", date(2026, 12, 23), None),
])
def test_composition(text, expected, juris):
    assert start(text, juris) == _ad(expected)


# -- day-wide width --------------------------------------------------------

def test_business_day_is_day_wide():
    from datetime import timedelta
    r = extract_timespan("in 3 business days", "en", ANCHOR, jurisdiction="US")
    assert r[0].width == timedelta(days=1)


# -- negatives: "business"/"working" without a count never fire ------------

@pytest.mark.parametrize("text", [
    "business as usual",
    "back to business",
    "mind your own business",
    "working from home",
])
def test_negatives(text):
    nomatch(text)
    nomatch(text, "US")
