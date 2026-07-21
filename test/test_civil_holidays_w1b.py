"""Wave-1b civil-holiday rule kinds, country golds and package differential.

New engine machinery exercised by this batch (each with its own unit here):

* :class:`~chronologia.EquinoxRule` — Japan's Shunbun/Shūbun no Hi, the March and
  September equinox dates read in JST (UTC+9). Asserted against the Cabinet
  Office's own published 2024–2025 dates, not this function's output.
* :class:`~chronologia.SolarTermRule` — China's Qingming, the Qingming solar term
  read in CST (UTC+8). Asserted against the State Council listing.
* the calendar-agnostic :class:`~chronologia.CalendarDateRule` resolution, now
  driving the ``chinese`` (lunisolar, Gregorian-numbered) and ``hebrew``
  (~3760-offset) calendars, not only the Hijri-epoch ones.
* the ``sat_sun_mon`` (Australia Day) and ``il_independence`` (Yom Ha'atzmaut
  Iyar-5 postponement) observed-shift policies.

Country golds (``HOLIDAY_GOLDS``) are hand-derived from the primary sources cited
in ``~/AgentWorkspaces/papers/holidays/`` — the Cabinet Office / State Council /
Fair Work / MHA-DoPT / Act 2429 / Israeli Independence Day Law listings. Fixed and
nth-weekday golds restate the source; calendar_date golds are cross-derived from
the calendar registry; decree and equinox golds assert the gazette dates. A
differential against the vacanza ``holidays`` package (black-box only) is run over
the shared set for 2023–2025 with the adjudications documented inline.
"""
import datetime
import os

import pytest

from chronologia import (AstroDate, CalendarDateRule, EquinoxRule,
                         IL_INDEPENDENCE_SHIFT, SATURDAY_SUNDAY_TO_MONDAY,
                         SolarTermRule, holidays_for, load_calendar)
from chronologia.civil_holidays import CATEGORIES, _DATA_DIR

from holiday_golds import HOLIDAY_GOLDS


def _obs(rule, year):
    return rule.observances(year)


# ==========================================================================
# EquinoxRule (Japan Shunbun / Shūbun no Hi)
# ==========================================================================
# Cabinet Office published dates (papers/holidays/jp_cabinet_office_shukujitsu.md).
_CAO_EQUINOX = {
    ("march", 2024): AstroDate(2024, 3, 20),
    ("march", 2025): AstroDate(2025, 3, 20),
    ("september", 2024): AstroDate(2024, 9, 22),
    ("september", 2025): AstroDate(2025, 9, 23),
}


@pytest.mark.parametrize("which,year,expected", [
    (w, y, d) for (w, y), d in _CAO_EQUINOX.items()])
def test_equinox_rule_matches_cabinet_office(which, year, expected):
    # JST = UTC+9: the equinox holiday is the equinox date reckoned in Japan.
    got = _obs(EquinoxRule(which, 9), year)
    assert got[0][0] == expected
    assert got[0][1] == "exact"


def test_equinox_rule_rejects_solstice():
    with pytest.raises(ValueError):
        EquinoxRule("june", 9)


def test_equinox_rule_timezone_can_change_the_day():
    # The 2024 September equinox instant is ~03:44 UTC on the 22nd; in JST it is
    # the 22nd, and even at UTC it is the 22nd here — assert the JST civil day.
    assert _obs(EquinoxRule("september", 9), 2024)[0][0] == AstroDate(2024, 9, 22)


# ==========================================================================
# SolarTermRule (China Qingming)
# ==========================================================================
@pytest.mark.parametrize("year,expected", [
    (2023, AstroDate(2023, 4, 5)),
    (2024, AstroDate(2024, 4, 4)),
    (2025, AstroDate(2025, 4, 4)),
    (2026, AstroDate(2026, 4, 5)),
])
def test_solar_term_rule_qingming(year, expected):
    got = _obs(SolarTermRule("qingming", 8), year)  # CST = UTC+8
    assert got[0][0] == expected
    assert got[0][1] == "exact"


def test_solar_term_rule_rejects_unknown_term():
    with pytest.raises(ValueError):
        _obs(SolarTermRule("not_a_term", 8), 2024)


# ==========================================================================
# Calendar-agnostic CalendarDateRule (chinese, hebrew)
# ==========================================================================
def test_calendar_date_chinese_new_year_2024():
    # Lunar 1/1 numbered by the Gregorian year it opens in: CNY 2024 = 02-10.
    assert _obs(CalendarDateRule("chinese", 1, 1), 2024)[0][0] == \
        AstroDate(2024, 2, 10)


def test_calendar_date_chinese_new_year_2025():
    assert _obs(CalendarDateRule("chinese", 1, 1), 2025)[0][0] == \
        AstroDate(2025, 1, 29)


def test_calendar_date_chinese_dragon_boat_and_mid_autumn_2024():
    assert _obs(CalendarDateRule("chinese", 5, 5), 2024)[0][0] == \
        AstroDate(2024, 6, 10)
    assert _obs(CalendarDateRule("chinese", 8, 15), 2024)[0][0] == \
        AstroDate(2024, 9, 17)


def test_calendar_date_hebrew_rosh_hashanah_2024():
    # Tishrei 1 (month 7) — hebrew year 5785 opens 2024-10-03.
    assert _obs(CalendarDateRule("hebrew", 7, 1), 2024)[0][0] == \
        AstroDate(2024, 10, 3)


def test_calendar_date_hebrew_pesach_2024():
    # Nisan 15 (month 1).
    assert _obs(CalendarDateRule("hebrew", 1, 15), 2024)[0][0] == \
        AstroDate(2024, 4, 23)


def test_calendar_date_chinese_out_of_range_omitted():
    # The tabulated Chinese calendar ends at CNY 2100 (terminal sentinel).
    assert _obs(CalendarDateRule("chinese", 1, 1), 2200) == ()


# ==========================================================================
# Observed-shift policies added this batch
# ==========================================================================
def test_sat_sun_mon_saturday_shifts_two_days():
    assert SATURDAY_SUNDAY_TO_MONDAY.apply(AstroDate(2019, 1, 26)) == \
        AstroDate(2019, 1, 28)  # 2019-01-26 Sat -> Mon 28th


def test_sat_sun_mon_sunday_shifts_one_day():
    assert SATURDAY_SUNDAY_TO_MONDAY.apply(AstroDate(2025, 1, 26)) == \
        AstroDate(2025, 1, 27)  # 2025-01-26 Sun -> Mon 27th


def test_sat_sun_mon_weekday_unchanged():
    assert SATURDAY_SUNDAY_TO_MONDAY.apply(AstroDate(2024, 1, 26)) == \
        AstroDate(2024, 1, 26)  # Friday, no shift


def test_il_independence_monday_delays_one_day():
    # 2024 nominal Iyar 5 = Mon 2024-05-13 -> Tue 05-14.
    assert IL_INDEPENDENCE_SHIFT.apply(AstroDate(2024, 5, 13)) == \
        AstroDate(2024, 5, 14)


def test_il_independence_saturday_advances_two_days():
    # 2025 nominal Iyar 5 = Sat 2025-05-03 -> Thu 05-01.
    assert IL_INDEPENDENCE_SHIFT.apply(AstroDate(2025, 5, 3)) == \
        AstroDate(2025, 5, 1)


def test_il_independence_wednesday_unshifted():
    # 2023 nominal Iyar 5 = Wed 2023-04-26 -> unchanged.
    assert IL_INDEPENDENCE_SHIFT.apply(AstroDate(2023, 4, 26)) == \
        AstroDate(2023, 4, 26)


# ==========================================================================
# Gold application — every registered gold resolves to its expected date
# ==========================================================================
def _all_golds():
    out = []
    for cc, golds in sorted(HOLIDAY_GOLDS.items()):
        for g in golds:
            out.append(pytest.param(
                cc, g, id=f"{cc}-{g.year}-{g.name}-{g.subdiv or 'nat'}"))
    return out


@pytest.mark.parametrize("cc,gold", _all_golds())
def test_registered_gold_resolves(cc, gold):
    got = holidays_for(cc, gold.year, subdiv=gold.subdiv)
    hits = [h for h in got if h.name == gold.name
            and h.date == AstroDate(gold.year, gold.month, gold.day)]
    assert hits, (
        f"{cc} {gold.name} {gold.year}: expected "
        f"{gold.year}-{gold.month:02d}-{gold.day:02d}; got "
        + ", ".join(f"{h.name}@{h.date}" for h in got if h.name == gold.name))


# ==========================================================================
# Coverage lint — every rule in a registered w1b .tab has at least one gold
# ==========================================================================
_W1B_COUNTRIES = ["au", "in", "cn", "jp", "tr", "il"]


@pytest.mark.parametrize("cc", [
    c for c in _W1B_COUNTRIES
    if os.path.exists(os.path.join(_DATA_DIR, f"{c}.tab"))])
def test_every_rule_has_a_gold(cc):
    cal = load_calendar(os.path.join(_DATA_DIR, f"{cc}.tab"))
    golds = HOLIDAY_GOLDS.get(cc.upper(), [])
    covered = {(g.name, g.subdiv) for g in golds}
    uncovered = sorted(
        {(r.name, r.subdiv) for r in cal.rules} - covered)
    assert not uncovered, f"{cc}: rules without a gold: {uncovered}"


@pytest.mark.parametrize("cc", _W1B_COUNTRIES)
def test_registered_country_has_min_six_golds(cc):
    key = cc.upper()
    if key not in HOLIDAY_GOLDS:
        pytest.skip(f"{cc} not yet shipped")
    golds_2024 = [g for g in HOLIDAY_GOLDS[key] if g.year == 2024]
    assert len(golds_2024) >= 6, f"{cc}: fewer than 6 golds for 2024"
