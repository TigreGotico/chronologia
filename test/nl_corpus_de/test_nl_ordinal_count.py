"""Ordinal counting from the anchor (feature 2), German.

Only the cross-linguistically clean member -- "das wochenende nach dem
nächsten" (the weekend after next) -- is carried into German here.  The
"N weekdays from now" idiom has no clean German equivalent (declined plural
"Freitagen" after "in", not a trailing "from now" marker), so it is left to
a later pass rather than forced into unnatural sentences.  Anchor
2017-06-27 (Dienstag).
"""
from datetime import timedelta

import pytest

from ._corpus import span, nomatch


def test_weekend_after_next():
    s = span("das wochenende nach dem nächsten")
    assert (s.start.year, s.start.month, s.start.day) == (2017, 7, 15)
    assert s.width == timedelta(days=2)


@pytest.mark.parametrize("text", [
    "3 freitage",                       # declined plural, no count idiom
    "nach dem nächsten",                # no weekend word to count from
])
def test_no_count_no_match(text):
    nomatch(text)
