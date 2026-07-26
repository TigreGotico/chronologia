# -*- coding: utf-8 -*-
"""Russian spelled-ordinal day-of-month in the NEUTER NOMINATIVE
("пятнадцатое апреля" = the fifteenth of April), the bare nominative form that
agrees with the elided neuter noun число.  #273 folded only the genitive and
feminine forms, so the neuter nominative stranded and the whole month was
returned -- a silent wrong answer.  The neuter must now fold to the exact day.
"""
from datetime import datetime

import pytest

from ._corpus import ad, start


@pytest.mark.parametrize("ordinal,d", [
    ("первое", 1),
    ("пятое", 5),
    ("одиннадцатое", 11),
    ("пятнадцатое", 15),
    ("двадцать первое", 21),
    ("двадцать третье", 23),
    ("тридцатое", 30),
])
def test_neuter_ordinal_of_april(ordinal, d):
    assert start(f"{ordinal} апреля") == ad(datetime(2018, 4, d))


def test_neuter_thirty_first_of_march():
    assert start("тридцать первое марта") == ad(datetime(2018, 3, 31))
