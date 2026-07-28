# -*- coding: utf-8 -*-
"""Non-existent "Nth weekday of month" for Galician must not fabricate a day.

A fifth (and sometimes fourth) occurrence of a weekday simply does not exist in
many months.  The month is enumerated by independent arithmetic; every case
here is one the real calendar cannot satisfy, and the parser must decline it
(return ``None``) rather than wrap around into the next month.  Anchor Tue
2017-06-27."""
import calendar
from datetime import datetime

import pytest

from ._corpus import nomatch

_WD = {"luns": 0, "martes": 1, "mércores": 2, "xoves": 3,
       "venres": 4, "sábado": 5, "domingo": 6}

_CASES = [
    ('quinto', 5, 'luns', 'xaneiro', 1, 2019),
    ('quinto', 5, 'luns', 'xaneiro', 1, 2020),
    ('quinto', 5, 'luns', 'febreiro', 2, 2019),
    ('quinto', 5, 'luns', 'febreiro', 2, 2020),
    ('quinto', 5, 'luns', 'marzo', 3, 2019),
    ('quinto', 5, 'luns', 'abril', 4, 2020),
    ('quinto', 5, 'luns', 'maio', 5, 2019),
    ('quinto', 5, 'luns', 'maio', 5, 2020),
    ('quinto', 5, 'luns', 'xuño', 6, 2019),
    ('quinto', 5, 'luns', 'xullo', 7, 2020),
    ('quinto', 5, 'luns', 'agosto', 8, 2019),
    ('quinto', 5, 'luns', 'setembro', 9, 2020),
    ('quinto', 5, 'luns', 'outubro', 10, 2019),
    ('quinto', 5, 'luns', 'outubro', 10, 2020),
    ('quinto', 5, 'luns', 'novembro', 11, 2019),
    ('quinto', 5, 'luns', 'decembro', 12, 2020),
    ('quinto', 5, 'martes', 'xaneiro', 1, 2020),
    ('quinto', 5, 'martes', 'febreiro', 2, 2019),
    ('quinto', 5, 'martes', 'febreiro', 2, 2020),
    ('quinto', 5, 'martes', 'marzo', 3, 2019),
    ('quinto', 5, 'martes', 'abril', 4, 2020),
    ('quinto', 5, 'martes', 'maio', 5, 2019),
    ('quinto', 5, 'martes', 'maio', 5, 2020),
    ('quinto', 5, 'martes', 'xuño', 6, 2019),
    ('quinto', 5, 'martes', 'xullo', 7, 2020),
    ('quinto', 5, 'martes', 'agosto', 8, 2019),
    ('quinto', 5, 'martes', 'agosto', 8, 2020),
    ('quinto', 5, 'martes', 'setembro', 9, 2019),
    ('quinto', 5, 'martes', 'outubro', 10, 2020),
    ('quinto', 5, 'martes', 'novembro', 11, 2019),
    ('quinto', 5, 'martes', 'novembro', 11, 2020),
    ('quinto', 5, 'mércores', 'febreiro', 2, 2019),
    ('quinto', 5, 'mércores', 'febreiro', 2, 2020),
    ('quinto', 5, 'mércores', 'marzo', 3, 2019),
    ('quinto', 5, 'mércores', 'marzo', 3, 2020),
    ('quinto', 5, 'mércores', 'abril', 4, 2019),
    ('quinto', 5, 'mércores', 'maio', 5, 2020),
    ('quinto', 5, 'mércores', 'xuño', 6, 2019),
    ('quinto', 5, 'mércores', 'xuño', 6, 2020),
    ('quinto', 5, 'mércores', 'agosto', 8, 2019),
    ('quinto', 5, 'mércores', 'agosto', 8, 2020),
    ('quinto', 5, 'mércores', 'setembro', 9, 2019),
    ('quinto', 5, 'mércores', 'outubro', 10, 2020),
    ('quinto', 5, 'mércores', 'novembro', 11, 2019),
    ('quinto', 5, 'mércores', 'novembro', 11, 2020),
    ('quinto', 5, 'mércores', 'decembro', 12, 2019),
    ('quinto', 5, 'xoves', 'febreiro', 2, 2019),
    ('quinto', 5, 'xoves', 'febreiro', 2, 2020),
    ('quinto', 5, 'xoves', 'marzo', 3, 2019),
    ('quinto', 5, 'xoves', 'marzo', 3, 2020),
    ('quinto', 5, 'xoves', 'abril', 4, 2019),
    ('quinto', 5, 'xoves', 'maio', 5, 2020),
    ('quinto', 5, 'xoves', 'xuño', 6, 2019),
    ('quinto', 5, 'xoves', 'xuño', 6, 2020),
    ('quinto', 5, 'xoves', 'xullo', 7, 2019),
    ('quinto', 5, 'xoves', 'agosto', 8, 2020),
    ('quinto', 5, 'xoves', 'setembro', 9, 2019),
    ('quinto', 5, 'xoves', 'setembro', 9, 2020),
    ('quinto', 5, 'xoves', 'novembro', 11, 2019),
    ('quinto', 5, 'xoves', 'novembro', 11, 2020),
    ('quinto', 5, 'xoves', 'decembro', 12, 2019),
    ('quinto', 5, 'venres', 'xaneiro', 1, 2019),
    ('quinto', 5, 'venres', 'febreiro', 2, 2019),
    ('quinto', 5, 'venres', 'febreiro', 2, 2020),
    ('quinto', 5, 'venres', 'marzo', 3, 2020),
    ('quinto', 5, 'venres', 'abril', 4, 2019),
    ('quinto', 5, 'venres', 'abril', 4, 2020),
    ('quinto', 5, 'venres', 'xuño', 6, 2019),
    ('quinto', 5, 'venres', 'xuño', 6, 2020),
    ('quinto', 5, 'venres', 'xullo', 7, 2019),
    ('quinto', 5, 'venres', 'agosto', 8, 2020),
    ('quinto', 5, 'venres', 'setembro', 9, 2019),
    ('quinto', 5, 'venres', 'setembro', 9, 2020),
    ('quinto', 5, 'venres', 'outubro', 10, 2019),
    ('quinto', 5, 'venres', 'novembro', 11, 2020),
    ('quinto', 5, 'venres', 'decembro', 12, 2019),
    ('quinto', 5, 'venres', 'decembro', 12, 2020),
    ('quinto', 5, 'sábado', 'xaneiro', 1, 2019),
    ('quinto', 5, 'sábado', 'xaneiro', 1, 2020),
    ('quinto', 5, 'sábado', 'febreiro', 2, 2019),
    ('quinto', 5, 'sábado', 'marzo', 3, 2020),
    ('quinto', 5, 'sábado', 'abril', 4, 2019),
    ('quinto', 5, 'sábado', 'abril', 4, 2020),
    ('quinto', 5, 'sábado', 'maio', 5, 2019),
    ('quinto', 5, 'sábado', 'xuño', 6, 2020),
    ('quinto', 5, 'sábado', 'xullo', 7, 2019),
    ('quinto', 5, 'sábado', 'xullo', 7, 2020),
    ('quinto', 5, 'sábado', 'setembro', 9, 2019),
    ('quinto', 5, 'sábado', 'setembro', 9, 2020),
    ('quinto', 5, 'sábado', 'outubro', 10, 2019),
    ('quinto', 5, 'sábado', 'novembro', 11, 2020),
    ('quinto', 5, 'sábado', 'decembro', 12, 2019),
    ('quinto', 5, 'sábado', 'decembro', 12, 2020),
    ('quinto', 5, 'domingo', 'xaneiro', 1, 2019),
    ('quinto', 5, 'domingo', 'xaneiro', 1, 2020),
    ('quinto', 5, 'domingo', 'febreiro', 2, 2019),
    ('quinto', 5, 'domingo', 'febreiro', 2, 2020),
    ('quinto', 5, 'domingo', 'abril', 4, 2019),
    ('quinto', 5, 'domingo', 'abril', 4, 2020),
    ('quinto', 5, 'domingo', 'maio', 5, 2019),
    ('quinto', 5, 'domingo', 'xuño', 6, 2020),
    ('quinto', 5, 'domingo', 'xullo', 7, 2019),
    ('quinto', 5, 'domingo', 'xullo', 7, 2020),
    ('quinto', 5, 'domingo', 'agosto', 8, 2019),
    ('quinto', 5, 'domingo', 'setembro', 9, 2020),
    ('quinto', 5, 'domingo', 'outubro', 10, 2019),
    ('quinto', 5, 'domingo', 'outubro', 10, 2020),
    ('quinto', 5, 'domingo', 'novembro', 11, 2019),
    ('quinto', 5, 'domingo', 'decembro', 12, 2020),
]


@pytest.mark.parametrize("ordw,n,wdw,monw,mon,year", _CASES)
def test_nonexistent_nth_weekday_is_nomatch(ordw, n, wdw, monw, mon, year):
    # guard: the case really is impossible on the real calendar
    days = [d for d in range(1, calendar.monthrange(year, mon)[1] + 1)
            if datetime(year, mon, d).weekday() == _WD[wdw]]
    assert n > len(days)
    nomatch(f"o {ordw} {wdw} de {monw} {year}")
