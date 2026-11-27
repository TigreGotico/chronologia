"""A weekday before "morgen" names that weekday's morning, da.

In da "morgen" after a weekday names its morning, the way "Dienstagmorgen" is
"Morgen des Dienstags" (Duden s.v. "Dienstagmorgen"); Den Danske Ordbog
"morgen" gives "mandag/søndag morgen".  Bare "morgen" is the noun "morning"
(en.wiktionary "morgen"), so the phrase is the weekday's 05:00 band start.

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
    ("tirsdag morgen", SATURDAY, 3, ""),
    ("søndag morgen", SATURDAY, 1, ""),
    ("tirsdag morgen", MONDAY, 1, ""),
])
def test_weekday_before_morgen_is_its_morning(text, anchor, offset, rest):
    day = anchor.replace(hour=5) + timedelta(days=offset)
    r = parse(text, anchor)
    assert r is not None, f"{text!r} did not parse"
    assert r[0].start == ad(day)
    assert r[1] == rest
