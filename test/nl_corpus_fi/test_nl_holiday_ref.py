"""Holiday references in Finnish (``holiday_ref``).

Anchor 2017-06-27. Western computus (independent table): Easter 2017 = 16 Apr,
2018 = 1 Apr, 2020 = 12 Apr. Bare rule = next occurrence on or after the anchor.
Movable non-Gregorian dates (Islamic/Hebrew/Chinese/solar-Hijri and the Diwali/
Vesak decree tables) are identical to the anchor-shared gold hand-derived for
the Romance reference corpus. Every expected date derived by hand."""
from datetime import datetime, timedelta
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import parse, span, start, nomatch

A = datetime(2017, 6, 27, 13, 4)

def _start(t):
    return start(t, A)

_BARE = [
    ("joulu", (2017, 12, 25)),
    ("joulupäivä", (2017, 12, 25)),
    ("jouluaatto", (2017, 12, 24)),
    ("uudenvuodenpäivä", (2018, 1, 1)),
    ("loppiainen", (2018, 1, 6)),
    ("pyhäinpäivä", (2017, 11, 1)),
    ("tapaninpäivä", (2017, 12, 26)),
    ("pääsiäinen", (2018, 4, 1)),
    ("pitkäperjantai", (2018, 3, 30)),
    ("toinen pääsiäispäivä", (2018, 4, 2)),
    ("helatorstai", (2018, 5, 10)),
    ("helluntai", (2018, 5, 20)),
]

@pytest.mark.parametrize("text,ymd", _BARE)
def test_bare_holiday(text, ymd):
    assert _start(text) == AstroDate(*ymd)
    assert span(text, A).width == timedelta(days=1)

@pytest.mark.parametrize("text,ymd", [
    ("ensi joulu", (2017, 12, 25)),
    ("viime joulu", (2016, 12, 25)),
])
def test_next_last(text, ymd):
    assert _start(text) == AstroDate(*ymd)

@pytest.mark.parametrize("text,ymd", [
    ("joulu 2020", (2020, 12, 25)),
    ("pääsiäinen 2020", (2020, 4, 12)),
])
def test_explicit_year(text, ymd):
    assert _start(text) == AstroDate(*ymd)

_EXPANDED = [
    ('id al-fitr', (2018, 6, 15)),
    ('ramadan', (2018, 5, 16)),
    ('juutalainen uusivuosi', (2017, 9, 21)),
    ('jom kippur', (2017, 9, 30)),
    ('pesah', (2018, 3, 31)),
    ('hanukka', (2017, 12, 13)),
    ('kiinalainen uusivuosi', (2018, 2, 16)),
    ('nowruz', (2018, 3, 21)),
    ('diwali', (2017, 10, 19)),
    ('vesak', (2018, 5, 29)),
    ('halloween', (2017, 10, 31)),
    ('ystävänpäivä', (2018, 2, 14)),
]

@pytest.mark.parametrize("text,ymd", _EXPANDED)
def test_bare_expanded(text, ymd):
    assert _start(text) == AstroDate(*ymd)
    assert span(text, A).width == timedelta(days=1)

@pytest.mark.parametrize("text,ymd", [
    ('diwali 2026', (2026, 11, 8)),
    ('kiinalainen uusivuosi 2026', (2026, 2, 17)),
    ('pesah 2026', (2026, 4, 2)),
])
def test_explicit_year_expanded(text, ymd):
    assert _start(text) == AstroDate(*ymd)

@pytest.mark.parametrize("text", [
    "riisin hinta nousi",
    "kokous budjetista",
    "kulho keittoa",
])
def test_no_holiday_no_match(text):
    nomatch(text, A)
