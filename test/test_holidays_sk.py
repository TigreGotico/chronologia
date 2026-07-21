"""Slovakia national differential + the 2023 consolidation year-gates.

Source: zákon NR SR 241/1993 Z. z., as amended by the 2023 consolidation package
(zákon 530/2023 Z. z.). Per-holiday gold dates live in the shared HOLIDAY_GOLDS
registry. Two days lost their work-free status:

* Deň Ústavy SR (1 Sep): work-free until 2023, a normal working day from 2024.
* Deň boja za slobodu a demokraciu (17 Nov): work-free until 2024, a normal
  working day from 2025.

With those year-gates our national set agrees with the reference across 2023-2025.
"""
from chronologia import AstroDate, holidays_for
from holiday_testkit import assert_national_differential

_J = "SK"


def test_national_differential_2023_2025():
    assert_national_differential(_J, (2023, 2024, 2025), {})


def test_constitution_day_lost_workfree_from_2024():
    assert {h.name: h.date for h in holidays_for(_J, 2023)}[
        "Deň Ústavy Slovenskej republiky"] == AstroDate(2023, 9, 1)
    assert "Deň Ústavy Slovenskej republiky" not in {
        h.name for h in holidays_for(_J, 2024)}


def test_nov17_lost_workfree_from_2025():
    assert {h.name: h.date for h in holidays_for(_J, 2024)}[
        "Deň boja za slobodu a demokraciu"] == AstroDate(2024, 11, 17)
    assert "Deň boja za slobodu a demokraciu" not in {
        h.name for h in holidays_for(_J, 2025)}
