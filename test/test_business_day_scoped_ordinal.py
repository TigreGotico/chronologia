"""The n-th business day of a month is one scoped_ordinal reading (ruling 39).

A named month with no year, and "the month" with no marker, name the next
month whose n-th business day is not before the anchor. Gold comes from
``calendar``: a business day is Monday to Friday.
"""
import calendar
from datetime import date, datetime

import pytest

from chronologia import ImpossibleDateError, extract_candidates, extract_timespan

ANCHOR = datetime(2026, 11, 22, 9, 0)


def business_days(year, month):
    return [date(year, month, d) for d in range(1, calendar.monthrange(year, month)[1] + 1)
            if date(year, month, d).weekday() < 5]


def next_nth(n, month=None):
    months = ([(ANCHOR.year + k, month) for k in range(28)] if month else
              [(ANCHOR.year + (ANCHOR.month - 1 + k) // 12, (ANCHOR.month - 1 + k) % 12 + 1)
               for k in range(24)])
    for year, mon in months:
        days = business_days(year, mon)
        if n <= len(days) and days[n - 1] >= ANCHOR.date():
            return days[n - 1]


@pytest.mark.parametrize("lang,text,n,month", [
    ("en", "the 3rd business day of march", 3, 3),
    ("en", "the 3rd weekday of march", 3, 3),
    ("en", "the third working day of the month", 3, None),
    ("en", "the third weekday of the month", 3, None),
    ("en", "the 22nd business day of the month", 22, None),
    ("pt", "o terceiro dia útil do mês", 3, None),
    ("pt", "o 3.º dia útil de março", 3, 3),
    ("de", "der dritte Werktag im März", 3, 3),
])
def test_a_past_month_rolls_forward(lang, text, n, month):
    expected = next_nth(n, month)
    result = extract_timespan(text, lang, ANCHOR)
    assert result is not None
    assert result.span.start.datetime() == datetime(expected.year, expected.month, expected.day)
    assert result.remainder == ""


@pytest.mark.parametrize("text,expected", [
    ("the last business day of next month", date(2026, 12, 31)),
    ("the 3rd business day of march 2026", date(2026, 3, 4)),
    ("the first weekday of this month", date(2026, 11, 2)),
])
def test_a_year_or_a_marker_fixes_the_month(text, expected):
    assert expected == [d for d in business_days(expected.year, expected.month)
                        ][0 if "first" in text else -1 if "last" in text else 2]
    result = extract_timespan(text, "en", ANCHOR)
    assert result is not None
    assert result.span.start.datetime() == datetime(expected.year, expected.month, expected.day)


@pytest.mark.parametrize("text,reason", [
    ("the 24th weekday of march", "no 24th business day"),
    ("the 25th weekday of the month", "no 25th business day"),
    # December 2026 holds 23 business days
    ("the 24th business day of next month", "December 2026 has no 24th business day"),
])
def test_no_such_business_day_is_refused(text, reason):
    assert len(business_days(2026, 12)) == 23
    assert extract_timespan(text, "en", ANCHOR) is None
    assert extract_candidates(text, "en", ANCHOR) == []
    with pytest.raises(ImpossibleDateError, match=reason):
        extract_candidates(text, "en", ANCHOR, impossible="raise")
