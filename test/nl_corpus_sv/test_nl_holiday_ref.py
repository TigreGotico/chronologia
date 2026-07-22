"""Holiday references (sv) (``holiday_ref``).

Anchor 2017-06-27. Western computus (independent table): Easter 2017 = 16 Apr,
2018 = 1 Apr, 2020 = 12 Apr. Bare rule = next occurrence on or after the anchor.
Every expected date derived by hand from published civil/computus tables."""
from datetime import timedelta
import pytest
from ._corpus import ANCHOR, AstroDate, parse, span, start, nomatch

_BARE = [
    ('juldagen', (2017, 12, 25)),
    ('julafton', (2017, 12, 24)),
    ('nyårsdagen', (2018, 1, 1)),
    ('nyårsafton', (2017, 12, 31)),
    ('trettondagen', (2018, 1, 6)),
    ('alla helgons dag', (2017, 11, 1)),
    ('påsk', (2018, 4, 1)),
    ('långfredagen', (2018, 3, 30)),
    ('annandag påsk', (2018, 4, 2)),
    ('pingst', (2018, 5, 20)),
    ('halloween', (2017, 10, 31)),
    ('alla hjärtans dag', (2018, 2, 14)),
]

@pytest.mark.parametrize("text,ymd", _BARE)
def test_bare_holiday(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)

@pytest.mark.parametrize("text,ymd", [
    ('nästa juldagen', (2017, 12, 25)),
    ('förra juldagen', (2016, 12, 25)),
])
def test_next_last(text, ymd):
    assert start(text) == AstroDate(*ymd)

def test_explicit_year():
    assert start('påsk 2020') == AstroDate(*(2020, 4, 12))

@pytest.mark.parametrize("text", ['ett möte om budgeten', 'priset på ris steg'])
def test_no_holiday_no_match(text):
    nomatch(text)
