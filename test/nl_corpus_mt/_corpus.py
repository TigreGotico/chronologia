"""Shared helpers for the Maltese natural-language corpus.

The contract under test is the public span-native edge
``extract_timespan(text, "mt", anchor)``: feed a sentence a Maltese speaker
would actually write and assert the exact parsed span.  Expected values are
derived by hand or by independent Python date arithmetic that never touches
the parser.

Three facts of the language drive most of what follows.  The definite article
assimilates to nine sun letters, so the same article surfaces as il-, l-, it-,
is-, iċ-, id-, in-, ir-, ix-, iz- and iż- and a date-bearing word is met in
whichever form its own initial consonant forces.  Numbers two through ten take
an attributive (construct) form before the noun they count, distinct from the
free-standing form, and from eleven upward the noun goes back to the singular
behind an ``-il`` linker.  And the clock changes anchor at the half hour:
minutes before it are added to the hour already named, minutes after it are
subtracted from the hour still coming.
"""
from datetime import datetime, timedelta

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate, DateSpan  # noqa: F401

#: the anchor -- a Wednesday, 13:04.
ANCHOR = datetime(2027, 5, 12, 13, 4)


def parse(text, anchor=ANCHOR):
    return extract_timespan(text, "mt", anchor)


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
