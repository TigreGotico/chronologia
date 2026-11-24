"""An end bound "until the end of <month>" in a recurrence is the next such month.

Anchor: Sunday 2026-11-22 09:00, so the next end of August is in 2027.  The last
Monday of August 2027 is the 30th; any UNTIL from that day up to the day before
the next Monday gives the same dates.
"""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_recurrence

ANCHOR = datetime(2026, 11, 22, 9, 0)


@pytest.mark.xfail(strict=True, reason="https://github.com/TigreGotico/chronologia/issues/1316")
def test_en_until_the_end_of_august_is_next_august():
    result = extract_recurrence("every monday until the end of august", "en", ANCHOR)
    last_monday = datetime(2027, 8, 30)
    assert result.remainder == ""
    assert last_monday <= result.recurrence.until.datetime() < last_monday + timedelta(days=7)
