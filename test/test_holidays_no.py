"""Norway national differential (source: Lov om helligdager og helligdagsfred).

Per-holiday gold dates live in the shared HOLIDAY_GOLDS registry. Norway's public
holidays are uniform nationwide (no county-specific statutory holidays), so only
the national set is shipped and it agrees with the reference across 2023-2025.
"""
from chronologia import AstroDate, holidays_for
from holiday_testkit import assert_national_differential

_J = "NO"


def test_national_differential_2023_2025():
    assert_national_differential(_J, (2023, 2024, 2025), {})


def test_constitution_day_and_labour_day_2024():
    got = {h.name: h.date for h in holidays_for(_J, 2024)}
    assert got["Grunnlovsdag"] == AstroDate(2024, 5, 17)
    assert got["Arbeidernes dag"] == AstroDate(2024, 5, 1)
