"""A weekday before a day word is not an apposition, es.

The apposed weekday follows the day word ("mañana, domingo"). Before the day
word it is not folded: es "martes mañana" reads as the Tuesday, as de
"dienstag morgen" names the Tuesday's morning. The phrase keeps the reading
it has without the fold: the weekday's day, with the day word left in the
remainder.

Anchors Saturday 2026-10-17 and Monday 2026-10-19, 12:00.  Gold is datetime
arithmetic on the anchor: the next Tuesday is 3 days after the Saturday and
1 day after the Monday, the next Sunday 1 day after the Saturday.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ad, parse

SATURDAY = datetime(2026, 10, 17, 12, 0)
MONDAY = datetime(2026, 10, 19, 12, 0)


@pytest.mark.parametrize("text,anchor,offset,rest", [
    ("martes mañana", SATURDAY, 3, "mañana"),
    ("domingo mañana", SATURDAY, 1, "mañana"),
    ("martes mañana", MONDAY, 1, "mañana"),
])
def test_weekday_before_the_day_word_is_not_folded(text, anchor, offset, rest):
    day = anchor.replace(hour=0) + timedelta(days=offset)
    r = parse(text, anchor)
    assert r is not None, f"{text!r} did not parse"
    assert r[0].start == ad(day)
    assert r[1] == rest
