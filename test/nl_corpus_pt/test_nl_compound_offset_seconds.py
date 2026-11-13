# -*- coding: utf-8 -*-
"""A compound offset that ends in seconds, pt.

The phrase counts minutes or hours and then seconds.  The offset composes
both parts and lands on the second.  Before, the anchored shift had no
second unit and the phrase raised ValueError.  Every expected value is the
anchor, Tuesday 2017-06-27 13:04, moved by the stated hours, minutes and
seconds, computed here and not read back from the engine.  The span is one
second wide, the finest unit the phrase names.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, parse


@pytest.mark.parametrize("text,offset", [
    ("daqui a 5 minutos e 30 segundos", timedelta(minutes=5, seconds=30)),
    ("daqui a 2 horas e 10 segundos", timedelta(hours=2, seconds=10)),
    ("em 1 hora e 30 segundos", timedelta(hours=1, seconds=30)),
    ("há 10 minutos e 5 segundos", -timedelta(minutes=10, seconds=5)),
])
def test_compound_offset_with_seconds(text, offset):
    span, rest = parse(text)
    assert span.start == ad(ANCHOR + offset)
    assert span.end == ad(ANCHOR + offset + timedelta(seconds=1))
    assert rest == ""
