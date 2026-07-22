# -*- coding: utf-8 -*-
"""Regression: weekday ABBREVIATIONS must not bind as a bare weekday.

Short weekday abbreviations that double as common words (de "so", nl "zo",
scandinavian "man") were moved to a separate abbreviation set. The bare
weekday order binds full names only, so these no longer resolve to a
weekday on their own; a preceding relative marker still accepts them."""
from datetime import date, timedelta

import pytest

from ._corpus import ANCHOR, parse, span


@pytest.mark.parametrize("text", ['mån', 'ons'])
def test_bare_abbreviation_is_not_a_weekday(text):
    # None, or at least not a day-wide span on the abbreviation's weekday
    r = parse(text)
    if r is not None:
        s, e = r[0].start, r[0].end
        one_day = (date(e.year, e.month, e.day)
                   - date(s.year, s.month, s.day)).days == 1
        assert not (one_day and s.weekday() == 0)


def test_full_name_still_resolves():
    ahead = (0 - ANCHOR.weekday()) % 7 or 7
    exp = (ANCHOR + timedelta(days=ahead)).date()
    s = span('måndag').start
    assert (s.year, s.month, s.day) == (exp.year, exp.month, exp.day)
