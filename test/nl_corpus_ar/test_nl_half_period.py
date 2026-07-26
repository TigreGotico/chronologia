# -*- coding: utf-8 -*-
"""Calendar halves (ar): "first/second half of <year>" splits the year at July 1.
half_period inherits the shared BASE_GRAMMAR and this locale supplies the
article-prefixed period noun (marker_half النصف) plus the postposed-ordinal order
("النصف الأول من 2020"). الأول/الثاني are now folded to the ordinal by
numfold_semitic._ar_month_ordinal_license, which applies Rule A (confirmed by
native speaker athmanemokraoui, #268): they are the ordinal EXCEPT immediately
after a Levantine month prefix (تشرين/كانون/جمادى/ربيع), where they form the
month name (تشرين الأول = October). So spelled first/second half now binds."""
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import parse

_CASES = [
    ("النصف الأول من 2020", 2020, 1, 1, 2020, 7, 1),
    ("النصف الثاني من 2020", 2020, 7, 1, 2021, 1, 1),
]

@pytest.mark.parametrize("text,sy,sm,sd,ey,em,ed", _CASES)
def test_half_period_ar(text, sy, sm, sd, ey, em, ed):
    r = parse(text)
    assert r is not None
    s, e = r[0].start, r[0].end
    assert s == AstroDate(sy, sm, sd)
    assert e == AstroDate(ey, em, ed)
