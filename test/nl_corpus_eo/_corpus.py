"""Shared helpers for the Esperanto natural-language corpus.

The contract under test is the public span-native edge
``extract_timespan(text, "eo", anchor)``: feed a sentence an Esperanto
speaker would actually say and assert the *exact* parsed span.  Expected
values are derived by hand or by independent Python date arithmetic that
does not touch the parser -- never by pinning the engine's own output.

Two facts drive most of what follows.  The numeral system is fully regular
(no case/gender agreement): 0..10, the nine fused tens ("dudek" = 20, ...,
"naŭdek" = 90), "cent" (100) and "mil" (1000), composed by writing words
left to right, most-significant first ("dek du" = 12, "cent tri" = 103).
And the spoken clock counts FORWARD from the hour it names -- the English
past-the-hour shape ("la sesa kaj duono" = 6:30), never the Baltic/Germanic
toward-the-hour one.
"""
from datetime import datetime

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate, DateSpan  # noqa: F401

#: the mission anchor -- a Tuesday, 13:04.
ANCHOR = datetime(2017, 6, 27, 13, 4)


def parse(text, anchor=ANCHOR):
    return extract_timespan(text, "eo", anchor)


def span(text, anchor=ANCHOR):
    r = parse(text, anchor)
    assert r is not None, f"{text!r} did not parse (expected a span)"
    return r[0]


def start(text, anchor=ANCHOR):
    return span(text, anchor).start


def remainder(text, anchor=ANCHOR):
    r = parse(text, anchor)
    assert r is not None, f"{text!r} did not parse (expected a span)"
    return r[1]


def nomatch(text, anchor=ANCHOR):
    r = parse(text, anchor)
    assert r is None, f"{text!r} unexpectedly parsed to {r!r}"
