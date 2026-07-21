"""Austria national differential + Landespatron (regional) behaviour.

Source: Arbeitsruhegesetz §7 (papers/holidays/at_holidays.md). Per-holiday gold
dates live in the shared HOLIDAY_GOLDS registry; this module owns the national
differential and the regional patron-saint checks.

Austria's 13 nationwide Feiertage are all work-free countrywide (Catholic-majority
state), so the national set agrees with the independent reference across 2023-2025
with no disagreements. Good Friday is deliberately absent (not a general holiday
since the 2019 ECJ ruling). The Länder split is the Landespatron layer (regional,
subdiv-scoped), which the reference package does not carry — our added depth.
"""
from chronologia import AstroDate, holidays_for
from holiday_testkit import assert_national_differential

_J = "AT"


def test_national_differential_2023_2025():
    assert_national_differential(_J, (2023, 2024, 2025), {})


def test_national_set_is_thirteen_no_good_friday():
    nat = {h.name for h in holidays_for(_J, 2024) if h.subdiv is None}
    assert len(nat) == 13
    assert "Karfreitag" not in nat


def test_landespatron_is_regional_not_national():
    # Heiliger Josef (19 Mar) is a Tyrol/Styria/Vorarlberg regional day, not nationwide.
    assert "Heiliger Josef" not in {h.name for h in holidays_for(_J, 2024)}
    tirol = {h.name: h.date for h in holidays_for(_J, 2024, subdiv="AT-7")}
    assert tirol["Heiliger Josef"] == AstroDate(2024, 3, 19)


def test_karnten_volksabstimmung_and_wien_leopold():
    kt = {h.name: h.date for h in holidays_for(_J, 2024, subdiv="AT-2")}
    wien = {h.name: h.date for h in holidays_for(_J, 2024, subdiv="AT-9")}
    assert kt["Tag der Volksabstimmung"] == AstroDate(2024, 10, 10)
    assert wien["Heiliger Leopold"] == AstroDate(2024, 11, 15)
    assert "Tag der Volksabstimmung" not in wien
