"""Spain national differential (national fixed set only; see es.tab scope note).

Per-holiday gold dates for ES live in the shared HOLIDAY_GOLDS registry
(test_holiday_golds.py).

Documented national differential disagreements (vacanza/holidays), all
adjudicated in the reference's favour — Spain's annual "traslado" drops a
national fiesta that falls on a Sunday, which chronologia's fixed rules do not
model:

* 2023 our-only 1 Jan: Año Nuevo 2023 fell on a Sunday, dropped from that year's
  national calendario laboral.
* 2024 our-only 8 Dec: Inmaculada Concepción 2024 fell on a Sunday, dropped.
* 2025 our-only 12 Oct: Fiesta Nacional 2025 falls on a Sunday, dropped.
"""
import os

from chronologia.civil_holidays import load_calendar, _DATA_DIR
from holiday_testkit import assert_national_differential

_J = "ES"
_DISAGREEMENTS = {
    2023: {"our_only": {(1, 1)}},
    2024: {"our_only": {(12, 8)}},
    2025: {"our_only": {(10, 12)}},
}


def test_national_differential_2023_2025():
    assert_national_differential(_J, (2023, 2024, 2025), _DISAGREEMENTS)


def test_ships_national_only_no_subdivisions():
    cal = load_calendar(os.path.join(_DATA_DIR, "es.tab"))
    assert all(r.subdiv is None for r in cal.rules)
