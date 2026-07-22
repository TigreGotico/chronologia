"""Holiday references in Estonian (``holiday_ref``).

Anchor 2017-06-27. Western computus (independent table): Easter 2018 = 1 Apr,
2020 = 12 Apr. Bare rule = next occurrence on or after the anchor. Movable
non-Gregorian dates are the anchor-shared gold hand-derived for the reference
corpus. Every expected date derived by hand."""
from datetime import datetime, timedelta
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import span, start, nomatch

A = datetime(2017, 6, 27, 13, 4)

def _start(t):
    return start(t, A)

_BARE = [
    ("jõulud", (2017, 12, 25)),
    ("esimene jõulupüha", (2017, 12, 25)),
    ("jõululaupäev", (2017, 12, 24)),
    ("teine jõulupüha", (2017, 12, 26)),
    ("uusaasta", (2018, 1, 1)),
    ("kolmekuningapäev", (2018, 1, 6)),
    ("hingedepäev", (2017, 11, 1)),
    ("lihavõtted", (2018, 4, 1)),
    ("suur reede", (2018, 3, 30)),
    ("teine ülestõusmispüha", (2018, 4, 2)),
    ("taevaminemispüha", (2018, 5, 10)),
    ("nelipühad", (2018, 5, 20)),
]

@pytest.mark.parametrize("text,ymd", _BARE)
def test_bare_holiday(text, ymd):
    assert _start(text) == AstroDate(*ymd)
    assert span(text, A).width == timedelta(days=1)

@pytest.mark.parametrize("text,ymd", [
    ("järgmine jõulud", (2017, 12, 25)),
    ("eelmine jõulud", (2016, 12, 25)),
])
def test_next_last(text, ymd):
    assert _start(text) == AstroDate(*ymd)

@pytest.mark.parametrize("text,ymd", [
    ("jõulud 2020", (2020, 12, 25)),
    ("lihavõtted 2020", (2020, 4, 12)),
])
def test_explicit_year(text, ymd):
    assert _start(text) == AstroDate(*ymd)

_EXPANDED = [
    ("id al-fitr", (2018, 6, 15)),
    ("ramadaan", (2018, 5, 16)),
    ("juudi uusaasta", (2017, 9, 21)),
    ("jom kippur", (2017, 9, 30)),
    ("paasapüha", (2018, 3, 31)),
    ("hanukaa", (2017, 12, 13)),
    ("hiina uusaasta", (2018, 2, 16)),
    ("nowruz", (2018, 3, 21)),
    ("diwali", (2017, 10, 19)),
    ("vesak", (2018, 5, 29)),
    ("halloween", (2017, 10, 31)),
    ("sõbrapäev", (2018, 2, 14)),
]

@pytest.mark.parametrize("text,ymd", _EXPANDED)
def test_bare_expanded(text, ymd):
    assert _start(text) == AstroDate(*ymd)
    assert span(text, A).width == timedelta(days=1)

@pytest.mark.parametrize("text,ymd", [
    ("diwali 2026", (2026, 11, 8)),
    ("hiina uusaasta 2026", (2026, 2, 17)),
    ("paasapüha 2026", (2026, 4, 2)),
])
def test_explicit_year_expanded(text, ymd):
    assert _start(text) == AstroDate(*ymd)

@pytest.mark.parametrize("text", [
    "riisi hind tõusis",
    "koosolek eelarvest",
    "kausitäis suppi",
])
def test_no_holiday_no_match(text):
    nomatch(text, A)
