"""Finland national differential + dual-language names (source: Finlex).

Per-holiday gold dates live in the shared HOLIDAY_GOLDS registry. Finnish and
Swedish are both official, so each holiday name carries both. Our national set
agrees with the reference across 2023-2025 with no disagreements.
"""
from chronologia import AstroDate, holidays_for
from holiday_testkit import assert_national_differential

_J = "FI"


def test_national_differential_2023_2025():
    assert_national_differential(_J, (2023, 2024, 2025), {})


def test_names_carry_finnish_and_swedish():
    names = {h.name for h in holidays_for(_J, 2024)}
    assert "Joulupäivä / Juldagen" in names
    assert "Vappu / Första maj" in names


def test_midsummer_eve_and_day_2024():
    got = {h.name: h.date for h in holidays_for(_J, 2024)}
    # Midsummer Eve = Friday (21 Jun 2024); Midsummer Day = Saturday (22 Jun).
    assert got["Juhannusaatto / Midsommarafton"] == AstroDate(2024, 6, 21)
    assert got["Juhannuspäivä / Midsommardagen"] == AstroDate(2024, 6, 22)
    assert got["Pyhäinpäivä / Alla helgons dag"] == AstroDate(2024, 11, 2)
