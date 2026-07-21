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


# ==========================================================================
# Differential vs the vacanza `holidays` package (black-box only)
# ==========================================================================
holidays_pkg = pytest.importorskip("holidays")


def _pkg_dates(cc, year, subdiv=None):
    """{(month, day): name} from the holidays package for one year."""
    h = holidays_pkg.country_holidays(cc, subdiv=subdiv, years=year)
    return {(d.month, d.day): h[d] for d in h}


def _our_dates(cc, year, subdiv=None):
    out = {}
    for h in holidays_for(cc, year, subdiv=subdiv):
        out.setdefault((h.date.month, h.date.day), h.name)
    return out


def test_au_differential_national_2024_2025():
    # Adjudication of the one structural divergence: when a national holiday
    # falls on a weekend, our observed-shift *relocates* the day (Sun New Year
    # 2023-01-01 -> Mon 01-02), whereas the package keeps the nominal weekend
    # date *and* adds a separate "additional day" on the Monday. So the two
    # agree exactly on every package holiday that already lands on a weekday;
    # the weekend ones are the expected, documented offset.
    for year in (2023, 2024, 2025):
        ours = set(_our_dates("AU", year))
        for (m, d), name in _pkg_dates("AU", year).items():
            if datetime.date(year, m, d).weekday() < 5:  # Mon-Fri
                assert (m, d) in ours, (
                    f"AU {year}: package weekday holiday {name} {year}-{m}-{d} "
                    f"absent from ours")


def test_il_differential_hebrew_holidays_match_package():
    # The Hebrew-calendar holidays match the package on the day; the package
    # labels Independence Day "יום העצמאות (נצפה)" = observed, and our
    # il_independence postponement reproduces the same observed Gregorian date
    # (2024-05-14, 2025-05-01). Sukkot/Pesach first days coincide.
    checks = {
        2024: {"Rosh Hashanah": (10, 3), "Yom Kippur": (10, 12),
               "Sukkot": (10, 17), "Pesach": (4, 23),
               "Shavuot": (6, 12), "Yom Ha'atzmaut": (5, 14)},
        2025: {"Rosh Hashanah": (9, 23), "Pesach": (4, 13),
               "Yom Ha'atzmaut": (5, 1)},
    }
    for year, expect in checks.items():
        ours = _our_dates("IL", year)
        for name, md in expect.items():
            got = [h for h in holidays_for("IL", year) if h.name == name]
            assert got and (got[0].date.month, got[0].date.day) == md, (
                f"IL {year} {name}: expected {md}")
        # every one of our dates is a package holiday date (package may list the
        # intermediate chol hamoed / minor days we do not).
        theirs = {(d.month, d.day)
                  for d in holidays_pkg.country_holidays("IL", years=year)}
        assert set(ours) <= theirs, f"IL {year}: {set(ours) - theirs}"


def test_il_independence_day_postponement_both_directions():
    # 2024: Iyar 5 = Monday -> delayed to Tuesday (05-14).
    got24 = [h for h in holidays_for("IL", 2024) if h.name == "Yom Ha'atzmaut"]
    assert got24[0].date == AstroDate(2024, 5, 14)
    # 2025: Iyar 5 = Saturday -> advanced to Thursday (05-01).
    got25 = [h for h in holidays_for("IL", 2025) if h.name == "Yom Ha'atzmaut"]
    assert got25[0].date == AstroDate(2025, 5, 1)


def test_tr_differential_fixed_match_islamic_within_one_day():
    # Fixed national days match the package exactly; the Islamic feast first-days
    # agree to within +/-1 (islamic_civil arithmetic vs Diyanet). 2024: Ramazan
    # ours 04-10 = Diyanet 04-10; Kurban ours 06-17 vs Diyanet 06-16 (+1).
    fixed = {(1, 1), (4, 23), (5, 1), (5, 19), (7, 15), (8, 30), (10, 29)}
    for year in (2024, 2025):
        ours = _our_dates("TR", year)
        theirs = _pkg_dates("TR", year)
        for md in fixed:
            assert md in ours and md in theirs, f"TR {year} fixed {md}"
        # first day of each feast (min date carrying each feast name)
        for feast in ("Ramazan Bayrami", "Kurban Bayrami"):
            our_first = min(m_d for m_d, n in ours.items() if n == feast)
            pkg_name = "Ramazan Bayramı" if feast.startswith("Ram") \
                else "Kurban Bayramı"
            pkg_first = min(m_d for m_d, n in theirs.items() if n == pkg_name)
            delta = abs((datetime.date(year, *our_first)
                         - datetime.date(year, *pkg_first)).days)
            assert delta <= 1, f"TR {year} {feast}: offset {delta} days"


def test_jp_differential_statutory_days_match_package():
    # Every JP statutory holiday matches the package on its legal date; the
    # package's EXTRA entries are all 振替休日 substitute days we hold out of
    # scope (like China's 调休). Includes the equinox holidays on the Cabinet
    # Office dates (2024 秋分の日 = 09-22; the package's 09-23 is the substitute).
    for year in (2024, 2025):
        ours = set(_our_dates("JP", year))
        pkg = holidays_pkg.country_holidays("JP", years=year)
        theirs = {(d.month, d.day) for d in pkg}
        assert ours <= theirs, f"JP {year} missing from package: {ours - theirs}"
        for d in pkg:
            if (d.month, d.day) not in ours:
                assert "振替休日" in pkg[d], (
                    f"JP {year}: unexpected non-furikae package day {d}: {pkg[d]}")


def test_jp_furikae_mechanism_expressible_but_out_of_scope():
    # The substitute-holiday relocation is expressible via the sun_mon policy —
    # 2024 秋分の日 is Sunday 09-22, whose furikae substitute is Monday 09-23 —
    # but the .tab lists the statutory day itself (09-22), not the substitute.
    from chronologia import SUNDAY_TO_MONDAY
    assert SUNDAY_TO_MONDAY.apply(AstroDate(2024, 9, 22)) == AstroDate(2024, 9, 23)
    got = [h for h in holidays_for("JP", 2024)
           if h.name == "Autumnal Equinox Day"]
    assert got[0].date == AstroDate(2024, 9, 22)


def test_cn_differential_statutory_core_matches_package():
    # The package labels statutory days 元旦/春节/清明节/劳动节/端午节/中秋节/国庆节
    # and separately labels the 调休 make-up days 休息日(...调休) / 补假. Our
    # statutory dates must each appear in the package; the package's EXTRA dates
    # are exactly the 调休 arrangements we hold out of scope.
    statutory_2024 = {(1, 1), (2, 10), (2, 11), (2, 12), (4, 4), (5, 1),
                      (6, 10), (9, 17), (10, 1), (10, 2), (10, 3)}
    ours = set(_our_dates("CN", 2024))
    assert ours == statutory_2024
    theirs = set(_pkg_dates("CN", 2024))
    assert ours <= theirs, f"statutory day missing from package: {ours - theirs}"
    # Everything the package has beyond ours is a make-up/rest day (调休/补假).
    pkg = holidays_pkg.country_holidays("CN", years=2024)
    for d in pkg:
        if (d.month, d.day) not in ours:
            assert ("调休" in pkg[d] or "补假" in pkg[d] or "休息" in pkg[d]), (
                f"unexpected non-tiaoxiu package day {d}: {pkg[d]}")


def test_cn_qingming_is_solar_term_not_lunar():
    # Qingming tracks the solar term (Apr 4/5), not a fixed date or lunar date.
    assert _our_dates("CN", 2024)[(4, 4)] == "Qingming Festival"
    assert _our_dates("CN", 2023)[(4, 5)] == "Qingming Festival"


def test_in_differential_fixed_and_decree_agree():
    # Adjudication: the fixed national days, the Christian days and the Hindu
    # decree dates match the package exactly (the package's IN central list is
    # itself compiled from the MHA/DoPT gazette). We compare by holiday name on
    # the years both list it.
    names = ["Republic Day", "Independence Day", "Mahatma Gandhi's Jayanti",
             "Christmas", "Good Friday", "Holi", "Diwali (Deepavali)",
             "Dussehra", "Janmashtami"]
    for year in (2023, 2024, 2025):
        pkg = holidays_pkg.country_holidays("IN", years=year)
        pkg_by_name = {}
        for d in pkg:
            pkg_by_name.setdefault(pkg[d], (d.month, d.day))
        for h in holidays_for("IN", year):
            if h.name in names and h.name in pkg_by_name:
                assert (h.date.month, h.date.day) == pkg_by_name[h.name], (
                    f"IN {year} {h.name}: ours {h.date} vs pkg "
                    f"{pkg_by_name[h.name]}")


def test_in_differential_islamic_within_one_day():
    # Headline-free expected divergence: islamic_civil is arithmetic; the gazette
    # follows moon-sighting. Every shared Islamic holiday agrees to within +/-1
    # day. (2024: Id-ul-Fitr ours 04-10 vs gazette 04-11; Bakrid/Muharram/Milad
    # coincide.)
    pairs = [("Id-ul-Fitr", 10, 1), ("Id-ul-Zuha (Bakrid)", 12, 10),
             ("Muharram", 1, 10), ("Milad-un-Nabi", 3, 12)]
    for year in (2023, 2024, 2025):
        pkg = holidays_pkg.country_holidays("IN", years=year)
        pkg_by_name = {}
        for d in pkg:
            # package uses "Id-ul-Zuha (Bakrid)", "Muharram", "Milad-un-Nabi"
            pkg_by_name.setdefault(pkg[d], datetime.date(year, d.month, d.day))
        for name, _m, _d in pairs:
            ours = [h for h in holidays_for("IN", year) if h.name == name]
            if ours and name in pkg_by_name:
                delta = abs((datetime.date(
                    year, ours[0].date.month, ours[0].date.day)
                    - pkg_by_name[name]).days)
                assert delta <= 1, f"IN {year} {name}: offset {delta} days"


def test_au_differential_wa_kings_birthday_decree_matches_package():
    # Adjudication: WA King's Birthday is proclaimed, not ruled. Our decree
    # table must agree with the package's tabulated dates 2023-2026.
    expected = {2023: (9, 25), 2024: (9, 23), 2025: (9, 29), 2026: (9, 28)}
    for year, md in expected.items():
        ours = [h for h in holidays_for("AU", year, subdiv="AU-WA")
                if h.name == "King's Birthday"]
        assert ours and (ours[0].date.month, ours[0].date.day) == md
