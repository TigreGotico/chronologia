# -*- coding: utf-8 -*-
"""Calendar quarters (pl). Quarter N spans months [3N-2 .. 3N]; anchor
2017-06-27 sits in Q2. Digit and Q-forms fold to the number; ordinal-WORD
forms ("trzeci kwartał") are unsupported because the pl number model does not fold
ordinal words, so that phrasing is xfailed. Every edge hand-derived."""
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end, parse

_CASES = [
    ('Q3 2026', 2026, 7, 2026, 10),
    ('3 kwartał 2026', 2026, 7, 2026, 10),
    ('1 kwartał 2020', 2020, 1, 2020, 4),
    ('2 kwartał 2018', 2018, 4, 2018, 7),
    ('4 kwartał 2019', 2019, 10, 2020, 1),
    ('następny kwartał', 2017, 7, 2017, 10),
    ('ten kwartał', 2017, 4, 2017, 7),
    ('Q1 2020', 2020, 1, 2020, 4),
]


@pytest.mark.parametrize("text,sy,sm,ey,em", _CASES)
def test_quarter(text, sy, sm, ey, em):
    s, e = start_end(text)
    assert s == AstroDate(sy, sm, 1)
    assert e == AstroDate(ey, em, 1)


@pytest.mark.parametrize("text", ['Q5 2026', 'spotkanie'])
def test_not_a_quarter(text):
    r = parse(text)
    if r is not None:
        s, e = r[0].start, r[0].end
        assert not (s.day == 1 and s.month in (1, 4, 7, 10)
                    and (e.year - s.year) * 12 + (e.month - s.month) == 3)


def test_ordinal_word_quarter():
    s, e = start_end("trzeci kwartał 2026")
    assert s == AstroDate(2026, 7, 1) and e == AstroDate(2026, 10, 1)
