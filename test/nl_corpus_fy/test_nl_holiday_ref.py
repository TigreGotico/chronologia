"""Holiday references (fy) (``holiday_ref``).

Anchor 2017-06-27. Western computus (independent table): Easter 2017 = 16 Apr,
2018 = 1 Apr, 2020 = 12 Apr. Bare rule = next occurrence on or after the anchor.
Every expected date derived by hand from published civil/computus tables."""
from datetime import timedelta
import pytest
from ._corpus import ANCHOR, AstroDate, parse, span, start, nomatch

_BARE = [
    ('earste krystdei', (2017, 12, 25)),
    ('krystjûn', (2017, 12, 24)),
    ('nijjiersdei', (2018, 1, 1)),
    ('âldjiersjûn', (2017, 12, 31)),
    ('driekeningen', (2018, 1, 6)),
    ('allerheljen', (2017, 11, 1)),
    ('peaske', (2018, 4, 1)),
    ('goedfreed', (2018, 3, 30)),
    ('twadde peaskedei', (2018, 4, 2)),
    ('pinkster', (2018, 5, 20)),
    ('halloween', (2017, 10, 31)),
    ('falentynsdei', (2018, 2, 14)),
]

@pytest.mark.parametrize("text,ymd", _BARE)
def test_bare_holiday(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)

@pytest.mark.parametrize("text,ymd", [
    ('kommende kryst', (2017, 12, 25)),
    ('ôfrûne kryst', (2016, 12, 25)),
])
def test_next_last(text, ymd):
    assert start(text) == AstroDate(*ymd)

def test_explicit_year():
    assert start('peaske 2020') == AstroDate(*(2020, 4, 12))

@pytest.mark.parametrize("text", ['in gearkomste oer it budzjet', 'de priis fan rys stiek'])
def test_no_holiday_no_match(text):
    nomatch(text)
