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
