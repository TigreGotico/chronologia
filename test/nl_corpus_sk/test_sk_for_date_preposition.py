"""Slovak "na" before a day names the day the thing is for.

"koľko stojí lístok na zajtra" asks about tomorrow's ticket; "na" belongs to
the date and is not left in the remainder.  Likewise "v piatok budúci týždeň"
and "na piatok budúci týždeň" name Friday of next week.

Anchor: Tuesday 2017-06-27 13:04.  Every gold value is read off a calendar.
"""
from datetime import datetime

import pytest

from ._corpus import parse


def test_na_zajtra_consumes_the_preposition():
    r = parse("koľko stojí lístok na zajtra")
    assert r[0].start == datetime(2017, 6, 28)
    assert r[1] == "koľko stojí lístok"


def test_na_piatok_consumes_the_preposition():
    r = parse("na piatok")
    assert r[0].start == datetime(2017, 6, 30)
    assert r[1] == ""


@pytest.mark.parametrize("text", ["v piatok budúci týždeň",
                                  "na piatok budúci týždeň"])
def test_weekday_of_next_week_consumes_its_preposition(text):
    r = parse(text)
    # week of Tue 2017-06-27 starts Mon 06-26; next week starts Mon 07-03
    assert r[0].start == datetime(2017, 7, 7)
    assert r[1] == ""
