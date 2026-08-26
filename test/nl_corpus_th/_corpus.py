# -*- coding: utf-8 -*-
"""Shared helpers for the Thai natural-language corpus.

The contract under test is the public span-native edge
``extract_timespan(text, "th", anchor)``: feed a phrase a Thai speaker would
actually write and assert the exact parsed span.  Expected values are derived
by hand or by independent Python date arithmetic that never touches the parser.

Three facts of the language drive most of what follows.  Thai is written
without spaces between words, so a date phrase reaches the engine as one
undivided run and has to be cut back into words before any slot can bind; the
cut is made only when the whole run is covered by surfaces the locale knows, so
ordinary prose is left alone.  The hour of the day is named on a six-hour
cycle whose word changes with the part of the day, and one of those words --
``โมง`` -- is ambiguous between the morning and the evening unless a day-part
word is attached, so bare ``N โมง`` does not parse at all.  And the civil year
is normally the Buddhist Era, 543 ahead of the Common Era, which is read from
the ``พ.ศ.`` marker and never guessed from a bare four-digit year.
"""
from datetime import datetime, timedelta

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate, DateSpan  # noqa: F401

#: the anchor -- a Wednesday, 13:04.
ANCHOR = datetime(2027, 5, 12, 13, 4)


def parse(text, anchor=ANCHOR):
    return extract_timespan(text, "th", anchor)


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
    assert r is not None, f"{text!r} did not parse (expected a span)"
    return r[1]


def nomatch(text, anchor=ANCHOR):
    r = parse(text, anchor)
    assert r is None, f"{text!r} unexpectedly parsed to {r!r}"


def ad(dt):
    return AstroDate(dt.year, dt.month, dt.day, dt.hour, dt.minute,
                     dt.second, dt.microsecond)


def day(y, m, d):
    """The whole-day span of a calendar date."""
    return (ad(datetime(y, m, d)), ad(datetime(y, m, d) + timedelta(days=1)))


def minute_at(y, m, d, hh, mm):
    """The minute-wide span a clock reading returns."""
    base = datetime(y, m, d, hh, mm)
    return (ad(base), ad(base + timedelta(minutes=1)))


def band(y, m, d, from_hm, to_hm, days=0):
    """The span of a day-part band on a given date."""
    s = datetime(y, m, d, *from_hm)
    e = datetime(y, m, d, *to_hm) + timedelta(days=days)
    return (ad(s), ad(e))
