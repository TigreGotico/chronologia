"""Spain golds + national differential (national fixed set only; see es.tab scope).

Golds hand-derived from the Estatuto de los Trabajadores art. 37.2 national
fiestas laborales (papers/holidays/es_estatuto_trabajadores_art37_boe.html).
Viernes Santo recomputes easter(2024) in-test.

Documented national differential disagreements (vacanza/holidays 0.101), all
adjudicated in the reference's favour — Spain's annual "traslado" drops a
national fiesta that falls on a Sunday, which chronologia's fixed rules do not
model:

* 2023 our-only 1 Jan: Año Nuevo 2023 fell on a Sunday and was dropped from that
  year's national calendario laboral.
* 2024 our-only 8 Dec: Inmaculada Concepción 2024 fell on a Sunday, dropped.
* 2025 our-only 12 Oct: Fiesta Nacional 2025 falls on a Sunday, dropped.
"""
import pytest

from chronologia import holidays_for
from holiday_golds import Gold, register
from holiday_testkit import assert_gold, assert_national_differential

_J = "ES"
GOLDS = [
    Gold(_J, None, "Año Nuevo", 2024, 1, 1),
    Gold(_J, None, "Epifanía del Señor", 2024, 1, 6),
    Gold(_J, None, "Viernes Santo", 2024, 3, 29, easter_offset=-2),
    Gold(_J, None, "Fiesta del Trabajo", 2024, 5, 1),
    Gold(_J, None, "Asunción de la Virgen", 2024, 8, 15),
    Gold(_J, None, "Fiesta Nacional de España", 2024, 10, 12),
    Gold(_J, None, "Todos los Santos", 2024, 11, 1),
    Gold(_J, None, "Día de la Constitución Española", 2024, 12, 6),
    Gold(_J, None, "Inmaculada Concepción", 2024, 12, 8),
    Gold(_J, None, "Natividad del Señor", 2024, 12, 25),
]
register(GOLDS)

_DISAGREEMENTS = {
    2023: {"our_only": {(1, 1)}},
    2024: {"our_only": {(12, 8)}},
    2025: {"our_only": {(10, 12)}},
}


@pytest.mark.parametrize("gold", GOLDS, ids=lambda g: g.name)
def test_gold_dates(gold):
    assert_gold(gold)


def test_national_differential_2023_2025():
    assert_national_differential(_J, (2023, 2024, 2025), _DISAGREEMENTS)


def test_ships_national_only_no_subdivisions():
    from chronologia.civil_holidays import load_calendar, _DATA_DIR
    import os
    cal = load_calendar(os.path.join(_DATA_DIR, "es.tab"))
    assert all(r.subdiv is None for r in cal.rules)
