"""Shared helpers for the Korean natural-language corpus.

The contract under test is the public span-native edge
``extract_timespan(text, "ko", anchor)``: feed a sentence a Korean speaker
would actually write and assert the exact parsed span.  Expected values are
derived by hand or by independent Python date arithmetic that never touches
the parser.

Three facts of the language drive most of what follows.  Korean runs two
complete numeral series and the counter chooses between them -- the hours of
the clock take the native series (세 시) while the minutes beside them and
every calendar field take Sino (십 분), so one phrase carries both and a
numeral in the wrong series names nothing.  The clock counts forward from the
hour just named, and the backward reading is marked, obligatorily and last, by
전.  And the same one-syllable words carry several senses at once: 일 is the
day, the numeral one and Sunday, 월 is the month and Monday, so every match is
decided by the slot a word stands in and never by the string.
"""
from datetime import datetime, timedelta

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate, DateSpan  # noqa: F401

#: the anchor -- a Wednesday, 13:04.
ANCHOR = datetime(2027, 5, 12, 13, 4)


def parse(text, anchor=ANCHOR):
    return extract_timespan(text, "ko", anchor)


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
