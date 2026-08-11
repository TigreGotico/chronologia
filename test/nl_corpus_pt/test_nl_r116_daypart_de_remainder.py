# -*- coding: utf-8 -*-
"""R116 (pt): "a manhã de depois de amanhã" -- a day-part composing with an
adjacent anchoring date must consume the connector between them ("de"), not
strand it in the remainder.  Mirrors test_nl_r116_daypart_of_remainder.py in
the en corpus; see that file's docstring for the shared-layer root cause.

Gold day-part bands are the pt row of chronologia/dayparts.py's CLDR-sourced
table: manhã ``[06:00, 12:00)``, tarde ``[12:00, 19:00)`` -- never read back
from the parser.
"""
from datetime import timedelta

from ._corpus import ANCHOR, AstroDate, parse


def test_manha_de_depois_de_amanha_consumes_connector():
    r = parse('a manhã de depois de amanhã')
    assert r is not None
    day = ANCHOR + timedelta(days=2)                # "depois de amanhã"
    assert r.span.start == AstroDate(day.year, day.month, day.day, 6, 0, 0)
    assert r.span.end == AstroDate(day.year, day.month, day.day, 12, 0, 0)
    assert r.remainder == ""


def test_tarde_de_sexta_que_vem_consumes_connector():
    r = parse('a tarde de sexta que vem')
    assert r is not None
    day = ANCHOR + timedelta(days=3)                # Tue -> next Friday
    assert r.span.start == AstroDate(day.year, day.month, day.day, 12, 0, 0)
    assert r.span.end == AstroDate(day.year, day.month, day.day, 19, 0, 0)
    assert r.remainder == ""
