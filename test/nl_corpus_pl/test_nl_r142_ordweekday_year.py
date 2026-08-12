# -*- coding: utf-8 -*-
"""R142 (pl) -- "pierwszy/ostatni <weekday> <bare YEAR>" (Polish drops the
connector entirely) silently ignored the year and answered relative to the
anchor. See ``test/nl_corpus_en/test_nl_r142_ordweekday_year.py`` for the
full defect writeup. Polish's ``scoped_ordinal`` fully ``override``s the
shared base grammar (postposed genitive month, no "of" word), so its
bare-year order is a per-locale addition to that override list rather than
an inherited base order.

Expected dates are computed by INDEPENDENT arithmetic -- a plain
``datetime.date`` weekday scan over the named year -- never read back from
the parser.
"""
from datetime import date, datetime, timedelta

import pytest

from chronologia import extract_timespan

LANG = "pl"
ANCHOR = datetime(2026, 8, 12)


def _nth_weekday(year, weekday, n):
    jan1 = date(year, 1, 1)
    first = jan1 + timedelta(days=(weekday - jan1.weekday()) % 7)
    days = []
    d = first
    while d.year == year:
        days.append(d)
        d += timedelta(days=7)
    return days[n - 1] if n > 0 else days[n]


def _span(text, anchor=ANCHOR):
    r = extract_timespan(text, LANG, anchor)
    assert r is not None, f"{text!r} did not parse (expected a span)"
    return r[0]


MONDAY = 0


@pytest.mark.parametrize("text,expected", [
    ("pierwszy poniedziałek 2027", _nth_weekday(2027, MONDAY, 1)),
    ("ostatni poniedziałek 2026", _nth_weekday(2026, MONDAY, -1)),
])
def test_ordinal_weekday_of_bare_year_pl(text, expected):
    span = _span(text)
    assert (span.start.year, span.start.month, span.start.day) == \
        (expected.year, expected.month, expected.day)


def test_control_ordinal_weekday_of_named_month_still_works_pl():
    expected = _nth_weekday(2027, MONDAY, 1)
    assert expected == date(2027, 1, 4)
    span = _span("pierwszy poniedziałek stycznia 2027")
    assert (span.start.year, span.start.month, span.start.day) == (2027, 1, 4)
