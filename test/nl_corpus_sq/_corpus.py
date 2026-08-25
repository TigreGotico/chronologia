"""Shared helpers for the Albanian natural-language corpus.

The contract under test is the public span-native edge
``extract_timespan(text, "sq", anchor)``: feed a sentence an Albanian speaker
would actually say and assert the *exact* parsed span.  Expected values are
derived by hand or by independent Python date arithmetic that does not touch
the parser -- never by pinning the engine's own output.

Two facts shape most of what follows.  Albanian marks definiteness and case
on the counted noun, and the form is chosen by the word governing it, not by
the writer: the ablative after ``pas`` ("pas dy ditësh"), the indefinite
after ``më parë``/``para`` ("dy ditë më parë"), the bare indefinite after
``këtë``/``çdo``, and the definite accusative only inside the fused
``e kaluar`` / ``e ardhshëm`` frame ("javën e kaluar").  And the clock names
the CURRENT hour when it counts forward ("shtatë e gjysmë" == 07:30) but the
NEXT hour when it counts backward with ``pa`` ("tre pa çerek" == 02:45).
"""
from datetime import datetime

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate, DateSpan  # noqa: F401

#: the mission anchor -- a Tuesday, 13:04.
ANCHOR = datetime(2017, 6, 27, 13, 4)


def parse(text, anchor=ANCHOR):
    return extract_timespan(text, "sq", anchor)


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
