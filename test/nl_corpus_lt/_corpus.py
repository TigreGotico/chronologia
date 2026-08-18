"""Shared helpers for the Lithuanian natural-language corpus.

The contract under test is the public span-native edge
``extract_timespan(text, "lt", anchor)``: feed a sentence a Lithuanian
speaker would actually say and assert the *exact* parsed span.  Expected
values are derived by hand or by independent Python date arithmetic that
does not touch the parser -- never by pinning the engine's own output.

Lithuanian is a heavily inflected Baltic language.  Two facts drive most of
what follows.  The counted noun's form is chosen by the numeral's LAST digit
(singular after 1, plural after 2-9, genitive plural after 0 and 11-19), not
by its magnitude, so "prieš vieną dieną", "prieš tris dienas" and "prieš
vienuolika dienų" are all the same construction.  And the spoken clock counts
toward the COMING hour: "pusė trijų" is half of the third hour, 02:30.

Dates run year-month-day with the month in the genitive and the day either a
digit closed by "d." or a feminine ordinal agreeing with an elided "diena"
("1990 m. kovo 1 d.", "liepos penktoji").
"""
from datetime import datetime

from dateutil.relativedelta import relativedelta  # noqa: F401

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate, DateSpan  # noqa: F401

#: the mission anchor -- a Tuesday, 13:04.
ANCHOR = datetime(2017, 6, 27, 13, 4)


def parse(text, anchor=ANCHOR):
    return extract_timespan(text, "lt", anchor)


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
