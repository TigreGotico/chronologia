"""UK national differential + subdivision behaviour (source: gov.uk/bank-holidays).

Per-holiday gold dates for GB live in the shared HOLIDAY_GOLDS registry
(test_holiday_golds.py); this module owns the national differential against the
independent reference package and a few subdivision behaviour checks.

chronologia now models gov.uk substitute ("in-lieu") days via the gb_substitute
policy, so the reference's observed substitutes are matched, not documented away.
The remaining documented disagreements are all one-off royal/special bank
holidays the reference lists and chronologia (recurring rules only) does not, plus
the reference's special relocation of the 2022 Spring Bank Holiday:

* 2022 our-only 30 May: our Spring Bank Holiday sits on its recurring last-Monday-
  of-May date; the reference moved it to 2 Jun 2022 for the Platinum Jubilee.
* 2022 ref-only 2 Jun: that specially-relocated Spring Bank Holiday.
* 2022 ref-only 3 Jun: the one-off Platinum Jubilee bank holiday (2022 only).
* 2022 ref-only 19 Sep: the one-off State Funeral of Queen Elizabeth II (2022).
* 2023 ref-only 8 May: the one-off bank holiday for the Coronation of King
  Charles III (2023 only) — not a recurring rule.

The 2021 Christmas/Boxing substitute cascade (Sat 25 Dec -> Mon 27, Sun 26 Dec ->
Tue 28) and the 2023 New Year substitute (Sun 1 Jan -> Mon 2 Jan) now agree with
the reference exactly; 2021 has no disagreements at all.
"""
from chronologia import AstroDate, holidays_for
from holiday_testkit import assert_national_differential

_J = "GB"
_DISAGREEMENTS = {
    2022: {"our_only": {(5, 30)}, "ref_only": {(6, 2), (6, 3), (9, 19)}},
    2023: {"ref_only": {(5, 8)}},
}


def test_national_differential_2021_2025():
    assert_national_differential(_J, (2021, 2022, 2023, 2024, 2025), _DISAGREEMENTS)


def test_christmas_boxing_substitute_cascade_2021():
    # Christmas Sat 25 Dec -> substitute Mon 27; Boxing Sun 26 Dec -> Tue 28.
    dates = {(h.date.month, h.date.day): h.name for h in holidays_for(_J, 2021)}
    assert dates[(12, 27)] == "Christmas Day (substitute day)"
    assert dates[(12, 28)] == "Boxing Day (substitute day)"
    # The nominal weekend dates are kept too.
    assert (12, 25) in dates and (12, 26) in dates


def test_new_year_substitute_2023():
    dates = {(h.date.month, h.date.day): h.name for h in holidays_for(_J, 2023)}
    assert dates[(1, 2)] == "New Year's Day (substitute day)"


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
