"""Shared helpers for the Macedonian natural-language corpus.

The contract under test is the public span-native edge
``extract_timespan(text, "mk", anchor)``: feed a sentence a Macedonian speaker
would actually write and assert the exact parsed span.  Expected values are
derived by hand or by independent Python date arithmetic that never touches the
parser.

Three facts of the language drive most of what follows.  The clock is additive
only -- minutes are counted forward from the hour already named, all the way
through fifty-nine, and the half hour is added to that hour rather than taken
off the next.  A noun behind a numeral takes its count form, which is a
different word from its general plural: five days is "пет дена" while денови is
the plural that counts nothing.  And last/next are said per unit: the year has
the dedicated adverbs лани and догодина, everything else takes минат/следен
agreeing in gender with its noun.
"""
from datetime import datetime, timedelta

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate, DateSpan  # noqa: F401

#: the anchor -- a Wednesday, 13:04.
ANCHOR = datetime(2027, 5, 12, 13, 4)


def parse(text, anchor=ANCHOR):
    return extract_timespan(text, "mk", anchor)


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
