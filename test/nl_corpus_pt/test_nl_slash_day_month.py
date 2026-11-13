# -*- coding: utf-8 -*-
"""A slash date with no year is a day and a month, pt.

CLDR 49 gives pt and pt-PT the numeric day-and-month pattern "dd/MM"
(``availableFormats``, skeletons ``Md`` and ``MMdd``), so "25/12" is 25
December.  A date with no year names the next time that day comes round
(class 3): the anchor's own day is that day.  Without the day word "dia"
both numbers are written with two digits, as the pattern writes them, so a
fraction ("1/2 hora", "3/4 do bolo") stays a fraction.  A day of the month
is a whole number, so a fraction after "dia" is no day, and "dia 1/1" is
1 January, never the first day of some month.

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
    ("dia 1/1", datetime(2027, 1, 1)),
    ("dia 2/1", datetime(2027, 1, 2)),
    ("no dia 24/12", datetime(2026, 12, 24)),
    ("no dia 6/3", datetime(2027, 3, 6)),
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
    "dia 30/2",
    "dia 13/13",
    "dia 2,5",
    "1/2 hora",
    "3/4 do bolo",
])
def test_no_such_day_and_a_fraction_are_no_date(text):
    assert extract_timespan(text, "pt-PT", THURSDAY) is None


def test_a_fraction_count_keeps_its_reading():
    r = extract_timespan("daqui a 1/2 hora", "pt-PT", THURSDAY)
    assert r.span.start == ad(datetime(2026, 11, 12, 10, 30))
    assert r.remainder == ""


def _next_day(day, month, hour=0):
    """The first (day, month) on or after the anchor's day, or None."""
    for year in range(2026, 2035):
        try:
            value = datetime(year, month, day, hour)
        except ValueError:
            continue
        if value.date() >= THURSDAY.date():
            return value
    return None


def test_every_day_and_month():
    # A day the month never holds has no reading: the phrase is refused, or
    # the date words stay in the remainder.
    forms = [("dia %d/%d", 0), ("dia %02d/%02d", 0), ("%02d/%02d", 0),
             ("no dia %d/%d às 10", 10)]
    wrong = []
    for form, hour in forms:
        for month in range(1, 13):
            for day in range(1, 32):
                text = form % (day, month)
                expected = _next_day(day, month, hour)
                r = extract_timespan(text, "pt-PT", THURSDAY)
                if expected is None:
                    if r is not None and f"{day}/{month}" not in r.remainder:
                        wrong.append((text, r.span.start, r.remainder))
                elif r is None or (r.span.start, r.remainder) != (
                        ad(expected), ""):
                    wrong.append((text, r and r.span.start,
                                  r and r.remainder))
    assert wrong == []


@pytest.mark.parametrize("text,start,end", [
    ("de 20/12 às 9h até 25 de dezembro",
     datetime(2026, 12, 20, 9), datetime(2026, 12, 26)),
    ("de 01/01 às 9:00 até 05/01",
     datetime(2027, 1, 1, 9), datetime(2027, 1, 6)),
])
def test_a_range_from_a_slash_date_with_a_clock(text, start, end):
    # The written left date is the start; the right date runs to its end.
    r = extract_timespan(text, "pt-PT", THURSDAY)
    assert r is not None, f"{text!r} did not parse"
    assert (r.span.start, r.span.end) == (ad(start), ad(end))
    assert r.remainder == ""


def test_a_weekday_that_labels_a_slash_date_keeps_the_count():
    # Friday 27 November is the written date; the count does not move it.
    r = extract_timespan("daqui a uma semana, sexta-feira 27/11", "pt-PT",
                         THURSDAY)
    assert r is not None
    assert (r.span.start, r.span.end) == (ad(datetime(2026, 11, 27)),
                                          ad(datetime(2026, 11, 28)))
    assert r.remainder == "daqui a uma semana"
