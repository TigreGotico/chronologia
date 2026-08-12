# -*- coding: utf-8 -*-
"""R142 (de) -- "letzter/erster <weekday> <bare YEAR>" (German drops the
connector entirely) silently ignored the year and answered relative to the
anchor. See ``test/nl_corpus_en/test_nl_r142_ordweekday_year.py`` for the
full defect writeup; this is the de sibling exercising the connector-less
"of? GYEAR" order.

Expected dates are computed by INDEPENDENT arithmetic -- a plain
``datetime.date`` weekday scan over the named year -- never read back from
the parser.
"""
from datetime import date, datetime, timedelta

import pytest

from chronologia import extract_timespan

LANG = "de"
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


def _nomatch(text, anchor=ANCHOR):
    r = extract_timespan(text, LANG, anchor)
    assert r is None, f"{text!r} unexpectedly parsed to {r!r}"


MONDAY = 0


@pytest.mark.parametrize("text,expected", [
    ("letzter montag 2026", _nth_weekday(2026, MONDAY, -1)),
    ("erster montag 2027", _nth_weekday(2027, MONDAY, 1)),
])
def test_ordinal_weekday_of_bare_year_de(text, expected):
    span = _span(text)
    assert (span.start.year, span.start.month, span.start.day) == \
        (expected.year, expected.month, expected.day)


def test_control_ordinal_weekday_of_named_month_still_works_de():
    expected = _nth_weekday(2027, MONDAY, 1)
    assert expected == date(2027, 1, 4)
    span = _span("erster montag im januar 2027")
    assert (span.start.year, span.start.month, span.start.day) == (2027, 1, 4)


def test_out_of_range_ordinal_refuses_whole_extraction_de():
    _nomatch("54. montag 2027")


def test_embedded_in_sentence_de():
    span = _span("wir treffen uns am letzter montag 2026 zur besprechung")
    expected = _nth_weekday(2026, MONDAY, -1)
    assert (span.start.year, span.start.month, span.start.day) == \
        (expected.year, expected.month, expected.day)
