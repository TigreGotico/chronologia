# -*- coding: utf-8 -*-
"""A Dutch clock followed by a today part-of-day word reads that word.

"vanavond", "vanmiddag" and "vanochtend" name the anchor day's own band, so
"om 8 uur vanavond" is 20:00 today, as "vanavond om 8 uur" and "om 8 uur 's
avonds" are.  A word that names today never rolls the clock to tomorrow, even
when the hour has passed.  The plain postposed words keep the roll.

Every expected instant is worked out by hand from the anchor.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)

# text, anchor, expected instant
CASES = [
    ("om 8 uur vanavond", ANCHOR, datetime(2017, 6, 27, 20, 0)),
    ("om 3 uur vanmiddag", ANCHOR, datetime(2017, 6, 27, 15, 0)),
    ("om 15 uur vanmiddag", ANCHOR, datetime(2017, 6, 27, 15, 0)),
    ("om 3 uur vanochtend", ANCHOR, datetime(2017, 6, 27, 3, 0)),
    ("om 8 uur vanmorgen", ANCHOR, datetime(2017, 6, 27, 8, 0)),
    ("om 8:30 vanavond", ANCHOR, datetime(2017, 6, 27, 20, 30)),
    ("om half 9 vanavond", ANCHOR, datetime(2017, 6, 27, 20, 30)),
    ("om 8 uur vanavond", datetime(2017, 6, 27, 22, 0),
     datetime(2017, 6, 27, 20, 0)),
    # controls: the forms that already read right
    ("vanmiddag om 3 uur", ANCHOR, datetime(2017, 6, 27, 15, 0)),
    ("om 3 uur 's middags", ANCHOR, datetime(2017, 6, 27, 15, 0)),
    ("om 8 uur 's avonds", ANCHOR, datetime(2017, 6, 27, 20, 0)),
    # a plain postposed word keeps the roll to the next reading
    ("om 3 uur 's ochtends", ANCHOR, datetime(2017, 6, 28, 3, 0)),
]


@pytest.mark.parametrize("text,anchor,expected", CASES)
def test_a_today_part_of_day_after_a_clock(text, anchor, expected):
    found = extract_timespan(text, "nl", anchor)
    assert found.span.start.datetime() == expected
    assert found.remainder == ""
