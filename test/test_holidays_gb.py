"""UK bank-holiday golds + national differential (source: gov.uk/bank-holidays).

Every gold is hand-derived from the gov.uk bank-holidays listing
(papers/holidays/gb_bank_holidays_govuk.html). Movable days recompute
easter(2024) in-test; nth-weekday bank holidays carry the 2024 calendar date the
listing publishes. Subdivisions: GB-EAW (England & Wales), GB-SCT (Scotland),
GB-NIR (Northern Ireland).

Documented national differential disagreements (vacanza/holidays 0.101), all
adjudicated in the reference's favour — chronologia deliberately omits
substitute ("in lieu") days and one-off royal bank holidays:

* 2023 ref-only 1 Jan substitute (2 Jan): 1 Jan 2023 was a Sunday; gov.uk grants
  a substitute Monday. chronologia carries statutory nominal dates only.
* 2023 ref-only 8 May: the one-off bank holiday for the Coronation of King
  Charles III (proclaimed for 2023 only) — not a recurring rule.
"""
import pytest

from chronologia import AstroDate, holidays_for
from holiday_golds import Gold, register
from holiday_testkit import assert_gold, assert_national_differential

_J = "GB"
GOLDS = [
    # --- UK-wide (all three regions), 2024 ---
    Gold(_J, None, "New Year's Day", 2024, 1, 1),
    Gold(_J, None, "Good Friday", 2024, 3, 29, easter_offset=-2),
    Gold(_J, None, "Early May Bank Holiday", 2024, 5, 6),   # 1st Monday of May
    Gold(_J, None, "Spring Bank Holiday", 2024, 5, 27),     # last Monday of May
    Gold(_J, None, "Christmas Day", 2024, 12, 25),
    Gold(_J, None, "Boxing Day", 2024, 12, 26),
    # --- England & Wales ---
    Gold(_J, "GB-EAW", "Easter Monday", 2024, 4, 1, easter_offset=1),
    Gold(_J, "GB-EAW", "Summer Bank Holiday", 2024, 8, 26),  # last Monday of Aug
    # --- Scotland ---
    Gold(_J, "GB-SCT", "2nd January", 2024, 1, 2),
    Gold(_J, "GB-SCT", "Summer Bank Holiday", 2024, 8, 5),   # 1st Monday of Aug
    Gold(_J, "GB-SCT", "St Andrew's Day", 2024, 11, 30),
    # --- Northern Ireland ---
    Gold(_J, "GB-NIR", "St Patrick's Day", 2024, 3, 17),
    Gold(_J, "GB-NIR", "Easter Monday", 2024, 4, 1, easter_offset=1),
    Gold(_J, "GB-NIR", "Battle of the Boyne", 2024, 7, 12),
    Gold(_J, "GB-NIR", "Summer Bank Holiday", 2024, 8, 26),  # last Monday of Aug
]
register(GOLDS)

_DISAGREEMENTS = {
    2023: {"ref_only": {(1, 2), (5, 8)}},
}


@pytest.mark.parametrize("gold", GOLDS, ids=lambda g: f"{g.subdiv or 'GB'}:{g.name}")
def test_gold_dates(gold):
    assert_gold(gold)


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
