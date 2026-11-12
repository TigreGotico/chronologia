# -*- coding: utf-8 -*-
"""A habitual weekday reads as the next such day, gl.

"Os luns estudio" is the habit (EOI Lugo, "O artigo", D) Usos do artigo
determinado, p. 3).  Ruling 5 of 2026-11-12 (knowledge/wiki/audits/
chronologia/disagreement-classes.md) reads it as the next occurrence, and
its article belongs to the date.  Anchor Tuesday 2017-06-27: the next Monday
is 3 July, the next Friday 30 June.
"""
import pytest

from ._corpus import parse, start_end, AstroDate


@pytest.mark.parametrize("text,ymd,rest", [
    ("os luns", (2017, 7, 3), ""),
    ("os venres estudo", (2017, 6, 30), "estudo"),
])
def test_habitual_weekday_is_the_next_one(text, ymd, rest):
    s, e = start_end(text)
    assert s == AstroDate(*ymd)
    assert (e - s).days == 1
    assert parse(text)[1] == rest
