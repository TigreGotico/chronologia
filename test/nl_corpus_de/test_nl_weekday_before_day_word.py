"""A weekday before a day word is not an apposition, de.

The apposed weekday follows the day word ("morgen, sonntag"). Before the day
word it is not folded: in de, nl, da and nb "morgen" after a weekday names
its morning: "Dienstagmorgen" is "Morgen des Dienstags" (Duden s.v.
"Dienstagmorgen"). The phrase keeps the reading it has without the fold: the
weekday's day, with the day word left in the remainder.

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
    ("dienstag morgen", SATURDAY, 3, "morgen"),
    ("sonntag morgen", SATURDAY, 1, "morgen"),
    ("dienstag morgen", MONDAY, 1, "morgen"),
])
def test_weekday_before_the_day_word_is_not_folded(text, anchor, offset, rest):
    day = anchor.replace(hour=0) + timedelta(days=offset)
    r = parse(text, anchor)
    assert r is not None, f"{text!r} did not parse"
    assert r[0].start == ad(day)
    assert r[1] == rest


def test_a_clock_after_weekday_morgen_keeps_the_tuesday():
    r = parse("dienstag morgen um 9 uhr", SATURDAY)
    assert r is not None, "'dienstag morgen um 9 uhr' did not parse"
    tuesday = SATURDAY.replace(hour=0) + timedelta(days=3)
    assert ad(tuesday) <= r[0].start < ad(tuesday + timedelta(days=1))
