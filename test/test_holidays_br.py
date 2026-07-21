"""Brazil national differential + facultative-day behaviour (source: Planalto).

Per-holiday gold dates for BR live in the shared HOLIDAY_GOLDS registry
(test_holiday_golds.py). Carnaval and Corpus Christi are facultative — not
statutory feriados — carried as "religious"-only (never "public"), so the
national public differential excludes them.

National differential (vacanza/holidays) is clean for 2023-2025: Dia da
Consciência Negra became a NATIONAL holiday only from 2024 (Lei 14.759/2023), and
its rule now carries a "2024-" validity range, so chronologia no longer emits the
2023 occurrence and there is nothing to document as a disagreement.
"""
from chronologia import AstroDate, holidays_for
from holiday_testkit import assert_national_differential

_J = "BR"
_DISAGREEMENTS: dict = {}


def test_national_differential_2023_2025():
    assert_national_differential(_J, (2023, 2024, 2025), _DISAGREEMENTS)


def test_consciencia_negra_year_gated_national_from_2024():
    """Lei 14.759/2023: national only from 2024 — absent 2023, present 2024."""
    name = "Dia Nacional de Zumbi e da Consciência Negra"
    dates_2023 = {h.name: h.date for h in holidays_for(_J, 2023)}
    dates_2024 = {h.name: h.date for h in holidays_for(_J, 2024)}
    assert name not in dates_2023
    assert dates_2024[name] == AstroDate(2024, 11, 20)


def test_carnaval_and_corpus_are_facultative_not_public():
    hs = {h.name: h for h in holidays_for(_J, 2024)}
    assert "public" not in hs["Carnaval"].categories
    assert "public" not in hs["Corpus Christi"].categories
    assert "religious" in hs["Carnaval"].categories
