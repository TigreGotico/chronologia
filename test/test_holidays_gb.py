"""UK national differential + subdivision behaviour (source: gov.uk/bank-holidays).

Per-holiday gold dates for GB live in the shared HOLIDAY_GOLDS registry
(test_holiday_golds.py); this module owns the national differential against the
independent reference package and a few subdivision behaviour checks.

Documented national differential disagreements (vacanza/holidays), all
adjudicated in the reference's favour — chronologia deliberately omits substitute
("in lieu") days and one-off royal bank holidays:

* 2023 ref-only 2 Jan: substitute Monday for New Year's Day (1 Jan 2023 was a
  Sunday). chronologia carries statutory nominal dates only.
* 2023 ref-only 8 May: the one-off bank holiday for the Coronation of King
  Charles III (2023 only) — not a recurring rule.
"""
from chronologia import AstroDate, holidays_for
from holiday_testkit import assert_national_differential

_J = "GB"
_DISAGREEMENTS = {
    2023: {"ref_only": {(1, 2), (5, 8)}},
}


def test_national_differential_2023_2025():
    assert_national_differential(_J, (2023, 2024, 2025), _DISAGREEMENTS)


def test_scotland_has_st_andrews_but_england_does_not():
    sct = {h.name for h in holidays_for(_J, 2024, subdiv="GB-SCT")}
    eaw = {h.name for h in holidays_for(_J, 2024, subdiv="GB-EAW")}
    assert "St Andrew's Day" in sct and "St Andrew's Day" not in eaw


def test_northern_ireland_battle_of_the_boyne_july_12():
    nir = holidays_for(_J, 2024, subdiv="GB-NIR")
    assert AstroDate(2024, 7, 12) in {h.date for h in nir if h.subdiv == "GB-NIR"}


def test_scotland_summer_bank_holiday_precedes_england():
    # Scotland: 1st Monday of Aug (5th); England: last Monday (26th).
    sct = [h for h in holidays_for(_J, 2024, subdiv="GB-SCT")
           if h.name == "Summer Bank Holiday" and h.subdiv == "GB-SCT"]
    eaw = [h for h in holidays_for(_J, 2024, subdiv="GB-EAW")
           if h.name == "Summer Bank Holiday" and h.subdiv == "GB-EAW"]
    assert sct[0].date == AstroDate(2024, 8, 5)
    assert eaw[0].date == AstroDate(2024, 8, 26)
