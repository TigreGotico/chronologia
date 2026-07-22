"""Business days (da): "N hverdage" counts forward over weekdays only
(holiday-blind without a jurisdiction). Anchor Tue 2017-06-27; the weekend
Sat/Sun is skipped. Counts derived by hand."""
from datetime import timedelta
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start, span, nomatch

_CASES = [('1 hverdage', 2017, 6, 28), ('2 hverdage', 2017, 6, 29), ('3 hverdage', 2017, 6, 30), ('4 hverdage', 2017, 7, 3), ('5 hverdage', 2017, 7, 4)]

@pytest.mark.parametrize("text,y,m,dd", _CASES)
def test_business_count(text, y, m, dd):
    assert start(text) == AstroDate(y, m, dd)

def test_next_business_day():
    assert start('næste hverdag') == AstroDate(2017, 6, 28)

def test_one_day_wide():
    assert span(f"3 hverdage").width == timedelta(days=1)

@pytest.mark.parametrize("text", ['som sædvanligt', 'alt normalt'])
def test_not_business(text):
    nomatch(text)
