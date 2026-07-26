"""Swedish spelled-ordinal day-of-month ("femtonde april" = the fifteenth of
April).  ovos-number-parser returns False for these ordinals, so chronologia
owns them locally (inverting ``pronounce_ordinal_sv``); the ordinal must fold
to the exact day, not strand and leave the whole month.
"""
from datetime import datetime

import pytest

from ._corpus import ad, start


@pytest.mark.parametrize("ordinal,d", [
    ("första", 1),
    ("femte", 5),
    ("elfte", 11),
    ("femtonde", 15),
    ("tjugoförsta", 21),
    ("tjugotredje", 23),
    ("trettionde", 30),
])
def test_spelled_ordinal_of_april(ordinal, d):
    assert start(f"{ordinal} april") == ad(datetime(2018, 4, d))


def test_spelled_thirty_first_of_march():
    assert start("trettioförsta mars") == ad(datetime(2018, 3, 31))
