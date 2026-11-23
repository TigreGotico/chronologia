"""Kabyle numbers read through numtag.

A compound day of the month ("waḥed u ɛecrin", twenty-one) reads whole, not
as its last word.  Every expected value is a ``datetime``.
"""
from datetime import datetime

import pytest

from ._corpus import ad, start


@pytest.mark.parametrize("text,day", [
    ("waḥed u ɛecrin mayyu 2025", 21),
    ("waḥed u tlatin mayyu 2025", 31),
    ("semmus mayyu 2025", 5),
])
def test_spelled_day(text, day):
    assert start(text) == ad(datetime(2025, 5, day))
