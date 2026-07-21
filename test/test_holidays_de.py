"""Germany national differential + subdivision behaviour (all 16 Länder).

Per-holiday gold dates for DE live in the shared HOLIDAY_GOLDS registry
(test_holiday_golds.py). Germany applies no weekend substitution, so the national
set agrees exactly with the reference in 2023-2025 (no documented disagreements).
"""
from chronologia import holidays_for
from holiday_testkit import assert_national_differential

_J = "DE"
_EPIPHANY = ("DE-BW", "DE-BY", "DE-ST")


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
