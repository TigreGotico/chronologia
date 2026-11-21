# -*- coding: utf-8 -*-
"""Aragonese "quarto trimestre" (4th quarter).

"quarto" (the qu- spelling, 4th) is spelled like the clock/duration fraction
word "quarto" ("un quarto de hora" = 15 min, see test_nl_duration.py).  The
numtag Aragonese lexicon lists "quarto" as an ordinal of value 4, beside the
ordinal "cuatreno"; its denominator for 4 is "cuarto".

"quarto" is an ordinal in the frames before the quarter noun "trimestre" and
after a definite article ("o quarto trimestre"), while the "cuarto"
quarter-hour fraction stays a fraction.  The ordinal "cuatreno" works the
same way (test_nl_quarter.py; feminine "cuatrena" in test_nl_ordinal_week.py,
citing Gramatica Basica de l'Aragones sec. 8.1.2).

Gold (independent arithmetic): quarter N spans calendar months [3N-2..3N];
Q4 = October-December.  The corpus anchor is 2018-06-05 13:04 (_corpus.ANCHOR),
so "o quarto trimestre" without a year defaults to the anchor year 2018,
matching the no-year quarter_ref behaviour of "o tercer trimestre" in
test_nl_quarter.py."""
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end


@pytest.mark.parametrize("text,sy,sm,ey,em", [
    ("o quarto trimestre", 2018, 10, 2019, 1),
    ("o quarto trimestre de 2018", 2018, 10, 2019, 1),
    ("quarto trimestre de 2018", 2018, 10, 2019, 1),
])
def test_quarto_trimestre(text, sy, sm, ey, em):
    s, e = start_end(text)
    assert s == AstroDate(sy, sm, 1)
    assert e == AstroDate(ey, em, 1)
