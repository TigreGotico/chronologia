# -*- coding: utf-8 -*-
"""A part of the day before a clock reads like the same words after it.

"evening at 8" said at 12:00 is 20:00 the same day, as "at 8 in the evening"
is: a bare part of the day names the anchor day's band while its hour is still
ahead (ruling 28), and the hour takes the half the part of the day names
(ruling 17).  Said after 20:00 the hour has passed, so it is 20:00 the next
day.  A morning word keeps the written hour, and a day word keeps its own day.

Every expected instant is worked out by hand from the anchor.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

FRIDAY_NOON = datetime(2026, 9, 25, 12, 0)

# text, language, anchor, expected instant
CASES = [
    ("evening at 8", "en", FRIDAY_NOON, datetime(2026, 9, 25, 20, 0)),
    ("at 8 in the evening", "en", FRIDAY_NOON, datetime(2026, 9, 25, 20, 0)),
    ("night at 9", "en", FRIDAY_NOON, datetime(2026, 9, 25, 21, 0)),
    ("afternoon at 3", "en", FRIDAY_NOON, datetime(2026, 9, 25, 15, 0)),
    ("na noite às 9", "pt", FRIDAY_NOON, datetime(2026, 9, 25, 21, 0)),
    ("na tarde às 3", "pt", FRIDAY_NOON, datetime(2026, 9, 25, 15, 0)),
    ("evening at 8", "en", datetime(2026, 9, 25, 9, 0),
     datetime(2026, 9, 25, 20, 0)),
    ("evening at 8", "en", datetime(2026, 9, 25, 21, 0),
     datetime(2026, 9, 26, 20, 0)),
    ("na noite às 9", "pt", datetime(2026, 9, 25, 22, 0),
     datetime(2026, 9, 26, 21, 0)),
    ("morning at 8", "en", FRIDAY_NOON, datetime(2026, 9, 26, 8, 0)),
    ("morning at 8", "en", datetime(2026, 9, 25, 6, 0),
     datetime(2026, 9, 25, 8, 0)),
    ("tomorrow evening at 8", "en", FRIDAY_NOON,
     datetime(2026, 9, 26, 20, 0)),
]


@pytest.mark.parametrize("text,lang,anchor,expected", CASES)
def test_a_part_of_the_day_before_a_clock(text, lang, anchor, expected):
    found = extract_timespan(text, lang, anchor)
    assert found.span.start.datetime() == expected
    assert found.remainder == ""
