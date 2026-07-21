"""Switzerland national differential + cantonal-sample behaviour.

Source: Swiss federal justice office (papers/holidays/ch_holidays.md). Per-holiday
gold dates live in the shared HOLIDAY_GOLDS registry; this module owns the national
differential and the cantonal-split behavioural checks.

Only 1 August is federally mandated; the de-facto national set is the four days
observed everywhere (Neujahr, Auffahrt, Bundesfeier, Weihnachten), which agrees
with the reference's national set. Cantonal holidays are shipped for a documented
6-canton sample (ZH, BE, LU, TI, GE, VS) exercising the split types.
"""
from chronologia import AstroDate, holidays_for
from holiday_testkit import assert_national_differential

_J = "CH"


def test_national_differential_2023_2025():
    assert_national_differential(_J, (2023, 2024, 2025), {})


def test_catholic_luzern_has_days_protestant_zurich_lacks():
    lu = {h.name for h in holidays_for(_J, 2024, subdiv="CH-LU")}
    zh = {h.name for h in holidays_for(_J, 2024, subdiv="CH-ZH")}
    for name in ("Fronleichnam", "Mariä Himmelfahrt", "Allerheiligen",
                 "Mariä Empfängnis"):
        assert name in lu and name not in zh


def test_geneva_jeune_and_restauration():
    ge = {h.name: h.date for h in holidays_for(_J, 2024, subdiv="CH-GE")}
    # Jeûne genevois: Thursday after the 1st Sunday of September (5 Sep 2024).
    assert ge["Jeûne genevois"] == AstroDate(2024, 9, 5)
    assert ge["Restauration de la République"] == AstroDate(2024, 12, 31)


def test_ticino_peter_und_paul_and_epiphany():
    ti = {h.name: h.date for h in holidays_for(_J, 2024, subdiv="CH-TI")}
    assert ti["Peter und Paul"] == AstroDate(2024, 6, 29)
    assert ti["Heilige Drei Könige"] == AstroDate(2024, 1, 6)


def test_bern_berchtoldstag_zurich_none():
    be = {h.name for h in holidays_for(_J, 2024, subdiv="CH-BE")}
    zh = {h.name for h in holidays_for(_J, 2024, subdiv="CH-ZH")}
    assert "Berchtoldstag" in be and "Berchtoldstag" not in zh
