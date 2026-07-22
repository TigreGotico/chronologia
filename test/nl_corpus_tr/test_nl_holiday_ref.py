"""Holiday references in Turkish (``holiday_ref``).

Anchor 2017-06-27. Bare rule = next occurrence on or after the anchor. The
bayram surfaces bind to the Islamic-registry keys; their dates come from
published Umm al-Qura tables cross-checked independently: Eid al-Fitr 1439 =
15 Jun 2018, Eid al-Adha 1438 = 1 Sep 2017, Islamic New Year 1439 = 21 Sep
2017, Ashura 1439 = 30 Sep 2017, Mawlid 1439 = 30 Nov 2017. Western/other
movable dates are the anchor-shared reference gold."""
from datetime import datetime, timedelta
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import span, start, nomatch

A = datetime(2017, 6, 27, 13, 4)

def _start(t):
    return start(t, A)

_BARE = [
    ("yılbaşı", (2018, 1, 1)),
    ("noel", (2017, 12, 25)),
    ("paskalya", (2018, 4, 1)),
    ("ramazan", (2018, 5, 16)),
    ("ramazan bayramı", (2018, 6, 15)),
    ("şeker bayramı", (2018, 6, 15)),
    ("kurban bayramı", (2017, 9, 1)),
    ("hicri yılbaşı", (2017, 9, 21)),
    ("aşure günü", (2017, 9, 30)),
    ("mevlid kandili", (2017, 11, 30)),
    ("nevruz", (2018, 3, 21)),
    ("sevgililer günü", (2018, 2, 14)),
    ("cadılar bayramı", (2017, 10, 31)),
]

@pytest.mark.parametrize("text,ymd", _BARE)
def test_bare_holiday(text, ymd):
    assert _start(text) == AstroDate(*ymd)
    assert span(text, A).width == timedelta(days=1)

@pytest.mark.parametrize("text,ymd", [
    ("gelecek noel", (2017, 12, 25)),
    ("geçen noel", (2016, 12, 25)),
])
def test_next_last(text, ymd):
    assert _start(text) == AstroDate(*ymd)

@pytest.mark.parametrize("text,ymd", [
    ("noel 2020", (2020, 12, 25)),
    ("paskalya 2020", (2020, 4, 12)),
])
def test_explicit_year(text, ymd):
    assert _start(text) == AstroDate(*ymd)

_EXPANDED = [
    ("çin yeni yılı", (2018, 2, 16)),
    ("divali", (2017, 10, 19)),
    ("vesak", (2018, 5, 29)),
    ("hamursuz bayramı", (2018, 3, 31)),
    ("hanuka", (2017, 12, 13)),
    ("yahudi yeni yılı", (2017, 9, 21)),
    ("yom kippur", (2017, 9, 30)),
]

@pytest.mark.parametrize("text,ymd", _EXPANDED)
def test_bare_expanded(text, ymd):
    assert _start(text) == AstroDate(*ymd)
    assert span(text, A).width == timedelta(days=1)

@pytest.mark.parametrize("text", [
    "pirinç fiyatı arttı",
    "bütçe toplantısı",
    "bir kase çorba",
])
def test_no_holiday_no_match(text):
    nomatch(text, A)
