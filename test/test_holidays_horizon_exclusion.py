"""Decree-horizon prediction (R6) and subtractive `exclude` rules (R9).

Two engine capabilities are exercised here, both making the holiday engine
honest about things it previously handled silently.

R6 -- decree horizon + prediction
----------------------------------
A ``decree`` rule tabulates a finite span of years (its *horizon*). Queried
beyond it, the old engine returned nothing -- indistinguishable from "no such
holiday" (no Diwali in India in 2028, silently). Now a decree row may carry a
``predict`` annotation naming a :data:`WELL_KNOWN` computable rule (an Islamic
feast on the Umm al-Qura calendar, the Chinese lunisolar cluster) that bridges
past the horizon with basis ``predicted``. The annotations were added
correct-by-construction: a row is annotated with a key only when that key's
*computed* date equals the row's *tabulated* date for every year the row lists
(so a jurisdiction whose gazetted observance diverges from the calendar is
left honestly un-predicted).

The 2028 golds below are the calendars' OWN values, independently derived from
the tabulated Umm al-Qura / Chinese calendars this engine ships, and match the
publicly published 2028 dates (Chinese New Year 26 Jan 2028; Mid-Autumn 3 Oct
2028; Eid al-Fitr 26 Feb 2028 on the Umm al-Qura table).

R9 -- exclude rules
-------------------
The engine was additive-only: "US-ND does not observe Columbus Day" was
inexpressible and stood as a documented skip. An ``exclude`` rule removes a
named inherited holiday for a subdivision. The US Columbus Day / Washington's
Birthday subtractions (verified against vacanza/holidays 0.101 for 2024/2025)
are now expressed in us.tab's SUBTRACTIVE LAYER; every such row is registered
here so the structural gold enforcement in ``test_holiday_golds`` still holds.
"""
import os

import pytest

from chronologia import AstroDate, coverage, holidays_for
from chronologia.astrodate import BASIS_PREDICTED, BASIS_TABULATED
from chronologia.civil_holidays import (COVERAGE_FULL, COVERAGE_NONE,
                                        COVERAGE_PARTIAL, COVERAGE_PREDICTED,
                                        DecreeTableRule, ExcludeRule,
                                        HolidayRule, _DATA_DIR, load_calendar)
from test_holiday_golds import HOLIDAY_GOLDS

# ==========================================================================
# Register every exclude row so the structural "every rule has a gold" test
# is satisfied. An exclude row asserts an ABSENCE, so its gold is the empty
# set (its positive behaviour is asserted by the exclusion tests below).
# ==========================================================================
_US = load_calendar(os.path.join(_DATA_DIR, "us.tab"))
_EXCLUDE_ROWS = [(r.subdiv, r.name) for r in _US.rules
                 if isinstance(r.kind, ExcludeRule)]
for _sub, _name in _EXCLUDE_ROWS:
    HOLIDAY_GOLDS.setdefault(("US", _sub, _name), set())


# ==========================================================================
# R6 -- 2028 predicted spot golds (past every listed horizon).
# ==========================================================================
#: (jurisdiction, holiday name, predicted 2028 (y, m, d)). Each row is a
#: decree table ending in 2026/2027; 2028 is past the horizon and bridged via
#: the row's ``predict`` key. Values are the shipped calendars' own 2028 dates.
PREDICTED_2028 = [
    ("AE", "عيد الفطر", (2028, 2, 26)),            # eid_al_fitr (Umm al-Qura)
    ("AL", "Dita e Kurban Bajramit", (2028, 5, 5)),  # eid_al_adha
    ("BH", "عاشوراء (2)", (2028, 6, 3)),            # ashura
    ("BF", "Mouloud (estimé)", (2028, 8, 3)),       # mawlid
    ("BN", "Tahun Baru Cina", (2028, 1, 26)),       # chinese_new_year
    ("KP", "추석", (2028, 10, 3)),                   # mid_autumn
]


@pytest.mark.parametrize("juris,name,ymd", PREDICTED_2028)
def test_predicted_2028_value(juris, name, ymd):
    y, m, d = ymd
    got = {h.name: h for h in holidays_for(juris, y)}
    assert name in got, f"{juris}/{name!r} vanished at {y} (horizon not bridged)"
    assert got[name].date == AstroDate(y, m, d)


@pytest.mark.parametrize("juris,name,ymd", PREDICTED_2028)
def test_past_horizon_basis_is_predicted_never_exact(juris, name, ymd):
    y = ymd[0]
    got = {h.name: h for h in holidays_for(juris, y)}
    assert got[name].basis == BASIS_PREDICTED
    assert got[name].basis != "exact"


def test_within_horizon_basis_stays_tabulated_not_predicted():
    """A listed (in-horizon) year resolves from the table, basis ``tabulated`` --
    prediction only fires PAST the horizon, never over real tabulated data."""
    got = {h.name: h for h in holidays_for("BN", 2025)}
    assert got["Tahun Baru Cina"].basis == BASIS_TABULATED


def test_decree_horizon_reports_min_max_year():
    rule = DecreeTableRule(((2024, (1, 1)), (2026, (3, 3)), (2025, (2, 2))))
    assert rule.horizon() == (2024, 2026)
    assert DecreeTableRule(()).horizon() is None


def test_past_horizon_predicate():
    rule = HolidayRule("x", DecreeTableRule(((2024, (1, 1)), (2027, (1, 1)))),
                       frozenset({"public"}), predict="eid_al_fitr")
    assert not rule.past_horizon(2024)
    assert not rule.past_horizon(2027)
    assert rule.past_horizon(2028)
    assert rule.past_horizon(2023)


def test_unannotated_decree_row_stays_silent_past_horizon():
    """A decree row WITHOUT a predict annotation must remain honestly silent
    past its horizon -- prediction is opt-in per row, never automatic."""
    rule = HolidayRule("x", DecreeTableRule(((2024, (1, 1)), (2027, (1, 1)))),
                       frozenset({"public"}))
    assert rule.resolve(2028) == ()


def test_predict_names_unknown_key_is_rejected():
    with pytest.raises(ValueError):
        HolidayRule("x", DecreeTableRule(((2024, (1, 1)), (2027, (1, 1)))),
                    frozenset({"public"}), predict="not_a_real_holiday")


def test_annotations_are_correct_by_construction_across_the_horizon():
    """Every predict-annotated decree row's tabulated dates equal its predict
    key's computed dates for EVERY tabulated year -- the invariant the
    annotation pass enforced. Guards against a hand-typo drifting a mapping."""
    from chronologia.civil_holidays import WELL_KNOWN_BY_KEY
    checked = 0
    for fn in sorted(os.listdir(_DATA_DIR)):
        if not fn.endswith(".tab"):
            continue
        cal = load_calendar(os.path.join(_DATA_DIR, fn))
        for r in cal.rules:
            if not r.predict:
                continue
            checked += 1
            wk = WELL_KNOWN_BY_KEY[r.predict]
            for y, (m, d) in r.kind.dates:
                computed = {dt for dt, _ in wk.kind.observances(y)}
                assert AstroDate(y, m, d) in computed, (
                    f"{cal.jurisdiction}/{r.name!r} predict={r.predict}: "
                    f"tabulated {y}-{m}-{d} not in computed {computed}")
    assert checked >= 100  # the sweep annotated 137 rows


# ==========================================================================
# R6 -- coverage() horizon detector.
# ==========================================================================
def test_coverage_full_when_no_decree_rule_past_horizon():
    # A purely computable jurisdiction (Germany: fixed/easter/nth_weekday, no
    # decree tables), so no horizon can be exceeded -- 'full' for any year.
    assert coverage("DE", 2028) == COVERAGE_FULL


def test_coverage_predicted_when_bridged():
    # Brunei's set is Islamic/Chinese decree rows, all predict-annotated where
    # a calendar exists; 2028 is past every horizon.
    cov = coverage("BN", 2028)
    assert cov in (COVERAGE_PREDICTED, COVERAGE_PARTIAL)


def test_coverage_is_one_of_the_four_verdicts():
    for juris in ("US", "MY", "PT", "SA", "BN"):
        assert coverage(juris, 2028) in (
            COVERAGE_FULL, COVERAGE_PARTIAL, COVERAGE_PREDICTED, COVERAGE_NONE)


def test_coverage_distinguishes_horizon_from_silence():
    """The whole point: past the horizon coverage is NOT silently 'full'.
    MY has many un-predicted gazette-only decree rows, so 2028 is 'partial',
    while a listed year is 'full'."""
    assert coverage("MY", 2025) == COVERAGE_FULL
    assert coverage("MY", 2028) == COVERAGE_PARTIAL


# ==========================================================================
# R9 -- exclude rules.
# ==========================================================================
def _names(juris, year, subdiv=None):
    return {h.name for h in holidays_for(juris, year, subdiv=subdiv)}


@pytest.mark.parametrize("subdiv", ["US-ND", "US-UM", "US-CA", "US-TX", "US-HI"])
def test_columbus_day_excluded_for_subdivision(subdiv):
    assert "Columbus Day" not in _names("US", 2024, subdiv)
    assert "Columbus Day" not in _names("US", 2025, subdiv)


def test_columbus_day_present_for_the_nation_and_non_excluded_subdiv():
    assert "Columbus Day" in _names("US", 2024)
    # A subdivision with NO exclude row still inherits it (e.g. US-NY).
    assert "Columbus Day" in _names("US", 2024, "US-NY")


def test_washingtons_birthday_excluded_for_de_fl_only():
    assert "Washington's Birthday" not in _names("US", 2024, "US-DE")
    assert "Washington's Birthday" not in _names("US", 2024, "US-FL")
    assert "Washington's Birthday" in _names("US", 2024)
    assert "Washington's Birthday" in _names("US", 2024, "US-NY")


def test_exclusion_removes_only_the_named_holiday():
    """ND drops Columbus Day but keeps every other federal holiday."""
    nd = _names("US", 2024, "US-ND")
    for kept in ("New Year's Day", "Independence Day", "Christmas Day",
                 "Thanksgiving Day", "Birthday of Martin Luther King, Jr."):
        assert kept in nd


def test_exclude_rule_produces_no_date_of_its_own():
    assert ExcludeRule("Columbus Day").observances(2024) == ()


def test_every_us_exclude_row_targets_a_real_federal_holiday():
    national = _names("US", 2024)
    for _sub, name in _EXCLUDE_ROWS:
        assert name in national, (
            f"exclude target {name!r} is not a federal holiday")
