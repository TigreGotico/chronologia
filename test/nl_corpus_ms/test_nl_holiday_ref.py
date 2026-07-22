"""Holiday references in Malay (``holiday_ref``).

Anchor 2017-06-27. Bare rule = next occurrence on or after the anchor. Hari
Raya Aidilfitri (= Eid al-Fitr) and the other Islamic surfaces bind the
Islamic-registry keys; Umm al-Qura dates cross-checked: Eid al-Fitr 1439 =
15 Jun 2018, Eid al-Adha 1438 = 1 Sep 2017, Islamic New Year 1439 = 21 Sep
2017, Mawlid 1439 = 30 Nov 2017. Wesak (Vesak) and the rest come from the
anchor-shared reference gold."""
from datetime import datetime, timedelta
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import span, start, nomatch

A = datetime(2017, 6, 27, 13, 4)

def _start(t):
    return start(t, A)

_BARE = [
    ("tahun baru", (2018, 1, 1)),
    ("krismas", (2017, 12, 25)),
    ("hari krismas", (2017, 12, 25)),
    ("paskah", (2018, 4, 1)),
    ("jumaat agung", (2018, 3, 30)),
    ("hari raya aidilfitri", (2018, 6, 15)),
    ("aidilfitri", (2018, 6, 15)),
    ("hari raya aidiladha", (2017, 9, 1)),
    ("ramadan", (2018, 5, 16)),
    ("maal hijrah", (2017, 9, 21)),
    ("maulidur rasul", (2017, 11, 30)),
]

@pytest.mark.parametrize("text,ymd", _BARE)
def test_bare_holiday(text, ymd):
    assert _start(text) == AstroDate(*ymd)
    assert span(text, A).width == timedelta(days=1)

@pytest.mark.parametrize("text,ymd", [
    ("krismas 2020", (2020, 12, 25)),
    ("paskah 2020", (2020, 4, 12)),
])
def test_explicit_year(text, ymd):
    assert _start(text) == AstroDate(*ymd)

_EXPANDED = [
    ("tahun baru cina", (2018, 2, 16)),
    ("hari wesak", (2018, 5, 29)),
    ("wesak", (2018, 5, 29)),
    ("deepavali", (2017, 10, 19)),
    ("halloween", (2017, 10, 31)),
    ("hari valentine", (2018, 2, 14)),
]

@pytest.mark.parametrize("text,ymd", _EXPANDED)
def test_bare_expanded(text, ymd):
    assert _start(text) == AstroDate(*ymd)
    assert span(text, A).width == timedelta(days=1)

@pytest.mark.parametrize("text", [
    "harga beras naik",
    "mesyuarat bajet",
    "semangkuk sup",
])
def test_no_holiday_no_match(text):
    nomatch(text, A)
