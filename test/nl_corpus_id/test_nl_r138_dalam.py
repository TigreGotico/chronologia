# -*- coding: utf-8 -*-
"""Regression for R138: id 'dalam <duration>' (in <duration>) preposed offset.

Before the fix, Indonesian had no preposed 'dalam' (in) marker at all, so
'dalam 3 hari' silently failed to parse even though the postposed 'lagi'
sibling and the 'yang lalu' ago sibling both worked.

Anchor is 2026-07-15 12:00 (Wednesday), from ``_corpus.ANCHOR``.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, start

A = ANCHOR


@pytest.mark.parametrize("text,days", [
    ("dalam 3 hari", 3), ("dalam 5 hari", 5),
])
def test_id_dalam_day_offsets(text, days):
    exp = (A + timedelta(days=days)).date()
    assert (start(text).month, start(text).day) == (exp.month, exp.day)


@pytest.mark.parametrize("text,days", [
    ("3 hari lagi", 3), ("3 hari yang lalu", -3),
])
def test_id_lagi_lalu_controls_unchanged(text, days):
    exp = (A + timedelta(days=days)).date()
    assert (start(text).month, start(text).day) == (exp.month, exp.day)
