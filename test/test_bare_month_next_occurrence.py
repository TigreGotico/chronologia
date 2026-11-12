"""A month named without a day is its next occurrence.

prefer_future means the next occurrence strictly after the anchor, and a month
is a span: the month that holds the anchor is this month, and a month that has
ended is next year's.  At the Tuesday 27 June 2017 anchor, January and March
have ended, so they are the 2018 months; June holds the anchor and July is
ahead, so both stay in 2017.  An explicit year is kept as written.

The Hebrew months take the same rule in their own calendar.  1 Nisan 5778 is
17 March 2018, 14 days before the first Passover day, 31 March 2018 (15
Nisan).  1 Tishrei 5778, Rosh Hashanah, is 21 September 2017.

A relative marker moves the bare reading.  "last October" is the latest
October that has ended, October 2016; "last June" said in June is June 2016.
"next June" said in June is June 2018, and "next July" is July 2017.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate

ANCHOR = datetime(2017, 6, 27, 13, 4)


def _span(text, lang):
    r = extract_timespan(text, lang, ANCHOR)
    assert r is not None, f"{text!r} did not parse"
    return r


@pytest.mark.parametrize("text,lang,year,month", [
    ("january", "en", 2018, 1),
    ("in january", "en", 2018, 1),
    ("march", "en", 2018, 3),
    ("june", "en", 2017, 6),
    ("july", "en", 2017, 7),
    ("janvier", "fr", 2018, 1),
    ("en janvier", "fr", 2018, 1),
    ("juin", "fr", 2017, 6),
    ("im Januar", "de", 2018, 1),
    ("janeiro", "pt", 2018, 1),
    ("en enero", "es", 2018, 1),
    ("januar", "sl", 2018, 1),
    ("junij", "sl", 2017, 6),
    ("január", "hu", 2018, 1),
    ("styczeń", "pl", 2018, 1),
    ("w styczniu", "pl", 2018, 1),
    ("в январе", "ru", 2018, 1),
    ("у січні", "uk", 2018, 1),
])
def test_bare_month_is_its_next_occurrence(text, lang, year, month):
    r = _span(text, lang)
    nyear, nmonth = (year, month + 1) if month < 12 else (year + 1, 1)
    assert r.span.start == AstroDate(year, month, 1)
    assert r.span.end == AstroDate(nyear, nmonth, 1)
    assert r.remainder == ""


@pytest.mark.parametrize("text,lang,year,month", [
    ("january 2017", "en", 2017, 1),
    ("janvier 2017", "fr", 2017, 1),
])
def test_explicit_year_is_kept(text, lang, year, month):
    assert _span(text, lang).span.start == AstroDate(year, month, 1)


@pytest.mark.parametrize("text,lang,start", [
    ("nisan", "en", AstroDate(2018, 3, 17)),
    ("tishrei", "en", AstroDate(2017, 9, 21)),
])
def test_calendar_month_is_its_next_occurrence(text, lang, start):
    assert _span(text, lang).span.start == start


@pytest.mark.parametrize("text,lang,year,month", [
    ("last october", "en", 2016, 10),
    ("last june", "en", 2016, 6),
    ("next june", "en", 2018, 6),
    ("next july", "en", 2017, 7),
    ("в прошлом октябре", "ru", 2016, 10),
    ("в следующем январе", "ru", 2018, 1),
    ("у минулому жовтні", "uk", 2016, 10),
    ("im letzten Oktober", "de", 2016, 10),
])
def test_relative_month(text, lang, year, month):
    r = _span(text, lang)
    assert r.span.start == AstroDate(year, month, 1)
    assert r.remainder == ""


@pytest.mark.parametrize("text,lang,year,month,remainder", [
    ("напомни мне в январе", "ru", 2018, 1, "напомни мне"),
    ("remind me in march", "en", 2018, 3, "remind me"),
])
def test_bare_month_inside_a_request(text, lang, year, month, remainder):
    r = _span(text, lang)
    assert r.span.start == AstroDate(year, month, 1)
    assert r.remainder == remainder
