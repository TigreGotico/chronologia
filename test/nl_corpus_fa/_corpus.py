# -*- coding: utf-8 -*-
"""Shared helpers for the fa natural-language corpus.

The contract: extract_timespan(text, 'fa', anchor). Anchor is a Tuesday (2017-06-27 13:04). Persian is RTL/Arabic-script; the tokenizer works in logical order so RTL is transparent. ZWNJ compounds ship as space surfaces glued by the multiword merge. The PRIMARY calendar is Solar Hijri (month_solar_hijri_arithmetic_N), resolved through solar_hijri_arithmetic. پیش/قبل=ago, بعد/دیگر=in. Spelled numbers fold via ovos-number-parser (numbers_fa).
"""
from datetime import datetime, timedelta  # noqa: F401

from dateutil.relativedelta import relativedelta  # noqa: F401

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate, DateSpan  # noqa: F401

LANG = "fa"

ANCHOR = datetime(2017, 6, 27, 13, 4)


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
