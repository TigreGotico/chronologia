"""Poland national differential + Christmas Eve year-gate (source: Ustawa 1951).

Per-holiday gold dates live in the shared HOLIDAY_GOLDS registry. Our national set
agrees with the reference across 2023-2025 with no disagreements. Wigilia
(Christmas Eve, 24 Dec) is year-gated: a statutory non-working day only from 2025.
"""
from chronologia import AstroDate, holidays_for
from holiday_testkit import assert_national_differential

_J = "PL"


def test_national_differential_2023_2025():
    assert_national_differential(_J, (2023, 2024, 2025), {})


def test_christmas_eve_year_gated_from_2025():
    assert "Wigilia Bożego Narodzenia" not in {h.name for h in holidays_for(_J, 2024)}
    got = {h.name: h.date for h in holidays_for(_J, 2025)}
    assert got["Wigilia Bożego Narodzenia"] == AstroDate(2025, 12, 24)
