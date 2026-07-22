# -*- coding: utf-8 -*-
"""Shared helpers for the mwl natural-language corpus.

The contract: extract_timespan(text, 'mwl', anchor). Anchor is a Tuesday (2017-06-27 13:04). Mirandese is a NEW language no parser supported before; every surface is cited in papers/linguistics/mwl/INDEX.md (Wiktionary + numbers_mwl), never copied from Asturian. Only the past-offset marker 'hai' is citable; forward offsets and weekday next/last markers are honestly absent. manhana carries the Ibero-Romance morning/tomorrow polysemy. Spelled numbers fold via ovos-number-parser (numbers_mwl).
"""
from datetime import datetime, timedelta  # noqa: F401

from dateutil.relativedelta import relativedelta  # noqa: F401

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate, DateSpan  # noqa: F401

LANG = "mwl"

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
