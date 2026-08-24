"""Shared helpers for the Eastern Armenian natural-language corpus.

The contract under test is the public span-native edge
``extract_timespan(text, "hy", anchor)``: feed a sentence an Armenian speaker
would actually say and assert the *exact* parsed span.  Expected values are
derived by hand or by independent Python date arithmetic that does not touch
the parser -- never by pinning the engine's own output.

Three facts drive most of what follows.  The relative-offset markers are
POSTPOSITIONS -- ``առաջ`` closes a backward offset and ``անց``/``հետո`` a
forward one -- and the forward offset has a second, suffixed realisation: the
ablative on the unit noun itself (``երեք օրից`` == in three days).  The spoken
clock counts from the hour already reached, English-style: ``ութ անց կես`` is
08:30.  And the numerals are decimal and write 21..99 as a single word
(``քսանմեկ`` == 21).

Dates run day-month-year in digits (``05.06.2019``) and month-genitive-first
when the month is spelled (``հունիսի 5``); a year may carry the trailing
``թ.``  The definite article is a suffix, so most nouns appear both bare and
in a ``-ը``/``-ն`` form.
"""
from datetime import datetime

from dateutil.relativedelta import relativedelta  # noqa: F401

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate, DateSpan  # noqa: F401

#: the mission anchor -- a Tuesday, 13:04.
ANCHOR = datetime(2017, 6, 27, 13, 4)


def parse(text, anchor=ANCHOR):
    return extract_timespan(text, "hy", anchor)


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
