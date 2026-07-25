# -*- coding: utf-8 -*-
"""Anchored arithmetic (hu): a signed unit offset on a resolved reference date,
with the direction marked by a trailing postposition -- "előtt" (before) /
"után" (after) -- and the "N UNIT" pre-amble leading the date:
"N nappal <date> előtt".  Anchor 2017-06-27; április 5. resolves forward to
2018-04-05.  Every expected date hand-derived.
"""
from datetime import date

import pytest

from ._corpus import AstroDate, parse, start


def _ad(d):
    return AstroDate(d.year, d.month, d.day)


@pytest.mark.parametrize("text,expected", [
    ("3 nappal április 5. előtt", date(2018, 4, 2)),
    ("3 nappal április 5. után", date(2018, 4, 8)),
])
def test_postfix_offset(text, expected):
    assert start(text) == _ad(expected)
    assert parse(text).remainder == ""
