"""A business-day ordinal of a month skips the public holidays of the jurisdiction.

Portugal keeps 1 December (Restauração da Independência), 8 December
(Imaculada Conceição) and 25 December as public holidays. December 2026 starts
on a Tuesday.
"""
import calendar
from datetime import date, datetime

import pytest

from chronologia import extract_timespan
from chronologia.civil_holidays import is_civil_holiday

ANCHOR = datetime(2026, 11, 22, 9, 0)
PT_DECEMBER_HOLIDAYS = {date(2026, 12, 1), date(2026, 12, 8), date(2026, 12, 25)}


def business_days(year, month, holidays=frozenset()):
    return [date(year, month, d) for d in range(1, calendar.monthrange(year, month)[1] + 1)
            if date(year, month, d).weekday() < 5 and date(year, month, d) not in holidays]


def test_the_calendar_holds_the_holidays():
    assert {d for d in business_days(2026, 12)
            if is_civil_holiday(datetime(d.year, d.month, d.day), "PT",
                                categories=("public",))} == PT_DECEMBER_HOLIDAYS


@pytest.mark.parametrize("text,n", [
    ("the third working day of next month", 3),
    ("the fifth working day of december", 5),
    ("the first business day of december", 1),
])
@pytest.mark.parametrize("jurisdiction", [None, "PT"])
def test_scoped_business_day_skips_holidays(text, n, jurisdiction):
    holidays = PT_DECEMBER_HOLIDAYS if jurisdiction else frozenset()
    expected = business_days(2026, 12, holidays)[n - 1]
    result = extract_timespan(text, "en", ANCHOR, jurisdiction=jurisdiction)
    assert result is not None
    assert result.span.start.datetime() == datetime(expected.year, expected.month, expected.day)
    assert result.remainder == ""
