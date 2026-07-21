"""Shared helpers + independent oracles for the sv corpus.

The contract: ``extract_timespan(text, "sv", anchor)`` on a sentence a
speaker would actually write, asserting the exact span.  Expected values are
hand-derived or computed by independent date arithmetic -- never pinned from
the engine.
"""
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate, DateSpan  # noqa: F401

LANG = "sv"
ANCHOR = datetime(2017, 6, 27, 13, 4)   # a Tuesday, 13:04

_UNIT = {
    "day": relativedelta(days=1), "week": relativedelta(weeks=1),
    "month": relativedelta(months=1), "year": relativedelta(years=1),
    "hour": relativedelta(hours=1), "minute": relativedelta(minutes=1),
}


def parse(text, anchor=ANCHOR):
    return extract_timespan(text, LANG, anchor)


def span(text, anchor=ANCHOR):
    r = parse(text, anchor)
    assert r is not None, f"{text!r} did not parse (expected a span)"
    return r[0]


def start(text, anchor=ANCHOR):
    return span(text, anchor).start


def start_end(text, anchor=ANCHOR):
    s = span(text, anchor)
    return s.start, s.end


def nomatch(text, anchor=ANCHOR):
    r = parse(text, anchor)
    assert r is None, f"{text!r} unexpectedly parsed to {r!r}"


def ad(dt):
    return AstroDate(dt.year, dt.month, dt.day, dt.hour, dt.minute,
                     dt.second, dt.microsecond)


def past(n, unit):
    d = _UNIT[unit]
    return ad(ANCHOR - n * d), ad(ANCHOR - (n - 1) * d)


def future(n, unit):
    d = _UNIT[unit]
    return ad(ANCHOR + n * d), ad(ANCHOR + (n + 1) * d)


def clk(h, mi, s=0):
    dt = ANCHOR.replace(hour=h, minute=mi, second=s, microsecond=0)
    if dt < ANCHOR:
        dt += timedelta(days=1)
    return ad(dt)
