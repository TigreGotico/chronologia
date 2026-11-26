""""every year on the <n-th|last> <weekday> of <month>" keeps its month.

Gold: the dates come from ``calendar`` for 2027 and 2028 (the n-th matching
day of the month, or the last one), and the rule is expanded with
``dateutil.rrule``.  The leading "every year on" stays as the remainder.
"""
import calendar
from datetime import datetime

import pytest
from dateutil.rrule import rrulestr

from chronologia import extract_event, extract_recurrence

ANCHOR = datetime(2026, 11, 26)

ROWS = [
    ("en", "every year on the last sunday of october", -1, 6, 10, "every year on"),
    ("en", "every year on the first monday of may", 1, 0, 5, "every year on"),
    ("en", "every year on the second tuesday of march", 2, 1, 3, "every year on"),
    ("en", "every year the last sunday of october", -1, 6, 10, "every year"),
    ("en", "each year on the 4th thursday of november", 4, 3, 11, "each year on"),
    ("de", "jedes jahr am letzten sonntag im oktober", -1, 6, 10, "jedes jahr"),
    ("es", "cada año el último domingo de octubre", -1, 6, 10, "cada año"),
    ("fr", "chaque année le dernier dimanche d'octobre", -1, 6, 10, "chaque année"),
    ("pt", "todos os anos no último domingo de outubro", -1, 6, 10, "todos os anos"),
    ("nl", "elk jaar op de laatste zondag van oktober", -1, 6, 10, "elk jaar op"),
]


def _nth(year, month, weekday, n):
    days = [d for d in calendar.Calendar().itermonthdates(year, month)
            if d.month == month and d.weekday() == weekday]
    return days[n - 1] if n > 0 else days[n]


@pytest.mark.parametrize("lang,text,n,weekday,month,remainder", ROWS)
def test_every_year_keeps_the_month(lang, text, n, weekday, month, remainder):
    got = extract_recurrence(text, lang, anchor=ANCHOR)
    assert got is not None
    assert got.remainder == remainder
    rule = rrulestr(got.recurrence.to_string(), dtstart=datetime(2027, 1, 1))
    assert [d.date() for d in rule[:2]] == [_nth(2027, month, weekday, n),
                                            _nth(2028, month, weekday, n)]


@pytest.mark.parametrize("lang,text,n,weekday,month,remainder", ROWS)
def test_event_keeps_the_month(lang, text, n, weekday, month, remainder):
    rule = extract_event(text, lang, anchor=ANCHOR).recurrence
    assert rule.bymonth == (month,) and rule.byday == ((n, weekday),)
