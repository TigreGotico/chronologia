"""Ireland national differential + St Brigid's Day behaviour.

Source: Organisation of Working Time Act 1997 + Public Holiday Regulations
(papers/holidays/ie_holidays.md). Per-holiday gold dates live in the shared
HOLIDAY_GOLDS registry; this module owns the national differential.

With the 2022 once-off "Day of Remembrance and Recognition" (18 Mar 2022,
gov.ie proclamation) modelled as a one_off rule, our national set agrees with the
independent reference across 2021-2025 — no documented disagreements. St Brigid's
Day is year-gated from 2023, so 2021 and 2022 correctly omit it.
"""
from chronologia import AstroDate, holidays_for
from holiday_testkit import assert_national_differential

_J = "IE"


def test_national_differential_2021_2025():
    assert_national_differential(_J, (2021, 2022, 2023, 2024, 2025), {})


def test_st_brigid_year_gated_from_2023():
    assert ("Saint Brigid's Day", None) not in {
        (h.name, h.subdiv) for h in holidays_for(_J, 2022)}
    got = {h.name: h.date for h in holidays_for(_J, 2023)}
    assert got["Saint Brigid's Day"] == AstroDate(2023, 2, 6)  # 1st Mon Feb


def test_2022_day_of_remembrance_is_one_off():
    y2022 = {(h.date.month, h.date.day): h.name for h in holidays_for(_J, 2022)}
    assert y2022[(3, 18)] == "Day of Remembrance and Recognition"
    for other in (2021, 2023):
        assert "Day of Remembrance and Recognition" not in {
            h.name for h in holidays_for(_J, other)}
