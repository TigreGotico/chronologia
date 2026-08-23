"""Shared helpers for the Welsh natural-language corpus.

The contract under test is the public span-native edge
``extract_timespan(text, "cy", anchor)``: feed a sentence a Welsh speaker
would actually say and assert the *exact* parsed span.  Expected values are
derived by hand or by independent Python date arithmetic that does not touch
the parser -- never by pinning the engine's own output.

Three facts drive most of what follows.  Welsh mutates a word's FIRST letter
after a preceding trigger, so the same noun surfaces several ways: the year's
count form is "blynedd" after three, "flynedd" after two and "mlynedd" after
five, and the month Mawrth becomes "Fawrth" after the linking "o".  The
numerals two, three and four agree in gender with the noun they count -- "dwy
flynedd" (feminine) beside "dau fis" (masculine).  And the spoken clock counts
from the hour just named, English-fashion: "hanner awr wedi tri" is 03:30, not
02:30.

Dates run day-month-year, the day either a bare digit, a digit with its
ordinal suffix written solid ("y 3ydd o Orffennaf"), or a spelled ordinal.
"""
from datetime import datetime

from dateutil.relativedelta import relativedelta  # noqa: F401

from chronologia import extract_recurrence, extract_timespan
from chronologia.astrodate import AstroDate, DateSpan  # noqa: F401

#: the mission anchor -- a Tuesday, 13:04.
ANCHOR = datetime(2017, 6, 27, 13, 4)


def parse(text, anchor=ANCHOR):
    return extract_timespan(text, "cy", anchor)


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


def recur(text, anchor=ANCHOR):
    return extract_recurrence(text, "cy", anchor)


def ad(dt):
    return AstroDate(dt.year, dt.month, dt.day, dt.hour, dt.minute,
                     dt.second, dt.microsecond)
