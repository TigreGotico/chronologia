"""Shared helpers for the Slovak natural-language corpus.

The contract under test is the public span-native edge
``extract_timespan(text, "sk", anchor)``: feed a sentence a Slovak speaker
would actually say and assert the *exact* parsed span.  Expected values are
derived by hand or by independent Python date arithmetic that does not touch
the parser -- never by pinning the engine's own output.

Slovak is a heavily inflected West-Slavic language: the offset unit noun
declines with its preposition ("před 2 lety" instrumental, "před 2 dnech"
locative, "za 5 let" genitive), and dates run day-month-year with a genitive
month name after an ordinal-dot day ("15. srpna 2020").  Direction is a fact
of the marker: "před" is past, "za" is future.
"""
from datetime import datetime

from dateutil.relativedelta import relativedelta  # noqa: F401

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate, DateSpan  # noqa: F401

#: the mission anchor -- a Tuesday, 13:04.
ANCHOR = datetime(2017, 6, 27, 13, 4)


def parse(text, anchor=ANCHOR):
    return extract_timespan(text, "sk", anchor)


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
