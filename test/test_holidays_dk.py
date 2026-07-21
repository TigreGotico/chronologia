"""Denmark national differential + Store bededag abolition (source: Lov 214/2023).

Per-holiday gold dates live in the shared HOLIDAY_GOLDS registry. Our national set
agrees with the reference across 2023-2025 with no disagreements. Store bededag
(General Prayer Day, 4th Friday after Easter) was abolished as a holiday from 2024
by Lov nr. 214 af 28. februar 2023 — present in 2023, absent from 2024.
"""
from chronologia import AstroDate, holidays_for
from holiday_testkit import assert_national_differential

_J = "DK"


def test_national_differential_2023_2025():
    assert_national_differential(_J, (2023, 2024, 2025), {})


def test_store_bededag_abolished_from_2024():
    assert {h.name: h.date for h in holidays_for(_J, 2023)}[
        "Store bededag"] == AstroDate(2023, 5, 5)
    assert "Store bededag" not in {h.name for h in holidays_for(_J, 2024)}
