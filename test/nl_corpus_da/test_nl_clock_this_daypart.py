"""A clock before "i aften" / "i eftermiddag" falls in that part of today.

"i aften" is this evening and "i eftermiddag" this afternoon, so "klokken
syv i aften" is 19:00 today, not 07:00 tomorrow.  "halv otte" is half an
hour before eight.  The gold is clock arithmetic: the spoken hour plus 12 on
the anchor day, Tuesday 2017-06-27; "i formiddag" keeps the hour.
"""
import pytest

from ._corpus import ANCHOR, ad, span


@pytest.mark.parametrize("text,hour,minute", [
    ("klokken syv i aften", 19, 0),
    ("klokken 7 i aften", 19, 0),
    ("klokken elleve i aften", 23, 0),
    ("klokken to i eftermiddag", 14, 0),
    ("klokken fem i eftermiddag", 17, 0),
    ("halv otte i aften", 19, 30),
    ("kvart over tre i eftermiddag", 15, 15),
    ("klokken ti i formiddag", 10, 0),
])
def test_clock_before_this_daypart(text, hour, minute):
    assert span(text).start == ad(ANCHOR.replace(hour=hour, minute=minute))


def test_i_morgen_stays_tomorrow():
    want = ad(ANCHOR.replace(day=28, hour=7, minute=0))
    assert span("klokken syv i morgen").start == want
