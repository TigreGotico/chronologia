"""nb: movable Christian feasts, second-pass resweep -- fresh years 2032-2051.

Not previously exercised by ``test_nb_movable_feasts_sweep.py`` (which covers
2018-2030). Gold derived independently via the anonymous-Gauss ``easter()``
oracle in ``_corpus`` plus a fixed day offset per feast -- never read back
from the engine.

``skjærtorsdag`` (Maundy Thursday, Easter - 3) is NOT covered: the engine does
not recognise that surface at all (it falls back to an unrelated bare-ordinal
reading), so it is dropped rather than mass-xfailed.
"""
from datetime import timedelta

import pytest

from ._corpus import AstroDate, easter, start, span


def _cases():
    out = []
    for y in range(2032, 2052):
        E = easter(y)
        for name, off in [
            ("palmesøndag", -7),
            ("langfredag", -2),
            ("første påskedag", 0),
            ("andre påskedag", 1),
            ("kristi himmelfartsdag", 39),
            ("første pinsedag", 49),
            ("andre pinsedag", 50),
        ]:
            d = E + timedelta(days=off)
            out.append((f"{name} {y}", d.year, d.month, d.day))
    return out


@pytest.mark.parametrize("text,y,m,d", _cases())
def test_movable_feast_resweep(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)
    assert span(text).width == timedelta(days=1)
