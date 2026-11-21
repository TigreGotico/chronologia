"""The last weekday of a month in ca and an: "darrer" (Wiktionary ca: "last
(most recent)") and "zaguer" (Wiktionary an: "last (final)") are ordinals
of the last order, as en "last" is."""
import calendar
from datetime import datetime, timedelta

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)
LAST_MONDAY_OF_MARCH = max(
    datetime(2017, 3, d)
    for d in range(1, calendar.monthrange(2017, 3)[1] + 1)
    if calendar.weekday(2017, 3, d) == 0)


@pytest.mark.parametrize("lang, text", [
    ("ca", "el darrer dilluns de març"),
    ("an", "lo zaguer luns de marzo"),
])
def test_the_last_weekday_of_a_month(lang, text):
    found = extract_timespan(text, lang, ANCHOR)
    assert (found.span.start, found.span.end, found.remainder) == (
        LAST_MONDAY_OF_MARCH, LAST_MONDAY_OF_MARCH + timedelta(days=1), "")
