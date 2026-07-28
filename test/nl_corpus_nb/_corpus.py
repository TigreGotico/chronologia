"""Shared helpers + independent oracles for the nb corpus.

The contract: ``extract_timespan(text, "nb", anchor)`` on a sentence a
speaker would actually write, asserting the exact span.  Expected values are
hand-derived or computed by independent date arithmetic -- never pinned from
the engine.
"""
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate, DateSpan  # noqa: F401

LANG = "nb"
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


def easter(year):
    """Western (Gregorian) computus -- anonymous Gauss algorithm.

    Independent of the engine; used to derive movable-feast golds by pure
    date arithmetic.  Returns a ``datetime.date``.
    """
    from datetime import date
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    m = (32 + 2 * e + 2 * i - h - k) % 7
    n = (a + 11 * h + 22 * m) // 451
    month = (h + m - 7 * n + 114) // 31
    day = ((h + m - 7 * n + 114) % 31) + 1
    return date(year, month, day)


def month_thirds(year, month):
    """The four boundaries splitting a calendar month into equal thirds.

    ``begynnelsen`` = [b0, b1), ``midten`` = [b1, b2), ``slutten`` = [b2, b3).
    Boundaries are the month duration divided by three, truncated to the
    second -- pure arithmetic, computed without consulting the engine.
    """
    b0 = datetime(year, month, 1)
    b3 = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)
    total = b3 - b0
    b1 = (b0 + total / 3).replace(microsecond=0)
    b2 = (b0 + 2 * total / 3).replace(microsecond=0)
    return b0, b1, b2, b3
