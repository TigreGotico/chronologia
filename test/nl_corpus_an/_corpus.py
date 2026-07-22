# -*- coding: utf-8 -*-
"""Shared helpers for the an natural-language corpus.

The contract: extract_timespan(text, 'an', anchor). Anchor is a Tuesday (2018-06-05 13:04). Aragonese vocabulary follows Juanpabl (the grammar author): demán/manyana tomorrow, pasadoman day after tomorrow, diya/diyas spelling, lowercase months, 'es' as a token-only plural article. fa=ago, en/dentro=in. Spelled numbers fold via ovos-number-parser (numbers_an).
"""
from datetime import datetime, timedelta  # noqa: F401

from dateutil.relativedelta import relativedelta  # noqa: F401

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate, DateSpan  # noqa: F401

LANG = "an"

ANCHOR = datetime(2018, 6, 5, 13, 4)


def parse(text, anchor=ANCHOR):
    return extract_timespan(text, LANG, anchor)


def span(text, anchor=ANCHOR):
    r = parse(text, anchor)
    assert r is not None, f"{text!r} did not parse (expected a span)"
    return r[0]


def start(text, anchor=ANCHOR):
    return span(text, anchor).start


def start_end(text, anchor=ANCHOR):
    s = span(text, anchor)
    return s.start, s.end


def nomatch(text, anchor=ANCHOR):
    r = parse(text, anchor)
    assert r is None, f"{text!r} unexpectedly parsed to {r!r}"


def ad(dt):
    return AstroDate(dt.year, dt.month, dt.day, dt.hour, dt.minute,
                     dt.second, dt.microsecond)
