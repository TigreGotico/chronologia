# -*- coding: utf-8 -*-
"""R145 (ru) -- "первый/последний <weekday> [<YEAR>] года" (postposed
"года" = genitive "of the year") stranded the year word. With an explicit
year ("первый понедельник 2027 года") the span was already correct but
"2027 года" left "года" unconsumed after only the number bound; with no
number at all ("первый понедельник года") there was no matching order
whatsoever and the phrase fell through to the anchor-relative reading,
silently ignoring the of-the-year scoping and stranding "года".

See ``test/nl_corpus_en/test_nl_r145_year_word_ordweekday.py`` for the full
defect writeup. Russian's ``scoped_ordinal`` fully ``override``s the shared
base grammar (R142 precedent), so its year_word orders are a per-locale
addition to that override list rather than an inherited base order.

Expected dates are computed by INDEPENDENT arithmetic -- a plain
``datetime.date`` weekday scan over the named/anchor year -- never read
back from the parser.
"""
from datetime import date, datetime, timedelta

import pytest

from chronologia import extract_timespan

LANG = "ru"
ANCHOR = datetime(2026, 8, 13, 10, 0)


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


def test_explicit_year_with_postposed_year_word_leaves_no_remainder():
    r = extract_timespan("первый понедельник 2027 года", LANG, ANCHOR)
    assert r is not None
    span, remainder = r
    expected = _nth_weekday(2027, MONDAY, 1)
    assert (span.start.year, span.start.month, span.start.day) == \
        (expected.year, expected.month, expected.day)
    assert remainder.strip() == ""


@pytest.mark.parametrize("text,expected", [
    ("первый понедельник года", _nth_weekday(2026, MONDAY, 1)),
    ("последний понедельник года", _nth_weekday(2026, MONDAY, -1)),
])
def test_ordinal_weekday_of_bare_year_word_ru(text, expected):
    r = extract_timespan(text, LANG, ANCHOR)
    assert r is not None
    span, remainder = r
    assert (span.start.year, span.start.month, span.start.day) == \
        (expected.year, expected.month, expected.day)
    assert remainder.strip() == ""


def test_control_ordinal_weekday_of_named_month_still_works_ru():
    expected = _nth_weekday(2027, MONDAY, 1)
    assert expected == date(2027, 1, 4)
    span = _span("первый понедельник января 2027")
    assert (span.start.year, span.start.month, span.start.day) == (2027, 1, 4)
