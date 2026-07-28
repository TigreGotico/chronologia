"""nb: movable Christian feasts across many years, gold by computus.

Every expected date is derived by the anonymous-Gauss ``easter()`` in
``_corpus`` plus a fixed offset -- never read back from the engine:

    Palmesondag         Easter - 7    Langfredag        Easter - 2
    Forste paskedag     Easter        Andre paskedag    Easter + 1
    Kristi himmelfart   Easter + 39   Forste pinsedag   Easter + 49
    Andre pinsedag      Easter + 50

The engine resolves the explicit-year form to a single civil day; we assert
both endpoints of that one-day span.
"""
from datetime import timedelta

import pytest

from ._corpus import AstroDate, easter, start, span


def _cases():
    out = []
    for y in range(2018, 2031):
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
def test_movable_feast(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)
    assert span(text).width == timedelta(days=1)
