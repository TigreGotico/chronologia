"""Holiday references in Kabyle (``holiday_ref``).

Anchor 2017-06-27. Bare rule = next occurrence on or after the anchor. The
Islamic surfaces (lɛid ameẓyan = Eid al-Fitr, lɛid ameqqran = Eid al-Adha,
tafaska = the sacrifice feast) bind the Islamic-registry keys; Umm al-Qura
dates cross-checked: Eid al-Fitr 1439 = 15 Jun 2018, Eid al-Adha 1438 = 1 Sep
2017, Islamic New Year 1439 = 21 Sep 2017. Other movable dates are the
anchor-shared reference gold. Kabyle has no relative markers, so no next/last
forms are asserted."""
from datetime import datetime, timedelta
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import span, start, nomatch

A = datetime(2017, 6, 27, 13, 4)

def _start(t):
    return start(t, A)

_BARE = [
    ("aseggas amaynut", (2018, 1, 1)),
    ("lɛid n tlalit", (2017, 12, 25)),
    ("ramḍan", (2018, 5, 16)),
    ("uẓum", (2018, 5, 16)),
    ("lɛid ameẓyan", (2018, 6, 15)),
    ("tafaska tameẓyant", (2018, 6, 15)),
    ("lɛid ameqqran", (2017, 9, 1)),
    ("tafaska tameqqrant", (2017, 9, 1)),
    ("aseggas ihjrawan", (2017, 9, 21)),
    ("nowruz", (2018, 3, 21)),
    ("diwali", (2017, 10, 19)),
    ("halloween", (2017, 10, 31)),
]

@pytest.mark.parametrize("text,ymd", _BARE)
def test_bare_holiday(text, ymd):
    assert _start(text) == AstroDate(*ymd)
    assert span(text, A).width == timedelta(days=1)

@pytest.mark.parametrize("text,ymd", [
    ("lɛid ameẓyan 2020", (2020, 5, 24)),
    ("nowruz 2020", (2020, 3, 20)),
])
def test_explicit_year(text, ymd):
    assert _start(text) == AstroDate(*ymd)

@pytest.mark.parametrize("text", [
    "azal n temẓin yuli",
    "aseqqamu n tedrimt",
])
def test_no_holiday_no_match(text):
    nomatch(text, A)
