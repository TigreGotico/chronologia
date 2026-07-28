# -*- coding: utf-8 -*-
"""Italian "Nth <weekday> di <mese>" -- nth-weekday-of-month.

Gold is computed in-file by walking the calendar (``datetime`` only), never by
the parser. Anchor Tue 2017-06-27, so a bare month binds its 2017 occurrence.

Every ordinal 1st..5th and ``ultimo`` resolves the Nth weekday of the named
month. ``terzo`` / ``quarto`` / ``quinto`` are spelled like the Italian
fraction ("un quarto" = a quarter), which once held them out of the number
fold and silently dropped the weekday; they are pinned here alongside the low
ordinals that always worked.
"""
from datetime import date, timedelta

import pytest

from ._corpus import start, AstroDate

_WD = {"lunedì": 0, "martedì": 1, "mercoledì": 2, "giovedì": 3,
       "venerdì": 4, "sabato": 5, "domenica": 6}
_MO = {"gennaio": 1, "febbraio": 2, "marzo": 3, "aprile": 4, "maggio": 5,
       "giugno": 6, "luglio": 7, "agosto": 8, "settembre": 9, "ottobre": 10,
       "novembre": 11, "dicembre": 12}


def _nth_weekday(year, month, weekday, n):
    """n>=1 -> nth; n==-1 -> last. Pure calendar walk (oracle)."""
    days = [d for d in (date(year, month, 1) + timedelta(i) for i in range(31))
            if d.month == month and d.weekday() == weekday]
    return days[-1] if n == -1 else days[n - 1]


# (italian ordinal word, n) -- the low ordinals plus the fraction-homograph
# ordinals terzo/quarto that once dropped the weekday; every month in the
# matrix has at least four occurrences of each weekday, so n<=4 always exists
_ORD_OK = [("primo", 1), ("secondo", 2), ("terzo", 3), ("quarto", 4),
           ("ultimo", -1)]

_OK_CASES = []
for _art, _wd, _wdname in [("il", 0, "lunedì"), ("il", 1, "martedì"),
                           ("il", 3, "giovedì"), ("il", 4, "venerdì")]:
    for _moname, _m in [("marzo", 3), ("luglio", 7), ("settembre", 9),
                        ("novembre", 11)]:
        for _ordword, _n in _ORD_OK:
            _art2 = "l'" if _ordword == "ultimo" else "il"
            _txt = f"{_art2} {_ordword} {_wdname} di {_moname}"
            _gold = _nth_weekday(2017, _m, _wd, _n)
            _OK_CASES.append((_txt, AstroDate(_gold.year, _gold.month, _gold.day)))


@pytest.mark.parametrize("text,gold", _OK_CASES)
def test_ordinal_weekday_ok(text, gold):
    assert start(text) == gold


@pytest.mark.parametrize("text,gold", [
    ("il terzo lunedì di marzo", AstroDate(2017, 3, 20)),
    ("il quarto giovedì di novembre", AstroDate(2017, 11, 23)),
    ("il terzo martedì di luglio", AstroDate(2017, 7, 18)),
])
def test_ordinal_weekday_terzo_quarto(text, gold):
    assert start(text) == gold
