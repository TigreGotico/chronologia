"""fy: ordinal-word quarters -- 'it <ordinal> kwartaal fan <year>'.

Complements the digit/Q-form quarter coverage: the spelled-out Frisian
ordinal (earste/twadde/tredde/fjirde) selects the three-month block.
"""
import pytest

from ._corpus import start_end, AstroDate

_Q = {1: (1, 4), 2: (4, 7), 3: (7, 10), 4: (10, 13)}


@pytest.mark.parametrize("text,q", [
    ('it earste kwartaal fan 2020', 1),
    ('it twadde kwartaal fan 2020', 2),
    ('it tredde kwartaal fan 2020', 3),
    ('it fjirde kwartaal fan 2020', 4),
])
def test_ordinal_quarter_of_year(text, q):
    m0, m1 = _Q[q]
    y = 2020
    s = AstroDate(y, m0, 1)
    e = AstroDate(y + 1, 1, 1) if m1 == 13 else AstroDate(y, m1, 1)
    assert start_end(text) == (s, e)


def test_bare_ordinal_quarter_current_year():
    # 'it twadde kwartaal' with no year -> Q2 of the anchor year (2017)
    assert start_end('it twadde kwartaal') == (AstroDate(2017, 4, 1),
                                               AstroDate(2017, 7, 1))
