"""Holiday references in Hungarian (``holiday_ref``).

Anchor 2017-06-27. Western computus (independent table): Easter 2018 = 1 Apr,
2020 = 12 Apr. Bare rule = next occurrence on or after the anchor. Movable
non-Gregorian dates are the anchor-shared gold hand-derived for the reference
corpus."""
from datetime import datetime, timedelta
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import span, start, nomatch

A = datetime(2017, 6, 27, 13, 4)

def _start(t):
    return start(t, A)

_BARE = [
    ("karácsony", (2017, 12, 25)),
    ("karácsony napja", (2017, 12, 25)),
    ("szenteste", (2017, 12, 24)),
    ("karácsony másnapja", (2017, 12, 26)),
    ("újév napja", (2018, 1, 1)),
    ("vízkereszt", (2018, 1, 6)),
    ("mindenszentek", (2017, 11, 1)),
    ("húsvét", (2018, 4, 1)),
    ("nagypéntek", (2018, 3, 30)),
    ("húsvéthétfő", (2018, 4, 2)),
    ("mennybemenetel", (2018, 5, 10)),
    ("pünkösd", (2018, 5, 20)),
]

@pytest.mark.parametrize("text,ymd", _BARE)
def test_bare_holiday(text, ymd):
    assert _start(text) == AstroDate(*ymd)
    assert span(text, A).width == timedelta(days=1)

@pytest.mark.parametrize("text,ymd", [
    ("jövő karácsony", (2017, 12, 25)),
    ("előző karácsony", (2016, 12, 25)),
])
def test_next_last(text, ymd):
    assert _start(text) == AstroDate(*ymd)

@pytest.mark.parametrize("text,ymd", [
    ("karácsony 2020", (2020, 12, 25)),
    ("húsvét 2020", (2020, 4, 12)),
])
def test_explicit_year(text, ymd):
    assert _start(text) == AstroDate(*ymd)

_EXPANDED = [
    ("id al-fitr", (2018, 6, 15)),
    ("ramadán", (2018, 5, 16)),
    ("zsidó újév", (2017, 9, 21)),
    ("jom kippur", (2017, 9, 30)),
    ("pészah", (2018, 3, 31)),
    ("hanuka", (2017, 12, 13)),
    ("kínai újév", (2018, 2, 16)),
    ("novruz", (2018, 3, 21)),
    ("diváli", (2017, 10, 19)),
    ("vészák", (2018, 5, 29)),
    ("halloween", (2017, 10, 31)),
    ("valentin-nap", (2018, 2, 14)),
]

@pytest.mark.parametrize("text,ymd", _EXPANDED)
def test_bare_expanded(text, ymd):
    assert _start(text) == AstroDate(*ymd)
    assert span(text, A).width == timedelta(days=1)

@pytest.mark.parametrize("text,ymd", [
    ("diváli 2026", (2026, 11, 8)),
    ("kínai újév 2026", (2026, 2, 17)),
    ("pészah 2026", (2026, 4, 2)),
])
def test_explicit_year_expanded(text, ymd):
    assert _start(text) == AstroDate(*ymd)

@pytest.mark.parametrize("text", [
    "a rizs ára emelkedett",
    "értekezlet a költségvetésről",
    "egy tál leves",
])
def test_no_holiday_no_match(text):
    nomatch(text, A)
