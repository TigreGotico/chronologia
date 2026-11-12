# -*- coding: utf-8 -*-
"""A habitual weekday reads as the next such day, pt.

"à sexta-feira" names a habit (Svobodová 2016, p. 25).  The caller has no
recurrence type and wants a date, so the habit reads as the next occurrence,
and its article belongs to the date.  Anchor Tuesday 2017-06-27: the next
Friday is 30 June, Saturday 1 July, Sunday 2 July.
"""
import pytest

from ._corpus import parse, start_end, AstroDate


@pytest.mark.parametrize("text,ymd,rest", [
    ("ao sábado", (2017, 7, 1), ""),
    ("à sexta", (2017, 6, 30), ""),
    ("às sextas-feiras", (2017, 6, 30), ""),
    ("ao domingo vou à missa", (2017, 7, 2), "vou à missa"),
])
def test_habitual_weekday_is_the_next_one(text, ymd, rest):
    s, e = start_end(text)
    assert s == AstroDate(*ymd)
    assert (e - s).days == 1
    assert parse(text)[1] == rest
