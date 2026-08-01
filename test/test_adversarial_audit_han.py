# -*- coding: utf-8 -*-
"""Regression locks for the han-specialist adversarial audit round (2026-07-31).

Each test pins a fix for a defect the audit reproduced live:
  SEC-001  Romance spelled-number fold was O(n^2) on a long number-word run.
  OCE-001  extract_timespan raised OverflowError on a deep-time range.
  DATA-001 is_civil_holiday missed a holiday shifted into an adjacent year.
  DATA-002 holidays_for emitted category-split duplicates.
  C1       explain()'s module-level compiler served a stale table for a second
           LangSpec sharing the same lang code.
"""
import importlib
import time
from datetime import datetime

import pytest

from chronologia import (extract_candidates, extract_duration,
                         extract_timespan)
from chronologia.astrodate import AstroDate
from chronologia.civil_holidays import holidays_for
from chronologia.civil_holidays.registry import is_civil_holiday

_A = datetime(2017, 6, 27, 13, 4)


# -- SEC-001 --------------------------------------------------------------
def test_romance_number_fold_is_linear_not_quadratic():
    """A long joiner-less run of a Romance number-word used to re-parse the
    growing prefix once per token -- O(n^2), ~7.5s at 8000 words.  The fold is
    now linear; a generous 3s budget (vs ~0.15s actual) fails loudly if the
    quadratic behaviour ever returns, while staying robust to a slow CI box."""
    t = time.time()
    extract_timespan("um " * 8000, "pt", _A)
    assert time.time() - t < 3.0


@pytest.mark.parametrize("text,lang,days", [
    ("cento e vinte e três dias", "pt", 123),
    ("ciento veintitrés días", "es", 123),
    ("vinte e um dias", "pt", 21),
])
def test_romance_additive_numbers_still_fold(text, lang, days):
    # the lazy seg_val change must not alter the additive-join result
    r = extract_duration(text, lang)
    assert r is not None and r.duration.days == days


# -- OCE-001 --------------------------------------------------------------
@pytest.mark.parametrize("text", [
    "from neolithic to oligocene",
    "neolithic till oligocene",
    "between neolithic and oligocene",
])
def test_deep_time_range_never_raises(text):
    # width classification overflowed datetime subtraction on a geological span;
    # extract_timespan must honour its never-raise contract (extract_candidates
    # already did), returning a span or None -- never an OverflowError.
    r = extract_timespan(text, "en")            # default now() anchor
    assert r is None or r[0].start is not None
    extract_candidates(text, "en")              # must also not raise


# -- DATA-001 -------------------------------------------------------------
@pytest.mark.parametrize("cc", ["XNYS", "XNAS"])
@pytest.mark.parametrize("d", [(2021, 12, 31), (2027, 12, 31)])
def test_new_year_observed_in_previous_year_is_a_holiday(cc, d):
    # 1 Jan 2022/2028 is a Saturday, so NYSE/Nasdaq observe New Year's Day on the
    # preceding Friday 31 Dec -- a real market closure that lives in the NEXT
    # year's bucket.  is_civil_holiday must consult the neighbouring year.
    assert is_civil_holiday(AstroDate(*d), cc) is True


def test_ordinary_non_holiday_still_false():
    assert is_civil_holiday(AstroDate(2021, 7, 15), "XNYS") is False


# -- DATA-002 -------------------------------------------------------------
def test_category_split_holidays_are_deduplicated():
    # HK Chinese New Year was listed once as public and once as optional, so
    # holidays_for emitted it twice on the same date.  It is now one entry with
    # the union of categories.
    from collections import Counter
    hs = holidays_for("HK", 2024)
    dup = {k: v for k, v in Counter(
        (h.name, h.span.start) for h in hs).items() if v > 1}
    assert not dup, f"duplicate (name,date) rows: {dup}"
    cny = [h for h in hs if h.name == "農曆年初一"]
    assert len(cny) == 1
    assert {"public", "optional"} <= cny[0].categories


# -- C1 -------------------------------------------------------------------
def test_explain_compiler_does_not_serve_a_stale_table_for_a_new_spec():
    from dataclasses import replace
    from chronologia.extract.loader import load_lang_spec
    mod = importlib.import_module("chronologia.extract.explain")
    mod._COMPILER._cache.clear()
    spec = load_lang_spec("en")
    stripped = replace(spec, orders={})          # a different spec, same lang
    assert len(mod.explain("next friday", spec, _A).winners) == 1
    # the stripped spec has no construction orders -> it must match NOTHING,
    # not be served the first spec's cached compiled table.
    assert len(mod.explain("next friday", stripped, _A).winners) == 0
    # and order-independent: stripped first, real spec after
    mod._COMPILER._cache.clear()
    assert len(mod.explain("next friday", stripped, _A).winners) == 0
    assert len(mod.explain("next friday", spec, _A).winners) == 1


# -- CA .tab redundant-decree cleanup (follow-up to DATA-002) --------------
@pytest.mark.parametrize("subdiv", [
    "CA-ON", "CA-QC", "CA-BC", "CA-AB", "CA-MB", "CA-NS",
    "CA-NT", "CA-NU", "CA-SK", "CA-YT", None])
def test_ca_no_same_scope_holiday_duplicates(subdiv):
    """The Canadian .tab listed several holidays as BOTH a computed rule and a
    redundant decree table for the same (name, subdiv); the decree rows were
    removed (the rule already covers those years and beyond).  No holiday may
    now appear twice within the SAME scope -- (name, subdiv, date).  National
    and provincial rows for the same day remain legitimately distinct."""
    from collections import Counter
    hs = holidays_for("CA", 2024, subdiv=subdiv)
    dup = {k: v for k, v in Counter(
        (h.name, h.subdiv, h.span.start.date()) for h in hs).items() if v > 1}
    assert not dup, f"{subdiv}: same-scope duplicate holidays: {dup}"


def test_ca_thanksgiving_survives_past_the_old_decree_horizon():
    # the removed decree tables stopped at 2027; the nth_weekday rule extrapolates
    thx = [h for h in holidays_for("CA", 2035, subdiv="CA-AB")
           if h.name == "Thanksgiving Day"]
    assert thx and thx[0].span.start.month == 10   # 2nd Monday of October


# ===== han adversarial audit round 2 (2026-07-31) =====

def test_weekday_not_swallowed_as_label_on_a_computed_date():
    """B3: the weekday-label rule ("Monday, March 2" -> the date, weekday
    consumed) must apply ONLY to a literal calendar date -- not to a DERIVED
    date (business-days / offset).  "in 5 business days on Monday" lands on a
    Tuesday, so "Monday" is a separate mention: it must stay VISIBLE in the
    remainder, never be silently swallowed."""
    from chronologia import extract_timespan
    A = datetime(2017, 6, 27, 13, 4)
    for text in ("in 5 business days on Monday", "Monday in 5 business days"):
        r = extract_timespan(text, "en", A)
        assert r is not None
        # honest either way: the answer IS a Monday, or "Monday" stays visible in
        # the remainder.  The old bug returned a Tuesday (the business-days date)
        # with "Monday" silently swallowed -- that must never happen.
        is_monday = r[0].start_datetime.weekday() == 0
        stranded = "monday" in getattr(r, "remainder", "").lower()
        assert is_monday or stranded, \
            f"{text!r}: 'Monday' silently swallowed (start={r[0].start_datetime}, rem={r.remainder!r})"
    # the label rule still fires for a genuine literal date
    r = extract_timespan("Monday March 2", "en", A)
    assert r[0].start_datetime.date().isoformat() == "2018-03-02"
    assert getattr(r, "remainder", "") == ""


def test_arabic_azzahira_is_noon_not_the_afternoon_band():
    """DATA-AR-1: الظهيرة (midday) is the noon clock-landmark, not the afternoon
    band; only بعد الظهر names [12:00, 18:00)."""
    from chronologia import extract_timespan
    A = datetime(2017, 6, 27, 13, 4)
    noon = extract_timespan("الظهيرة", "ar", A)
    assert noon is not None and noon[0].start_datetime.hour == 12
    assert noon[0].width.total_seconds() <= 60          # a point, not a 6h band
    band = extract_timespan("بعد الظهر", "ar", A)
    assert band is not None
    assert band[0].start_datetime.hour == 12 and band[0].width.total_seconds() == 6 * 3600


@pytest.mark.parametrize("subdiv,name,years", [
    ("CA-SK", "Thanksgiving Day", (2024, 2030, 2035)),
    ("CA-YT", "Discovery Day", (2024, 2030, 2035)),
    ("CA-NT", "Victoria Day", (2024, 2030, 2035)),
    ("CA-NB", "New Brunswick Day", (2024, 2030, 2035)),
    ("CA-PE", "Islander Day", (2024, 2030, 2035)),
])
def test_ca_computable_holidays_no_longer_vanish_after_2027(subdiv, name, years):
    """DATA-CA-1: NT/NU/SK/YT/NB/PE statutory holidays were encoded as decree
    tables ending 2027, so they vanished past the horizon.  Re-expressed as the
    same computable rules the Wave-1 provinces use, they now resolve every year."""
    from chronologia.civil_holidays import holidays_for
    for y in years:
        assert any(h.name == name for h in holidays_for("CA", y, subdiv=subdiv)), \
            f"{name} missing for {subdiv} in {y}"
    # (The federal "government"-category annotation rows are deliberately left as
    #  bounded decree tables -- they are category-parity annotations of holidays
    #  that already resolve computably provincially, not the primary source; the
    #  category-parity design keeps them fixed/decree, per test_holiday_categories.)


@pytest.mark.parametrize("text", [
    "March 2 at 3pm", "june 5th at 3pm",      # date + clock
    "Monday morning", "yesterday morning",     # weekday/named-day + daypart
    "Monday March 2", "Monday March 2 morning at 3pm",  # weekday-label (+clock)
    "5 days after christmas", "in 5 business days", "3 fridays from now",  # offsets
])
def test_extract_candidates_top_equals_extract_timespan(text):
    """B1/B2: extract_candidates ran the post-passes but not the COMPOSE block,
    so its #1 candidate could differ from extract_timespan for the very phrases
    composition exists for.  Both now go through the shared _compose helper, so
    the top candidate is exactly extract_timespan's selected reading (while the
    un-composed runner-ups are still exposed below it)."""
    from chronologia import extract_candidates
    A = datetime(2017, 6, 27, 13, 4)
    ts = extract_timespan(text, "en", A)
    cs = extract_candidates(text, "en", A)
    assert ts is not None and cs, text
    assert str(cs[0].span.start).replace("T", " ") == str(ts[0].start_datetime)
    assert cs[0].remainder == getattr(ts, "remainder", "")


def test_extract_candidates_still_exposes_runner_ups():
    # the composed primary is #1 but the alternative readings remain visible
    from chronologia import extract_candidates
    cs = extract_candidates("March 2 at 3pm", "en", datetime(2017, 6, 27, 13, 4))
    assert len(cs) > 1
    assert all(0 < c.confidence <= 1 for c in cs)


# ===== han adversarial audit round 3 (2026-07-31) =====

def test_ical_rejects_out_of_range_years_instead_of_malformed_output():
    """E1: RFC 5545 dates are years 0001-9999; a BC or >=10000 year has no valid
    iCal form, so to_ical must raise (not emit '-0440315'/'123450101' that no
    client, including the reader, can parse)."""
    from chronologia.astrodate import AstroDate, DateSpan
    from chronologia.ical import Event, to_ical, from_ical
    def ev(y):
        return Event(summary="x", span=DateSpan(AstroDate(y, 3, 15),
                                                AstroDate(y, 3, 16)))
    for y in (2024, 1, 9999):                    # in range -> round-trips
        assert from_ical(to_ical(ev(y))) == ev(y)
    for y in (-44, 0, 12345):                    # out of range -> clear error
        with pytest.raises(ValueError):
            to_ical(ev(y))


def test_candidates_do_not_leak_group_gated_constructions():
    """B1: extract_candidates' runner-up enumeration must honour the same
    construction-group gate the composed loop does -- no classical-group (or any
    group-gated) construction may appear that extract_timespan would not return."""
    from chronologia import extract_candidates
    from chronologia.extract.loader import load_lang_spec
    spec = load_lang_spec("en")
    A = datetime(2017, 6, 27, 13, 4)
    for text in ("june", "march 2", "antediem V kalends june", "tomorrow at 3pm"):
        cs = extract_candidates(text, "en", A)
        gated = [c.construction for c in cs
                 if spec.construction_flags.get(c.construction, {}).get("group")]
        assert not gated, f"{text!r}: leaked group-gated {gated}"


@pytest.mark.parametrize("text", [
    "yesterday morning", "june 5th at 3pm", "March 2 at 3pm", "Monday morning"])
def test_composed_primary_has_the_highest_confidence(text):
    """B2: the composed primary is scored over its FULL span, so its confidence
    is at least that of every partial reading it was built from -- a threshold/
    re-sorting consumer can no longer prefer a worse partial by score."""
    from chronologia import extract_candidates
    cs = extract_candidates(text, "en", datetime(2017, 6, 27, 13, 4))
    assert cs and cs[0].confidence == max(c.confidence for c in cs)


# ---------------------------------------------------------------------------
# Round 4 (han holiday-data audit): DATA-001 -- computable holidays that were
# staged as horizon-limited decree tables used to VANISH the year after their
# last tabulated entry.  They are now real computable rules (fixed / easter /
# nth_weekday / weekday_onbefore), verified to reproduce every formerly-
# tabulated date, so they extend indefinitely.
# ---------------------------------------------------------------------------
import pytest as _pytest
from chronologia.civil_holidays import holidays_for, coverage


@_pytest.mark.parametrize("cc,subdiv,name,year", [
    ("ES", "ES-AN", "Día de Andalucía", 2027),      # fixed 2-28; horizon was 2026
    ("ES", "ES-AN", "Día de Andalucía", 2035),
    ("ES", "ES-CN", "Día de Canarias", 2030),        # fixed 5-30
    ("GB", "GB-ENG", "Late Summer Bank Holiday", 2028),  # nth_weekday last-Mon-Aug
    ("GB", "GB-ENG", "Late Summer Bank Holiday", 2040),
])
def test_computable_holiday_no_longer_vanishes_past_old_horizon(cc, subdiv, name, year):
    names = {h.name for h in holidays_for(cc, year, subdiv=subdiv)}
    assert name in names, f"{cc}/{subdiv}/{name} vanished at {year}"


def test_converted_regional_holiday_restores_full_coverage():
    # ES-AN carried a fixed regional holiday as a decree ending 2026; 2027 used
    # to report coverage 'partial' (a holiday silently missing).  Now full.
    assert coverage("ES", 2027, "ES-AN") == "full"


def test_converted_easter_holiday_tracks_easter():
    # Jueves Santo (Maundy Thursday) was a decree table; now easter -3.
    from datetime import date, timedelta
    def easter(y):
        a=y%19;b=y//100;c=y%100;d=b//4;e=b%4;f=(b+8)//25;g=(b-f+1)//3
        h=(19*a+b-d-g+15)%30;i=c//4;k=c%4;l=(32+2*e+2*i-h-k)%7
        m=(a+11*h+22*l)//451;mo=(h+l-7*m+114)//31;da=((h+l-7*m+114)%31)+1
        return date(y,mo,da)
    for yr in (2029, 2033):
        got = {h.name: h.date for h in holidays_for("ES", yr, subdiv="ES-AN")}
        assert "Jueves Santo" in got
        exp = easter(yr) - timedelta(days=3)   # Maundy Thursday
        assert (got["Jueves Santo"].month, got["Jueves Santo"].day) == (exp.month, exp.day)


# ---------------------------------------------------------------------------
# Round 4 (han holiday-data audit): DATA-002 -- a holiday emitted TWICE because
# a computable rule (basis exact) and a redundant decree that re-states it only
# to attach a secondary category (basis tabulated) both fired.  They are one
# civil day: holidays_for must collapse them, keeping the strongest basis and
# unioning categories.
# ---------------------------------------------------------------------------
def test_no_holiday_emitted_twice_on_the_same_day():
    from chronologia.civil_holidays import holidays_for
    from collections import Counter
    for cc in ("GU", "PT", "MK", "LB", "EG", "US", "ES", "GB", "HK", "DE"):
        for yr in (2024, 2025, 2026, 2027):
            counts = Counter((h.name, h.date, h.subdiv, h.span.end)
                             for h in holidays_for(cc, yr))
            dups = [k for k, n in counts.items() if n > 1]
            assert not dups, f"{cc} {yr}: duplicate holiday emissions {dups}"


def test_redundant_decree_merges_category_into_computable_holiday():
    from chronologia.civil_holidays import holidays_for
    gf = [h for h in holidays_for("GU", 2024) if h.name == "Good Friday"]
    assert len(gf) == 1                       # not two rows
    assert gf[0].basis == "exact"             # strongest basis kept
    assert {"public", "unofficial"} <= gf[0].categories   # both categories kept
