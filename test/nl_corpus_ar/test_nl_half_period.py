# -*- coding: utf-8 -*-
"""Calendar halves (ar): "first/second half of <year>" splits the year at July 1.
half_period inherits the shared BASE_GRAMMAR and this locale supplies the
article-prefixed period noun (marker_half النصف) plus the postposed-ordinal order
("النصف الأول من 2020"). The ORDINAL الأول/الثاني DELIBERATELY does NOT fold to a
digit: it is the ordinal component of the Levantine month names (تشرين الأول =
October, كانون الثاني = January), so folding it would erase the month
(numfold_semitic.fold_ar exclude=("الأول","الثاني")). Spelled first/second half is
therefore the same documented, principled limitation as the spelled Arabic Q1/Q2 --
tracked as xfail for a separate numfold PR."""
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import parse

_CASES = [
    ("النصف الأول من 2020", 2020, 1, 1, 2020, 7, 1),
    ("النصف الثاني من 2020", 2020, 7, 1, 2021, 1, 1),
]

@pytest.mark.xfail(reason="الأول/الثاني withheld from the ordinal fold (Levantine "
                          "month-name collision); spelled Arabic first/second half "
                          "cannot bind NUM, same as spelled Q1/Q2", strict=True)
@pytest.mark.parametrize("text,sy,sm,sd,ey,em,ed", _CASES)
def test_half_period_ar(text, sy, sm, sd, ey, em, ed):
    r = parse(text)
    assert r is not None
    s, e = r[0].start, r[0].end
    assert s == AstroDate(sy, sm, sd)
    assert e == AstroDate(ey, em, ed)
