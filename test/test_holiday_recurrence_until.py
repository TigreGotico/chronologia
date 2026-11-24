"""A movable holiday with an until bound (TigreGotico/chronologia#1368)."""
from datetime import date, datetime

import pytest

from chronologia import extract_event, extract_recurrence

ANCHOR = datetime(2026, 11, 24, 9)
ISSUE = "https://github.com/TigreGotico/chronologia/issues/1368"

# Easter Sunday 2027, 2028 and 2029; the bound "until 2030" ends before Easter 2030.
EASTERS = [date(2027, 3, 28), date(2028, 4, 16), date(2029, 4, 1)]


@pytest.mark.xfail(strict=True, reason=ISSUE)
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


@pytest.mark.xfail(strict=True, reason=ISSUE)
def test_easter_until_year_event_keeps_the_bound():
    event = extract_event("every easter until 2030", "en", ANCHOR)
    start = event.span.start
    assert date(start.year, start.month, start.day) == EASTERS[0]
    starts = [date(s.start.year, s.start.month, s.start.day)
              for s in event.recurrence.occurrences(ANCHOR, count=10)]
    assert starts == EASTERS
