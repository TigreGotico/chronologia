# -*- coding: utf-8 -*-
"""Scoped-ordinal "Nth century" for sk, gained for FREE from the shared base
grammar (Slovak declared no scoped_ordinal on dev).  "3. storočie" is the
3rd century = [200, 300).  Expected bounds from calendar arithmetic."""

from ._corpus import parse, start_end


def test_tretie_storocie():
    for phrase in ("3. storočie", "3 storočie"):
        s, e = start_end(phrase)
        assert (s.year, e.year) == (200, 300), phrase
        assert parse(phrase)[1] == "", phrase
