"""Shared helpers for the Hindi natural-language corpus.

The contract under test is the public span-native edge
``extract_timespan(text, "hi", anchor)``: feed a sentence a Hindi speaker
would actually say and assert the *exact* parsed span.  Expected values are
derived by hand, from the dictionary's own worked example, or by independent
Python date arithmetic that never touches the parser.

Three facts of the language drive most of what follows.  Numerals 1..99 are
suppletive -- बयालीस (42) is not built from any smaller word -- so the whole
range is a curated table and a boundary case anywhere in it is a table entry,
not a rule.  Markers are POSTPOSED: the date leads and को / से / तक / पहले /
बाद trail it, so an offset reads NUM UNIT MARKER ("तीन दिन पहले").  And the
spoken clock is asymmetric: साढ़े and सवा count FORWARD from the hour they
name while पौने counts BACK from it, so पौने दस is 09:45.

Both digit systems are attested and both are exercised: ASCII and the
Devanagari ०-९.
"""
from datetime import datetime

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate, DateSpan  # noqa: F401

#: the mission anchor -- a Tuesday, 13:04.
ANCHOR = datetime(2017, 6, 27, 13, 4)


def parse(text, anchor=ANCHOR):
    return extract_timespan(text, "hi", anchor)


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
