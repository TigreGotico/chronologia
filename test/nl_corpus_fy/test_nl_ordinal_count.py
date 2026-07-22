"""Ordinal counting from the anchor (fy): "the weekend after next" -- the
Saturday/Sunday two weeks past the anchor's week. Anchor 2017-06-27 (Tue)."""
from datetime import timedelta
import pytest
from ._corpus import span, nomatch

def test_weekend_after_next():
    s = span('it wykein nei it folgjende')
    assert (s.start.year, s.start.month, s.start.day) == (2017, 7, 15)
    assert s.width == timedelta(days=2)

@pytest.mark.parametrize("text", ['3 freeden', 'nei it folgjende'])
def test_no_count_no_match(text):
    nomatch(text)
