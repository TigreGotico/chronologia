"""nb: bare month + year, second-pass resweep -- fresh years 2102-2116.

``test_nb_calendar.py`` covers 1999-2020. Gold: [month 1st, next-month 1st)
-- pure calendar arithmetic, no engine round-trip.
"""
import pytest

from ._corpus import AstroDate, start_end

_MONTHS = [
    "januar", "februar", "mars", "april", "mai", "juni",
    "juli", "august", "september", "oktober", "november", "desember",
]


def _cases():
    out = []
    for y in range(2102, 2117):
        for mi, mo in enumerate(_MONTHS, 1):
            ny, nm = (y + 1, 1) if mi == 12 else (y, mi + 1)
            out.append((f"{mo} {y}", y, mi, ny, nm))
    return out


@pytest.mark.parametrize("text,y,m,ny,nm", _cases())
def test_month_year_resweep(text, y, m, ny, nm):
    s, e = start_end(text)
    assert s == AstroDate(y, m, 1)
    assert (e.year, e.month) == (ny, nm)
