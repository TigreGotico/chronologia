"""Shared helpers for the Filipino natural-language corpus.

The contract under test is the public span-native edge
``extract_timespan(text, "fil", anchor)``: feed a sentence a Filipino speaker
would actually say and assert the *exact* parsed span.  Expected values are
derived by hand from the sourced worked examples or by independent Python
date arithmetic that does not touch the parser -- never by pinning the
engine's own output.

Two facts drive most of what follows.  Filipino counts with two whole numeral
systems at once -- native (isa, dalawa, ...) and Spanish-derived (uno, dos,
...) -- and the clock uses both: the Spanish set after ``alas``/``ala`` with
the hour as a bare cardinal, the native set with the hour as an ``ika-``
ordinal and a minute count running toward it.  That native count runs FORWARD
from the named hour with ``makalipas`` and BACKWARD from it with ``bago``,
and the source states the backward frame is how a time past the half hour is
told.

Dates run day-month-year with the day spelled as an ``ika-`` ordinal, the
month as its Spanish-derived name, and a spelled year in native numerals --
three slots, two numeral systems, one date.
"""
from datetime import datetime, timedelta

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate, DateSpan  # noqa: F401

#: the mission anchor -- a Tuesday, 13:04.
ANCHOR = datetime(2017, 6, 27, 13, 4)


def parse(text, anchor=ANCHOR):
    return extract_timespan(text, "fil", anchor)


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


def next_time(h, mi, anchor=ANCHOR):
    """The next wall-clock occurrence of ``h:mi`` at or after the anchor."""
    cand = anchor.replace(hour=h, minute=mi, second=0, microsecond=0)
    if cand <= anchor:
        cand += timedelta(days=1)
    return ad(cand)
