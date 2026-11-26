"""A range of counts before "ago" runs from the larger offset to the smaller.

"from two thousand to three thousand days ago" is the span from 3000 days ago
to 2000 days ago.  Anchor: 2026-01-30 10:00.  The instants are 2026-01-30 10:00
minus 3000 and minus 2000 days, by calendar arithmetic.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ISSUE = "https://github.com/TigreGotico/chronologia/issues/1041"


@pytest.mark.xfail(raises=AssertionError, strict=True, reason=ISSUE)
def test_a_spelled_range_of_days_before_ago_is_a_range():
    found = extract_timespan(
        "from two thousand to three thousand days ago", "en",
        datetime(2026, 1, 30, 10, 0))
    assert (found.span.start.datetime(), found.span.end.datetime()) == (
        datetime(2017, 11, 13, 10, 0), datetime(2020, 8, 9, 10, 0))
    assert found.remainder == ""
