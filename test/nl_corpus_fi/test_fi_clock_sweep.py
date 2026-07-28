"""Finnish "kello <spelled hour>" and "kello <digit>" whole-hour times.

The clock resolves to the next occurrence of that hour after the anchor
(2017-06-27 13:04): hours <= 13 roll to the following day, 14..23 stay on the
anchor day.  Oracle is independent arithmetic.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, start

_WORD = {
    "yksi": 1, "kaksi": 2, "kolme": 3, "neljä": 4, "viisi": 5, "kuusi": 6,
    "seitsemän": 7, "kahdeksan": 8, "yhdeksän": 9, "kymmenen": 10,
    "yksitoista": 11, "kaksitoista": 12,
}


def _next_hour(h):
    cand = ANCHOR.replace(hour=h, minute=0, second=0, microsecond=0)
    if cand <= ANCHOR:
        cand += timedelta(days=1)
    return ad(cand)


@pytest.mark.parametrize("word,h", list(_WORD.items()))
def test_kello_spelled(word, h):
    assert start(f"kello {word}") == _next_hour(h)


@pytest.mark.parametrize("h", list(range(0, 24)))
def test_kello_digit(h):
    assert start(f"kello {h}") == _next_hour(h)
