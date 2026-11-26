"""extract_candidates reads nothing from the words of a refused date, and in
raise mode it reports the reason extract_timespan reports.

The gold comes from the calendar module, not from chronologia: a day past the
length of its month, or a business-day ordinal past the weekdays of its month,
names no date.
"""
import calendar
from datetime import datetime

import pytest

from chronologia import ImpossibleDateError, extract_candidates, extract_timespan

ANCHOR = datetime(2026, 11, 26, 12, 0)


def weekdays(year, month):
    days = calendar.monthrange(year, month)[1]
    return sum(calendar.weekday(year, month, d) < 5 for d in range(1, days + 1))


# (lang, text, year, month, day or business-day ordinal, unit)
ROWS = [
    ("en", "31 february", 2027, 2, 31, "day"),
    ("en", "29 february 2027", 2027, 2, 29, "day"),
    ("en", "31 april", 2027, 4, 31, "day"),
    ("de", "31. Februar", 2027, 2, 31, "day"),
    ("en", "the 30th business day of march", 2027, 3, 30, "business"),
    ("en", "the 25th business day of june", 2027, 6, 25, "business"),
    ("en", "the 23rd business day of february", 2027, 2, 23, "business"),
]


@pytest.mark.parametrize("lang,text,year,month,n,unit", ROWS)
def test_gold_names_no_date(lang, text, year, month, n, unit):
    most = (calendar.monthrange(year, month)[1] if unit == "day"
            else weekdays(year, month))
    assert n > most


@pytest.mark.parametrize("lang,text,year,month,n,unit", ROWS)
def test_candidates_read_nothing(lang, text, year, month, n, unit):
    assert extract_timespan(text, lang, ANCHOR) is None
    assert extract_candidates(text, lang, ANCHOR) == []


@pytest.mark.parametrize("lang,text,year,month,n,unit", ROWS)
def test_candidates_raise_the_timespan_reason(lang, text, year, month, n, unit):
    reasons = []
    for extract in (extract_timespan, extract_candidates):
        with pytest.raises(ImpossibleDateError) as err:
            extract(text, lang, ANCHOR, impossible="raise")
        reasons.append(err.value.reason)
    assert reasons[0] == reasons[1]


def test_a_date_beside_the_refused_words_stays():
    found = extract_candidates("31 april or 5 may", "en", ANCHOR)
    assert (found[0].span.start.datetime(), found[0].char_span) == (
        datetime(2027, 5, 5), (12, 17))
    # no candidate reads a word of "31 april"
    assert all(c.char_span[0] >= 12 for c in found)


def test_a_clock_beside_the_refused_words_stays():
    found = extract_candidates("on 31 april at 3pm", "en", ANCHOR)
    assert found[0].span.start.datetime() == datetime(2026, 11, 26, 15, 0)
    assert {c.construction for c in found} == {"clock_time"}
