# -*- coding: utf-8 -*-
"""Anchored arithmetic (eu): a signed unit offset on a resolved reference date,
with the direction marked by a trailing word -- "lehenago" (before) /
"geroago" (after) -- and the comparative "baino N UNIT" pre-amble trailing the
date: "<date> baino N egun lehenago".  Anchor 2017-06-27; apirilaren 5a
resolves forward to 2018-04-05.  Every expected date hand-derived.
"""
from datetime import date

import pytest

from ._corpus import AstroDate, parse, start


def _ad(d):
    return AstroDate(d.year, d.month, d.day)


@pytest.mark.parametrize("text,expected", [
    ("apirilaren 5a baino 3 egun lehenago", date(2018, 4, 2)),
    ("apirilaren 5a baino 3 egun geroago", date(2018, 4, 8)),
])
def test_postfix_offset(text, expected):
    assert start(text) == _ad(expected)
    assert parse(text).remainder == ""
