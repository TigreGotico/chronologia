"""A movable holiday with an until bound (TigreGotico/chronologia#1368)."""
from datetime import date, datetime

import pytest

from chronologia import extract_event, extract_recurrence

ANCHOR = datetime(2026, 11, 24, 9)
ISSUE = "https://github.com/TigreGotico/chronologia/issues/1368"

# Easter Sunday 2027, 2028 and 2029; the bound "until 2030" ends before Easter 2030.
EASTERS = [date(2027, 3, 28), date(2028, 4, 16), date(2029, 4, 1)]


@pytest.mark.parametrize("text, lang", [
    ("every easter until 2030", "en"),
    ("jedes Jahr zu Ostern bis 2030", "de"),
])
def test_easter_until_year_ends_before_that_year(text, lang):
    result = extract_recurrence(text, lang, ANCHOR)
    assert result.remainder == ""
    starts = [date(s.start.year, s.start.month, s.start.day)
              for s in result.recurrence.occurrences(ANCHOR, count=10)]
    assert starts == EASTERS


def test_easter_until_year_event_keeps_the_bound():
    event = extract_event("every easter until 2030", "en", ANCHOR)
    start = event.span.start
    assert date(start.year, start.month, start.day) == EASTERS[0]
    starts = [date(s.start.year, s.start.month, s.start.day)
              for s in event.recurrence.occurrences(ANCHOR, count=10)]
    assert starts == EASTERS


def test_until_roundtrips_through_json_and_old_json_loads():
    from chronologia.recurrence import HolidayRecurrence
    rec = extract_recurrence("every easter until 2030", "en", ANCHOR).recurrence
    assert rec.until.year == 2030 and (rec.until.month, rec.until.day) == (1, 1)
    assert HolidayRecurrence.from_json(rec.to_json()) == rec
    assert "until" not in HolidayRecurrence("easter").to_json()
    old = {"type": "HolidayRecurrence", "holiday": "easter"}
    assert HolidayRecurrence.from_json(old) == HolidayRecurrence("easter")


def test_caller_until_overrides_the_rule_until():
    from chronologia.recurrence import HolidayRecurrence
    rec = HolidayRecurrence("easter", until=datetime(2028, 1, 1))
    got = [s.start.year for s in rec.occurrences(ANCHOR, until=datetime(2030, 1, 1))]
    assert got == [2027, 2028, 2029]
    assert [s.start.year for s in rec.occurrences(ANCHOR)] == [2027]


def test_the_until_day_itself_is_included():
    from chronologia.recurrence import HolidayRecurrence
    rec = HolidayRecurrence("easter", until=datetime(2028, 4, 16))
    assert [s.start.year for s in rec.occurrences(ANCHOR)] == [2027, 2028]
