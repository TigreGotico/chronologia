# -*- coding: utf-8 -*-
"""Shared helpers for the id natural-language corpus.

The contract: extract_timespan(text, 'id', anchor). Anchor is a Wednesday noon (2026-07-15). Indonesian is isolating (no inflection); lalu is the past (ago) marker, lagi the future one, depan the 'next' relative marker; spelled numbers fold via ovos-number-parser (numbers_id). Sunday is registered as 'ahad' so 'minggu' stays unambiguously the week unit.
"""
from datetime import datetime, timedelta  # noqa: F401

from dateutil.relativedelta import relativedelta  # noqa: F401

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate, DateSpan  # noqa: F401

LANG = "id"

ANCHOR = datetime(2026, 7, 15, 12, 0)


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
