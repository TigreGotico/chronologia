"""Czechia national differential (source: zákon 245/2000 Sb.).

Per-holiday gold dates live in the shared HOLIDAY_GOLDS registry. Our national set
agrees with the reference across 2023-2025 with no disagreements. Good Friday has
been a public holiday since 2016.
"""
from chronologia import AstroDate, holidays_for
from holiday_testkit import assert_national_differential

_J = "CZ"


def test_national_differential_2023_2025():
    assert_national_differential(_J, (2023, 2024, 2025), {})


def test_good_friday_is_public_2024():
    got = {h.name: h.date for h in holidays_for(_J, 2024)}
    assert got["Velký pátek"] == AstroDate(2024, 3, 29)
    assert len([h for h in holidays_for(_J, 2024) if h.subdiv is None]) == 13
