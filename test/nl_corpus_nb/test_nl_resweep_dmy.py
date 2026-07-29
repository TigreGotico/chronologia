"""nb: full day-month-year dates, second-pass resweep -- fresh years 2092-2101.

``test_nb_calendar.py`` only covers 1944-2020. This sweeps the 1st, 15th and
28th (safe across all months, no leap-year ambiguity) of every month across
ten fresh far-future years. Gold is the literal calendar date -- pure
arithmetic, no engine round-trip.
"""
from datetime import timedelta

import pytest

from ._corpus import AstroDate, span, start

_MONTHS = [
    "januar", "februar", "mars", "april", "mai", "juni",
    "juli", "august", "september", "oktober", "november", "desember",
]


def _cases():
    out = []
    for y in range(2092, 2102):
        for mi, mo in enumerate(_MONTHS, 1):
            for d in (1, 15, 28):
                out.append((f"{d}. {mo} {y}", y, mi, d))
    return out


@pytest.mark.parametrize("text,y,m,d", _cases())
def test_full_dmy_resweep(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)
    assert span(text).width == timedelta(days=1)
