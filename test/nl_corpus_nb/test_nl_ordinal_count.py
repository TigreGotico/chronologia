"""Ordinal counting from the anchor (nb): "the weekend after next" -- the
Saturday/Sunday two weeks past the anchor's week. Anchor 2017-06-27 (Tue)."""
from datetime import timedelta
import pytest
from ._corpus import span, nomatch

def test_weekend_after_next():
    s = span('helgen etter den neste')
    assert (s.start.year, s.start.month, s.start.day) == (2017, 7, 15)
    assert s.width == timedelta(days=2)

@pytest.mark.parametrize("text", ['3 fredager', 'etter den neste'])
def test_no_count_no_match(text):
    nomatch(text)
