"""Holiday references (da) (``holiday_ref``).

Anchor 2017-06-27. Western computus (independent table): Easter 2017 = 16 Apr,
2018 = 1 Apr, 2020 = 12 Apr. Bare rule = next occurrence on or after the anchor.
Every expected date derived by hand from published civil/computus tables."""
from datetime import timedelta
import pytest
from ._corpus import ANCHOR, AstroDate, parse, span, start, nomatch

_BARE = [
    ('juledag', (2017, 12, 25)),
    ('juleaften', (2017, 12, 24)),
    ('nytårsdag', (2018, 1, 1)),
    ('nytårsaften', (2017, 12, 31)),
    ('helligtrekonger', (2018, 1, 6)),
    ('allehelgen', (2017, 11, 1)),
    ('påske', (2018, 4, 1)),
    ('langfredag', (2018, 3, 30)),
    ('påskemandag', (2018, 4, 2)),
    ('pinse', (2018, 5, 20)),
    ('halloween', (2017, 10, 31)),
    ('valentinsdag', (2018, 2, 14)),
]

@pytest.mark.parametrize("text,ymd", _BARE)
def test_bare_holiday(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)

@pytest.mark.parametrize("text,ymd", [
    ('næste juledag', (2017, 12, 25)),
    ('sidste juledag', (2016, 12, 25)),
])
def test_next_last(text, ymd):
    assert start(text) == AstroDate(*ymd)

def test_explicit_year():
    assert start('påske 2020') == AstroDate(*(2020, 4, 12))

@pytest.mark.parametrize("text", ['et møde om budgettet', 'prisen på ris steg'])
def test_no_holiday_no_match(text):
    nomatch(text)
