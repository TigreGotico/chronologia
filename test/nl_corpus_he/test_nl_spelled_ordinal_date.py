# -*- coding: utf-8 -*-
"""Hebrew spelled-ordinal day-of-month ("החמישה עשר באפריל" = the fifteenth of
April).  The definite ordinal TEEN is two words -- a definite unit word
followed by the teen word עשר -- so the definite unit failed to fold while עשר
folded to 10 on its own, binding the wrong day (April 10).  The two-word
ordinal teen must now fold to 11..19.

Deferred (documented): the unit ordinals 1..10 (ראשון/שני/שלישי ...) are the
Hebrew weekday names and are withheld from the number fold (folding them would
destroy weekday parsing); the compound tens 21..31 are out of scope.
"""
from datetime import datetime

import pytest

from ._corpus import ad, start


@pytest.mark.parametrize("ordinal,d", [
    ("האחד עשר", 11),
    ("השנים עשר", 12),
    ("החמישה עשר", 15),
    ("השבעה עשר", 17),
    ("התשעה עשר", 19),
])
def test_spelled_ordinal_of_april(ordinal, d):
    assert start(f"{ordinal} באפריל") == ad(datetime(2018, 4, d))
