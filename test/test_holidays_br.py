"""Brazil national differential + facultative-day behaviour (source: Planalto).

Per-holiday gold dates for BR live in the shared HOLIDAY_GOLDS registry
(test_holiday_golds.py). Carnaval and Corpus Christi are facultative — not
statutory feriados — carried as "religious"-only (never "public"), so the
national public differential excludes them.

Documented national differential disagreement (vacanza/holidays), adjudicated in
the reference's favour:

* 2023 our-only 20 Nov: Dia da Consciência Negra became a NATIONAL holiday only
  from 2024 (Lei 14.759/2023). chronologia's FixedRule cannot year-gate, so it
  over-emits the 2023 occurrence.
"""
from chronologia import holidays_for
from holiday_testkit import assert_national_differential

_J = "BR"
_DISAGREEMENTS = {
    2023: {"our_only": {(11, 20)}},
}


def test_national_differential_2023_2025():
    assert_national_differential(_J, (2023, 2024, 2025), _DISAGREEMENTS)


def test_carnaval_and_corpus_are_facultative_not_public():
    hs = {h.name: h for h in holidays_for(_J, 2024)}
    assert "public" not in hs["Carnaval"].categories
    assert "public" not in hs["Corpus Christi"].categories
    assert "religious" in hs["Carnaval"].categories
