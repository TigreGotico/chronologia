""""aankomende" and "aanstaande" mean "next" before a season, a month or a week.

Wiktionary nl "aankomend": coming, next ("Aanstaande woensdag komen mijn kinderen
eten").  They read like "komende" and "volgende".  Every date is worked out by
hand from the anchor, Tuesday 2017-06-27 13:04: the spring after it is
2018-03-01 to 2018-06-01, the next month is July 2017, and the next week starts
on Monday 2017-07-03.  "komende", "aankomende" and "aanstaande" name the
first weekend or evening that follows ("eerstvolgend", Wiktionary nl, s.v.
"aanstaand"): on that Tuesday the weekend is Saturday 2017-07-01 to Monday
2017-07-03 and the evening is the one of that day, from 18:00.  "volgende"
skips one.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)

ROWS = [
    ("aankomende lente", datetime(2018, 3, 1), datetime(2018, 6, 1)),
    ("aanstaande lente", datetime(2018, 3, 1), datetime(2018, 6, 1)),
    ("aankomende maand", datetime(2017, 7, 1), datetime(2017, 8, 1)),
    ("aanstaande maand", datetime(2017, 7, 1), datetime(2017, 8, 1)),
    ("aankomende week", datetime(2017, 7, 3), datetime(2017, 7, 10)),
    ("aanstaande week", datetime(2017, 7, 3), datetime(2017, 7, 10)),
    ("aankomend jaar", datetime(2018, 1, 1), datetime(2019, 1, 1)),
    ("aanstaand jaar", datetime(2018, 1, 1), datetime(2019, 1, 1)),
    ("aankomende zomer", datetime(2018, 6, 1), datetime(2018, 9, 1)),
]


@pytest.mark.parametrize("text,start,end", ROWS)
def test_aankomende_is_next(text, start, end):
    found = extract_timespan(text, "nl", ANCHOR)
    assert (found.span.start.datetime(), found.span.end.datetime()) == (start, end)
    assert found.remainder == ""


UPCOMING = [
    ("aankomend weekend", ANCHOR, datetime(2017, 7, 1), datetime(2017, 7, 3)),
    ("aanstaand weekend", ANCHOR, datetime(2017, 7, 1), datetime(2017, 7, 3)),
    ("aanstaande weekend", ANCHOR, datetime(2017, 7, 1), datetime(2017, 7, 3)),
    ("komende weekend", ANCHOR, datetime(2017, 7, 1), datetime(2017, 7, 3)),
    ("volgende weekend", ANCHOR, datetime(2017, 7, 8), datetime(2017, 7, 10)),
    ("aanstaand weekend", datetime(2017, 7, 1, 10, 0), datetime(2017, 7, 8), datetime(2017, 7, 10)),
    ("aanstaande avond", ANCHOR, datetime(2017, 6, 27, 18), datetime(2017, 6, 28)),
    ("aankomende avond", ANCHOR, datetime(2017, 6, 27, 18), datetime(2017, 6, 28)),
    ("komende avond", ANCHOR, datetime(2017, 6, 27, 18), datetime(2017, 6, 28)),
    ("aanstaande avond", datetime(2017, 6, 27, 19, 0), datetime(2017, 6, 28, 18), datetime(2017, 6, 29)),
    ("volgende avond", ANCHOR, datetime(2017, 6, 28, 18), datetime(2017, 6, 29)),
]


@pytest.mark.parametrize("text,anchor,start,end", UPCOMING)
def test_the_first_weekend_or_evening_that_follows(text, anchor, start, end):
    found = extract_timespan(text, "nl", anchor)
    assert (found.span.start.datetime(), found.span.end.datetime()) == (start, end)
    assert found.remainder == ""
