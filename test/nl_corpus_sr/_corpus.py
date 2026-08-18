"""Shared helpers for the Serbian natural-language corpus.

The contract under test is the public span-native edge
``extract_timespan(text, "sr", anchor)``: feed a sentence a Serbian speaker
would actually say (Ekavian, Cyrillic OR Latin) and assert the *exact* parsed
span.  Expected values are derived by hand or by independent Python date
arithmetic that never touches the parser.

Serbian is the first dual-script locale: every construction is exercised in
both alphabets, related by the deterministic digraph-aware transliteration
in ``chronologia.extract.numfold_slavic.sr_lat2cyr`` (lj/nj/dž -> љ/њ/џ).

Two grammatical facts drive most of the duration phrasing.  A counted noun
takes the NOMINATIVE SINGULAR after 1, the GENITIVE SINGULAR after 2-4
("dva sata", "tri dana" -- the paucal, not the genitive plural), and the
GENITIVE PLURAL after 5+ ("pet sati").  And the spoken clock counts toward
the COMING hour on the half ("pola četiri" == 3:30) while quarters are
additive/subtractive around the NAMED hour ("dva i četvrt" == 2:15,
"četvrt do tri" == 2:45).
"""
from datetime import datetime

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate, DateSpan  # noqa: F401

#: the mission anchor -- a Tuesday, 13:04.
ANCHOR = datetime(2017, 6, 27, 13, 4)


def parse(text, anchor=ANCHOR):
    return extract_timespan(text, "sr", anchor)


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
