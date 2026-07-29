"""Días hábiles / laborables: "en N días hábiles", "el próximo día hábil",
"N días hábiles después de navidad".

Un día hábil es un día entre semana que no es fin de semana ni festivo de la
``jurisdiction``.  Sin jurisdicción la cuenta ignora los festivos.

Ancla: miércoles 2026-12-23.  Festivos públicos ES en el intervalo:
vie 2026-12-25 (Navidad), vie 2027-01-01 (Año Nuevo), mié 2027-01-06 (Epifanía).

ES (salta Navidad, Año Nuevo, Epifanía), desde mié 12-23:
    jue24(1) lun28(2) mar29(3) mié30(4) jue31(5) lun Jan4(6) mar5(7) jue7(8)
Sin jurisdicción (sólo días entre semana):
    jue24(1) vie25(2) lun28(3)
"""
from datetime import date, datetime, timedelta

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate

import pytest

ANCHOR = datetime(2026, 12, 23, 9, 0)   # miércoles


def start(text, jurisdiction=None):
    r = extract_timespan(text, "es", ANCHOR, jurisdiction=jurisdiction)
    assert r is not None, f"{text!r} no resolvió"
    return r[0].start


def nomatch(text, jurisdiction=None):
    r = extract_timespan(text, "es", ANCHOR, jurisdiction=jurisdiction)
    assert r is None, f"{text!r} resolvió inesperadamente a {r!r}"


def _ad(d):
    return AstroDate(d.year, d.month, d.day)


@pytest.mark.parametrize("text,expected", [
    ("en 1 día hábil", date(2026, 12, 24)),
    ("en 2 días hábiles", date(2026, 12, 28)),
    ("en 4 días hábiles", date(2026, 12, 30)),
    ("en 6 días hábiles", date(2027, 1, 4)),
    ("en 8 días hábiles", date(2027, 1, 7)),    # salta Epifanía (Jan 6)
    ("4 días laborables", date(2026, 12, 30)),
])
def test_cuenta_es(text, expected):
    assert start(text, "ES") == _ad(expected)


@pytest.mark.parametrize("text,expected", [
    ("en 1 día hábil", date(2026, 12, 24)),
    ("en 2 días hábiles", date(2026, 12, 25)),   # ciega a festivos
    ("en 3 días hábiles", date(2026, 12, 28)),
])
def test_cuenta_ciega(text, expected):
    assert start(text) == _ad(expected)


def test_proximo_dia_habil():
    assert start("el próximo día hábil", "ES") == _ad(date(2026, 12, 24))


@pytest.mark.parametrize("text,expected,juris", [
    ("3 días hábiles después de navidad", date(2026, 12, 30), "ES"),
    ("3 días hábiles después de navidad", date(2026, 12, 30), None),
    ("2 días hábiles antes de navidad", date(2026, 12, 23), "ES"),
])
def test_composicion(text, expected, juris):
    assert start(text, juris) == _ad(expected)


def test_ancho_de_un_dia():
    r = extract_timespan("en 3 días hábiles", "es", ANCHOR, jurisdiction="ES")
    assert r[0].width == timedelta(days=1)


@pytest.mark.parametrize("text", ["como siempre", "todo normal"])
def test_negativos(text):
    nomatch(text)
    nomatch(text, "ES")


# -- día hábil de un mes NOMBRADO + AÑO explícito --------------------------
# El año explícito debe vincularse: la cuenta se acota al mes nombrado de ESE
# año, no al año del ancla.  Oro por aritmética lunes-viernes independiente
# (sin jurisdicción, ciego a festivos).
#
#   marzo 2019:  1 vie  4 lun  5 mar          -> 3er hábil = 5 mar
#   enero 2020:  1 mié (1er hábil)            -> 1er hábil = 1 ene
#   junio 2018: 29 vie = último hábil de junio

@pytest.mark.parametrize("text,expected", [
    ("el tercer día hábil de marzo de 2019", date(2019, 3, 5)),
    ("el primer día laborable de enero de 2020", date(2020, 1, 1)),
    ("el último día hábil de junio de 2018", date(2018, 6, 29)),
])
def test_dia_habil_mes_nombrado_con_anio(text, expected):
    assert start(text) == _ad(expected)


@pytest.mark.parametrize("text", [
    "el tercer día hábil de marzo de 2019",
    "el último día hábil de junio de 2018",
])
def test_anio_no_queda_suelto(text):
    r = extract_timespan(text, "es", ANCHOR)
    assert not any(ch.isdigit() for ch in r[1]), \
        f"{text!r} dejó suelto un año: {r[1]!r}"
