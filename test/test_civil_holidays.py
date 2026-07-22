"""Civil holidays: rule kinds, the Portugal municipal pilot, US and SA golds.

Golds are hand-derived from primary sources cited in
``~/AgentWorkspaces/papers/holidays/`` (the OPM/Wikipedia federal list, the
Público-holidays-in-Portugal page carrying Código do Trabalho art. 234, and the
Umm al-Qura table already in the calendar registry). Includes rule-kind units,
the observed-shift golds, calendar_date out-of-range behaviour, subdivision and
category filtering, adversarial inputs, and a data-file lint over every
``holiday_data/*.tab``.
"""
import os

import pytest

from chronologia import (AstroDate, CalendarDateRule, CivilHoliday,
                         DecreeTableRule, OneOffRule, EasterOffsetRule,
                         FixedRule, HolidayCalendar, HolidayRule, NthWeekdayRule,
                         ObservedShift, SUNDAY_TO_MONDAY, US_OBSERVED_SHIFT,
                         holidays_for, is_civil_holiday, load_calendar)
from chronologia.civil_holidays import CATEGORIES, _DATA_DIR, _day_span


def _date(rule, year, i=0):
    return rule.observances(year)[i][0]


# --------------------------------------------------------------------------
# Rule-kind units
# --------------------------------------------------------------------------
def test_fixed_rule_same_date_every_year():
    r = FixedRule(1, 1)
    assert _date(r, 2024) == AstroDate(2024, 1, 1)
    assert _date(r, 1789) == AstroDate(1789, 1, 1)


def test_fixed_rule_basis_exact():
    assert FixedRule(12, 25).observances(2024)[0][1] == "exact"


def test_fixed_rule_rejects_bad_month():
    with pytest.raises(ValueError):
        FixedRule(13, 1)


def test_fixed_rule_rejects_bad_day():
    with pytest.raises(ValueError):
        FixedRule(1, 32)


def test_one_off_resolves_only_in_its_year():
    r = OneOffRule(2023, 5, 8, "https://example.gov/coronation")
    assert _date(r, 2023) == AstroDate(2023, 5, 8)
    assert r.observances(2022) == ()
    assert r.observances(2024) == ()


def test_one_off_basis_tabulated():
    r = OneOffRule(2022, 6, 3, "https://www.gov.uk/bank-holidays")
    assert r.observances(2022)[0][1] == "tabulated"


def test_one_off_requires_citation():
    with pytest.raises(ValueError):
        OneOffRule(2022, 6, 3, "   ")


def test_one_off_rejects_bad_date():
    with pytest.raises(ValueError):
        OneOffRule(2022, 13, 3, "cite")


def test_nth_weekday_third_monday_january_2024():
    # US MLK Day 2024 = 2024-01-15.
    assert _date(NthWeekdayRule(1, 3, 0), 2024) == AstroDate(2024, 1, 15)


def test_nth_weekday_last_monday_may_2024():
    # US Memorial Day 2024 = 2024-05-27.
    assert _date(NthWeekdayRule(5, -1, 0), 2024) == AstroDate(2024, 5, 27)


def test_nth_weekday_fourth_thursday_november_2024():
    # Thanksgiving 2024 = 2024-11-28.
    assert _date(NthWeekdayRule(11, 4, 3), 2024) == AstroDate(2024, 11, 28)


def test_nth_weekday_post_offset_monday_after_second_sunday_july():
    # 2024: 2nd Sunday of July is 2024-07-14, the Monday after is 2024-07-15.
    assert _date(NthWeekdayRule(7, 2, 6, 1), 2024) == AstroDate(2024, 7, 15)


def test_nth_weekday_rejects_zero_ordinal():
    with pytest.raises(ValueError):
        NthWeekdayRule(1, 0, 0)


def test_nth_weekday_rejects_bad_weekday():
    with pytest.raises(ValueError):
        NthWeekdayRule(1, 1, 7)


def test_easter_offset_good_friday_2024():
    # Good Friday 2024 = Easter (03-31) - 2 = 2024-03-29.
    assert _date(EasterOffsetRule(-2), 2024) == AstroDate(2024, 3, 29)


def test_easter_offset_easter_sunday_itself():
    assert _date(EasterOffsetRule(0), 2024) == AstroDate(2024, 3, 31)


def test_easter_offset_corpus_christi_2024():
    # Corpo de Deus = Easter + 60 = 2024-05-30.
    assert _date(EasterOffsetRule(60), 2024) == AstroDate(2024, 5, 30)


def test_easter_offset_ascension_is_39():
    # Ascension = Easter + 39 = 2024-05-09.
    assert _date(EasterOffsetRule(39), 2024) == AstroDate(2024, 5, 9)


def test_easter_offset_rejects_bad_method():
    with pytest.raises(ValueError):
        EasterOffsetRule(1, "orthodox")


def test_easter_offset_julian_method_allowed():
    r = EasterOffsetRule(1, "julian_gregorian_date")
    # Orthodox Easter 2024 civil = 2024-05-05, Monday after = 2024-05-06.
    assert _date(r, 2024) == AstroDate(2024, 5, 6)


def test_calendar_date_eid_al_fitr_2024_tabulated():
    r = CalendarDateRule("umm_al_qura", 10, 1)
    obs = r.observances(2024)
    assert obs[0][0] == AstroDate(2024, 4, 10)
    assert obs[0][1] == "tabulated"


def test_calendar_date_eid_al_adha_2024():
    assert _date(CalendarDateRule("umm_al_qura", 12, 10), 2024) == \
        AstroDate(2024, 6, 16)


def test_calendar_date_out_of_range_omitted():
    # Gregorian 2100 -> ~AH 1523, past the Umm al-Qura table -> no occurrence.
    assert CalendarDateRule("umm_al_qura", 10, 1).observances(2100) == ()


def test_calendar_date_rejects_unknown_calendar():
    with pytest.raises(ValueError):
        CalendarDateRule("mayan_nonsense", 1, 1)


def test_decree_table_rule_matches_year():
    r = DecreeTableRule(((2024, (5, 1)), (2025, (5, 2))))
    assert _date(r, 2024) == AstroDate(2024, 5, 1)
    assert _date(r, 2025) == AstroDate(2025, 5, 2)


def test_decree_table_basis_tabulated():
    assert DecreeTableRule(((2024, (1, 1)),)).observances(2024)[0][1] == \
        "tabulated"


def test_decree_table_absent_year_empty():
    assert DecreeTableRule(((2024, (1, 1)),)).observances(2030) == ()


# --------------------------------------------------------------------------
# Observed-shift modifier
# --------------------------------------------------------------------------
def test_us_shift_saturday_to_friday():
    # 2021-12-25 is a Saturday -> observed Friday 2021-12-24.
    assert US_OBSERVED_SHIFT.apply(AstroDate(2021, 12, 25)) == \
        AstroDate(2021, 12, 24)


def test_us_shift_sunday_to_monday():
    # 2021-07-04 is a Sunday -> observed Monday 2021-07-05.
    assert US_OBSERVED_SHIFT.apply(AstroDate(2021, 7, 4)) == \
        AstroDate(2021, 7, 5)


def test_us_shift_weekday_unchanged():
    # 2024-07-04 is a Thursday -> unchanged.
    assert US_OBSERVED_SHIFT.apply(AstroDate(2024, 7, 4)) == \
        AstroDate(2024, 7, 4)


def test_sunday_to_monday_leaves_saturday():
    assert SUNDAY_TO_MONDAY.apply(AstroDate(2022, 1, 1)) == \
        AstroDate(2022, 1, 1)


def test_holiday_rule_applies_observed_shift():
    rule = HolidayRule("X", FixedRule(7, 4), frozenset({"public"}),
                       observed=US_OBSERVED_SHIFT)
    assert rule.resolve(2021)[0][0] == AstroDate(2021, 7, 5)


# --------------------------------------------------------------------------
# Portugal national golds (Código do Trabalho art. 234, 2024)
# --------------------------------------------------------------------------
_PT_NATIONAL_2024 = {
    (1, 1), (3, 29), (3, 31), (4, 25), (5, 1), (5, 30), (6, 10),
    (8, 15), (10, 5), (11, 1), (12, 1), (12, 8), (12, 25),
}


def test_pt_national_2024_thirteen_public_days():
    pub = [h for h in holidays_for("PT", 2024)
           if h.subdiv is None and "public" in h.categories
           and h.name != "Carnaval"]
    got = {(h.date.month, h.date.day) for h in pub}
    assert got == _PT_NATIONAL_2024
    assert len(pub) == 13


def test_pt_sexta_feira_santa_2024():
    got = [h for h in holidays_for("PT", 2024) if h.name == "Sexta-feira Santa"]
    assert got[0].date == AstroDate(2024, 3, 29)
    assert got[0].categories == frozenset({"public", "religious"})


def test_pt_corpo_de_deus_2024():
    got = [h for h in holidays_for("PT", 2024) if h.name == "Corpo de Deus"]
    assert got[0].date == AstroDate(2024, 5, 30)


def test_pt_carnaval_facultative_present():
    got = [h for h in holidays_for("PT", 2024) if h.name == "Carnaval"]
    assert got[0].date == AstroDate(2024, 2, 13)


# --------------------------------------------------------------------------
# Portugal regional + municipal golds
# --------------------------------------------------------------------------
def test_pt_madeira_regional_day():
    reg = holidays_for("PT", 2024, subdiv="PT-30")
    names = {h.name for h in reg if h.subdiv == "PT-30"}
    assert "Dia da Regiao Autonoma da Madeira" in names


def test_pt_lisboa_santo_antonio_june_13():
    lis = holidays_for("PT", 2024, subdiv="PT-LSB")
    got = [h for h in lis if h.subdiv == "PT-LSB"
           and h.date == AstroDate(2024, 6, 13)]
    assert got and got[0].name.startswith("Santo Ant")
    assert got[0].categories == frozenset({"municipal"})


def test_pt_porto_sao_joao_june_24():
    por = holidays_for("PT", 2024, subdiv="PT-PRT")
    got = [h for h in por if h.subdiv == "PT-PRT"
           and h.date == AstroDate(2024, 6, 24)]
    assert got and "São João" in got[0].name


def test_pt_castelo_de_vide_easter_monday_2024():
    # Movable municipal gold: Nossa Senhora da Luz = Easter Monday 2024-04-01.
    cv = holidays_for("PT", 2024, subdiv="PT-CVD")
    got = [h for h in cv if h.subdiv == "PT-CVD"]
    assert AstroDate(2024, 4, 1) in {h.date for h in got}


def test_pt_covers_at_least_250_municipalities():
    cal = load_calendar(os.path.join(_DATA_DIR, "pt.tab"))
    munis = {r.subdiv for r in cal.rules
             if r.subdiv and r.subdiv not in ("PT-30", "PT-20", "PT-01", "PT-02", "PT-03", "PT-04", "PT-05", "PT-06", "PT-07", "PT-08", "PT-09", "PT-10", "PT-11", "PT-12", "PT-13", "PT-14", "PT-15", "PT-16", "PT-17", "PT-18")}
    assert len(munis) >= 250


def test_pt_municipal_rules_are_category_municipal():
    cal = load_calendar(os.path.join(_DATA_DIR, "pt.tab"))
    for r in cal.rules:
        if r.subdiv and r.subdiv not in ("PT-30", "PT-20", "PT-01", "PT-02", "PT-03", "PT-04", "PT-05", "PT-06", "PT-07", "PT-08", "PT-09", "PT-10", "PT-11", "PT-12", "PT-13", "PT-14", "PT-15", "PT-16", "PT-17", "PT-18"):
            assert r.categories == frozenset({"municipal"})


def test_pt_subdiv_filter_adds_only_that_subdivision():
    base = holidays_for("PT", 2024)
    lis = holidays_for("PT", 2024, subdiv="PT-LSB")
    extra = {h.subdiv for h in lis} - {h.subdiv for h in base}
    assert extra == {"PT-LSB"}


def test_pt_category_filter_public_only():
    pub = holidays_for("PT", 2024, categories=["public"])
    assert all("public" in h.categories for h in pub)
    assert all(h.subdiv is None for h in pub)


def test_pt_category_filter_municipal_lisboa():
    muni = holidays_for("PT", 2024, subdiv="PT-LSB", categories=["municipal"])
    assert muni and all(h.categories == frozenset({"municipal"}) for h in muni)


# --------------------------------------------------------------------------
# US federal golds
# --------------------------------------------------------------------------
_US_2024 = {
    "New Year's Day": (1, 1),
    "Birthday of Martin Luther King, Jr.": (1, 15),
    "Washington's Birthday": (2, 19),
    "Memorial Day": (5, 27),
    "Juneteenth National Independence Day": (6, 19),
    "Independence Day": (7, 4),
    "Labor Day": (9, 2),
    "Columbus Day": (10, 14),
    "Veterans Day": (11, 11),
    "Thanksgiving Day": (11, 28),
    "Christmas Day": (12, 25),
}


def test_us_2024_full_list():
    # "public" only: holidays_for's default (no categories filter) now also
    # returns the vacanza-parity government/unofficial rows backfilled by
    # test_holiday_categories.py, which this pre-existing federal-list check
    # predates and is not about.
    got = {h.name: (h.date.month, h.date.day)
           for h in holidays_for("US", 2024, categories=("public",))}
    assert got == _US_2024


def test_us_juneteenth_present():
    assert any(h.name.startswith("Juneteenth") for h in holidays_for("US", 2024))


def test_us_independence_day_2021_observed_monday():
    got = [h for h in holidays_for("US", 2021) if h.name == "Independence Day"]
    assert got[0].date == AstroDate(2021, 7, 5)


def test_us_christmas_2022_observed_monday():
    got = [h for h in holidays_for("US", 2022) if h.name == "Christmas Day"]
    assert got[0].date == AstroDate(2022, 12, 26)


def test_us_veterans_day_2024_no_shift_monday():
    # 2024-11-11 is already a Monday -> not shifted.
    got = [h for h in holidays_for("US", 2024) if h.name == "Veterans Day"]
    assert got[0].date == AstroDate(2024, 11, 11)


# --------------------------------------------------------------------------
# Saudi Arabia calendar_date golds + out-of-range
# --------------------------------------------------------------------------
def test_sa_eid_al_fitr_2024():
    # Primary name is the official Arabic one; English is available via `names`.
    got = [h for h in holidays_for("SA", 2024) if h.name == "عيد الفطر"]
    assert got[0].date == AstroDate(2024, 4, 10)
    assert got[0].basis == "tabulated"
    assert got[0].names["en"] == "Eid al-Fitr"
    assert got[0].display_name("en") == "Eid al-Fitr"


def test_sa_eid_al_adha_2024():
    got = [h for h in holidays_for("SA", 2024) if h.name == "عيد الأضحى"]
    assert got[0].date == AstroDate(2024, 6, 16)


def test_sa_national_day_fixed_exact():
    got = [h for h in holidays_for("SA", 2024) if h.name == "اليوم الوطني"]
    assert got[0].date == AstroDate(2024, 9, 23)
    assert got[0].basis == "exact"


def test_sa_out_of_range_year_drops_islamic_keeps_fixed():
    got = holidays_for("SA", 2100)
    names = {h.name for h in got}
    assert names == {"يوم التأسيس", "اليوم الوطني"}   # Founding Day, National Day


# --------------------------------------------------------------------------
# is_civil_holiday
# --------------------------------------------------------------------------
def test_is_civil_holiday_true():
    assert is_civil_holiday(AstroDate(2024, 1, 1), "PT")


def test_is_civil_holiday_false():
    assert not is_civil_holiday(AstroDate(2024, 1, 2), "PT")


def test_is_civil_holiday_subdiv():
    assert is_civil_holiday(AstroDate(2024, 6, 13), "PT", subdiv="PT-LSB")
    # "public" only: nationwide PT now also carries an "optional" category row
    # for Dia de Santo António (test_holiday_categories.py's vacanza-parity
    # backfill) -- this pre-existing check is about the statutory/public
    # holiday, which stays Lisbon-only.
    assert not is_civil_holiday(AstroDate(2024, 6, 13), "PT",
                                categories=("public",))


# --------------------------------------------------------------------------
# Adversarial inputs
# --------------------------------------------------------------------------
def test_unknown_jurisdiction_raises():
    with pytest.raises(KeyError):
        holidays_for("ZZ", 2024)


def test_unknown_subdiv_yields_no_subdiv_holidays():
    got = holidays_for("PT", 2024, subdiv="PT-NOSUCH")
    assert all(h.subdiv is None for h in got)


def test_unknown_category_filter_yields_nothing():
    assert holidays_for("PT", 2024, categories=["invented"]) == ()


def test_holiday_rule_rejects_unknown_category():
    with pytest.raises(ValueError):
        HolidayRule("X", FixedRule(1, 1), frozenset({"bogus"}))


def test_malformed_data_file_too_few_columns(tmp_path):
    p = tmp_path / "xx.tab"
    p.write_text(
        "# jurisdiction: XX\n# source: x\n# retrieved: x\n"
        "fixed | Broken | 1 1\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_calendar(str(p))


def test_missing_provenance_header_rejected(tmp_path):
    p = tmp_path / "xx.tab"
    p.write_text("# jurisdiction: XX\nfixed | Day | 1 1 | public\n",
                 encoding="utf-8")
    with pytest.raises(ValueError):
        load_calendar(str(p))


def test_unknown_rule_kind_rejected(tmp_path):
    p = tmp_path / "xx.tab"
    p.write_text(
        "# jurisdiction: XX\n# source: x\n# retrieved: x\n"
        "wobble | Day | 1 1 | public\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_calendar(str(p))


# --------------------------------------------------------------------------
# Output object + data-file lint
# --------------------------------------------------------------------------
def test_civil_holiday_span_is_day_wide():
    h = holidays_for("PT", 2024)[0]
    assert h.span.width.days == 1
    assert h.span.start == h.date


def test_day_span_carries_basis():
    span = _day_span(AstroDate(2024, 1, 1), "tabulated")
    assert span.basis == "tabulated"


def test_holidays_sorted_chronologically():
    got = holidays_for("US", 2024)
    assert list(got) == sorted(got, key=lambda h: h.span.start)


def _tab_files():
    return sorted(f for f in os.listdir(_DATA_DIR) if f.endswith(".tab"))


@pytest.mark.parametrize("filename", _tab_files())
def test_every_tab_file_parses_with_provenance(filename):
    cal = load_calendar(os.path.join(_DATA_DIR, filename))
    assert isinstance(cal, HolidayCalendar)
    assert cal.source and cal.retrieved and cal.jurisdiction


@pytest.mark.parametrize("filename", _tab_files())
def test_every_tab_categories_within_schema(filename):
    cal = load_calendar(os.path.join(_DATA_DIR, filename))
    for r in cal.rules:
        assert r.categories <= CATEGORIES
        assert r.categories  # non-empty


def test_at_least_three_jurisdictions_shipped():
    assert {"pt.tab", "us.tab", "sa.tab"} <= set(_tab_files())
