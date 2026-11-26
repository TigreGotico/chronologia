"""The n-th weekday or business day "of every month" is one scoped_ordinal
reading: extract_recurrence builds the rule from it and extract_timespan
reads its next occurrence.

Gold comes from ``calendar``: the n-th matching day of each month, with the
weekend of the locale (Saturday and Sunday, Friday and Saturday for ar).
The rule is expanded with ``dateutil.rrule`` and compared month by month.
"""
import calendar
from datetime import date, datetime

import pytest
from dateutil.rrule import rrulestr

from chronologia import (ImpossibleDateError, extract_candidates,
                         extract_recurrence, extract_timespan)

ANCHOR = datetime(2026, 11, 22, 9, 0)
MON, SUN = 0, 6
SAT_SUN = (5, 6)
FRI_SAT = (4, 5)


def nth_day(year, month, n, keep):
    days = [date(year, month, d)
            for d in range(1, calendar.monthrange(year, month)[1] + 1)
            if keep(date(year, month, d))]
    return days[n - 1] if n > 0 else days[n]


def gold(n, keep, months=12):
    out, y, m = [], 2026, 12
    for _ in range(months):
        out.append(nth_day(y, m, n, keep))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def business(weekend):
    return lambda d: d.weekday() not in weekend


def weekday(wd):
    return lambda d: d.weekday() == wd


def expand(rule, months=12):
    start = datetime(2026, 12, 1)
    got = rrulestr(rule, dtstart=start)
    return [d.date() for d in got.between(start, datetime(2027, 12, 1), inc=True)][:months]


@pytest.mark.parametrize("lang,text,n,keep", [
    ("en", "the last business day of every month", -1, business(SAT_SUN)),
    ("en", "the third business day of every month", 3, business(SAT_SUN)),
    ("en", "the first business day of each month", 1, business(SAT_SUN)),
    ("en", "the third working day of every month", 3, business(SAT_SUN)),
    ("en", "the third weekday of each month", 3, business(SAT_SUN)),
    ("de", "der dritte Werktag jedes Monats", 3, business(SAT_SUN)),
    ("pt", "o terceiro dia útil de cada mês", 3, business(SAT_SUN)),
    ("ar", "ثالث يوم عمل من كل شهر", 3, business(FRI_SAT)),
    ("de", "der erste Montag jedes Monats", 1, weekday(MON)),
    ("en", "every month on the first monday", 1, weekday(MON)),
    ("pt", "todos os meses no primeiro domingo", 1, weekday(SUN)),
])
def test_rule_expands_to_the_nth_day_of_each_month(lang, text, n, keep):
    result = extract_recurrence(text, lang, ANCHOR)
    assert result is not None
    assert result.remainder == ""
    assert expand(result.recurrence.to_string()) == gold(n, keep)


@pytest.mark.parametrize("text", [
    "the sixth monday of every month",
    "the 25th weekday of every month",
    "the 24th business day of every month",
])
def test_an_ordinal_no_month_holds_reads_no_rule(text):
    assert extract_recurrence(text, "en", ANCHOR) is None


@pytest.mark.parametrize("lang,text,n,keep", [
    ("en", "the second monday of every month", 2, weekday(MON)),
    ("en", "the last business day of every month", -1, business(SAT_SUN)),
    ("de", "der erste Montag jedes Monats", 1, weekday(MON)),
])
def test_timespan_reads_the_next_occurrence(lang, text, n, keep):
    # the anchor's own month first, then the next month
    first = nth_day(2026, 11, n, keep)
    if first < ANCHOR.date():
        first = nth_day(2026, 12, n, keep)
    result = extract_timespan(text, lang, ANCHOR)
    assert result is not None
    assert result.span.start.datetime().date() == first
    assert result.remainder == ""


def test_sixth_monday_of_every_month_has_no_candidate():
    text = "the sixth monday of every month"
    assert extract_candidates(text, "en", ANCHOR) == []
    with pytest.raises(ImpossibleDateError, match="no 6th Monday"):
        extract_candidates(text, "en", ANCHOR, impossible="raise")
