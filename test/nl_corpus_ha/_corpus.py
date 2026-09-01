"""Shared helpers for the Hausa natural-language corpus.

The contract under test is the public span-native edge
``extract_timespan(text, "ha", anchor)``: feed a sentence a Hausa speaker
would actually write and assert the exact parsed span.  Expected values are
derived by hand or by independent Python date arithmetic that never touches
the parser.

Three facts of the language drive most of what follows.  The date line puts
*ga* between the day and the month -- "10 ga watan Oktoba 2022" -- and the
month name takes a genitive *-n* when a noun leans on it.  A relative offset
trails its marker and the marker is a whole relative clause agreeing with the
unit noun, so "kwanaki uku da suka gabata" is three days ago and "watan da ya
gabata" is last month with the same words.  And the hour of the day is the
Western one: *ƙarfe* leads the number and a following *na*-phrase says which
half of the day is meant, so "ƙarfe 1:00 na rana" is 13:00 and not 01:00.
"""
from datetime import datetime, timedelta

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate, DateSpan  # noqa: F401

#: the anchor -- a Wednesday, 13:04.
ANCHOR = datetime(2027, 5, 12, 13, 4)


def parse(text, anchor=ANCHOR):
    return extract_timespan(text, "ha", anchor)


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


def month_span(y, m):
    """The whole-month span, ending at the first of the following month."""
    end = datetime(y + (m == 12), m % 12 + 1, 1)
    return (ad(datetime(y, m, 1)), ad(end))


def year_span(y):
    return (ad(datetime(y, 1, 1)), ad(datetime(y + 1, 1, 1)))


def minute_at(y, m, d, hh, mm):
    """The minute-wide span a clock reading returns."""
    base = datetime(y, m, d, hh, mm)
    return (ad(base), ad(base + timedelta(minutes=1)))


def offset_day(n, anchor=ANCHOR):
    """The day-wide span n whole days from the anchor instant."""
    base = anchor + timedelta(days=n)
    return (ad(base), ad(base + timedelta(days=1)))


def offset_week(n, anchor=ANCHOR):
    base = anchor + timedelta(weeks=n)
    return (ad(base), ad(base + timedelta(weeks=1)))
