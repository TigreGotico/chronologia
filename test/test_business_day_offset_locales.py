"""A working-day offset counts Monday to Friday, not calendar days.

The anchor is Tuesday 2023-06-27.  The gold dates come from
``numpy.busday_offset("2023-06-27", n)``, a Monday-to-Friday count outside
chronologia: n=1 -> 2023-06-28, n=3 -> 2023-06-30, n=5 -> 2023-07-04,
n=6 -> 2023-07-05.
"""
from datetime import date, datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2023, 6, 27, 9, 0)

CITED = [
    ("it", "Il pacco verrà consegnato fra cinque giorni lavorativi.", date(2023, 7, 4)),
    ("it", "La risposta arriverà tra tre giorni lavorativi.", date(2023, 6, 30)),
    ("it", "Il tecnico passerà tra un giorno lavorativo.", date(2023, 6, 28)),
    ("ro", "Coletul va ajunge la birou în cinci zile lucrătoare.", date(2023, 7, 4)),
    ("ro", "Comanda va fi livrată în șase zile lucrătoare.", date(2023, 7, 5)),
]

# TigreGotico/chronologia#1458: no cited working-day surface in these locales
UNCITED = [
    ("gl", "A biblioteca abrirá dentro de cinco días hábiles.", date(2023, 7, 4)),
    ("ast", "La biblioteca va abrir dientro de cinco díes hábiles.", date(2023, 7, 4)),
    ("mwl", "La ancomienda ha de chegar an cinco dies úteis.", date(2023, 7, 4)),
    ("eo", "La riparisto revenos post kvin labortagoj.", date(2023, 7, 4)),
    ("sr", "Paket će stići za pet radnih dana.", date(2023, 7, 4)),
    ("lt", "Baldai bus pristatyti po penkių darbo dienų.", date(2023, 7, 4)),
]


def _day(lang, text):
    res = extract_timespan(text, lang, ANCHOR)
    return res.span.start.date() if res else None


@pytest.mark.parametrize("lang,text,gold", CITED)
def test_working_days_skip_the_weekend(lang, text, gold):
    assert _day(lang, text) == gold


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="TigreGotico/chronologia#1458")
@pytest.mark.parametrize("lang,text,gold", UNCITED)
def test_uncited_locales(lang, text, gold):
    assert _day(lang, text) == gold
