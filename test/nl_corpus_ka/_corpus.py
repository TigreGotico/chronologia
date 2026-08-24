"""Shared helpers for the Georgian natural-language corpus.

The contract under test is the public span-native edge
``extract_timespan(text, "ka", anchor)``: feed a sentence a Georgian speaker
would actually say and assert the *exact* parsed span.  Expected values are
derived by hand or by independent Python date arithmetic that does not touch
the parser -- never by pinning the engine's own output.

Three facts drive most of what follows.  Georgian counts in base twenty, so
30 is ოცდაათი ("twenty-and-ten") and 99 is ოთხმოცდაცხრამეტი
("eighty-and-nineteen"); the temporal markers are POSTPOSITIONS that trail
the noun they govern and put it in the genitive, so "three months ago" is
"სამი თვის წინ" with თვის the genitive of თვე; and the spoken clock names the
hour it is APPROACHING, in the genitive, so "ორის ნახევარი" is half toward
two, 01:30.

Dates run day-month-year, and the month name never inflects.
"""
from datetime import datetime

from dateutil.relativedelta import relativedelta  # noqa: F401

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate, DateSpan  # noqa: F401

#: the mission anchor -- a Tuesday, 13:04.
ANCHOR = datetime(2017, 6, 27, 13, 4)


def parse(text, anchor=ANCHOR):
    return extract_timespan(text, "ka", anchor)


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
