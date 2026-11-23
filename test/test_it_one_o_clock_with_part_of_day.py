"""Italian "una" after "alle" or "all'" is the hour 1, with a part of the day after it.

"alle una di notte" is 01:00 at night.  The word "una" is also the indefinite
article, so the number reader keeps it as a word unless a clock preposition
stands before it.  Every expected instant is worked out by hand from the
anchor, Tuesday 2017-06-27 13:04.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)

CLOCKS = [
    ("alle una di notte", datetime(2017, 6, 28, 1, 0)),
    ("all'una di notte", datetime(2017, 6, 28, 1, 0)),
    ("alle una di mattina", datetime(2017, 6, 28, 1, 0)),
    ("alle una", datetime(2017, 6, 28, 1, 0)),
    ("alle due di notte", datetime(2017, 6, 28, 2, 0)),
]


@pytest.mark.parametrize("text,expected", CLOCKS)
def test_una_after_a_clock_preposition_is_the_hour_one(text, expected):
    assert extract_timespan(text, "it", ANCHOR).span.start.datetime() == expected


@pytest.mark.parametrize("text", ["una riunione di lavoro",
                                  "una ciotola di zuppa"])
def test_the_article_una_is_no_hour(text):
    assert extract_timespan(text, "it", ANCHOR) is None


def test_the_article_before_a_unit_keeps_its_reading():
    found = extract_timespan("una settimana prima del 5 aprile", "it", ANCHOR)
    assert found.span.start.datetime() == datetime(2018, 3, 29)
