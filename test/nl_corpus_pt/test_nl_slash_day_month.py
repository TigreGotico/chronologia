# -*- coding: utf-8 -*-
"""A slash date with no year is a day and a month, pt.

CLDR 49 gives pt and pt-PT the numeric day-and-month pattern "dd/MM"
(``availableFormats``, skeletons ``Md`` and ``MMdd``), so "25/12" is 25
December.  A date with no year names the next time that day comes round
(class 3): the anchor's own day is that day.  Without the day word "dia"
both numbers are written with two digits, as the pattern writes them, so a
fraction ("1/2 hora", "3/4 do bolo") stays a fraction.  A day of the month
is a whole number, so a fraction after "dia" is no day.

Anchor Thursday 2026-11-12 10:00.
"""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_timespan

from ._corpus import ad

THURSDAY = datetime(2026, 11, 12, 10, 0)


@pytest.mark.parametrize("lang", ["pt-PT", "pt-BR"])
@pytest.mark.parametrize("text,expected", [
    ("no dia 25/12 às 19h30", datetime(2026, 12, 25, 19, 30)),
    ("25/12 às 19h30", datetime(2026, 12, 25, 19, 30)),
])
def test_a_slash_date_with_a_clock(lang, text, expected):
    r = extract_timespan(text, lang, THURSDAY)
    assert r is not None, f"{text!r} did not parse"
    assert r.span.start == ad(expected)
    assert r.remainder == ""


@pytest.mark.parametrize("text,expected", [
    ("25/12", datetime(2026, 12, 25)),
    ("no dia 25/12", datetime(2026, 12, 25)),
    ("dia 5/3", datetime(2027, 3, 5)),
    ("o dia 05/03", datetime(2027, 3, 5)),
    ("12/11", datetime(2026, 11, 12)),
    ("11/11", datetime(2027, 11, 11)),
    ("29/02", datetime(2028, 2, 29)),
])
def test_a_slash_date_is_the_next_such_day(text, expected):
    r = extract_timespan(text, "pt-PT", THURSDAY)
    assert r is not None, f"{text!r} did not parse"
    assert (r.span.start, r.span.end) == (
        ad(expected), ad(expected + timedelta(days=1)))
    assert r.remainder == ""


@pytest.mark.parametrize("text", [
    "31/04",
    "25/13",
    "no dia 25/13",
    "no dia 31/04",
    "1/2 hora",
    "3/4 do bolo",
])
def test_no_such_day_and_a_fraction_are_no_date(text):
    assert extract_timespan(text, "pt-PT", THURSDAY) is None


def test_a_fraction_count_keeps_its_reading():
    r = extract_timespan("daqui a 1/2 hora", "pt-PT", THURSDAY)
    assert r.span.start == ad(datetime(2026, 11, 12, 10, 30))
    assert r.remainder == ""
