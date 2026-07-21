"""Germany golds + national differential (national nine + all 16 Länder).

Golds hand-derived from Bavaria's and Berlin's official Feiertagsgesetze
(papers/holidays/de_bayern_feiertagsgesetz.html, de_berlin_feiertagsgesetz.html)
and the all-Länder overview (de_feiertage_uebersicht.html), cross-checked against
vacanza/holidays 0.101 (MIT). Movable days recompute easter(2024) in-test.
Germany applies no weekend substitution, so the national differential agrees
exactly with the reference in 2023-2025 (no documented disagreements).
"""
import pytest

from chronologia import holidays_for
from holiday_golds import Gold, register
from holiday_testkit import assert_gold, assert_national_differential

_J = "DE"


def _fixed(sub, name, m, d):
    return Gold(_J, sub, name, 2024, m, d)


def _easter(sub, name, off):
    from chronologia.computus import easter
    from datetime import timedelta
    dt = easter(2024) + timedelta(days=off)
    return Gold(_J, sub, name, 2024, dt.month, dt.day, easter_offset=off)


_EPIPHANY = ["DE-BW", "DE-BY", "DE-ST"]
_FRAUENTAG = ["DE-BE", "DE-MV"]
_FRONLEICHNAM = ["DE-BW", "DE-BY", "DE-HE", "DE-NW", "DE-RP", "DE-SL"]
_REFORMATION = ["DE-BB", "DE-HB", "DE-HH", "DE-MV", "DE-NI", "DE-SN", "DE-ST",
                "DE-SH", "DE-TH"]
_ALLERHEILIGEN = ["DE-BW", "DE-BY", "DE-NW", "DE-RP", "DE-SL"]

GOLDS = [
    # --- nationwide ---
    _fixed(None, "Neujahr", 1, 1),
    _easter(None, "Karfreitag", -2),
    _easter(None, "Ostermontag", 1),
    _fixed(None, "Erster Mai", 5, 1),
    _easter(None, "Christi Himmelfahrt", 39),
    _easter(None, "Pfingstmontag", 50),
    _fixed(None, "Tag der Deutschen Einheit", 10, 3),
    _fixed(None, "Erster Weihnachtstag", 12, 25),
    _fixed(None, "Zweiter Weihnachtstag", 12, 26),
    # --- Brandenburg statewide Sundays ---
    _easter("DE-BB", "Ostersonntag", 0),
    _easter("DE-BB", "Pfingstsonntag", 49),
    # --- Saarland Assumption + Thuringia children's day ---
    _fixed("DE-SL", "Mariä Himmelfahrt", 8, 15),
    _fixed("DE-TH", "Weltkindertag", 9, 20),
    # --- Saxony Buß- und Bettag (Wed on/before 22 Nov -> 20 Nov 2024) ---
    Gold(_J, "DE-SN", "Buß- und Bettag", 2024, 11, 20),
]
GOLDS += [_fixed(s, "Heilige Drei Könige", 1, 6) for s in _EPIPHANY]
GOLDS += [_fixed(s, "Internationaler Frauentag", 3, 8) for s in _FRAUENTAG]
GOLDS += [_easter(s, "Fronleichnam", 60) for s in _FRONLEICHNAM]
GOLDS += [_fixed(s, "Reformationstag", 10, 31) for s in _REFORMATION]
GOLDS += [_fixed(s, "Allerheiligen", 11, 1) for s in _ALLERHEILIGEN]
register(GOLDS)


@pytest.mark.parametrize("gold", GOLDS,
                         ids=lambda g: f"{g.subdiv or 'DE'}:{g.name}")
def test_gold_dates(gold):
    assert_gold(gold)


def test_national_differential_2023_2025():
    assert_national_differential(_J, (2023, 2024, 2025), {})


def test_epiphany_only_in_bw_by_st():
    for sub in _EPIPHANY:
        assert "Heilige Drei Könige" in {
            h.name for h in holidays_for(_J, 2024, subdiv=sub)}
    assert "Heilige Drei Könige" not in {
        h.name for h in holidays_for(_J, 2024, subdiv="DE-BE")}


def test_reformationstag_split_excludes_catholic_south():
    assert "Reformationstag" in {
        h.name for h in holidays_for(_J, 2024, subdiv="DE-SN")}
    assert "Reformationstag" not in {
        h.name for h in holidays_for(_J, 2024, subdiv="DE-BY")}
