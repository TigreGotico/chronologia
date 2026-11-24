# -*- coding: utf-8 -*-
""""Today" beside a spoken lone hour limits the choice to the anchor's day.

Ruling 26: "today at 5" said at 15:00 is 17:00 and said at 03:00 is 05:00.  The
hour takes whichever of its two twelve-hour readings comes next within the
anchor's day, and reads as written when both have passed.  A day word other
than "today" and a part of the day keep the written hour.

Every expected instant is worked out by hand from the anchor.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

DAY = (2017, 6, 27)


def at(hour, minute=0, day=DAY):
    return datetime(*day, hour, minute)


# text, language, anchor, expected instant
CASES = [
    ("today at 5", "en", at(15), at(17)),
    ("remind me today at five", "en", at(15), at(17)),
    ("today at 5", "en", at(3), at(5)),
    ("today at 5", "en", at(13, 4), at(17)),
    ("at three thirty today", "en", at(15), at(15, 30)),
    ("today at 5", "en", at(23), at(5)),
    ("today at 5:15", "en", at(13, 4), at(17, 15)),
    ("hoje às 5", "pt", at(15), at(17)),
    ("hoje às 5 e meia", "pt", at(15), at(17, 30)),
    ("tomorrow at 5", "en", at(15), at(5, day=(2017, 6, 28))),
    ("today at 5 in the morning", "en", at(15), at(5)),
    ("today at 17:00", "en", at(15), at(17)),
]


@pytest.mark.parametrize("text,lang,anchor,expected", CASES)
def test_today_takes_the_next_reading_within_the_day(text, lang, anchor,
                                                     expected):
    found = extract_timespan(text, lang, anchor)
    assert found.span.start.datetime() == expected
