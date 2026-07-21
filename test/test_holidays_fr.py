"""France golds + national differential (11 national + Alsace-Moselle's 2 extras).

Golds hand-derived from service-public.fr's jours fériés listing
(papers/holidays/fr_jours_feries_service_public.html). Movable days recompute
easter(2024) in-test. France applies no weekend substitution; the national
differential agrees exactly with vacanza/holidays 0.101 in 2023-2025.
"""
import pytest

from chronologia import holidays_for
from holiday_golds import Gold, register
from holiday_testkit import assert_gold, assert_national_differential

_J = "FR"
GOLDS = [
    Gold(_J, None, "Jour de l'an", 2024, 1, 1),
    Gold(_J, None, "Lundi de Pâques", 2024, 4, 1, easter_offset=1),
    Gold(_J, None, "Fête du Travail", 2024, 5, 1),
    Gold(_J, None, "Fête de la Victoire", 2024, 5, 8),
    Gold(_J, None, "Ascension", 2024, 5, 9, easter_offset=39),
    Gold(_J, None, "Lundi de Pentecôte", 2024, 5, 20, easter_offset=50),
    Gold(_J, None, "Fête nationale", 2024, 7, 14),
    Gold(_J, None, "Assomption", 2024, 8, 15),
    Gold(_J, None, "Toussaint", 2024, 11, 1),
    Gold(_J, None, "Armistice 1918", 2024, 11, 11),
    Gold(_J, None, "Noël", 2024, 12, 25),
    # Alsace-Moselle local law
    Gold(_J, "FR-57", "Vendredi saint", 2024, 3, 29, easter_offset=-2),
    Gold(_J, "FR-57", "Saint Étienne", 2024, 12, 26),
    Gold(_J, "FR-6AE", "Vendredi saint", 2024, 3, 29, easter_offset=-2),
    Gold(_J, "FR-6AE", "Saint Étienne", 2024, 12, 26),
]
register(GOLDS)


@pytest.mark.parametrize("gold", GOLDS,
                         ids=lambda g: f"{g.subdiv or 'FR'}:{g.name}")
def test_gold_dates(gold):
    assert_gold(gold)


def test_national_differential_2023_2025():
    assert_national_differential(_J, (2023, 2024, 2025), {})


def test_alsace_moselle_two_extras_not_national():
    national = {h.name for h in holidays_for(_J, 2024)}
    assert "Vendredi saint" not in national and "Saint Étienne" not in national
    moselle = {h.name for h in holidays_for(_J, 2024, subdiv="FR-57")}
    assert {"Vendredi saint", "Saint Étienne"} <= moselle
