"""Holiday references in Basque (``holiday_ref``).

Anchor 2017-06-27. Western computus (independent table): Easter 2018 = 1 Apr,
2020 = 12 Apr. Bare rule = next occurrence on or after the anchor. Movable
non-Gregorian dates are the anchor-shared reference gold."""
from datetime import datetime, timedelta
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import span, start, nomatch

A = datetime(2017, 6, 27, 13, 4)

def _start(t):
    return start(t, A)

_BARE = [
    ("gabonak", (2017, 12, 25)),
    ("eguberri", (2017, 12, 25)),
    ("gabon gaua", (2017, 12, 24)),
    ("urte berri", (2018, 1, 1)),
    ("erregen eguna", (2018, 1, 6)),
    ("domu santu", (2017, 11, 1)),
    ("pazkoa", (2018, 4, 1)),
    ("ostiral santua", (2018, 3, 30)),
    ("pazko astelehena", (2018, 4, 2)),
    ("igokundea", (2018, 5, 10)),
    ("andre maria", (2017, 8, 15)),
]

@pytest.mark.parametrize("text,ymd", _BARE)
def test_bare_holiday(text, ymd):
    assert _start(text) == AstroDate(*ymd)
    assert span(text, A).width == timedelta(days=1)

@pytest.mark.parametrize("text,ymd", [
    ("datorren gabonak", (2017, 12, 25)),
    ("aurreko gabonak", (2016, 12, 25)),
])
def test_next_last(text, ymd):
    assert _start(text) == AstroDate(*ymd)

@pytest.mark.parametrize("text,ymd", [
    ("gabonak 2020", (2020, 12, 25)),
    ("pazkoa 2020", (2020, 4, 12)),
])
def test_explicit_year(text, ymd):
    assert _start(text) == AstroDate(*ymd)

_EXPANDED = [
    ("id al-fitr", (2018, 6, 15)),
    ("ramadana", (2018, 5, 16)),
    ("txinako urte berria", (2018, 2, 16)),
    ("nowruz", (2018, 3, 21)),
    ("diwali", (2017, 10, 19)),
    ("vesak", (2018, 5, 29)),
    ("gau beltza", (2017, 10, 31)),
    ("san valentin", (2018, 2, 14)),
]

@pytest.mark.parametrize("text,ymd", _EXPANDED)
def test_bare_expanded(text, ymd):
    assert _start(text) == AstroDate(*ymd)
    assert span(text, A).width == timedelta(days=1)

@pytest.mark.parametrize("text", [
    "arrozaren prezioa igo da",
    "aurrekontuari buruzko bilera",
    "zopa katilu bat",
])
def test_no_holiday_no_match(text):
    nomatch(text, A)
