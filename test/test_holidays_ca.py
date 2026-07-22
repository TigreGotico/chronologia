"""Canada national differential + provincial behaviour (federal + compact sample).

Per-holiday gold dates for CA live in the shared HOLIDAY_GOLDS registry
(test_holiday_golds.py). This module owns the national differential and the rule
behaviours that distinguish provinces (the Monday-preceding-25-May rule, the
Canada Day Sunday shift, and Nova Scotia's lack of Victoria Day).

Documented national differential disagreement (vacanza/holidays), adjudicated in
the reference's favour:

* 2023 ref-only 2 Jan: substitute Monday for New Year's Day (1 Jan 2023 was a
  Sunday). Only Canada Day carries the Holidays Act Sunday->Monday shift; New
  Year's Day keeps its statutory nominal date.
"""
from chronologia import AstroDate, NearestWeekdayRule, holidays_for
from holiday_testkit import assert_national_differential

_J = "CA"
_DISAGREEMENTS = {
    2023: {"ref_only": {(1, 2)}},
}


def test_national_differential_2023_2025():
    assert_national_differential(_J, (2023, 2024, 2025), _DISAGREEMENTS)


def test_victoria_day_is_monday_preceding_may_25():
    # Independent re-derivation: the latest Monday on or before 24 May.
    rule = NearestWeekdayRule(5, 24, 0, -1)
    for year, expected in ((2023, (5, 22)), (2024, (5, 20)), (2025, (5, 19))):
        d = rule.observances(year)[0][0]
        assert (d.month, d.day) == expected


def test_canada_day_sunday_shifts_to_monday():
    # 1 July 2018 was a Sunday -> observed Monday 2 July.
    got = [h for h in holidays_for(_J, 2018) if h.name == "Canada Day"]
    assert got[0].date == AstroDate(2018, 7, 2)


def test_nova_scotia_has_no_victoria_day():
    ns = {h.name for h in holidays_for(_J, 2024, subdiv="CA-NS")}
    assert "Victoria Day" not in ns
