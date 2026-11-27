"""Shared helpers for the Bengali natural-language corpus.

Each test feeds ``extract_timespan(text, "bn", anchor)`` a sentence a
Bengali speaker writes and asserts the exact span.  Expected values come from
Python date arithmetic on the anchor, never from the parser.
"""
from datetime import datetime, timedelta

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate

#: a Tuesday, 13:04.
ANCHOR = datetime(2017, 6, 27, 13, 4)


def parse(text, anchor=ANCHOR):
    return extract_timespan(text, "bn", anchor)


def span(text, anchor=ANCHOR):
    r = parse(text, anchor)
    assert r is not None, f"{text!r} did not parse (expected a span)"
    return r[0]


def start(text, anchor=ANCHOR):
    return span(text, anchor).start


def nomatch(text, anchor=ANCHOR):
    r = parse(text, anchor)
    assert r is None, f"{text!r} unexpectedly parsed to {r!r}"


def ad(dt):
    return AstroDate(dt.year, dt.month, dt.day, dt.hour, dt.minute)


def day(offset, hour=0, minute=0):
    """The anchor day moved by ``offset`` days, at ``hour``:``minute``."""
    return ad((ANCHOR + timedelta(days=offset)).replace(
        hour=hour, minute=minute))
