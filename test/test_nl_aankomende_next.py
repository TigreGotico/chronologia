""""aankomende" and "aanstaande" mean "next" before a season, a month or a week.

Wiktionary nl "aankomend": coming, next ("Aanstaande woensdag komen mijn kinderen
eten").  They read like "komende" and "volgende".  Every date is worked out by
hand from the anchor, Tuesday 2017-06-27 13:04: the spring after it is
2018-03-01 to 2018-06-01, the next month is July 2017, and the next week starts
on Monday 2017-07-03.
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
]


@pytest.mark.parametrize("text,start,end", ROWS)
def test_aankomende_is_next(text, start, end):
    found = extract_timespan(text, "nl", ANCHOR)
    assert (found.span.start.datetime(), found.span.end.datetime()) == (start, end)
    assert found.remainder == ""
