# -*- coding: utf-8 -*-
"""R116 (es): "la mañana de pasado mañana" -- a day-part composing with an
adjacent anchoring date must consume the connector between them ("de"), not
strand it in the remainder.  Mirrors test_nl_r116_daypart_of_remainder.py in
the en corpus; see that file's docstring for the shared-layer root cause.

Gold day-part bands are the es row of chronologia/dayparts.py's CLDR-sourced
table: mañana ``[06:00, 12:00)``, tarde ``[12:00, 20:00)`` -- never read back
from the parser.
"""
from datetime import timedelta

from ._corpus import ANCHOR, AstroDate, parse


def test_manana_de_pasado_manana_consumes_connector():
    r = parse('la mañana de pasado mañana')
    assert r is not None
    day = ANCHOR + timedelta(days=2)                # "pasado mañana"
    assert r.span.start == AstroDate(day.year, day.month, day.day, 6, 0, 0)
    assert r.span.end == AstroDate(day.year, day.month, day.day, 12, 0, 0)
    assert r.remainder == ""


def test_tarde_del_proximo_viernes_consumes_connector():
    r = parse('la tarde del próximo viernes')
    assert r is not None
    day = ANCHOR + timedelta(days=3)                # Tue -> next Friday
    assert r.span.start == AstroDate(day.year, day.month, day.day, 12, 0, 0)
    assert r.span.end == AstroDate(day.year, day.month, day.day, 20, 0, 0)
    assert r.remainder == ""
