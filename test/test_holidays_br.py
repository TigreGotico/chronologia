"""Brazil golds + national differential (national feriados + movable facultatives).

Golds hand-derived from Lei 662/1949 and Lei 14.759/2023
(papers/holidays/br_lei662_planalto.html, br_lei14759_consciencia_planalto.html).
Movable days (Sexta-feira Santa, and the facultative Carnaval / Corpus Christi)
recompute easter(2024) in-test. Carnaval and Corpus Christi are facultative — not
statutory feriados — carried as "religious"-only (never "public"); the national
public differential therefore excludes them.

Documented national differential disagreement (vacanza/holidays 0.101),
adjudicated in the reference's favour:

* 2023 our-only 20 Nov: Dia da Consciência Negra became a NATIONAL holiday only
  from 2024 (Lei 14.759/2023). chronologia's FixedRule emits it every year and
  cannot year-gate, so it over-emits the 2023 occurrence.
"""
import pytest

from chronologia import holidays_for
from holiday_golds import Gold, register
from holiday_testkit import assert_gold, assert_national_differential

_J = "BR"
GOLDS = [
    Gold(_J, None, "Confraternização Universal", 2024, 1, 1),
    Gold(_J, None, "Sexta-feira Santa", 2024, 3, 29, easter_offset=-2),
    Gold(_J, None, "Tiradentes", 2024, 4, 21),
    Gold(_J, None, "Dia do Trabalhador", 2024, 5, 1),
    Gold(_J, None, "Independência do Brasil", 2024, 9, 7),
    Gold(_J, None, "Nossa Senhora Aparecida", 2024, 10, 12),
    Gold(_J, None, "Finados", 2024, 11, 2),
    Gold(_J, None, "Proclamação da República", 2024, 11, 15),
    Gold(_J, None, "Dia Nacional de Zumbi e da Consciência Negra", 2024, 11, 20),
    Gold(_J, None, "Natal", 2024, 12, 25),
    # facultative national religious days (movable)
    Gold(_J, None, "Carnaval", 2024, 2, 13, easter_offset=-47),
    Gold(_J, None, "Corpus Christi", 2024, 5, 30, easter_offset=60),
    # state examples
    Gold(_J, "BR-SP", "Revolução Constitucionalista", 2024, 7, 9),
    Gold(_J, "BR-RJ", "São Jorge", 2024, 4, 23),
]
register(GOLDS)

_DISAGREEMENTS = {
    2023: {"our_only": {(11, 20)}},
}


@pytest.mark.parametrize("gold", GOLDS,
                         ids=lambda g: f"{g.subdiv or 'BR'}:{g.name}")
def test_gold_dates(gold):
    assert_gold(gold)


def test_national_differential_2023_2025():
    assert_national_differential(_J, (2023, 2024, 2025), _DISAGREEMENTS)


def test_carnaval_and_corpus_are_facultative_not_public():
    hs = {h.name: h for h in holidays_for(_J, 2024)}
    assert "public" not in hs["Carnaval"].categories
    assert "public" not in hs["Corpus Christi"].categories
    assert "religious" in hs["Carnaval"].categories
