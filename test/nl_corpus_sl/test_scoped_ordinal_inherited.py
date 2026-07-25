# -*- coding: utf-8 -*-
"""Scoped-ordinal "Nth century" for sl, gained for FREE from the shared base
grammar (Slovenian declared no scoped_ordinal on dev).  "3. stoletje" is the
3rd century = [200, 300).  Expected bounds from calendar arithmetic."""

from ._corpus import parse, start_end


def test_tretje_stoletje():
    for phrase in ("3. stoletje", "3 stoletje"):
        s, e = start_end(phrase)
        assert (s.year, e.year) == (200, 300), phrase
        assert parse(phrase)[1] == "", phrase
