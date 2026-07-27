"""Easter-relative movable feasts resolve through the computus, not as bare weekdays.

A movable feast whose spoken name embeds a weekday word ("Ash Wednesday",
"Maundy Thursday", "Trinity Sunday", "Holy Saturday") must resolve to its
Easter-anchored liturgical date -- NOT strand the qualifier and grab the next
literal weekday.  The offsets (days from Easter Sunday, Easter = day 0) are the
liturgical-calendar constants:

    Ash Wednesday  -46   Shrove Tuesday -47   Palm Sunday    -7
    Maundy/Holy Thu -3   Good Friday    -2    Holy Saturday  -1
    Easter           0   Ascension     +39    Pentecost     +49
    Trinity Sunday +56   Corpus Christi +60

Western (Gregorian) computus only (Orthodox is a separate key set).  Easter
Sunday dates taken from an independent published table, never the engine:

    Easter 2017 = 16 Apr    Easter 2018 = 1 Apr

Anchor 2017-06-27 is AFTER Easter 2017, so a bare feast name rolls forward to
the 2018 occurrence (the same next-occurrence rule fixed holidays follow).
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, AstroDate, parse, span, start  # noqa: F401
from datetime import datetime

#: a pre-Easter anchor pins the *same-year* branch (Easter 2017 = 16 Apr).
_PRE_EASTER = datetime(2017, 1, 1, 12, 0)

# -- bare name -> next occurrence on/after 2017-06-27 -> 2018 (Easter 1 Apr) --

_BARE_2018 = [
    ("ash wednesday", (2018, 2, 14)),    # 1 Apr 2018 - 46
    ("shrove tuesday", (2018, 2, 13)),   # 1 Apr 2018 - 47 (Carnival)
    ("palm sunday", (2018, 3, 25)),      # 1 Apr 2018 - 7
    ("maundy thursday", (2018, 3, 29)),  # 1 Apr 2018 - 3
    ("holy thursday", (2018, 3, 29)),    # alias of Maundy Thursday
    ("good friday", (2018, 3, 30)),      # 1 Apr 2018 - 2
    ("holy saturday", (2018, 3, 31)),    # 1 Apr 2018 - 1
    ("easter", (2018, 4, 1)),
    ("pentecost", (2018, 5, 20)),        # 1 Apr 2018 + 49
    ("whitsun", (2018, 5, 20)),          # alias of Pentecost
    ("trinity sunday", (2018, 5, 27)),   # 1 Apr 2018 + 56
    ("corpus christi", (2018, 5, 31)),   # 1 Apr 2018 + 60
]


@pytest.mark.parametrize("text,ymd", _BARE_2018)
def test_bare_feast_rolls_to_next_year(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,ymd", _BARE_2018)
def test_no_qualifier_stranded(text, ymd):
    """The full feast name is consumed -- nothing is left in the remainder."""
    r = parse(text)
    assert r is not None
    assert r[1].strip() == "", f"stranded remainder {r[1]!r} for {text!r}"


# -- same-year branch: a pre-Easter anchor keeps the feast in 2017 --------

_SAME_YEAR_2017 = [
    ("ash wednesday", (2017, 3, 1)),     # 16 Apr 2017 - 46
    ("maundy thursday", (2017, 4, 13)),  # 16 Apr 2017 - 3
    ("holy saturday", (2017, 4, 15)),    # 16 Apr 2017 - 1
    ("trinity sunday", (2017, 6, 11)),   # 16 Apr 2017 + 56
]


@pytest.mark.parametrize("text,ymd", _SAME_YEAR_2017)
def test_same_year_before_easter(text, ymd):
    assert start(text, anchor=_PRE_EASTER) == AstroDate(*ymd)


# -- collision guard: a BARE weekday is untouched by the feast surfaces ----

@pytest.mark.parametrize("text,ymd", [
    ("wednesday", (2017, 6, 28)),   # next literal Wednesday after the anchor
    ("thursday", (2017, 6, 29)),
    ("friday", (2017, 6, 30)),
    ("saturday", (2017, 7, 1)),
    ("sunday", (2017, 7, 2)),
])
def test_bare_weekday_unaffected(text, ymd):
    assert start(text) == AstroDate(*ymd)
