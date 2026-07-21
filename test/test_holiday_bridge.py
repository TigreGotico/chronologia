"""Tests for the optional civil-holiday bridge.

Optional-dependency exemption from the "never skip tests on missing deps" rule
------------------------------------------------------------------------------
The repo rule forbids skipping tests when a *development* dependency is absent
(``importorskip`` per test hides real breakage).  These tests are the sanctioned
exception: they exercise the ``chronologia[holidays]`` **optional extra**, not a
missing dev dep.  The sanctioned pattern is a single module-level availability
check with a loud, documented skip reason that names the extra — so a developer
who has not installed the extra sees exactly why, and CI that installs it (this
environment does) runs every test.  Do NOT convert these to per-test
``importorskip``; the one guard below is deliberate.
"""
import datetime
import sys

import pytest

try:
    import holidays as _holidays  # noqa: F401
    _HOLIDAYS_AVAILABLE = True
except ImportError:  # pragma: no cover - extra is installed in this env
    _HOLIDAYS_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not _HOLIDAYS_AVAILABLE,
    reason=("optional extra not installed: run `pip install "
            "chronologia[holidays]` to exercise the civil-holiday bridge"),
)

from chronologia.astrodate import AstroDate, DateSpan
from chronologia.holiday_bridge import (Holiday, HolidaysNotInstalled,
                                        civil_holidays, is_holiday)


# --- shape / typing --------------------------------------------------------

def test_returns_tuple_of_holiday():
    result = civil_holidays("US", 2026)
    assert isinstance(result, tuple)
    assert result and all(isinstance(h, Holiday) for h in result)


def test_holiday_is_frozen():
    h = civil_holidays("US", 2026)[0]
    with pytest.raises((AttributeError, TypeError)):
        h.name = "mutated"


def test_span_is_day_wide_datespan():
    h = is_holiday(datetime.date(2026, 1, 1), "US")
    assert isinstance(h.span, DateSpan)
    assert h.span.width == datetime.timedelta(days=1)
    assert h.span.start == AstroDate(2026, 1, 1)
    assert h.span.end == AstroDate(2026, 1, 2)


def test_results_sorted_by_date():
    result = civil_holidays("US", 2026)
    dates = [h.date for h in result]
    assert dates == sorted(dates)


def test_holiday_date_property_matches_span_start():
    h = civil_holidays("US", 2026)[0]
    assert h.date == datetime.date(h.span.start.year, h.span.start.month,
                                   h.span.start.day)


# --- golds: fixed New Year across countries --------------------------------

def test_us_new_year_gold():
    h = is_holiday(datetime.date(2026, 1, 1), "US")
    assert h.name == "New Year's Day"
    assert h.basis == "tabulated"


def test_de_new_year_gold():
    h = is_holiday(datetime.date(2026, 1, 1), "DE")
    assert h is not None and h.name == "Neujahr"


def test_br_new_year_gold():
    h = is_holiday(datetime.date(2026, 1, 1), "BR")
    assert h is not None and "Universal" in h.name


def test_sa_national_day_gold():
    # Saudi National Day is a fixed decree on 23 September.
    h = is_holiday(datetime.date(2026, 9, 23), "SA", language="en_US")
    assert h is not None and "National Day" in h.name


def test_us_midyear_fixed_gold():
    h = is_holiday(datetime.date(2026, 7, 4), "US")
    assert h.name == "Independence Day"
    assert h.basis == "tabulated"


def test_de_midyear_fixed_gold():
    # Tag der Deutschen Einheit, fixed 3 October.
    h = is_holiday(datetime.date(2026, 10, 3), "DE")
    assert h is not None


# --- the honesty layer: estimated -> predicted -----------------------------

def test_future_islamic_is_predicted_and_name_is_clean():
    # Egypt shows the estimated label for far-future lunar dates.
    eg = civil_holidays("EG", 2033, language="en_US")
    fitr = [h for h in eg if "Eid al-Fitr" in h.name]
    assert fitr, "expected an Eid al-Fitr entry"
    assert all(h.basis == "predicted" for h in fitr)
    # estimate marker is stripped back off the name
    assert all("estimated" not in h.name.lower() for h in fitr)
    assert all(h.span.basis == "predicted" for h in fitr)


def test_saudi_umm_al_qura_future_eid_is_tabulated_not_predicted():
    # SA publishes the official Umm al-Qura calendar years ahead, so it does
    # NOT mark future Eid as estimated -> tabulated, not predicted.
    sa = civil_holidays("SA", 2033, language="en_US")
    fitr = [h for h in sa if "Eid al-Fitr" in h.name]
    assert fitr
    assert all(h.basis == "tabulated" for h in fitr)


def test_estimate_detection_is_language_independent():
    # Arabic build wraps with the Arabic marker; detection must still work and
    # still strip the marker, leaving a clean (Arabic) name and predicted basis.
    ar = civil_holidays("EG", 2033, language="ar")
    predicted = [h for h in ar if h.basis == "predicted"]
    assert predicted, "expected estimated lunar dates in the Arabic build"
    assert all("تقدير" not in h.name for h in predicted)


def test_past_confirmed_lunar_is_tabulated():
    eg = civil_holidays("EG", 2020, language="en_US")
    fitr = [h for h in eg if "Eid al-Fitr" in h.name]
    assert fitr
    assert all(h.basis == "tabulated" for h in fitr)


# --- multi-day / in-lieu pass-through --------------------------------------

def test_multiday_eid_passes_through_as_separate_entries():
    sa = civil_holidays("SA", 2026, language="en_US")
    fitr = [h for h in sa if h.name == "Eid al-Fitr Holiday"]
    assert len(fitr) >= 2  # multi-day feast -> multiple dated entries
    assert len({h.date for h in fitr}) == len(fitr)  # each a distinct day


def test_in_lieu_observed_day_is_separate_entry():
    cn = civil_holidays("CN", 2026, language="en_US")
    substituted = [h for h in cn if "substituted" in h.name.lower()]
    assert substituted  # in-lieu / bridge days surface as their own spans


# --- subdivisions ----------------------------------------------------------

def test_subdiv_adds_state_specific_holiday():
    national = civil_holidays("US", 2026)
    ca = civil_holidays("US", 2026, subdiv="CA")
    assert len(ca) > len(national)
    assert any("Chavez" in h.name for h in ca)  # Cesar Chavez Day is CA-only
    assert all(h.subdiv == "CA" for h in ca)


def test_subdiv_none_by_default():
    assert all(h.subdiv is None for h in civil_holidays("US", 2026))


# --- categories ------------------------------------------------------------

def test_category_filter_tags_each_holiday():
    result = civil_holidays("US", 2026, categories=["public", "unofficial"])
    seen = set()
    for h in result:
        seen.update(h.categories)
    assert "public" in seen
    # each holiday records only the categories that actually claim it
    assert all(set(h.categories) <= {"public", "unofficial"} for h in result)


def test_single_category_string_accepted():
    result = civil_holidays("US", 2026, categories="public")
    assert result
    assert all(h.categories == ("public",) for h in result)


# --- is_holiday hit / miss / astro -----------------------------------------

def test_is_holiday_hit():
    assert is_holiday(datetime.date(2026, 7, 4), "US").name == "Independence Day"


def test_is_holiday_miss_returns_none():
    assert is_holiday(datetime.date(2026, 7, 5), "US") is None


def test_is_holiday_accepts_astrodate():
    h = is_holiday(AstroDate(2026, 1, 1), "US")
    assert h is not None and h.name == "New Year's Day"


def test_is_holiday_rejects_bad_type():
    with pytest.raises(TypeError):
        is_holiday("2026-01-01", "US")


# --- ImportError path (optional-extra absence) -----------------------------

def test_import_error_path(monkeypatch):
    # Simulate the extra being absent: block the import and confirm the bridge
    # raises the actionable HolidaysNotInstalled naming the extra.
    import chronologia.holiday_bridge as hb
    monkeypatch.setitem(sys.modules, "holidays", None)
    with pytest.raises(HolidaysNotInstalled) as exc:
        hb.civil_holidays("US", 2026)
    assert "chronologia[holidays]" in str(exc.value)


def test_import_error_is_importerror_subclass():
    assert issubclass(HolidaysNotInstalled, ImportError)


# --- differential-harness summary assertions -------------------------------

def test_differential_chinese_exact_agreement():
    from benchmarks.holiday_differential import chinese_differential
    res = chinese_differential()
    assert res.years_tested > 0
    # ANY mismatch is a lead; within our range we expect exact agreement.
    assert res.exact_agreements == res.years_tested
    assert res.leads == []


def test_differential_hebrew_exact_agreement():
    from benchmarks.holiday_differential import hebrew_differential
    res = hebrew_differential()
    assert res.years_tested > 0
    assert res.exact_agreements == res.years_tested
    assert res.offset_distribution == {0: res.years_tested}


def test_differential_islamic_offsets_within_two_days():
    from benchmarks.holiday_differential import islamic_differential
    res = islamic_differential(calendar_key="islamic_civil")
    assert res.years_tested > 0
    # observance-vs-arithmetic: every offset must be within +/-2 days (no leads)
    assert all(abs(off) <= 2 for off in res.offset_distribution)
    assert res.leads == []


def test_differential_umm_al_qura_closer_than_tabular():
    from benchmarks.holiday_differential import islamic_differential
    uaq = islamic_differential(calendar_key="umm_al_qura")
    tab = islamic_differential(calendar_key="islamic_civil")

    def mean_abs(res):
        total = sum(abs(o) * n for o, n in res.offset_distribution.items())
        return total / max(1, sum(res.offset_distribution.values()))

    # Umm al-Qura tracks the official Saudi observance more closely than the
    # generic tabular Hijri calendar does.
    assert mean_abs(uaq) <= mean_abs(tab)


def test_differential_easter_is_documented_placeholder():
    from benchmarks.holiday_differential import easter_differential
    res = easter_differential()
    assert res.years_tested == 0
    assert "computus" in res.note.lower()


def test_run_differential_covers_all_axes():
    from benchmarks.holiday_differential import run_differential
    results = run_differential()
    axes = " ".join(results)
    for token in ("easter", "islamic", "hebrew", "chinese"):
        assert token in axes
