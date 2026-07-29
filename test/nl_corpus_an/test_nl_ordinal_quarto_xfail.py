# -*- coding: utf-8 -*-
"""KNOWN BUG (strict-xfail): "quarto" (4th) collides with the clock/duration
fraction word "quarto" ("un quarto de hora" = 15 min, see test_nl_duration.py)
and does not fold to the ordinal 4 the way "primer"/"tercer" do (fold_an's
explicit apocope table only covers 1 and 3, see chronologia/extract/numfold.py).
The working masculine ordinal for "4th quarter" is "cuatreno" (already covered,
test_nl_quarter.py uses the parallel feminine "cuatrena" for "the 4th week of
a month" in test_nl_ordinal_week.py, citing Gramatica Basica de l'Aragonés
sec. 8.1.2).

    o quarto trimestre            -> None (expected: Q4 of the anchor year)
    o quarto trimestre de 2018    -> matches, but swallows the whole marker
                                      "o quarto trimestre de" and returns the
                                      *entire year* 2018 instead of Q4 2018

Gold (independent arithmetic): quarter N spans calendar months [3N-2..3N];
Q4 = October-December.  Anchor 2017-06-27 13:04, so "o quarto trimestre"
without a year defaults to the anchor year (matching the no-year quarter_ref
behaviour already exercised by "o tercer trimestre" -> Q3 2017 in
test_nl_quarter.py).

Marked xfail(strict) so the day fold_an learns "quarto" as ordinal 4, this
flips to a failure and the assertions become live regression guards.

For the human reviewer (Juanpabl): confirm "quarto" is in fact the idiomatic
masculine ordinal 4th before "trimestre" (as opposed to "cuatreno" always
being preferred there), since "quarto" is independently attested as the
quarter-hour fraction word."""
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end


@pytest.mark.xfail(strict=True, reason="'quarto' ordinal-4 not folded; collides with the quarter-hour fraction word")
@pytest.mark.parametrize("text,sy,sm,ey,em", [
    ("o quarto trimestre", 2017, 10, 2018, 1),
    ("o quarto trimestre de 2018", 2018, 10, 2019, 1),
])
def test_quarto_trimestre(text, sy, sm, ey, em):
    s, e = start_end(text)
    assert s == AstroDate(sy, sm, 1)
    assert e == AstroDate(ey, em, 1)
