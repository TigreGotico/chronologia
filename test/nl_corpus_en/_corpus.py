"""Shared helpers for the English natural-language corpus.

The contract under test is the public span-native edge
``extract_timespan(text, "en", anchor)``: feed a sentence a human would
actually say and assert the *exact* parsed span.  Expected values are
derived by hand (or by independent Python date arithmetic that does not
touch the parser) -- never by pinning the engine's own output.
"""
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate, DateSpan  # noqa: F401

#: the mission anchor -- a Tuesday, 13:04.
ANCHOR = datetime(2017, 6, 27, 13, 4)


def parse(text, anchor=ANCHOR):
    """Return ``(span, remainder)`` or ``None``."""
    return extract_timespan(text, "en", anchor)


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
    """datetime -> AstroDate (drops nothing; keeps the time-of-day)."""
    return AstroDate(dt.year, dt.month, dt.day, dt.hour, dt.minute,
                     dt.second, dt.microsecond)
