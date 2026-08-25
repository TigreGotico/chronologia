"""Shared helpers for the Latvian natural-language corpus.

The contract under test is the public span-native edge
``extract_timespan(text, "lv", anchor)``: feed a sentence a Latvian speaker
would actually say and assert the *exact* parsed span.  Expected values are
derived by hand or by independent Python date arithmetic that does not touch
the parser -- never by pinning the engine's own output.

Three facts drive most of what follows.  A Latvian date has two shapes, not
one: the dateline names its month in the nominative ("2017. gada 29. maijs")
and the sentence-embedded adverbial names it in the locative ("3. maijā").
A duration marker puts its phrase in the dative, with the unit noun in the
genitive singular after a numeral ending in 1 and the dative plural otherwise
("pirms gada", "pirms 11 gadiem").  And the spoken clock counts toward the
COMING hour, written as one word: "pusčetri" is half of the fourth hour,
03:30.
"""
from datetime import datetime

from dateutil.relativedelta import relativedelta  # noqa: F401

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate, DateSpan  # noqa: F401

#: the mission anchor -- a Tuesday, 13:04.
ANCHOR = datetime(2017, 6, 27, 13, 4)


def parse(text, anchor=ANCHOR):
    return extract_timespan(text, "lv", anchor)


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
