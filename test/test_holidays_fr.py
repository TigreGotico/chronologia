"""France national differential + Alsace-Moselle behaviour (source: service-public.fr).

Per-holiday gold dates for FR live in the shared HOLIDAY_GOLDS registry
(test_holiday_golds.py). France applies no weekend substitution; the national set
agrees exactly with the reference in 2023-2025.
"""
from chronologia import holidays_for
from holiday_testkit import assert_national_differential

_J = "FR"


def test_national_differential_2023_2025():
    assert_national_differential(_J, (2023, 2024, 2025), {})


def test_alsace_moselle_two_extras_not_national():
    national = {h.name for h in holidays_for(_J, 2024)}
    assert "Vendredi saint" not in national and "Saint Étienne" not in national
    moselle = {h.name for h in holidays_for(_J, 2024, subdiv="FR-57")}
    assert {"Vendredi saint", "Saint Étienne"} <= moselle
