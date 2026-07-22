"""Ordinal counting from the anchor (nl): "the weekend after next" -- the
Saturday/Sunday two weeks past the anchor's week. Anchor 2017-06-27 (Tue)."""
from datetime import timedelta
import pytest
from ._corpus import span, nomatch

def test_weekend_after_next():
    s = span('het weekend na het volgende')
    assert (s.start.year, s.start.month, s.start.day) == (2017, 7, 15)
    assert s.width == timedelta(days=2)

@pytest.mark.parametrize("text", ['3 vrijdagen', 'na het volgende'])
def test_no_count_no_match(text):
    nomatch(text)
