"""Holiday references in Azerbaijani (``holiday_ref``).

Anchor 2017-06-27. Bare rule = next occurrence on or after the anchor. Bayram
surfaces bind the Islamic-registry keys; dates from published Umm al-Qura
tables cross-checked independently: Eid al-Fitr 1439 = 15 Jun 2018, Eid al-Adha
1438 = 1 Sep 2017, Islamic New Year 1439 = 21 Sep 2017, Ashura 1439 = 30 Sep
2017, Mawlid 1439 = 30 Nov 2017. Novruz 2018 = 21 Mar. Other movable dates are
the anchor-shared reference gold."""
from datetime import datetime, timedelta
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import span, start, nomatch

A = datetime(2017, 6, 27, 13, 4)

def _start(t):
    return start(t, A)

_BARE = [
    ("yeni il", (2018, 1, 1)),
    ("milad", (2017, 12, 25)),
    ("pasxa", (2018, 4, 1)),
    ("ramazan", (2018, 5, 16)),
    ("ramazan bayramı", (2018, 6, 15)),
    ("orucluq bayramı", (2018, 6, 15)),
    ("qurban bayramı", (2017, 9, 1)),
    ("hicri yeni il", (2017, 9, 21)),
    ("aşura", (2017, 9, 30)),
    ("mövlud", (2017, 11, 30)),
    ("novruz", (2018, 3, 21)),
    ("novruz bayramı", (2018, 3, 21)),
    ("sevgililər günü", (2018, 2, 14)),
]

@pytest.mark.parametrize("text,ymd", _BARE)
def test_bare_holiday(text, ymd):
    assert _start(text) == AstroDate(*ymd)
    assert span(text, A).width == timedelta(days=1)

@pytest.mark.parametrize("text,ymd", [
    ("gələn milad", (2017, 12, 25)),
    ("keçən milad", (2016, 12, 25)),
])
def test_next_last(text, ymd):
    assert _start(text) == AstroDate(*ymd)

@pytest.mark.parametrize("text,ymd", [
    ("milad 2020", (2020, 12, 25)),
    ("pasxa 2020", (2020, 4, 12)),
])
def test_explicit_year(text, ymd):
    assert _start(text) == AstroDate(*ymd)

_EXPANDED = [
    ("çin yeni ili", (2018, 2, 16)),
    ("divali", (2017, 10, 19)),
    ("vesak", (2018, 5, 29)),
    ("hanuka", (2017, 12, 13)),
    ("yəhudi yeni ili", (2017, 9, 21)),
    ("yom kippur", (2017, 9, 30)),
    ("hellowin", (2017, 10, 31)),
]

@pytest.mark.parametrize("text,ymd", _EXPANDED)
def test_bare_expanded(text, ymd):
    assert _start(text) == AstroDate(*ymd)
    assert span(text, A).width == timedelta(days=1)

@pytest.mark.parametrize("text", [
    "düyünün qiyməti artdı",
    "büdcə iclası",
    "bir kasa şorba",
])
def test_no_holiday_no_match(text):
    nomatch(text, A)
