"""Shared helpers for the Belarusian natural-language corpus.

The contract under test is the public span-native edge
``extract_timespan(text, "be", anchor)``: feed a sentence a Belarusian speaker
would actually say and assert the *exact* parsed span.  Expected values are
derived by hand or by independent Python date arithmetic that does not touch
the parser -- never by pinning the engine's own output.

Three facts drive most of what follows.  Belarusian names the minute хвіліна
and the hour гадзіна, not the Russian cognates мінута and час, so a locale
bootstrapped from Russian would be wrong on the two most load-bearing unit
words.  A date names its month in the genitive after the day number ("25
сакавіка") and in the nominative on its own ("сакавік"), and the long form
closes with the skarot "г.".  And the spoken clock counts toward the COMING
hour in both halves: "палова на пятую" is half of the way to the fifth hour,
04:30, and "без чвэрці адзінаццаць" is a quarter short of the eleventh, 10:45.
"""
from datetime import datetime

from dateutil.relativedelta import relativedelta  # noqa: F401

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate, DateSpan  # noqa: F401

#: the mission anchor -- a Tuesday, 13:04.
ANCHOR = datetime(2017, 6, 27, 13, 4)


def parse(text, anchor=ANCHOR):
    return extract_timespan(text, "be", anchor)


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
