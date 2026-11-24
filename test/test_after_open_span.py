"""A bare "after X" is the open span that starts when X ends.

Ruling 33: "A bare 'after X' is the open span that starts when X ends."  A
consumer that needs an instant takes the span's start.  Anchor: Saturday
2026-10-17 12:00, so the next 4 July is in 2027 and "after" it starts at
00:00 on 5 July 2027.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ISSUE = "https://github.com/TigreGotico/chronologia/issues/1098"


@pytest.mark.xfail(strict=True, reason=ISSUE)
@pytest.mark.parametrize("text,start", [
    ("after the fourth of july", datetime(2027, 7, 5, 0, 0)),
    ("after july fourth", datetime(2027, 7, 5, 0, 0)),
    ("after july 4th", datetime(2027, 7, 5, 0, 0)),
    # the next Monday is 19 October 2026, so "after monday" starts on the 20th
    ("after monday", datetime(2026, 10, 20, 0, 0)),
])
def test_after_a_day_starts_the_day_after_it(text, start):
    found = extract_timespan(text, "en", datetime(2026, 10, 17, 12, 0))
    assert found.span.start.datetime() == start
