# -*- coding: utf-8 -*-
"""Shared helpers for the Arabic (ar) natural-language corpus.

The contract under test is the public span-native edge
``extract_timespan(text, "ar", anchor)``: a sentence a human would say,
asserting the exact parsed span.  Expected values are derived by hand or by
independent Python date arithmetic that never touches the parser.

The mission anchor is a Tuesday, 13:04.  Arabic is written right-to-left; the
tokenizer is script-agnostic and mixed-direction strings (Western or
Arabic-Indic digits inside RTL text) tokenize the same -- exercised
explicitly by ``test_nl_rtl``.
"""
from datetime import datetime, timedelta  # noqa: F401

from dateutil.relativedelta import relativedelta  # noqa: F401

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate, DateSpan  # noqa: F401

LANG = "ar"

#: the mission anchor -- a Tuesday, 13:04.
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


def remainder(text, anchor=ANCHOR):
    r = parse(text, anchor)
    assert r is not None, f"{text!r} did not parse"
    return r[1]


def nomatch(text, anchor=ANCHOR):
    r = parse(text, anchor)
    assert r is None, f"{text!r} unexpectedly parsed to {r!r}"


def ad(dt):
    return AstroDate(dt.year, dt.month, dt.day, dt.hour, dt.minute,
                     dt.second, dt.microsecond)
