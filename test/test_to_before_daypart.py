# -*- coding: utf-8 -*-
"""An infinitive "to" before a part of the day opens no range.

"remind me to call the bank tomorrow morning" names the morning of the next
day.  The word "to" before a verb is the infinitive marker.  A left side that
holds no number cannot borrow the part of the day of the right side, so the
text has no "A to B" range.  A bare hour on the left still borrows it:
"from 3 to 5 pm" and "from three to five pm" are one range.

Every expected instant is worked out by hand from the anchor, Tuesday
2017-06-27 13:04.  Tomorrow is Wednesday 2017-06-28; the morning runs from
06:00 to 12:00, the afternoon from 12:00 to 18:00 and the evening from 18:00
to 21:00.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)
TOMORROW = datetime(2017, 6, 28)

# text, start hour, end hour, remainder
INFINITIVE = [
    ("remind me to call the bank tomorrow morning", 6, 12,
     "remind me to call the bank"),
    ("remind me to call the bank tomorrow afternoon", 12, 18,
     "remind me to call the bank"),
    ("remind me to call the bank tomorrow evening", 18, 21,
     "remind me to call the bank"),
    ("I want to go to the park tomorrow morning", 6, 12,
     "I want to go to the park"),
    ("go to tomorrow morning", 6, 12, "go to"),
]


@pytest.mark.parametrize("text,start,end,rest", INFINITIVE)
def test_infinitive_to_opens_no_range(text, start, end, rest):
    res = extract_timespan(text, "en", ANCHOR)
    assert res is not None
    assert res.span.start == TOMORROW.replace(hour=start)
    assert res.span.end == TOMORROW.replace(hour=end)
    assert res.remainder == rest


# text, language, start, end: a numeral on the left shares the part of the day
SHARED = [
    ("from 3 to 5 pm", "en", datetime(2017, 6, 27, 15, 0),
     datetime(2017, 6, 27, 17, 1)),
    ("from three to five pm", "en", datetime(2017, 6, 27, 15, 0),
     datetime(2017, 6, 27, 17, 1)),
    ("between 3 and 5 pm", "en", datetime(2017, 6, 27, 15, 0),
     datetime(2017, 6, 27, 17, 1)),
    ("de tres a cinco de la tarde", "es", datetime(2017, 6, 27, 15, 0),
     datetime(2017, 6, 27, 17, 1)),
]


@pytest.mark.parametrize("text,lang,start,end", SHARED)
def test_numeral_still_borrows_the_part_of_the_day(text, lang, start, end):
    res = extract_timespan(text, lang, ANCHOR)
    assert res is not None
    assert (res.span.start, res.span.end) == (start, end)
