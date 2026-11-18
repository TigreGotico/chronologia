"""Polish half hours with "w pół do" written apart.

The dictionary writes the half hour solid: "wpół do dziewiątej" is 8:30
(Słownik języka polskiego PWN, "wpół").  Writers and speech recognisers also
give the spaced "w pół do".  "do" in it is no "until": "spotkajmy się o wpół
do ósmej wieczorem" is 19:30, not an open span that ends at 20:00.  The
anchor is Tuesday 2017-06-27 13:04; a lone clock hour takes the next
twelve-hour reading at or after it.
"""
from datetime import datetime

import pytest

from ._corpus import ad, nomatch, start


@pytest.mark.parametrize("text,expected", [
    ("w pół do ósmej", datetime(2017, 6, 27, 19, 30)),
    ("o w pół do ósmej", datetime(2017, 6, 27, 19, 30)),
    ("w pół do pierwszej", datetime(2017, 6, 28, 0, 30)),
    ("w pół do ósmej rano", datetime(2017, 6, 28, 7, 30)),
    ("spotkajmy się w pół do ósmej wieczorem", datetime(2017, 6, 27, 19, 30)),
    ("spotkajmy się o wpół do ósmej wieczorem", datetime(2017, 6, 27, 19, 30)),
    ("spotkajmy się wpół do ósmej wieczorem", datetime(2017, 6, 27, 19, 30)),
])
def test_half_hour(text, expected):
    assert start(text) == ad(expected)


def test_half_way_is_no_clock():
    nomatch("w pół drogi do domu")
