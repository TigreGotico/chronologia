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
from chronologia.astrodate import (BASIS_EXACT, BASIS_PREDICTED,
                                    BASIS_TABULATED)
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
# R6 -- strict_horizon: opt-in authoritative-only mode (refuse, don't predict).
#
# The predict bridge is honest but silent: a caller who ignores `.basis` gets a
# fabricated future date mixed in with facts. `strict_horizon=True` lets a
# caller require authoritative-only results -- past a decree row's OWN horizon
# it returns nothing rather than a predicted date. It is additive: the lenient
# default is unchanged, and computable holidays (no horizon) are never refused.
#
# Hand-derived values: Brunei's Chinese-New-Year decree ends at its horizon and
# is predict-annotated (chinese_new_year); 2028 (26 Jan 2028, the shipped
# calendar's own value) is past it. The FixedRule/DecreeTableRule constructions
# below use tables the test itself authors, so their expected outputs are read
# straight off the constructed data, not off the engine.
# ==========================================================================
def test_lenient_default_predicts_past_horizon_unchanged():
    """Baseline: without the flag, 2028 still yields the predicted date."""
    got = {h.name: h for h in holidays_for("BN", 2028)}
    assert "Tahun Baru Cina" in got
    assert got["Tahun Baru Cina"].basis == BASIS_PREDICTED
    assert got["Tahun Baru Cina"].date == AstroDate(2028, 1, 26)


def test_strict_refuses_the_same_query_past_horizon():
    """Same jurisdiction/year as above -- strict omits the predicted holiday."""
    got = {h.name for h in holidays_for("BN", 2028, strict_horizon=True)}
    assert "Tahun Baru Cina" not in got


def test_strict_still_returns_authoritative_dates_before_horizon():
    """A listed (in-horizon) year is authoritative -- strict must NOT refuse it,
    and it stays basis tabulated (never predicted)."""
    got = {h.name: h for h in holidays_for("BN", 2025, strict_horizon=True)}
    assert "Tahun Baru Cina" in got
    assert got["Tahun Baru Cina"].basis == BASIS_TABULATED


def test_strict_exactly_on_horizon_is_not_refused():
    """Boundary: the last tabulated year is authoritative, not past the horizon.
    The table ends 2027; strict at 2027 returns the tabulated date, at 2028 () --
    while lenient 2028 predicts. Refusal begins strictly AFTER the last year."""
    rule = HolidayRule(
        "x", DecreeTableRule(((2024, (4, 10)), (2025, (3, 30)),
                              (2026, (3, 20)), (2027, (3, 9)))),
        frozenset({"public"}), predict="eid_al_fitr")
    assert rule.resolve(2027, strict_horizon=True) == (
        (AstroDate(2027, 3, 9), BASIS_TABULATED),)
    assert rule.resolve(2028, strict_horizon=True) == ()
    # Lenient still bridges 2028 -- the default is untouched.
    lenient = rule.resolve(2028)
    assert len(lenient) == 1 and lenient[0][1] == BASIS_PREDICTED


def test_strict_refusal_is_per_rule_not_global():
    """Two decree rows with DIFFERENT horizons, queried for the SAME year 2029:
    the row whose horizon ended 2027 is refused, the row tabulating through 2030
    is still authoritative and returns its 2029 date. Strict refuses per-rule."""
    short = HolidayRule(
        "short", DecreeTableRule(((2026, (3, 20)), (2027, (3, 9)))),
        frozenset({"public"}), predict="eid_al_fitr")
    long = HolidayRule(
        "long", DecreeTableRule(((2028, (2, 26)), (2029, (2, 15)),
                                 (2030, (2, 5)))),
        frozenset({"public"}), predict="eid_al_fitr")
    assert short.past_horizon(2029) and not long.past_horizon(2029)
    assert short.resolve(2029, strict_horizon=True) == ()
    assert long.resolve(2029, strict_horizon=True) == (
        (AstroDate(2029, 2, 15), BASIS_TABULATED),)


def test_strict_never_refuses_computable_holidays():
    """A fixed / nth-weekday holiday has no horizon: it is computable forever,
    so strict must resolve it for any year, however far out."""
    from chronologia.civil_holidays import FixedRule, NthWeekdayRule
    fixed = HolidayRule("New Year", FixedRule(1, 1), frozenset({"public"}))
    assert fixed.resolve(9999, strict_horizon=True) == (
        (AstroDate(9999, 1, 1), BASIS_EXACT),)
    # First Monday of September 9999 -- computable, unaffected by strict.
    labor = HolidayRule("Labor Day", NthWeekdayRule(9, 1, 0, 0),
                        frozenset({"public"}))
    assert len(labor.resolve(9999, strict_horizon=True)) == 1


def test_strict_keeps_computable_holidays_while_dropping_predicted():
    """Integration: at a past-horizon year strict drops the predicted Islamic
    feast but keeps the fixed civil holidays (Benin: New Year 1 Jan is fixed)."""
    lenient = {h.name for h in holidays_for("BJ", 2028)}
    strict = {h.name for h in holidays_for("BJ", 2028, strict_horizon=True)}
    assert "Fête du Nouvel An" in strict          # fixed -- kept
    assert "Jour du Ramadan (estimé)" in lenient  # predicted -- present lenient
    assert "Jour du Ramadan (estimé)" not in strict  # ...refused under strict


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
