# -*- coding: utf-8 -*-
"""R116 (fr): "le matin d apres demain" -- a day-part composing with an
adjacent anchoring date must consume the connector between them ("d'"), not
strand it in the remainder.  Mirrors test_nl_r116_daypart_of_remainder.py in
the en corpus; see that file's docstring for the shared-layer root cause.

Gold day-part bands are the fr row of chronologia/dayparts.py's CLDR-sourced
table: matin ``[04:00, 12:00)`` -- never read back from the parser.
"""
from datetime import timedelta

from ._corpus import ANCHOR, AstroDate, parse


def test_matin_d_apres_demain_consumes_connector():
    r = parse('le matin d apres demain')
    assert r is not None
    day = ANCHOR + timedelta(days=2)                # "apres demain"
    assert r.span.start == AstroDate(day.year, day.month, day.day, 4, 0, 0)
    assert r.span.end == AstroDate(day.year, day.month, day.day, 12, 0, 0)
    assert r.remainder == ""


def test_matin_de_vendredi_prochain_consumes_connector():
    r = parse('le matin de vendredi prochain')
    assert r is not None
    day = ANCHOR + timedelta(days=3)                # Tue -> next Friday
    assert r.span.start == AstroDate(day.year, day.month, day.day, 4, 0, 0)
    assert r.span.end == AstroDate(day.year, day.month, day.day, 12, 0, 0)
    assert r.remainder == ""
