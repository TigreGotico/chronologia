# -*- coding: utf-8 -*-
"""Arabic spelled-ordinal day-of-month ("الخامس عشر من أبريل" = the fifteenth
of April).  The ordinal TEEN is written as two words -- an inflected unit
ordinal followed by the teen word عشر -- so the unit ordinal used to fold to
its UNIT value (الخامس -> 5) while عشر folded to 10 on its own, binding the
wrong day (April 5).  The two-word ordinal teen must now fold to 11..19.

Deferred (documented): الأول/الثاني (1st/2nd) are withheld because they are the
Levantine month-name components (تشرين الأول, كانون الثاني); the compound tens
21..31 (الحادي والعشرون ...) are out of the single/teen fold's scope.
"""
from datetime import datetime

import pytest

from ._corpus import ad, start


@pytest.mark.parametrize("ordinal,d", [
    ("الثالث", 3),
    ("الخامس", 5),
    ("التاسع", 9),
    ("الحادي عشر", 11),
    ("الخامس عشر", 15),
    ("التاسع عشر", 19),
])
def test_spelled_ordinal_of_april(ordinal, d):
    assert start(f"{ordinal} من أبريل") == ad(datetime(2018, 4, d))
