# -*- coding: utf-8 -*-
"""The article that opens a date belongs to the date, gl.

The definite article is required to name one specific weekday: "É
obrigatorio se van en plural ou se quere precisar o día: Os luns estudio.
Quedamos o venres." (EOI Lugo, "O artigo", D) Usos do artigo determinado,
p. 3).  "o luns" is that day, and "o" left in the remainder strands half of
it.  Anchor 2017-06-27, a martes, 13:04; dates by hand.
"""
import pytest

from ._corpus import parse, start_end, AstroDate


@pytest.mark.parametrize("text,ymd,rest", [
    ("o luns", (2017, 7, 3), ""),
    ("quedamos o venres", (2017, 6, 30), "quedamos"),
    ("reunión o luns", (2017, 7, 3), "reunión"),
    ("o luns 3 de xullo", (2017, 7, 3), ""),
])
def test_article_is_part_of_the_date(text, ymd, rest):
    s, e = start_end(text)
    assert s == AstroDate(*ymd)
    assert (e - s).days == 1
    assert parse(text)[1] == rest
