# -*- coding: utf-8 -*-
"""R145 (pl) -- "pierwszy/ostatni <weekday> roku" (bare "roku" = genitive
"of the year", no number) silently ignored the year word and answered
relative to the anchor with "roku" stranded; "pierwszy poniedziałek 2027
roku" (postposed year word trailing an explicit year) resolved the correct
span but still stranded "roku" as unmatched remainder.

See ``test/nl_corpus_en/test_nl_r145_year_word_ordweekday.py`` for the full
defect writeup. Polish's ``scoped_ordinal`` fully ``override``s the shared
base grammar (R142 precedent), so its year_word orders are a per-locale
addition to that override list rather than an inherited base order.

Expected dates are computed by INDEPENDENT arithmetic -- a plain
``datetime.date`` weekday scan over the named/anchor year -- never read back
from the parser.
"""
from datetime import date, datetime, timedelta

import pytest

from chronologia import extract_timespan

LANG = "pl"
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


@pytest.mark.parametrize("text,expected", [
    ("pierwszy poniedziałek roku", _nth_weekday(2026, MONDAY, 1)),
    ("ostatni poniedziałek roku", _nth_weekday(2026, MONDAY, -1)),
])
def test_ordinal_weekday_of_bare_year_word_pl(text, expected):
    span = _span(text)
    assert (span.start.year, span.start.month, span.start.day) == \
        (expected.year, expected.month, expected.day)


def test_ostatni_is_not_anchor_relative():
    # the literal shape of the defect: without the fix "ostatni poniedziałek
    # roku" answered the PAST anchor-relative Monday (Aug 10 2026), not the
    # last Monday of the whole year.
    span = _span("ostatni poniedziałek roku")
    assert span.start != date(2026, 8, 10)
    assert span.start == _nth_weekday(2026, MONDAY, -1)
    assert span.start == date(2026, 12, 28)


@pytest.mark.parametrize("text", [
    "pierwszy poniedziałek roku",
    "ostatni poniedziałek roku",
])
def test_no_remainder_stranded_bare_year_word_pl(text):
    r = extract_timespan(text, LANG, ANCHOR)
    assert r is not None
    assert r[1].strip() == ""


def test_explicit_year_with_postposed_year_word_leaves_no_remainder():
    # cosmetic half of the defect: the span was already correct, only
    # "roku" was left stranded.
    r = extract_timespan("pierwszy poniedziałek 2027 roku", LANG, ANCHOR)
    assert r is not None
    span, remainder = r
    expected = _nth_weekday(2027, MONDAY, 1)
    assert (span.start.year, span.start.month, span.start.day) == \
        (expected.year, expected.month, expected.day)
    assert remainder.strip() == ""


def test_control_ordinal_weekday_of_bare_gyear_still_works_pl():
    # the R142 bare-GYEAR reading (no year_word at all) must not regress.
    expected = _nth_weekday(2027, MONDAY, -1)
    span = _span("ostatni poniedziałek 2027")
    assert (span.start.year, span.start.month, span.start.day) == \
        (expected.year, expected.month, expected.day)


def test_control_ordinal_weekday_of_named_month_still_works_pl():
    expected = _nth_weekday(2027, MONDAY, 1)
    assert expected == date(2027, 1, 4)
    span = _span("pierwszy poniedziałek stycznia 2027")
    assert (span.start.year, span.start.month, span.start.day) == (2027, 1, 4)
