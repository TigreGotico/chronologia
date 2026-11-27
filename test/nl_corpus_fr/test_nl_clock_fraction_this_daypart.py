"""A clock with a quarter, a half or minutes before "ce soir" / "cet
après-midi" falls in that part of today.

"moins le quart" takes 15 minutes from the hour, "et quart" adds 15 and
"et demie" adds 30 (see test_nl_moins_minutes.py).  "ce soir" puts the hour
in the evening of today, as it does for a plain hour ("six heures ce soir").
The gold is clock arithmetic: the spoken hour plus 12 on the anchor day,
Tuesday 2017-06-27.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, parse, span


@pytest.mark.parametrize("text,hour,minute", [
    ("à sept heures moins le quart ce soir", 6, 45),
    ("à neuf heures moins le quart ce soir", 8, 45),
    ("à dix heures moins quart ce soir", 9, 45),
    ("à six heures et quart ce soir", 6, 15),
    ("à neuf heures et demie ce soir", 9, 30),
    ("à six heures quinze ce soir", 6, 15),
    ("à deux heures et quart cet après-midi", 2, 15),
])
def test_fraction_clock_before_this_daypart(text, hour, minute):
    want = ANCHOR.replace(hour=hour + 12, minute=minute)
    assert span(text).start == ad(want)
    assert span(text).width == timedelta(minutes=1)
    assert parse(text)[1].strip() == ""


def test_plain_hour_before_this_daypart_unchanged():
    assert span("à six heures ce soir").start == ad(ANCHOR.replace(hour=18, minute=0))
