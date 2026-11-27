# -*- coding: utf-8 -*-
"""Shared helpers for the kab natural-language corpus.

The contract: extract_timespan(text, 'kab', anchor). Anchor is a Tuesday (2017-06-27 13:04). Kabyle vocabulary comes from the cited tables; the future offset markers "deg" and "sya" rest on Tatoeba sentences cited in marker_future.voc. Spelled numbers read through numtag.
"""
from datetime import datetime, timedelta  # noqa: F401

from dateutil.relativedelta import relativedelta  # noqa: F401

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate, DateSpan  # noqa: F401

LANG = "kab"

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
