# -*- coding: utf-8 -*-
"""Calendar quarters (an).  Quarter N spans months [3N-2 .. 3N]; edges
hand-derived (anchor 2018-06-05, in Q2).

Aragonese uses the ``T3`` short form and a digit before the head noun
(``3 trimestre`` / ``o 3 trimestre``).  The spoken spelled ordinal
``o tercer trimestre`` needs Aragonese ordinals folded to a number, which
``fold_an`` does not yet do -- out of scope (engine follow-up), covered by
``test_spelled_ordinal_pending``.  A relative marker (``que viene`` next /
``pasau`` last / ``iste`` this) shifts by whole quarters.

Per Juanpabl's orthography the month/quarter surfaces stay lowercase and no
``y`` conjunction appears."""
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end, parse

_CASES = [
    ('T3', 2018, 7, 2018, 10),
    ('3 trimestre', 2018, 7, 2018, 10),
    ('o 3 trimestre', 2018, 7, 2018, 10),
    ('T1 2020', 2020, 1, 2020, 4),
    ('T3 2026', 2026, 7, 2026, 10),
    ('2 trimestre', 2018, 4, 2018, 7),
    ('trimestre que viene', 2018, 7, 2018, 10),
    ('iste trimestre', 2018, 4, 2018, 7),
    ('trimestre pasau', 2018, 1, 2018, 4),
]


@pytest.mark.parametrize("text,sy,sm,ey,em", _CASES)
def test_quarter(text, sy, sm, ey, em):
    s, e = start_end(text)
    assert s == AstroDate(sy, sm, 1)
    assert e == AstroDate(ey, em, 1)


@pytest.mark.parametrize("text", ['T5 2026', 'o 5 trimestre'])
def test_not_a_quarter(text):
    r = parse(text)
    if r is not None:
        s, e = r[0].start, r[0].end
        assert not (s.day == 1 and s.month in (1, 4, 7, 10)
                    and (e.year - s.year) * 12 + (e.month - s.month) == 3)


def test_spelled_ordinal_pending():
    s, e = start_end('o tercer trimestre')
    assert s == AstroDate(2018, 7, 1) and e == AstroDate(2018, 10, 1)
