"""nb: "fra N. til M. <month> <year>" day-ranges, second-pass resweep.

``test_nb_ranges_adv.py`` only exercises June 2018 / cross-month / bare-year
ranges. This sweeps the 5th-to-12th of every month across ten fresh years
(2082-2091), in both the ``fra ... til ...`` and bare ``... til ...`` forms.
Gold: [5th, 12th] inclusive -> half-open [day5, day13) -- pure arithmetic.
"""
from datetime import timedelta

import pytest

from ._corpus import AstroDate, start_end

_MONTHS = [
    "januar", "februar", "mars", "april", "mai", "juni",
    "juli", "august", "september", "oktober", "november", "desember",
]


def _cases():
    out = []
    for y in range(2082, 2092):
        for mi, mo in enumerate(_MONTHS, 1):
            for tpl in (f"fra 5. til 12. {mo} {y}", f"5. til 12. {mo} {y}"):
                out.append((tpl, y, mi))
    return out


@pytest.mark.parametrize("text,y,m", _cases())
def test_day_range_resweep(text, y, m):
    s, e = start_end(text)
    assert s == AstroDate(y, m, 5)
    assert e == AstroDate(y, m, 13)
