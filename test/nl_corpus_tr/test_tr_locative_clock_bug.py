# -*- coding: utf-8 -*-
"""BUG: the locative-inflected bare hour "saat üçte" ("at three o'clock")
does not parse.

Turkish marks "at <hour>" with the locative case on the numeral: "saat üçte"
(= at 3), "saat dokuzda" (= at 9).  These are the everyday way to state a
clock time, yet on ``dev`` they return no span at all -- the locative suffix
(-te/-de/-ta/-da, per vowel harmony) is not stripped before the hour is read.
The uninflected "saat üç" reads correctly (see test_nl_clock.py), which pins
this to the locative morphology alone.

Strict xfail: the day the suffix is handled, this flips to a failure and the
marker must be removed.  Anchor: 2017-06-27 13:04.
"""
from datetime import datetime

import pytest

from ._corpus import parse

A = datetime(2017, 6, 27, 13, 4)

# (surface, expected hour) once the locative is handled.
_LOCATIVE = [
    ("saat üçte", 3), ("saat dörtte", 4), ("saat beşte", 5),
    ("saat altıda", 6), ("saat yedide", 7), ("saat sekizde", 8),
    ("saat dokuzda", 9), ("saat onda", 10), ("saat on birde", 11),
]


@pytest.mark.xfail(strict=True, reason="locative-case hour (-te/-de) not parsed")
@pytest.mark.parametrize("text,h", _LOCATIVE)
def test_locative_hour(text, h):
    r = parse(text, A)
    assert r is not None, f"{text!r} did not parse"
    assert r[0].start.hour == h
