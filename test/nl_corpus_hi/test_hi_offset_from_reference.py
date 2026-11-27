"""An offset counted from a reference: REF से [NUM] UNIT बाद/पहले.

से is the postposed ablative "from" (en.wiktionary.org, entry "से"), so the
reference leads and the offset trails it: "आज से तीन दिन बाद" is three days
from today.  Gold is plain date arithmetic on the anchor.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, nomatch, parse, start, start_end

TODAY = ANCHOR.replace(hour=0, minute=0)
#: the next Monday after the Tuesday anchor
MONDAY = TODAY + timedelta(days=6)
JULY_5 = TODAY.replace(month=7, day=5)


@pytest.mark.parametrize("text,base,days", [
    ("आज से 3 दिन बाद", TODAY, 3),
    ("आज से तीन दिन बाद", TODAY, 3),
    ("आज से तीन दिन पहले", TODAY, -3),
    ("आज से दो हफ़्ते बाद", TODAY, 14),
    ("सोमवार से तीन दिन बाद", MONDAY, 3),
    ("5 जुलाई से तीन दिन बाद", JULY_5, 3),
])
def test_offset_counts_from_the_reference(text, base, days):
    day = base + timedelta(days=days)
    assert start_end(text) == (ad(day), ad(day + timedelta(days=1)))
    assert parse(text).remainder == ""


def test_unread_offset_unit_gives_no_reading():
    # घड़ी is not a unit the engine reads: the bare आज must not stand in.
    nomatch("आज से तीन घड़ी बाद")


def test_from_today_without_offset_stays_today():
    # "I am happy from today": no offset follows, so the day is today.
    assert start("मैं आज से खुश हूँ") == ad(TODAY)
