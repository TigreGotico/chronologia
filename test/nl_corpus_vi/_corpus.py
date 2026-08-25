"""Shared helpers for the Vietnamese natural-language corpus.

The contract under test is the public span-native edge
``extract_timespan(text, "vi", anchor)``: feed a sentence a Vietnamese speaker
would actually say and assert the *exact* parsed span.  Expected values are
derived by hand or by independent Python date arithmetic that does not touch
the parser -- never by pinning the engine's own output.

Vietnamese is isolating: no case, no gender, no number, no agreement of any
kind.  What carries the grammar instead is word order and a set of positional
numeral substitutions -- mười becomes mươi above nineteen, five becomes lăm at
the end of a compound, one becomes mốt and four becomes tư after mươi -- and
those substitutions reach into the calendar, because both the weekdays and the
months are NUMBERED: thứ hai is Monday ("rank two") and tháng tư is April
("month four", with the tư substitute).

The clock splits across the hour.  rưỡi counts forward from the hour already
named, so hai giờ rưỡi is 02:30, while kém names the hour being approached and
subtracts, so ba giờ kém mười lăm is 02:45.  Both idioms live in the same
sentence-grammar and neither direction is the locale's default.

Dates run day-month-year, and the temporal markers trail what they govern
(ba ngày trước) except cách đây, which leads it.
"""
from datetime import datetime

from dateutil.relativedelta import relativedelta  # noqa: F401

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate, DateSpan  # noqa: F401

#: the mission anchor -- a Tuesday, 13:04.
ANCHOR = datetime(2017, 6, 27, 13, 4)


def parse(text, anchor=ANCHOR):
    return extract_timespan(text, "vi", anchor)


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
