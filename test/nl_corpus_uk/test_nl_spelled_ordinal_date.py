# -*- coding: utf-8 -*-
"""Ukrainian spelled-ordinal day-of-month in the NEUTER NOMINATIVE
("п'ятнадцяте квітня" = the fifteenth of April), the bare nominative form that
agrees with the elided neuter noun число.  Same class as Russian: the neuter
nominative was not folded and the whole month was returned; it must now fold to
the exact day.
"""
from datetime import datetime

import pytest

from ._corpus import ad, start


@pytest.mark.parametrize("ordinal,d", [
    ("перше", 1),
    ("п'яте", 5),
    ("одинадцяте", 11),
    ("п'ятнадцяте", 15),
    ("двадцять перше", 21),
    ("двадцять третє", 23),
    ("тридцяте", 30),
])
def test_neuter_ordinal_of_april(ordinal, d):
    assert start(f"{ordinal} квітня") == ad(datetime(2018, 4, d))


def test_neuter_thirty_first_of_march():
    assert start("тридцять перше березня") == ad(datetime(2018, 3, 31))
