"""Croatian "za" before a day names the day the thing is for.

"koliko košta karta za sutra" asks about tomorrow's ticket; "za" belongs to
the date and is not left in the remainder.  Likewise "u petak sljedeći tjedan"
and "za petak sljedeći tjedan" name Friday of next week.

Anchor: Tuesday 2017-06-27 13:04.  Every gold value is read off a calendar.
"""
from datetime import datetime

import pytest

from ._corpus import parse


def test_za_sutra_consumes_the_preposition():
    r = parse("koliko košta karta za sutra")
    assert r[0].start == datetime(2017, 6, 28)
    assert r[1] == "koliko košta karta"


def test_za_petak_consumes_the_preposition():
    r = parse("za petak")
    assert r[0].start == datetime(2017, 6, 30)
    assert r[1] == ""


@pytest.mark.parametrize("text", ["u petak sljedeći tjedan",
                                  "za petak sljedeći tjedan"])
def test_weekday_of_next_week_consumes_its_preposition(text):
    r = parse(text)
    # week of Tue 2017-06-27 starts Mon 06-26; next week starts Mon 07-03
    assert r[0].start == datetime(2017, 7, 7)
    assert r[1] == ""
