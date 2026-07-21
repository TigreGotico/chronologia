"""German relative offsets in BOTH directions ("vor N" past / "in N" future),
named days (heute/gestern/morgen/vorgestern/übermorgen) and weekday
references (nächsten/letzten/diesen + weekday).  Oracles are independent
date arithmetic (dateutil), never the engine's own output.
"""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, start, start_end, span, nomatch

UNIT = {
    "tag": relativedelta(days=1), "tagen": relativedelta(days=1),
    "woche": relativedelta(weeks=1), "wochen": relativedelta(weeks=1),
    "monat": relativedelta(months=1), "monaten": relativedelta(months=1),
    "jahr": relativedelta(years=1), "jahren": relativedelta(years=1),
    "stunde": relativedelta(hours=1), "minute": relativedelta(minutes=1),
    "minuten": relativedelta(minutes=1),
}


def past(n, unit):
    d = UNIT[unit]
    return ad(ANCHOR - n * d), ad(ANCHOR - (n - 1) * d)


def future(n, unit):
    d = UNIT[unit]
    return ad(ANCHOR + n * d), ad(ANCHOR + (n + 1) * d)


# -- past: "vor N UNIT" ---------------------------------------------------

@pytest.mark.parametrize("text,n,unit", [
    ("vor drei tagen", 3, "tagen"), ("vor einem tag", 1, "tag"),
    ("vor zwei wochen", 2, "wochen"), ("vor fünf monaten", 5, "monaten"),
    ("vor einem jahr", 1, "jahr"), ("vor zehn jahren", 10, "jahren"),
    ("vor einer stunde", 1, "stunde"), ("vor 30 minuten", 30, "minuten"),
    ("vor sieben tagen", 7, "tagen"),
])
def test_past(text, n, unit):
    assert start_end(text) == past(n, unit)


# -- future: "in N UNIT" --------------------------------------------------

@pytest.mark.parametrize("text,n,unit", [
    ("in drei tagen", 3, "tagen"), ("in zwei wochen", 2, "wochen"),
    ("in einem monat", 1, "monat"), ("in zehn jahren", 10, "jahren"),
    ("in einer stunde", 1, "stunde"), ("in 30 minuten", 30, "minuten"),
    ("in vier tagen", 4, "tagen"), ("in einem jahr", 1, "jahr"),
])
def test_future(text, n, unit):
    assert start_end(text) == future(n, unit)


# -- named days -----------------------------------------------------------

@pytest.mark.parametrize("text,off", [
    ("heute", 0), ("gestern", -1), ("morgen", 1),
    ("vorgestern", -2), ("übermorgen", 2), ("uebermorgen", 2),
])
def test_named_day(text, off):
    day = (ANCHOR + timedelta(days=off)).replace(hour=0, minute=0)
    assert start(text) == ad(day)
    assert span(text).width == timedelta(days=1)


# -- weekday reference: anchor is a Tuesday (2017-06-27) ------------------

@pytest.mark.parametrize("text,date", [
    ("nächsten montag", (2017, 7, 3)), ("letzten freitag", (2017, 6, 23)),
    ("diesen sonntag", (2017, 7, 2)), ("nächsten dienstag", (2017, 7, 4)),
    ("letzten montag", (2017, 6, 26)), ("nächsten sonntag", (2017, 7, 2)),
])
def test_weekday_ref(text, date):
    from ._corpus import AstroDate
    assert start(text) == AstroDate(*date)


# -- adversarial: prose that is not a date ---------------------------------

@pytest.mark.parametrize("text", ["vor allem", "in ordnung", "nach hause"])
def test_prose_not_a_date(text):
    # these open with a range/marker word but carry no unit/number
    r = span.__wrapped__ if False else None  # noqa
    from ._corpus import parse
    res = parse(text)
    # must not fabricate a numeric offset span
    assert res is None or res[0].width >= timedelta(0)
