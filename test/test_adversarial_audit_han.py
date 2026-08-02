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


# ===========================================================================
# Round 5 (fresh-roster han audit)
# ===========================================================================
from datetime import datetime as _datetime
_A = _datetime(2017, 6, 27, 13, 4)   # a Tuesday


# --- D2: "since <weekday> <clock>" is PAST-anchored, like a bare weekday -----
def test_since_weekday_with_clock_rolls_back_to_most_recent():
    from chronologia import extract_timespan
    span, rem = extract_timespan("since monday 3pm", "en", _A)
    # most recent Monday 3pm at-or-before Tue 27 Jun 13:04 is Mon 26 Jun 15:00
    assert (span.start.year, span.start.month, span.start.day, span.start.hour) \
        == (2017, 6, 26, 15)
    assert span.end.day == 27 and span.end.hour == 13          # open to "now"
    assert rem == ""                                            # "since" consumed


def test_since_weekday_clock_two_sided_range():
    from chronologia import extract_timespan
    span, rem = extract_timespan("since monday 3pm until friday 5pm", "en", _A)
    assert (span.start.month, span.start.day, span.start.hour) == (6, 26, 15)
    assert (span.end.month, span.end.day) == (6, 30)           # Fri 30 Jun
    assert rem == ""


def test_since_bare_weekday_and_qualified_weekday_unchanged():
    from chronologia import extract_timespan
    s1, _ = extract_timespan("since monday", "en", _A)
    assert (s1.start.month, s1.start.day) == (6, 26)
    s2, _ = extract_timespan("since friday 9am", "en", _A)     # Fri 23 Jun 9am
    assert (s2.start.month, s2.start.day, s2.start.hour) == (6, 23, 9)


# --- B1: "at <hour> o'clock" no longer strands the o'clock marker -----------
def test_at_oclock_does_not_strand_marker_en():
    from chronologia import extract_timespan
    _, rem = extract_timespan("at 3 o'clock", "en", _A)
    assert rem == ""
    _, rem2 = extract_timespan("meet at 3 o'clock sharp", "en", _A)
    assert "o'clock" not in rem2 and "oclock" not in rem2


def test_at_oclock_does_not_strand_marker_de():
    from chronologia import extract_timespan
    _, rem = extract_timespan("morgen um 15 uhr", "de", _A)
    assert "uhr" not in rem


# --- Holiday rule corrections (nth-weekday, not weekday_onbefore / last) -----
def test_holiday_nth_weekday_corrections_hold_past_divergence():
    from chronologia.civil_holidays import holidays_for
    import datetime as dt
    def nth(y, m, n, wd):
        d = dt.date(y, m, 1)
        while d.weekday() != wd:
            d += dt.timedelta(days=1)
        return d + dt.timedelta(days=7 * (n - 1))
    # KY National Heroes Day is the 4th Monday of January (Cayman statute); the
    # US territories' Thanksgiving is the 4th Thursday of November (5 USC 6103,
    # matching the vacanza-witnessed us.tab).  Both used to degrade past 2027 --
    # KY to the 3rd Monday, the territories to a 5th Thursday.  (GI/MS/NF King's
    # Birthday is deliberately NOT here: it is the Monday on/before 17 June per
    # the vacanza reference, not the 3rd Monday.)
    cases = [
        ("KY", "National Heroes Day", 2030, nth(2030, 1, 4, 0)),   # 4th Mon Jan
        ("GU", "Thanksgiving Day", 2029, nth(2029, 11, 4, 3)),     # 4th Thu Nov
        ("VI", "Thanksgiving Day", 2035, nth(2035, 11, 4, 3)),
        ("PR", "Thanksgiving Day", 2029, nth(2029, 11, 4, 3)),
    ]
    for cc, name, yr, exp in cases:
        got = {h.name: h.date for h in holidays_for(cc, yr)}
        assert name in got, f"{cc}/{name} {yr} missing"
        assert (got[name].month, got[name].day) == (exp.month, exp.day), \
            f"{cc}/{name} {yr}: {got[name]} != {exp}"


# --- R6 duration: unfolded scale-number tail, and folded-fraction additive ---
def test_duration_scale_tail_is_composed_not_truncated():
    # "one thousand five hundred hours" folds to [1, thousand, 500, hours]; the
    # thousand-scale word is withheld from the generic fold (deep-time frame) but
    # a fixed-width duration has no deep-time reading, so it is composed to the
    # true 1500h -- not the truncated 500h, and not honest-None.
    from chronologia import extract_duration
    assert extract_duration("one thousand five hundred hours", "en-us") \
        .duration.total_seconds() == 1500 * 3600
    assert extract_duration("two thousand five hundred minutes", "en-us") \
        .duration.total_seconds() == 2500 * 60
    # legit hundred-scale counts are unaffected
    assert extract_duration("five hundred hours", "en-us").duration.total_seconds() \
        == 500 * 3600


def test_duration_additive_half_parity_across_inflecting_languages():
    from chronologia import extract_duration
    from datetime import timedelta
    # German inflects "half" to "halbe", which the folder turns into a 0.5 token;
    # the "... und eine halbe" idiom must still add 30 min, like en/fr.
    assert extract_duration("eine stunde und eine halbe", "de-de").duration \
        == timedelta(minutes=90)
    assert extract_duration("zwei stunden und eine halbe", "de-de").duration \
        == timedelta(minutes=150)
    assert extract_duration("an hour and a half", "en-us").duration \
        == timedelta(minutes=90)


# --- R6 deep-time resolvers: clean ValueError on malformed / non-finite -------
def test_resolve_bp_and_cosmic_reject_bad_values_as_valueerror():
    import pytest as _pt
    from chronologia.eras import resolve_bp
    from chronologia.cosmology import resolve_cosmic
    for bad in ("abc", float("nan"), float("inf"), float("-inf")):
        with _pt.raises(ValueError):
            resolve_bp(bad, "Ma")
        with _pt.raises(ValueError):
            resolve_cosmic(bad, "ka")
    # documented string input still works
    assert resolve_bp("66", "Ma").start.year == -65998050


# --- R6 NZ Labour Day is the FOURTH Monday of October (Holidays Act 2003 s44) -
def test_nz_labour_day_is_fourth_monday_not_last():
    from chronologia.civil_holidays import holidays_for
    import datetime as dt
    for yr in (2028, 2029, 2035):          # 5-Monday Octobers: 4th != last
        d = dt.date(yr, 10, 1)
        while d.weekday() != 0:
            d += dt.timedelta(days=1)
        fourth = d + dt.timedelta(days=21)
        got = [h.date for h in holidays_for("NZ", yr) if h.name == "Labour Day"]
        assert got and (got[0].month, got[0].day) == (fourth.month, fourth.day)


# --- R6 B1: extract_candidates must surface range/open-range readings ---------
def test_extract_candidates_surfaces_range_readings_as_primary():
    from chronologia import extract_timespan
    from chronologia.extract import extract_candidates
    for t in ["june 5 to june 12", "between monday and friday",
              "until friday", "from 9 to 5", "since 2019"]:
        span, _ = extract_timespan(t, "en", _A)
        cands = extract_candidates(t, "en", _A, limit=5)
        assert cands, t
        # extract_timespan's own answer is present AND ranked first (the two
        # APIs must agree on the top reading)
        assert any(c.span.start == span.start and c.span.end == span.end
                   for c in cands), f"{t}: range answer missing from candidates"
        assert (cands[0].span.start == span.start
                and cands[0].span.end == span.end), \
            f"{t}: top candidate disagrees with extract_timespan"


# --- R7 iCal timezone (E1): a tz-aware instant serializes as UTC+Z, not floating
def test_ical_serializes_tzaware_as_utc_z_not_floating():
    from chronologia.astrodate import AstroDate, DateSpan
    from chronologia.ical import to_ical, from_ical
    from datetime import timezone, timedelta
    a = AstroDate(2024, 6, 1, 10, 30, 0, tzinfo=timezone(timedelta(hours=5)))
    b = AstroDate(2024, 6, 1, 12, 30, 0, tzinfo=timezone(timedelta(hours=5)))
    lines = to_ical(DateSpan(a, b))
    # +05:00 10:30 is 05:30 UTC, written with a trailing Z (not floating)
    assert "DTSTART:20240601T053000Z" in lines
    # round-trip preserves the instant AND the UTC zone
    ev = from_ical(lines)
    assert ev.span.start.hour == 5 and ev.span.start.tzinfo is not None
    assert ev.span.start.utcoffset().total_seconds() == 0
    # a naive AstroDate stays floating (no Z)
    naive = to_ical(DateSpan(AstroDate(2024, 6, 1, 10, 30, 0),
                             AstroDate(2024, 6, 1, 11, 0, 0)))
    assert "DTSTART:20240601T103000" in naive and "103000Z" not in naive


# --- R7 Niue Peniamina Gospel Day (nth/last class) = 4th Monday of October -----
def test_niue_peniamina_gospel_day_is_fourth_monday():
    from chronologia.civil_holidays import holidays_for
    import datetime as dt
    for yr in (2028, 2029, 2035):
        d = dt.date(yr, 10, 1)
        while d.weekday() != 0:
            d += dt.timedelta(days=1)
        fourth = d + dt.timedelta(days=21)
        got = [h.date for h in holidays_for("NU", yr)
               if h.name == "Peniamina Gospel Day"]
        assert got and (got[0].month, got[0].day) == (fourth.month, fourth.day)


# --- R7 range candidate confidence (D1): not laundered from unrelated text -----
def test_range_candidate_confidence_not_laundered_from_unrelated_reading():
    from chronologia.extract import extract_candidates
    alone = extract_candidates("since monday", "en", _A)
    carried = extract_candidates(
        "since monday, exactly 2020-06-15T10:00:00", "en", _A)
    op_a = [c for c in alone if c.construction == "open_range"]
    op_c = [c for c in carried if c.construction == "open_range"]
    assert op_a and op_c
    # the trailing unrelated ISO literal (not consumed by the range) must not
    # raise the range's own confidence
    assert op_a[0].confidence == op_c[0].confidence


# --- R8 strftime %W off-by-one when Jan 1 is a Monday -------------------------
def test_strftime_W_matches_stdlib_including_monday_jan1():
    from chronologia.astrodate import AstroDate
    from datetime import date
    # years starting on Monday (jan1_wd==0) were one week short
    for y in (2018, 2024, 1, 2029):
        for (m, d) in [(1, 1), (1, 7), (1, 8), (6, 15), (12, 31)]:
            assert AstroDate(y, m, d).strftime("%W") == date(y, m, d).strftime("%W")


# --- R8 bare clock range with a trailing meridiem uses the am/pm fallback -----
def test_bare_clock_range_with_meridiem_no_bogus_day_roll():
    from chronologia import extract_timespan
    # "9 to 5 pm" (no from/between) must read 09:00-17:00, like "from 9 to 5 pm",
    # not borrow pm onto 9 (21:00) and roll 5pm to the next day (~20h span).
    s, _ = extract_timespan("9 to 5 pm", "en", _A)
    assert (s.start.hour, s.start.day) == (9, 28)
    assert (s.end.hour, s.end.day) == (17, 28)
    # a meridiem-less "9 to 5" stays the subtractive clock ("nine minutes to 5")
    s2, _ = extract_timespan("9 to 5", "en", _A)
    assert (s2.start.hour, s2.start.minute) == (4, 51)


# --- R9 numfold: "hundred" word recognized (was excluded by range(0,100)) -----
def test_numfold_hundred_word_recognized_across_families():
    from chronologia import extract_timespan
    from datetime import datetime, timedelta
    r = datetime(2017, 6, 27, 13, 4)
    # +100 days / +100 minutes must resolve, not vanish or default to +1 day
    assert extract_timespan("через сто дней", "ru", r)[0].start.day == 5      # Oct 5
    assert extract_timespan("через сто дней", "ru", r)[0].start.month == 10
    assert extract_timespan("za sto minut", "pl", r)[0].start.hour == 14      # 14:44
    assert extract_timespan("száz nap múlva", "hu", r)[0].start.month == 10
    assert extract_timespan("sata päivän kuluttua", "fi", r)[0].start.month == 10


# --- R9 D3: a distant clock/daypart must NOT fold onto a date across junk -----
def test_compose_requires_adjacency_no_distant_clock_bleed():
    from chronologia import extract_timespan
    # "and also 10:00" is separated from monday by unrelated tokens -> the clock
    # must NOT attach; monday stays day-wide and 10:00 lands in the remainder.
    s, rem = extract_timespan("since monday and also 10:00", "en", _A)
    assert (s.start.month, s.start.day, s.start.hour) == (6, 26, 0)
    assert "10:00" in rem
    s2, rem2 = extract_timespan("from monday to friday and also 10:00", "en", _A)
    assert (s2.start.day, s2.end.day) == (3, 8)      # Mon 3 Jul .. Sat 8 Jul
    assert "10:00" in rem2
    # adjacent composition still works
    s3, _ = extract_timespan("since monday 3pm", "en", _A)
    assert (s3.start.day, s3.start.hour) == (26, 15)


# --- R9 clock-range: extract_candidates top == extract_timespan for N to M pm -
def test_candidates_agree_on_meridiem_clock_range_top():
    from chronologia import extract_timespan
    from chronologia.extract import extract_candidates
    for t in ["5 to 9 am", "11 to 1 pm", "monday 9 to 5 pm", "9 to 5 pm"]:
        s, _ = extract_timespan(t, "en", _A)
        cands = extract_candidates(t, "en", _A)
        assert cands and cands[0].span.start == s.start \
            and cands[0].span.end == s.end, t


# --- R10 B2: "ramadan <Gregorian year>" is the holiday, not AH-year reckoned ---
def test_ramadan_gregorian_year_is_holiday_not_far_future_hijri():
    from chronologia import extract_timespan
    # AH 2027 would be 2588 CE; the reckoned candidate is vetoed (year beyond the
    # umm_al_qura table) so holiday_ref wins: Ramadan 2027 starts 2027-02-08.
    s, _ = extract_timespan("ramadan 2027", "en-us", _A)
    assert s.start.year == 2027 and s.start.month == 2
    # genuine Hijri years still read as reckoned dates (unbounded arithmetic)
    assert extract_timespan("ramadan 1446", "en-us", _A)[0].start.year == 2025
    assert extract_timespan("ramadan 1000", "en-us", _A)[0].start.year == 1592


# --- R10 Hungarian possessive day-ordinal folds ("-e"/"-én") -----------------
def test_hungarian_possessive_day_ordinal_folds():
    from chronologia import extract_timespan
    for text, day in [("április tizenötödike", 15), ("április tizenötödikén", 15),
                      ("május huszonegyedike", 21), ("március harmincegyedike", 31),
                      ("április elseje", 1)]:
        s, _ = extract_timespan(text, "hu", _A)
        assert s is not None and s.start.day == day, (text, s)
    # bare ordinal + digit forms unaffected
    assert extract_timespan("április tizenötödik", "hu", _A)[0].start.day == 15


# --- R10 Estonian compound tens-ordinal folds (21-29, 31) --------------------
def test_estonian_compound_ordinal_folds():
    from chronologia import extract_timespan
    for text, day in [("kahekümne esimene aprill", 21),
                      ("kahekümne üheksas mai", 29),
                      ("kolmekümne esimene mai", 31)]:
        s, _ = extract_timespan(text, "et", _A)
        assert s is not None and s.start.day == day, (text, s)
    # a bare unit ordinal is still day 1, not merged
    assert extract_timespan("esimene aprill", "et", _A)[0].start.day == 1


# --- R11 recurrence: occurrences() preserves a datetime's time-of-day --------
def test_occurrences_datetime_dtstart_keeps_time_for_until_cutoff():
    from datetime import datetime
    from chronologia.recurrence import parse_rrule, occurrences
    from chronologia.astrodate import AstroDate
    rec = parse_rrule("FREQ=DAILY;UNTIL=20170627T000000")
    # a 23:00 dtstart is AFTER the 00:00 wall-clock cutoff, so it is excluded --
    # and a datetime input must behave identically to the AstroDate input (the
    # time-of-day used to be silently dropped to midnight for datetimes).
    dt = list(occurrences(rec, datetime(2017, 6, 27, 23, 0, 0)))
    ad = list(occurrences(rec, AstroDate(2017, 6, 27, 23, 0, 0)))
    assert dt == ad == []
    # a call-level until= override honours the time-of-day too
    from chronologia.recurrence import every
    occ = list(occurrences(every("daily", count=100),
                           datetime(2017, 6, 27, 20, 0, 0),
                           until=datetime(2017, 6, 29, 5, 0, 0)))
    assert len(occ) == 2   # 06-29 20:00 is after the 05:00 cutoff -> excluded


# --- R11 timespan: a trailing weekday on the RIGHT range endpoint scopes both -
def test_bare_clock_range_with_trailing_weekday_scopes_both_endpoints():
    from chronologia import extract_timespan
    # "9am to 5pm on monday": the Monday on the right endpoint applies to the
    # left bare clock too -- Monday 09:00-17:00, not a ~6-day span from the
    # anchor's day to Monday.
    for t in ["9am to 5pm on monday", "9am to 5pm monday",
              "from 9am to 5pm on monday"]:
        s, _ = extract_timespan(t, "en", _A)
        assert (s.start.month, s.start.day, s.start.hour) == (7, 3, 9), t
        assert (s.end.month, s.end.day, s.end.hour) == (7, 3, 17), t
    # the mirror (weekday on the left) and plain clock ranges are unchanged
    s2, _ = extract_timespan("monday 9am to 5pm", "en", _A)
    assert (s2.start.day, s2.start.hour) == (3, 9)
    s3, _ = extract_timespan("9am to 5pm", "en", _A)
    assert (s3.start.month, s3.start.day) == (6, 28)   # anchor's own next day


# --- R11 numfold thousand-scale: composed to the TRUE value, az no bogus span -
def test_thousand_scale_duration_is_composed_across_locales():
    from chronologia import extract_duration, extract_timespan
    from datetime import datetime
    r = datetime(2017, 6, 27, 13, 4)
    # a spelled thousand-scale word is withheld from the generic fold (deep-time
    # frame) but a fixed-width duration composes it: "bin beş yüz gün" = 1500,
    # "mil e quinhentos dias" = 1500 -- the true value, not the truncated 500.
    assert extract_duration("bin beş yüz gün önce", "tr").duration.days == 1500
    assert extract_duration("mil e quinhentos dias atrás", "pt").duration.days == 1500
    assert extract_duration("mil días", "es").duration.days == 1000
    assert extract_duration("dois mil dias", "pt").duration.days == 2000
    assert extract_duration("iki min gün əvvəl", "az").duration.days == 2000
    # small durations are unaffected
    assert extract_duration("3 gün önce", "tr").duration.days == 3
    assert extract_duration("há 3 dias", "pt").duration.days == 3
    # az "il əvvəl" (year + bare "ago" postposition) must NOT fabricate a span;
    # the locative early-of-year form still resolves.
    assert extract_timespan("il əvvəl", "az", r) is None
    assert extract_timespan("min il əvvəl", "az", r) is None
    assert extract_timespan("il əvvəlində", "az", r) is not None


# --- R12 broad sweep + calendars ---------------------------------------------
def test_spanish_pasado_manana_is_day_after_tomorrow():
    from chronologia import extract_timespan
    # "pasado mañana" = day after tomorrow (2017-06-29 from Tue 27 Jun), NOT
    # parsed as "pasado"(last)+"mañana"(morning) = yesterday morning.
    s, _ = extract_timespan("pasado mañana", "es", _A)
    assert (s.start.month, s.start.day) == (6, 29)
    # the daypart/marker uses of the same words are unaffected
    assert extract_timespan("esta mañana", "es", _A)[0].start.hour == 6
    assert extract_timespan("el mes pasado", "es", _A)[0].start.month == 5


def test_arabic_baad_azzuhr_composes_pm_clock():
    from chronologia import extract_timespan
    # "الساعة الثالثة بعد الظهر" = 3 PM (today 15:00, still future vs 13:04), not
    # 3 AM tomorrow with the PM marker stranded.
    s, rem = extract_timespan("الساعة الثالثة بعد الظهر", "ar", _A)
    assert (s.start.day, s.start.hour) == (27, 15) and "بعد" not in rem
    # bare afternoon daypart band is unchanged
    b, _ = extract_timespan("بعد الظهر", "ar", _A)
    assert (b.start.hour, b.end.hour) == (12, 18)


def test_saka_era_matches_canonical_gregorian_correspondence():
    from chronologia.eras import resolve_era
    from datetime import date
    # Gregorian = Saka + 78 (Saka 1879 = 22 Mar 1957, the adoption epoch);
    # Chaitra 1 shifts to 21 March in a Gregorian leap year.
    assert resolve_era("saka", 1879) == date(1957, 3, 22)
    assert resolve_era("saka", 1947) == date(2025, 3, 22)     # common year
    assert resolve_era("saka", 1946) == date(2024, 3, 21)     # leap year -> 21


# --- R13 Portuguese "depois de amanhã" = day after tomorrow (was tomorrow) ----
def test_portuguese_depois_de_amanha_is_day_after_tomorrow():
    from chronologia import extract_timespan
    s, rem = extract_timespan("depois de amanhã", "pt", _A)
    assert (s.start.month, s.start.day) == (6, 29) and rem == ""
    # the -2 form and bare tomorrow are unchanged
    assert extract_timespan("anteontem", "pt", _A)[0].start.day == 25
    assert extract_timespan("amanhã", "pt", _A)[0].start.day == 28


# --- R13 cosmology: negative "years since Big Bang" is rejected ---------------
def test_resolve_cosmic_rejects_negative_years_since_big_bang():
    import pytest as _pt
    from chronologia.cosmology import resolve_cosmic
    with _pt.raises(ValueError):
        resolve_cosmic(-5, "Ga")     # before the Big Bang -> nonsensical
    # zero and positive are fine
    assert resolve_cosmic(0, "Ga") is not None
    assert resolve_cosmic(13, "Ga") is not None


# --- R13 numfold: Romance feminine hundreds + Italian fused thousands fold ----
def test_romance_feminine_hundreds_fold():
    from chronologia import extract_duration
    assert extract_duration("mil e quinhentas horas", "pt").duration.total_seconds() \
        == 1500 * 3600
    assert extract_duration("quinientas horas", "es").duration.total_seconds() \
        == 500 * 3600
    assert extract_duration("cincocentas horas", "gl").duration.total_seconds() \
        == 500 * 3600
    # masculine and invariable "cem" unaffected
    assert extract_duration("quinhentos dias", "pt").duration.days == 500
    assert extract_duration("cem dias", "pt").duration.days == 100


def test_italian_fused_thousands_fold():
    from chronologia import extract_duration
    assert extract_duration("duemila giorni", "it").duration.days == 2000
    assert extract_duration("diecimila giorni", "it").duration.days == 10000
    # space-separated and bare forms unchanged
    assert extract_duration("due mila giorni", "it").duration.days == 2000
    assert extract_duration("mille giorni", "it").duration.days == 1000


# --- R14 cross-locale ±2 relative-day idioms (missing named_day_2/-2 files) ---
def test_cross_locale_day_after_before_idioms():
    from chronologia import extract_timespan
    _A2 = _A  # Tue 27 Jun 2017
    cases = [
        ("demà passat", "ca", 29), ("despús-demà", "ca", 29),      # +2
        ("abans-d'ahir", "ca", 25), ("despús-ahir", "ca", 25),     # -2
        ("pasado mañá", "gl", 29),                                 # +2
        ("завчера", "bg", 25), ("онзи ден", "bg", 25),             # -2
        ("kelmarin dulu", "ms", 25),                               # -2
    ]
    for idiom, lang, day in cases:
        s, rem = extract_timespan(idiom, lang, _A2)
        assert s is not None and s.start.day == day and rem == "", (idiom, lang, s)
    # existing +/-1 forms unchanged
    assert extract_timespan("demà", "ca", _A2)[0].start.day == 28
    assert extract_timespan("ahir", "ca", _A2)[0].start.day == 26


# --- R14 D1: an ordinal weekday ("2nd monday") is not mis-read as a day-of-month
def test_nth_weekday_after_does_not_misread_ordinal_weekday_as_day():
    from chronologia import extract_timespan
    # "the tuesday after the 2nd monday": the old code read the "2" of "2nd
    # monday" as June 2 and returned a fabricated date; it must not do that.
    s, _ = extract_timespan("the tuesday after the 2nd monday", "en", _A)
    assert not (s.start.month == 6 and s.start.day == 2)   # no bogus "day 2"
    # genuine "weekday after the <day-of-month>" still works
    assert extract_timespan("the monday after the 15th", "en", _A)[0].start.day == 19
    assert extract_timespan("tuesday after april 1", "en", _A)[0].start.day == 3


# --- R15 D3: "the last N days of X" is not the ordinal Nth day ----------------
def test_last_n_days_of_scope_not_misread_as_ordinal_day():
    from chronologia import extract_timespan
    # a rel-marker before a scoped-ordinal means the number is a COUNT, not the
    # ordinal day-of-month; "the last two days of the month" must not return the
    # 2nd day (June 2).
    s = extract_timespan("the last two days of the month", "en", _A)
    assert s is None or not (s[0].start.month == 6 and s[0].start.day == 2)
    # legitimate scoped-ordinal readings are unaffected
    assert extract_timespan("the last day of the month", "en", _A)[0].start.day == 30
    assert extract_timespan("the 2nd day of the month", "en", _A)[0].start.day == 2
    assert extract_timespan("the last friday of june", "en", _A)[0].start.day == 30
    assert extract_timespan("last saturday of february 2016", "en", _A)[0].start.day == 27


# --- R16: adversarial wave 16 -----------------------------------------------
def test_scoped_century_bc_ad_keeps_era_under_part():
    """"the mid 5th century BC" must stay on the BC axis, not silently drop the
    era word and return a positive-year AD span."""
    from chronologia import extract_timespan
    early = extract_timespan("the early 5th century BC", "en", _A)
    assert early[0].start.year == -499 and early[0].end.year == -466
    assert early.remainder == ""                       # "BC" consumed
    late = extract_timespan("the late 2nd century BC", "en", _A)
    assert late[0].start.year == -132 and late[0].end.year == -99
    ad = extract_timespan("the mid 5th century AD", "en", _A)
    assert ad[0].start.year == 433 and ad.remainder == ""
    # plain (part-less) scoped BC/AD unchanged
    plain = extract_timespan("5th century BC", "en", _A)
    assert plain[0].start.year == -499 and plain[0].end.year == -399


def test_french_plural_weekday_recurrence():
    """"tous les lundis" (the standard French "every Monday") must read WEEKLY,
    not fall through to a spurious YEARLY-on-a-month reading."""
    from chronologia import extract_recurrence
    r = extract_recurrence("tous les lundis", "fr", _A)
    assert r is not None and r[0].to_string() == "FREQ=WEEKLY;BYDAY=MO"
    # bounded with the French "jusqu'en <month>" until-marker
    b = extract_recurrence("tous les lundis jusqu'en août", "fr", _A)
    assert b is not None
    assert b[0].to_string() == "FREQ=WEEKLY;UNTIL=20170801T000000;BYDAY=MO"
    # the yearly-date reading ("tous les 10 mai") must still win where meant
    y = extract_recurrence("tous les 10 mai", "fr", _A)
    assert y[0].to_string() == "FREQ=YEARLY;BYMONTH=5;BYMONTHDAY=10"


def test_ical_allday_until_is_date_only():
    """RFC 5545 3.3.10: an all-day (VALUE=DATE) event's RRULE UNTIL must be a
    bare DATE, matching DTSTART -- not a DATE-TIME."""
    from datetime import datetime
    from chronologia import to_ical
    from chronologia.events import Event
    from chronologia.astrodate import AstroDate, DateSpan
    from chronologia.recurrence import every
    span = DateSpan(AstroDate(2017, 6, 27), AstroDate(2017, 6, 28))
    ev = Event(summary="Standup", span=span, duration=None,
               recurrence=every("daily", until=AstroDate(2017, 7, 5)))
    ics = to_ical(ev)
    assert "DTSTART;VALUE=DATE:20170627" in ics
    assert "RRULE:FREQ=DAILY;UNTIL=20170705\r\n" in ics or \
           "RRULE:FREQ=DAILY;UNTIL=20170705" in ics
    assert "UNTIL=20170705T000000" not in ics


def test_french_un_compound_tail_folds_as_cardinal():
    """R17: French "un"/"une" is blacklisted from the number vocabulary so it
    stays the indefinite article ("un jour") and the clock-fraction article
    ("un quart d'heure").  That blacklist truncated every compound number that
    *ends* in one -- "vingt et un" read as 1, "cent un" dropped the "un"
    entirely.  The un-compound licensing reads "un"/"une" as the cardinal 1 in
    exactly the tail position (directly after a number, or across "et" from
    one) so the compound composes, while every article use stays untouched."""
    from datetime import timedelta
    # compound tails now fold: <tens> et un, hundreds/thousands un, vigesimal
    assert extract_duration("vingt et un jours", "fr").duration == timedelta(days=21)
    assert extract_duration("trente et un jours", "fr").duration == timedelta(days=31)
    assert extract_duration("soixante et un jours", "fr").duration == timedelta(days=61)
    assert extract_duration("cent un jours", "fr").duration == timedelta(days=101)
    assert extract_duration("quatre-vingt-un jours", "fr").duration == timedelta(days=81)
    assert extract_duration("deux cent un jours", "fr").duration == timedelta(days=201)
    assert extract_duration("mille un jours", "fr").duration == timedelta(days=1001)
    assert extract_duration("cent vingt et un jours", "fr").duration == timedelta(days=121)
    # feminine tail before the hour unit: "vingt et une heures" == 21 hours
    assert extract_duration("vingt et une heures", "fr").duration == timedelta(hours=21)
    # no regression: the article readings stay byte-identical
    assert extract_duration("un jour", "fr").duration == timedelta(days=1)
    assert extract_duration("une heure", "fr").duration == timedelta(hours=1)
    assert extract_duration("un quart d heure", "fr").duration == timedelta(minutes=15)
    assert extract_duration("une semaine", "fr").duration == timedelta(days=7)
    assert extract_duration("une heure et demie", "fr").duration == timedelta(hours=1, minutes=30)


# --- R17 E1: leading fraction scales an explicit following count -------------
def test_leading_fraction_scales_following_count():
    """"half of a hundred days" is 0.5*100 = 50 days, not the full 100 with the
    fraction silently dropped into the remainder."""
    from datetime import timedelta
    from chronologia import extract_duration
    assert extract_duration("half of a hundred days", "en")[0] == timedelta(days=50)
    assert extract_duration("quarter of two hundred days", "en")[0] == timedelta(days=50)
    assert extract_duration("half of two hundred minutes", "en")[0] == timedelta(minutes=100)
    assert extract_duration("half of one thousand days", "en")[0] == timedelta(days=500)
    # the plain / unit-adjacent forms are unchanged
    assert extract_duration("half a day", "en")[0] == timedelta(hours=12)
    assert extract_duration("a hundred days", "en")[0] == timedelta(days=100)
    assert extract_duration("three quarters of an hour", "en")[0] == timedelta(minutes=45)


# --- R18 E1: spoken-hour meridiem for subtractive "to twelve am/pm" ----------
def test_subtractive_to_twelve_meridiem_side_of_noon():
    """"a quarter to twelve pm" is a quarter to NOON (11:45), not 23:45: the
    meridiem must attach to the SPOKEN hour (12), not the value after the "to"
    rollback decrements it to 11."""
    from chronologia import extract_timespan
    def hm(p):
        r = extract_timespan(p, "en", _A); return (r.span.start.hour, r.span.start.minute)
    assert hm("quarter to twelve pm") == (11, 45)   # quarter to noon
    assert hm("quarter to twelve am") == (23, 45)   # quarter to midnight
    assert hm("quarter to one pm") == (12, 45)
    assert hm("quarter to eleven pm") == (22, 45)
    # bare meridiem hours unchanged
    assert hm("twelve pm") == (12, 0)
    assert hm("twelve am") == (0, 0)
    assert hm("half past twelve pm") == (12, 30)
    assert hm("half past twelve am") == (0, 30)


# --- R18 V1: business-days offset declines an unresolvable reference ---------
def test_business_days_before_unresolved_reference_declines():
    """"N business days before/after <X>" where <X> does not resolve must NOT
    silently compute N business days FORWARD from the anchor (dropping the
    marker and inverting a "before"); it declines, like the plain offset path."""
    from chronologia import extract_timespan
    assert extract_timespan("2 business days before new year", "en", _A) is None
    assert extract_timespan("3 business days after new year", "en", _A) is None
    # a resolvable reference and the bare form are unaffected
    assert extract_timespan("2 business days before christmas", "en", _A) is not None
    assert extract_timespan("in 3 business days", "en", _A)[0].start.day == 30


# --- R18 DATA-002: Romania Epiphany / St John only from 2024 -----------------
def test_romania_epiphany_only_from_2024():
    from chronologia.civil_holidays import holidays_for
    names_2023 = {h.name for h in holidays_for("RO", 2023)}
    names_2024 = {h.name for h in holidays_for("RO", 2024)}
    assert "Botezul Domnului - Boboteaza" not in names_2023
    assert "Botezul Domnului - Boboteaza" in names_2024
    assert "Soborul Sfântului Proroc Ioan Botezătorul" not in names_2023
    assert "Soborul Sfântului Proroc Ioan Botezătorul" in names_2024


# --- R19: EDTF reversed interval must raise, not accept a zero-width span ----
def test_edtf_reversed_interval_raises():
    """A reversed EDTF interval ("2004-01/2003-12") is malformed per ISO 8601-2
    and must raise EdtfParseError -- not silently return a zero-width span at the
    later endpoint (the off-by-one the non-strict DateSpan guard let through)."""
    import pytest as _pytest
    from chronologia.edtf import parse_edtf, EdtfParseError
    for s in ("2004-01/2003-12", "2004-01-01/2003-12-31", "2005/2004-12",
              "1985/1980"):
        with _pytest.raises(EdtfParseError):
            parse_edtf(s)
    # valid intervals (ascending, equal, qualified) are unaffected
    assert parse_edtf("2004-01/2004-03").span.start.month == 1
    assert parse_edtf("2004/2004").span.start.year == 2004
    assert parse_edtf("1984?/2004").span.start.year == 1984


# --- R19 B1: %y for a BCE/negative year is the magnitude's last two digits ---
def test_strftime_y_directive_for_negative_year():
    """AstroDate.strftime('%y') must give the last two digits of the year
    magnitude, not Python's negative-modulo artifact (-44 %% 100 == 56)."""
    from chronologia.astrodate import AstroDate
    assert AstroDate(-44, 3, 15).strftime("%y") == "44"
    assert AstroDate(-1, 1, 1).strftime("%y") == "01"
    # CE years unchanged
    assert AstroDate(2017, 6, 27).strftime("%y") == "17"
    assert AstroDate(5, 1, 1).strftime("%y") == "05"


# --- R20 EC1: Russian/Ukrainian feminine "one" in compounds folds correctly --
def test_slavic_feminine_one_compound():
    """"двадцать одна минута" is 21 minutes: the feminine "одна" (agreeing with
    the feminine noun минута) must be a number-run member, or the compound folds
    to N-1 (20)."""
    from datetime import timedelta
    from chronologia import extract_duration
    assert extract_duration("двадцать одна минута", "ru")[0] == timedelta(minutes=21)
    assert extract_duration("сорок одна минута", "ru")[0] == timedelta(minutes=41)
    assert extract_duration("сто одна минута", "ru")[0] == timedelta(minutes=101)
    assert extract_duration("двадцать одну минуту", "ru")[0] == timedelta(minutes=21)
    assert extract_duration("тридцять одна хвилина", "uk")[0] == timedelta(minutes=31)
    assert extract_duration("двадцять одна хвилина", "uk")[0] == timedelta(minutes=21)
    # unchanged: bare one, masculine compound, feminine two
    assert extract_duration("одна минута", "ru")[0] == timedelta(minutes=1)
    assert extract_duration("двадцать один день", "ru")[0] == timedelta(days=21)
    assert extract_duration("двадцать две минуты", "ru")[0] == timedelta(minutes=22)


# --- R22 B1: extract_candidates must apply the same impossible-date veto ------
def test_candidates_agree_with_timespan_on_impossible_date_veto():
    """extract_candidates must not surface a fabricated reading that
    extract_timespan refuses via the stranded-impossible-date veto: "the ides of
    march 44 BC" strands "44 BC", so the roman_date 2017 reading is a fabricated
    date -- extract_timespan returns None and extract_candidates must not rank
    that 2017 reading first (the two APIs must agree on the top answer)."""
    from chronologia import extract_timespan, extract_candidates
    assert extract_timespan("the ides of march 44 BC", "en", _A) is None
    cands = extract_candidates("the ides of march 44 BC", "en", _A)
    # no surfaced candidate may be the fabricated roman_date 2017-03-15 reading
    for c in cands:
        if c.construction == "roman_date" and c.span is not None:
            assert c.span.start.year != 2017, "fabricated 2017 ides re-surfaced"
    # the 32nd-of-february fabrication is likewise refused by both APIs
    assert extract_timespan("the 32nd of february 2017", "en", _A) is None
    # legitimate readings are NOT over-vetoed: both APIs still agree
    assert extract_timespan("the ides of march", "en", _A) is not None
    ic = extract_candidates("the ides of march", "en", _A)
    assert ic and ic[0].span.start.month == 3 and ic[0].span.start.day == 15
    assert extract_candidates("the 5th of june 2020", "en", _A)[0].span.start.day == 5


# --- R21: reverse-chronological deep-time ranges span both endpoints ----------
def test_deep_time_reverse_range_spans_both_endpoints():
    """"from the neolithic to the oligocene" (left younger than right) is not a
    civil ordering error -- deep time is acyclic -- so it names the same span as
    the forward "from the oligocene to the neolithic", not a broken partial."""
    from chronologia import extract_timespan
    fwd = extract_timespan("from the oligocene to the neolithic", "en", _A)
    rev = extract_timespan("from the neolithic to the oligocene", "en", _A)
    assert rev is not None and rev.remainder == ""
    assert (rev.span.start, rev.span.end) == (fwd.span.start, fwd.span.end)
    # a civil reversed range (no deep-time endpoint) is still NOT swapped
    civ = extract_timespan("june 12 2020 to june 5 2020", "en", _A)
    assert civ is None or "june 5" in civ.remainder
    # forward deep-time and civil/clock/weekday ranges unaffected
    assert extract_timespan("from the jurassic to the neolithic", "en", _A) is not None
    assert extract_timespan("from june 5 to june 12", "en", _A).span.start.month == 6


# --- R18: subtractive clock must beat an absurd cross-midnight clock range ----
def test_subtractive_clock_beats_descending_meridiem_range():
    """"ten to eight pm" is the subtractive clock (ten minutes to eight pm ==
    19:50), not a range.  Read as two endpoints the same-meridiem pair descends
    (10pm > 8pm), so the range only became a span by rolling the right end a day
    forward -- an absurd ~22h band (22:00 -> 20:01 next day) that used to preempt
    the correct minute-wide clock.  A bare (unled) descending same-meridiem pair
    whose whole slice reads as one clock must yield the subtractive clock."""
    from chronologia import extract_timespan

    def hm(t):
        r = extract_timespan(t, "en", _A)
        assert r is not None and r.span is not None and r.remainder == ""
        s = r.span.start
        return s.hour, s.minute

    assert hm("ten to eight pm") == (19, 50)
    assert hm("twenty to twelve pm") == (11, 40)
    assert hm("ten to twelve pm") == (11, 50)
    # no meridiem still reads as the subtractive clock, unchanged
    assert hm("ten to eight") == (7, 50)
    assert hm("quarter to five") == (4, 45)

    # ASCENDING same-day clock ranges are real ranges and stay ranges: the pair
    # never crosses midnight, so the bail never fires.
    def span(t):
        r = extract_timespan(t, "en", _A)
        assert r is not None and r.span is not None
        return r.span.start, r.span.end

    a, b = span("5 to 9 am")
    assert (a.hour, b.hour) == (5, 9)
    a, b = span("8 to 11 pm")
    assert (a.hour, b.hour) == (20, 23)
    # an explicit lead is a deliberate range even across midnight: "from 10 pm
    # to 8 am" is a legit overnight span (no single subtractive reading), kept.
    a, b = span("from 10 pm to 8 am")
    assert (a.hour, a.day) == (22, 27) and (b.hour, b.day) == (8, 28)


# --- R22a: spelled ordinal LIST across "and" is not folded into one date ------
def test_spelled_ordinal_list_across_and_keeps_first():
    """"first and third of June" is a LIST of the 1st and the 3rd; the English
    spelled-number fold must not merge "first and third" across "and" and read
    it as the bare last ordinal (June 3, "first" erased).  The additive "and"
    is genuine only after a magnitude >= 100 ("one hundred and five"), never
    between two small ordinals.  Accept None, or a June-3 reading only while
    "first" is still visible in a non-empty remainder, or a real two-date span
    -- but never a silent June 3 with "first" erased."""
    from chronologia import extract_timespan
    r = extract_timespan("first and third of June", "en", _A)
    if r is not None:
        d = r.span.start.day
        if d == 3:
            # June 3 is only acceptable if "first" was NOT silently swallowed
            assert "first" in r.remainder, "'first' silently erased from a list"
    # the genuine magnitude-additive folds are unchanged (not turned into lists)
    from chronologia.extract.numfold import fold_en
    from chronologia.extract.pipeline import pretokens
    from chronologia.extract.loader import load_lang_spec
    _spec = load_lang_spec("en")
    def _folded(text):
        return " ".join(t.text for t in fold_en(pretokens(text, _spec)))
    # the ordinal LIST is cut at "and" -- BOTH ordinals survive, "first" is not
    # swallowed into a lone "3" the way it was before the bridge gate.
    assert _folded("first and third of June") == "1 and 3 of june"
    # every genuine magnitude-additive fold is byte-for-byte unchanged by the
    # gate (these are exactly the pre-fix outputs).
    assert _folded("one hundred and five") == "1 hundred and 5"
    assert _folded("two hundred and fifty") == "2 hundred and 50"
    assert _folded("a thousand and one") == "a thousand and 1"
    assert _folded("one hundred and first") == "1 hundred and 1"
    # spelled years still fold to their single value, untouched by the gate
    assert _folded("nineteen eighty four") == "84"
    assert _folded("twenty twenty") == "20"


# --- R17: a bare cardinal + plural unit is a count, not the ordinal day -------
def test_cardinal_plural_unit_is_not_the_ordinal_day_of_month():
    """"the two days of June" is a COUNT ("two days"), not "the 2nd day of June".

    The number fold collapses the spelled ordinal "second" and the cardinal
    "two" to one token, so unit plurality is the only surviving signal: a
    scoped-ordinal selection ("the Nth <unit> of ...") is grammatically
    singular, so a PLURAL unit in that frame can never be the ordinal
    day-of-month.  The mis-read had fabricated June 2.
    """
    def _day2(text):
        r = extract_timespan(text, "en", _A)
        return r is not None and r.span.start.month == 6 and r.span.start.day == 2

    # the bug: neither phrasing may resolve to June 2 any more
    assert not _day2("the two days of June")
    assert not _day2("two days of June")

    # every singular ordinal-selection reading MUST stay correct
    def _start(text):
        r = extract_timespan(text, "en", _A)
        assert r is not None, text
        return (r.span.start.year, r.span.start.month, r.span.start.day)

    assert _start("the second day of June") == (2017, 6, 2)
    assert _start("the 2nd day of June") == (2017, 6, 2)
    assert _start("the 100th day of the year") == (2017, 4, 10)
    assert _start("the last day of the month") == (2017, 6, 30)
    assert _start("the third week of June") == (2017, 6, 19)
    assert _start("the 21st century") == (2000, 1, 1)
    assert _start("the 3rd quarter of 2018") == (2018, 7, 1)
    assert _start("the first decade of the 21st century") == (2000, 1, 1)


# --- R23: non-Latin plurals veto the count reading too ------------------------
def test_cardinal_plural_unit_is_a_count_across_non_latin_plurals():
    """"N <plural-unit> of <month>" is a COUNT, not "the Nth day", in locales
    whose plural is not a bare ``-s`` -- Italian giorno/giorni, Dutch dag/dagen,
    Russian case-based день/дня.  The plural-unit veto derives from each
    locale's explicit ``unit1_`` singular vocab, so these read None while their
    genuine singular ordinal ("il secondo giorno", "второй день") still resolve.
    """
    def _day2(text, lang):
        r = extract_timespan(text, lang, _A)
        return r is not None and r.span.start.month == 6 and r.span.start.day == 2

    # the bug: the plural/count phrasing must NOT resolve to June 2
    assert not _day2("i due giorni di giugno", "it")
    assert not _day2("de twee dagen van juni", "nl")
    assert not _day2("два дня июня", "ru")

    # the genuine singular ordinal selection MUST stay correct
    def _start(text, lang):
        r = extract_timespan(text, lang, _A)
        assert r is not None, text
        return (r.span.start.year, r.span.start.month, r.span.start.day)

    assert _start("il secondo giorno di giugno", "it") == (2017, 6, 2)
    assert _start("de tweede dag van juni", "nl") == (2017, 6, 2)
    assert _start("второй день июня", "ru") == (2017, 6, 2)


def test_month_day_not_bare_hour_morning():
    """"June 15 in the morning" is the 15th's morning, not the anchor day.

    The "at? HOUR in? article? MERIDIEM" clock order bound the day-of-month
    number "15" as a bare HOUR and its 4-token span out-spanned the 2-token
    "June 15" calendar_date in the parse-winner contest, so the clock hijacked
    the day and the anchor's day (June 27) supplied the date -- 15:00 with
    "June" stranded.  A bare hour sitting immediately after a month surface is
    a date, so the clock reading is vetoed and the date wins.
    """
    r = extract_timespan("June 15 in the morning", "en", _A)
    assert r is not None
    assert (r.span.start.year, r.span.start.month, r.span.start.day) == (2018, 6, 15)
    assert r.span.start.hour == 6  # the morning band of the 15th, not 15:00

    # bare hours with NO preceding month stay clocks
    def _hour(text):
        r = extract_timespan(text, "en", _A)
        assert r is not None, text
        return r.span.start.hour

    assert _hour("3pm") == 15
    assert _hour("at 3pm") == 15
    assert _hour("10 in the morning") == 10

    # a real date + clock composition after a month still composes
    r = extract_timespan("June 15 at 3pm", "en", _A)
    assert (r.span.start.month, r.span.start.day, r.span.start.hour) == (6, 15, 15)

    # a bare date after a month stays a whole day
    r = extract_timespan("June 15", "en", _A)
    assert (r.span.start.month, r.span.start.day) == (6, 15)
    assert r.span.start.hour == 0


def test_week_of_does_not_collapse_to_clock():
    """"the week of June 15 at 3pm" keeps the week; the clock stays uncomposed.

    The week-of post-pass widens June 15 to its seven-day calendar week, but
    the composer then read only the widened span's start and placed a
    one-minute 3pm reading on the Monday -- silently discarding the week AND
    swallowing the clock tokens (empty remainder).  A week is a span, not a
    day: a pinpoint clock/daypart must not compose onto it, so the week stands
    and the time is stranded in the remainder.
    """
    def _week(text, lang):
        r = extract_timespan(text, lang, _A)
        assert r is not None, text
        return r

    r = _week("the week of June 15 at 3pm", "en")
    assert (r.span.start.year, r.span.start.month, r.span.start.day) == (2018, 6, 11)
    assert (r.span.end.year, r.span.end.month, r.span.end.day) == (2018, 6, 18)
    assert r.span.start.hour == 0 and r.span.end.hour == 0  # a 7-day span
    assert r.remainder.strip() != ""  # the clock did not silently vanish

    r = _week("the week of June 15 in the morning", "en")
    assert (r.span.start.month, r.span.start.day) == (6, 11)
    assert (r.span.end.month, r.span.end.day) == (6, 18)
    assert r.remainder.strip() != ""

    # cross-locale: same collapse existed in es
    r = _week("la semana del 15 de junio a las 3", "es")
    assert (r.span.start.month, r.span.start.day) == (6, 11)
    assert (r.span.end.month, r.span.end.day) == (6, 18)

    # the bare "week of X" still gives the 7-day span (unchanged)
    r = _week("the week of June 15", "en")
    assert (r.span.start.month, r.span.start.day) == (6, 11)
    assert (r.span.end.month, r.span.end.day) == (6, 18)

    # a normal date + clock composition is untouched
    r = extract_timespan("June 15 at 3pm", "en", _A)
    assert (r.span.start.month, r.span.start.day, r.span.start.hour) == (6, 15, 15)


# --- R23 F1: Spanish exclusion/negation parity ("no mañana" -> None) ----------
def test_spanish_exclusion_parity():
    """Spanish lacked exclusion vocabulary, so "no mañana" ("not tomorrow")
    handed back tomorrow's date instead of vetoing -- a scheduler could act on
    the exact day it was told to avoid.  Parity with en/de/fr/it/pt."""
    from chronologia import extract_timespan
    assert extract_timespan("no mañana", "es", _A) is None
    assert extract_timespan("no domingo", "es", _A) is None
    assert extract_timespan("excepto el lunes", "es", _A) is None
    # a plain positive date is unaffected
    assert extract_timespan("mañana", "es", _A)[0].start.day == 28


# --- R23 F2: leading past marker in the weekday-count ("hace 2 lunes") --------
def test_leading_past_marker_weekday_count():
    """Romance puts the past particle first ("hace 2 lunes" == 2 mondays ago);
    the trailing-only scan missed it and returned the NEXT monday instead."""
    from chronologia import extract_timespan
    assert extract_timespan("hace 2 lunes", "es", _A)[0].start.isoformat()[:10] == "2017-06-19"
    assert extract_timespan("il y a 2 lundis", "fr", _A)[0].start.isoformat()[:10] == "2017-06-19"
    # trailing-marker and future forms unchanged
    assert extract_timespan("2 mondays ago", "en", _A)[0].start.isoformat()[:10] == "2017-06-19"
    assert extract_timespan("3 fridays from now", "en", _A)[0].start.isoformat()[:10] == "2017-07-14"
    assert extract_timespan("3 viernes a partir de ahora", "es", _A)[0].start.isoformat()[:10] == "2017-07-14"


# --- R24: format_edtf renders a January month-precision span as one token -----
def test_edtf_january_month_precision_not_a_degenerate_interval():
    """A one-month January span must format to the single reduced-precision
    token "YYYY-01", not the degenerate interval "YYYY-01/YYYY-01" (the month=1
    guard used to fall through to the year/decade block and fail)."""
    from chronologia.edtf import parse_edtf, format_edtf
    for t in ("1760-01", "1950-01", "2020-01", "-0099-01", "0044-01"):
        assert format_edtf(parse_edtf(t)) == t, t
    # the other precisions are unchanged
    assert format_edtf(parse_edtf("1760-02")) == "1760-02"
    assert format_edtf(parse_edtf("1760")) == "1760"
    assert format_edtf(parse_edtf("176X")) == "176X"
    assert format_edtf(parse_edtf("17XX")) == "17XX"
    assert format_edtf(parse_edtf("1760-01-15")) == "1760-01-15"


# --- R25 E2: from_ical honours the TZID parameter -----------------------------
def test_from_ical_tzid_anchors_the_zone():
    """A DTSTART;TZID=America/New_York:... value must read back anchored to that
    IANA zone, not as a floating naive time (RFC 5545 3.2.19)."""
    from zoneinfo import ZoneInfo
    from chronologia import from_ical
    text = ("BEGIN:VCALENDAR\r\nBEGIN:VEVENT\r\nUID:x\r\n"
            "DTSTART;TZID=America/New_York:20170627T130400\r\n"
            "DTEND;TZID=America/New_York:20170627T140400\r\n"
            "END:VEVENT\r\nEND:VCALENDAR\r\n")
    ev = from_ical(text)
    assert ev.span.start.tzinfo == ZoneInfo("America/New_York")
    assert ev.span.start.utcoffset().total_seconds() == -4 * 3600  # EDT
    # UTC Z, all-day VALUE=DATE, and an unknown zone are unaffected/lenient
    utc = from_ical("BEGIN:VCALENDAR\r\nBEGIN:VEVENT\r\nUID:y\r\n"
                    "DTSTART:20170627T130400Z\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n")
    assert utc.span.start.utcoffset().total_seconds() == 0
    allday = from_ical("BEGIN:VCALENDAR\r\nBEGIN:VEVENT\r\nUID:z\r\n"
                       "DTSTART;VALUE=DATE:20170627\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n")
    assert allday.span.start.tzinfo is None

    # honest DST: an ambiguous fall-back wall time takes the LATER occurrence
    # (matching daypart anchoring), not zoneinfo's silent fold=0 earlier one.
    def _ny(dt):
        e = from_ical(f"BEGIN:VCALENDAR\r\nBEGIN:VEVENT\r\nUID:f\r\n"
                      f"DTSTART;TZID=America/New_York:{dt}\r\n"
                      f"END:VEVENT\r\nEND:VCALENDAR\r\n")
        return e.span.start
    fold = _ny("20171105T013000")            # 01:30 occurs twice on fall-back
    assert fold.utcoffset().total_seconds() == -5 * 3600   # EST, the later one
    # seconds survive the minute-precision DST resolution
    assert _ny("20170627T130437").second == 37


# --- R25 B2: a label shadowed by an INSERT returns NeverExisted, not a raise --
def test_timeline_insert_shadowed_label_is_never_existed():
    """Sweden's phantom "29 February 1712" is shadowed by the inserted double
    leap day (displayed as 30 February); it must return a typed NeverExisted,
    not raise OutOfTimeline (the module's no-raise-for-bad-labels contract)."""
    from chronologia.timelines import TIMELINES, NeverExisted
    r = TIMELINES["sweden_1700_1712"].to_jdn((1712, 2, 29))
    assert isinstance(r, NeverExisted)
    # the inserted day itself and ordinary days still resolve
    assert isinstance(TIMELINES["sweden_1700_1712"].to_jdn((1712, 2, 30)), int)
    assert isinstance(TIMELINES["sweden_1700_1712"].to_jdn((1712, 1, 1)), int)


# --- R27: an ordinal surface ("10th") must not bind as a YEAR -----------------
def test_ordinal_surface_does_not_bind_as_year():
    """"March 5th, 10th" used to read "10th" as GYEAR=10 (year 10 AD, empty
    remainder) because the "th" suffix made the 2-digit raw 4 chars long,
    passing the ">=4 digit year" check.  An ordinal surface is a day, never a
    year -- it must fall back to the date-list reading."""
    from chronologia import extract_timespan
    r = extract_timespan("March 5th, 10th", "en", _A)
    assert r is not None and r.span.start.year != 10
    assert r.span.start.month == 3 and r.span.start.day == 5   # like "5th and 10th"
    # real years, pivots, decades, and day+year are unaffected
    assert extract_timespan("March 5, 2020", "en", _A).span.start.year == 2020
    assert extract_timespan("March 5th 2020", "en", _A).span.start.year == 2020
    assert extract_timespan("March 5th, 99", "en", _A).span.start.year == 1999
    assert extract_timespan("15th of March 2020", "en", _A).span.start.year == 2020
    assert extract_timespan("the summer of 69", "en", _A).span.start.year == 1969


# --- R29 B: a year lent across a range must roll a wrapped endpoint's year ----
def test_range_year_lend_rolls_wrapped_endpoint():
    """"from december 2020 to march" lends 2020 to the bare "march", reading it
    in 2020 -- before december -- so the range reversed and the whole "to march"
    clause was silently dropped (bare "December 2020" with remainder "from to
    march").  When the lent year reverses the pair, the borrowed endpoint rolls
    into the adjacent year so the range reads forward.  Symmetric for a lent
    left endpoint; non-wrapping lends are unchanged."""
    from chronologia import extract_timespan
    r = extract_timespan("from december 2020 to march", "en-us", _A)
    assert (str(r.span.start.date()), str(r.span.end.date())) \
        == ("2020-12-01", "2021-04-01") and r.remainder == ""
    # mirror: the year on the RIGHT, bare month on the LEFT, rolls the left back
    l = extract_timespan("from december to march 2021", "en-us", _A)
    assert (str(l.span.start.date()), str(l.span.end.date())) \
        == ("2020-12-01", "2021-04-01")
    # non-wrapping lends stay in the single lent year
    assert str(extract_timespan("from january 2020 to march", "en-us", _A)
               .span.end.date()) == "2020-04-01"
    assert str(extract_timespan("from march 2020 to december", "en-us", _A)
               .span.end.date()) == "2021-01-01"
    # both endpoints already carry their own year -- untouched
    b = extract_timespan("from december 2019 to march 2020", "en-us", _A)
    assert (str(b.span.start.date()), str(b.span.end.date())) \
        == ("2019-12-01", "2020-04-01")


# --- R33: recursive impossible-date veto must not blow up exponentially -------
def test_impossible_date_veto_is_not_exponential():
    """The veto re-parses a stranded fragment through the public extract_timespan,
    which re-enters the veto; a self-similar input ("5th of june 5th of june ...")
    used to recurse 2**n times (a few hundred chars hung for hours). A re-entrancy
    guard bounds it to one linear pass."""
    import time
    from chronologia import extract_timespan
    text = "5th of june " * 40   # would be astronomically slow pre-fix
    t0 = time.perf_counter()
    extract_timespan(text, "en-us", _A)
    assert time.perf_counter() - t0 < 5.0


# --- R33: an out-of-range "Nth month/week of the year" must refuse, not wrap ---
def test_out_of_range_scoped_ordinal_of_year_is_none():
    """A year has 12 months / 52-53 weeks; "the 13th month of the year" is
    contradictory and must return None, not January of the next year."""
    from chronologia import extract_timespan
    for text in ("the 13th month of the year", "the 20th month of the year",
                 "the 53rd week of the year"):
        assert extract_timespan(text, "en-us", _A) is None, text
    # valid ordinals still resolve
    assert extract_timespan("the 12th month of the year", "en-us", _A) \
        .span.start.month == 12
    assert extract_timespan("the 3rd month of the year", "en-us", _A) \
        .span.start.month == 3
