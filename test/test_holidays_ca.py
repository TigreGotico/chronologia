"""Canada golds + national differential (federal set + a compact provincial sample).

Golds hand-derived from the federal Holidays Act
(papers/holidays/ca_holidays_act_justice.html) and the provincial statutory
listings cross-checked against vacanza/holidays 0.101 (MIT). Good Friday
recomputes easter(2024) in-test. Victoria Day and Quebec's National Patriots'
Day use the Monday-preceding-25-May rule (WeekdayOnOrBeforeRule); the four
"third Monday of February" provincial days (Family Day / Louis Riel Day /
Heritage Day) and Thanksgiving / BC Day / Labour Day are nth-weekday days.

Documented national differential disagreement (vacanza/holidays 0.101),
adjudicated in the reference's favour:

* 2023 ref-only 2 Jan: 1 Jan 2023 was a Sunday; the reference grants a substitute
  Monday. chronologia carries statutory nominal dates for New Year's Day (only
  Canada Day carries the Holidays Act Sunday->Monday shift), so it does not emit
  the substitute.
"""
import pytest

from chronologia import (AstroDate, WeekdayOnOrBeforeRule, holidays_for)
from holiday_golds import Gold, register
from holiday_testkit import assert_gold, assert_national_differential

_J = "CA"
GOLDS = [
    # --- federal ---
    Gold(_J, None, "New Year's Day", 2024, 1, 1),
    Gold(_J, None, "Good Friday", 2024, 3, 29, easter_offset=-2),
    Gold(_J, None, "Canada Day", 2024, 7, 1),
    Gold(_J, None, "Labour Day", 2024, 9, 2),        # 1st Monday of September
    Gold(_J, None, "Christmas Day", 2024, 12, 25),
    # --- Ontario ---
    Gold(_J, "CA-ON", "Family Day", 2024, 2, 19),    # 3rd Monday of February
    Gold(_J, "CA-ON", "Victoria Day", 2024, 5, 20),  # Monday preceding 25 May
    Gold(_J, "CA-ON", "Thanksgiving Day", 2024, 10, 14),  # 2nd Monday of October
    Gold(_J, "CA-ON", "Boxing Day", 2024, 12, 26),
    # --- Quebec ---
    Gold(_J, "CA-QC", "National Patriots' Day", 2024, 5, 20),
    Gold(_J, "CA-QC", "Saint-Jean-Baptiste", 2024, 6, 24),
    Gold(_J, "CA-QC", "Thanksgiving Day", 2024, 10, 14),
    # --- British Columbia ---
    Gold(_J, "CA-BC", "Family Day", 2024, 2, 19),
    Gold(_J, "CA-BC", "Victoria Day", 2024, 5, 20),
    Gold(_J, "CA-BC", "British Columbia Day", 2024, 8, 5),  # 1st Monday of August
    Gold(_J, "CA-BC", "National Day for Truth and Reconciliation", 2024, 9, 30),
    Gold(_J, "CA-BC", "Thanksgiving Day", 2024, 10, 14),
    Gold(_J, "CA-BC", "Remembrance Day", 2024, 11, 11),
    # --- Alberta ---
    Gold(_J, "CA-AB", "Family Day", 2024, 2, 19),
    Gold(_J, "CA-AB", "Victoria Day", 2024, 5, 20),
    Gold(_J, "CA-AB", "Thanksgiving Day", 2024, 10, 14),
    Gold(_J, "CA-AB", "Remembrance Day", 2024, 11, 11),
    # --- Manitoba ---
    Gold(_J, "CA-MB", "Louis Riel Day", 2024, 2, 19),
    Gold(_J, "CA-MB", "Victoria Day", 2024, 5, 20),
    Gold(_J, "CA-MB", "National Day for Truth and Reconciliation", 2024, 9, 30),
    Gold(_J, "CA-MB", "Thanksgiving Day", 2024, 10, 14),
    # --- Nova Scotia ---
    Gold(_J, "CA-NS", "Heritage Day", 2024, 2, 19),
    Gold(_J, "CA-NS", "Remembrance Day", 2024, 11, 11),
]
register(GOLDS)

_DISAGREEMENTS = {
    2023: {"ref_only": {(1, 2)}},
}


@pytest.mark.parametrize("gold", GOLDS,
                         ids=lambda g: f"{g.subdiv or 'CA'}:{g.name}")
def test_gold_dates(gold):
    assert_gold(gold)


def test_national_differential_2023_2025():
    assert_national_differential(_J, (2023, 2024, 2025), _DISAGREEMENTS)


def test_victoria_day_is_monday_preceding_may_25():
    # Independent re-derivation: the latest Monday on or before 24 May.
    rule = WeekdayOnOrBeforeRule(5, 24, 0)
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
