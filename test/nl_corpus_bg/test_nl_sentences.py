"""Bulgarian offsets embedded in full sentences a user would speak."""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, AstroDate, ad, start, span


@pytest.mark.parametrize("text,delta", [
    ("ще се видим след три дни", timedelta(days=3)),
    ("обади ми се след два часа", timedelta(hours=2)),
    ("напомни ми след десет минути", timedelta(minutes=10)),
    ("това се случи преди пет дни", timedelta(days=-5)),
    ("бяхме там преди две години", relativedelta(years=-2)),
    ("срещата е след две седмици", timedelta(weeks=2)),
    ("пристига след четири дни", timedelta(days=4)),
    ("ще се обадя след три часа", timedelta(hours=3)),
    ("приключи преди три седмици", timedelta(weeks=-3)),
    ("започваме след шест месеца", relativedelta(months=6)),
])
def test_sentence_offset(text, delta):
    assert start(text) == ad(ANCHOR + delta)


@pytest.mark.parametrize("n", [4, 6, 7, 8, 9, 12])
def test_more_days(n):
    assert start(f"след {n} дни") == ad(ANCHOR + timedelta(days=n))


@pytest.mark.parametrize("n", [15, 20, 25, 45])
def test_more_minutes(n):
    assert start(f"след {n} минути") == ad(ANCHOR + timedelta(minutes=n))


@pytest.mark.parametrize("text,y,m,d", [
    ("резервацията е 5 юни 2020", 2020, 6, 5),
    ("рожденият ден е 22 март", 2018, 3, 22),
    ("изпитът е 1 септември 2019", 2019, 9, 1),
])
def test_sentence_date(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)


def test_offset_width():
    assert span("след 3 дни").width == timedelta(days=1)
    assert span("след 2 седмици").width == timedelta(weeks=1)
