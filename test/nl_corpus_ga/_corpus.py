"""Shared helpers for the Irish natural-language corpus.

The contract under test is the public span-native edge
``extract_timespan(text, "ga", anchor)``: feed a sentence an Irish speaker
would actually say and assert the *exact* parsed span.  Expected values are
derived by hand or by independent Python date arithmetic that does not touch
the parser -- never by pinning the engine's own output.

Two facts drive most of what follows.  A numeral counting a noun mutates that
noun's initial, and which mutation it is depends on the numeral: two lenites
("dhá bhliain"), three to six leave a consonant bare and prefix h to a vowel
("trí bliana", "cúig huaire"), seven to ten eclipse ("seacht mbliana",
"seacht n-uaire").  Every one of those surfaces is enumerated in the locale's
unit vocabulary, so the phrase matches whichever the numeral imposes.  And the
spoken clock runs toward the PAST hour, English-style: "leathuair tar éis a
trí" is 03:30, not 02:30.

Dates run day-month-year with no connector; the month stands bare, follows
"mí" in the genitive ("mí Aibreáin"), or follows a bare "i" eclipsed
("i mBealtaine").
"""
from datetime import datetime

from dateutil.relativedelta import relativedelta  # noqa: F401

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate, DateSpan  # noqa: F401

#: the mission anchor -- a Tuesday, 13:04.
ANCHOR = datetime(2017, 6, 27, 13, 4)


def parse(text, anchor=ANCHOR):
    return extract_timespan(text, "ga", anchor)


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
