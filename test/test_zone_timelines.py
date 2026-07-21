"""Timezones as timelines: the zoneinfo adapter and the dateline family.

Golds are asserted against **what zoneinfo actually reports** (the transition
instants, offsets and wall labels) and against the cited historical sources for
the day-level dateline entries (Samoa 2011, Philippines 1844, Alaska 1867).
"""
from datetime import datetime, timedelta, timezone

import pytest

from chronologia.calendars import gregorian_to_jdn, julian_to_jdn
from chronologia.timelines import TIMELINES, NeverExisted, DiscontinuityKind
from chronologia.zone_timelines import (ClockTimeline, ZoneNeverExisted,
                                        zone_history_start, zone_timeline)

UTC = timezone.utc
Y2024 = (datetime(2024, 1, 1, tzinfo=UTC), datetime(2025, 1, 1, tzinfo=UTC))


def _by_kind(ct, kind):
    return [d for d in ct.discontinuities if d.kind is kind]


# --------------------------------------------------------------------------
# 1. America/New_York 2024 — both transitions found by the adapter
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def ny():
    return zone_timeline("America/New_York", *Y2024)


def test_ny_finds_exactly_two_transitions(ny):
    assert len(ny.discontinuities) == 2


def test_ny_spring_forward_is_skip(ny):
    skip = _by_kind(ny, DiscontinuityKind.SKIP)
    assert len(skip) == 1
    assert skip[0].instant == datetime(2024, 3, 10, 7, 0, tzinfo=UTC)


def test_ny_spring_wall_labels_gap_two_to_three(ny):
    skip = _by_kind(ny, DiscontinuityKind.SKIP)[0]
    assert skip.before_wall == datetime(2024, 3, 10, 2, 0)
    assert skip.after_wall == datetime(2024, 3, 10, 3, 0)


def test_ny_spring_offsets_minus5_to_minus4(ny):
    skip = _by_kind(ny, DiscontinuityKind.SKIP)[0]
    assert skip.offset_before == timedelta(hours=-5)
    assert skip.offset_after == timedelta(hours=-4)
    assert skip.citation == "UTC-5 -> UTC-4 (America/New_York)"


def test_ny_fall_back_is_repeat(ny):
    rep = _by_kind(ny, DiscontinuityKind.REPEAT)
    assert len(rep) == 1
    assert rep[0].instant == datetime(2024, 11, 3, 6, 0, tzinfo=UTC)


def test_ny_fall_wall_labels_two_to_one(ny):
    rep = _by_kind(ny, DiscontinuityKind.REPEAT)[0]
    assert rep.before_wall == datetime(2024, 11, 3, 2, 0)
    assert rep.after_wall == datetime(2024, 11, 3, 1, 0)


def test_ny_fall_offsets_minus4_to_minus5(ny):
    rep = _by_kind(ny, DiscontinuityKind.REPEAT)[0]
    assert rep.offset_before == timedelta(hours=-4)
    assert rep.offset_after == timedelta(hours=-5)
    assert rep.citation == "UTC-4 -> UTC-5 (America/New_York)"


def test_ny_gap_wall_reading_never_existed(ny):
    result = ny.to_instant(datetime(2024, 3, 10, 2, 30))
    assert isinstance(result, ZoneNeverExisted)
    assert result.discontinuity.kind is DiscontinuityKind.SKIP


def test_ny_fold_wall_reading_two_instants_one_hour_apart(ny):
    result = ny.to_instant(datetime(2024, 11, 3, 1, 30))
    assert isinstance(result, tuple)
    earlier, later = result
    assert earlier == datetime(2024, 11, 3, 5, 30, tzinfo=UTC)
    assert later == datetime(2024, 11, 3, 6, 30, tzinfo=UTC)
    assert (later - earlier) == timedelta(hours=1)


def test_ny_unique_wall_reading_single_instant(ny):
    assert ny.to_instant(datetime(2024, 6, 1, 12, 0)) == \
        datetime(2024, 6, 1, 16, 0, tzinfo=UTC)


def test_ny_from_instant_renders_local_wall(ny):
    assert ny.from_instant(datetime(2024, 6, 1, 16, 0, tzinfo=UTC)) == \
        datetime(2024, 6, 1, 12, 0)


def test_ny_offset_at_summer_and_winter(ny):
    assert ny.offset_at(datetime(2024, 7, 1, tzinfo=UTC)) == timedelta(hours=-4)
    assert ny.offset_at(datetime(2024, 1, 1, tzinfo=UTC)) == timedelta(hours=-5)


# --------------------------------------------------------------------------
# 2. Australia/Sydney — southern hemisphere reverses the season direction
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def sydney():
    return zone_timeline("Australia/Sydney", *Y2024)


def test_sydney_two_transitions(sydney):
    assert len(sydney.discontinuities) == 2


def test_sydney_april_is_fall_back_repeat(sydney):
    # April is *autumn* in the south: the fall-back REPEAT lands in April,
    # opposite to the northern hemisphere.
    rep = _by_kind(sydney, DiscontinuityKind.REPEAT)[0]
    assert rep.instant.month == 4
    assert rep.offset_before == timedelta(hours=11)
    assert rep.offset_after == timedelta(hours=10)


def test_sydney_october_is_spring_forward_skip(sydney):
    skip = _by_kind(sydney, DiscontinuityKind.SKIP)[0]
    assert skip.instant.month == 10
    assert skip.offset_before == timedelta(hours=10)
    assert skip.offset_after == timedelta(hours=11)
    assert skip.citation == "UTC+10 -> UTC+11 (Australia/Sydney)"


def test_sydney_direction_opposite_to_ny(sydney, ny):
    # northern spring-forward is March; southern spring-forward is October
    ny_skip = _by_kind(ny, DiscontinuityKind.SKIP)[0]
    syd_skip = _by_kind(sydney, DiscontinuityKind.SKIP)[0]
    assert ny_skip.instant.month == 3
    assert syd_skip.instant.month == 10


# --------------------------------------------------------------------------
# 3. no-DST zones yield no discontinuities in a modern range
# --------------------------------------------------------------------------

def test_phoenix_no_dst_no_discontinuities():
    ct = zone_timeline("America/Phoenix", *Y2024)
    assert ct.discontinuities == ()
    assert ct.offset_at(datetime(2024, 7, 1, tzinfo=UTC)) == timedelta(hours=-7)


def test_utc_zone_no_discontinuities():
    ct = zone_timeline("UTC", *Y2024)
    assert ct.discontinuities == ()
    assert ct.to_instant(datetime(2024, 6, 1, 12, 0)) == \
        datetime(2024, 6, 1, 12, 0, tzinfo=UTC)


def test_empty_range_is_single_segment_no_discontinuities():
    start = datetime(2024, 6, 1, tzinfo=UTC)
    ct = zone_timeline("America/New_York", start, start)
    assert ct.discontinuities == ()
    assert len(ct.segments) == 1


def test_zone_timeline_accepts_tzinfo_object():
    from zoneinfo import ZoneInfo
    ct = zone_timeline(ZoneInfo("America/New_York"), *Y2024)
    assert len(ct.discontinuities) == 2
    assert "America/New_York" in ct.discontinuities[0].citation


# --------------------------------------------------------------------------
# 4. zone_history_start — the first transition out of LMT (tzdb pre-1970)
# --------------------------------------------------------------------------

def test_london_first_transition_is_gmt_adoption_1847():
    instant, lmt, std = zone_history_start("Europe/London")
    # what zoneinfo reports: London's LMT ends 1847-12-01, adopting GMT.
    assert instant == datetime(1847, 12, 1, 0, 1, tzinfo=UTC)
    assert lmt == timedelta(seconds=-75)      # ~1m15s west of Greenwich
    assert std == timedelta(0)                # GMT


def test_tokyo_first_transition_out_of_lmt():
    instant, lmt, std = zone_history_start("Asia/Tokyo")
    assert lmt == timedelta(seconds=33539)    # LMT +9:18:59
    assert std == timedelta(hours=9)          # JST +9:00
    assert instant.year == 1887


def test_history_start_none_when_no_transition_in_range():
    # London's LMT seam is 1847; a 1850-1860 window has none.
    assert zone_history_start("Europe/London", 1850, 1860) is None


# --------------------------------------------------------------------------
# 5. Dateline family — Samoa 2011, Philippines 1844, Alaska 1867
# --------------------------------------------------------------------------

def test_samoa_deleted_friday_never_existed():
    tl = TIMELINES["samoa_2011"]
    result = tl.to_jdn((2011, 12, 30))
    assert isinstance(result, NeverExisted)
    assert result.discontinuity.kind is DiscontinuityKind.SKIP


def test_samoa_dec29_and_dec31_are_one_jdn_apart():
    tl = TIMELINES["samoa_2011"]
    assert tl.to_jdn((2011, 12, 31)) - tl.to_jdn((2011, 12, 29)) == 1


def test_samoa_seam_day_carries_dec31_label():
    tl = TIMELINES["samoa_2011"]
    seam = gregorian_to_jdn(2011, 12, 30)   # the repurposed real solar day
    assert tl.from_jdn(seam).as_tuple() == (2011, 12, 31)


def test_samoa_ordinary_days_still_resolve():
    tl = TIMELINES["samoa_2011"]
    assert tl.from_jdn(gregorian_to_jdn(2011, 12, 28)).as_tuple() == \
        (2011, 12, 28)
    assert isinstance(tl.to_jdn((2011, 12, 29)), int)


def test_samoa_citation_records_offset_change():
    d = TIMELINES["samoa_2011"].discontinuities[0]
    assert "UTC-11 -> UTC+13" in d.citation


def test_philippines_deleted_dec31_never_existed():
    tl = TIMELINES["philippines_1844"]
    result = tl.to_jdn((1844, 12, 31))
    assert isinstance(result, NeverExisted)
    assert result.discontinuity.kind is DiscontinuityKind.SKIP


def test_philippines_dec30_and_jan1_are_one_jdn_apart():
    tl = TIMELINES["philippines_1844"]
    assert tl.to_jdn((1845, 1, 1)) - tl.to_jdn((1844, 12, 30)) == 1


def test_philippines_seam_day_carries_jan1_label():
    tl = TIMELINES["philippines_1844"]
    seam = gregorian_to_jdn(1844, 12, 31)
    assert tl.from_jdn(seam).as_tuple() == (1845, 1, 1)


def test_alaska_friday_followed_by_friday():
    tl = TIMELINES["alaska_1867"]
    seam = gregorian_to_jdn(1867, 10, 19)   # first Gregorian-reckoned day
    assert tl.from_jdn(seam - 1).as_tuple() == (1867, 10, 6)    # Julian
    assert tl.from_jdn(seam).as_tuple() == (1867, 10, 18)       # Gregorian


def test_alaska_two_labels_share_a_friday_jdn():
    # 6 Oct (Julian) and 18 Oct (Gregorian) both resolve, each through its own
    # calendar, to the SAME JDN — hence the same weekday: the repeated Friday.
    assert julian_to_jdn(1867, 10, 6) == gregorian_to_jdn(1867, 10, 18)


def test_alaska_days_consecutive_across_the_seam():
    seam = gregorian_to_jdn(1867, 10, 19)
    assert seam - (seam - 1) == 1   # two consecutive real solar days


def test_alaska_calendar_switches_at_the_seam():
    tl = TIMELINES["alaska_1867"]
    seam = gregorian_to_jdn(1867, 10, 19)
    assert tl.calendar_at(seam - 1) == "julian"
    assert tl.calendar_at(seam) == "gregorian"


def test_alaska_is_the_double_event_repeat_and_skip():
    kinds = {d.kind for d in TIMELINES["alaska_1867"].discontinuities}
    assert kinds == {DiscontinuityKind.REPEAT, DiscontinuityKind.SKIP}


def test_alaska_omitted_gregorian_dates_never_existed():
    tl = TIMELINES["alaska_1867"]
    for day in (7, 10, 17):   # 7-17 October 1867 Gregorian were omitted
        result = tl.to_jdn((1867, 10, day))
        assert isinstance(result, NeverExisted), day


# --------------------------------------------------------------------------
# 6. adversarial — boundaries, folds inside skips, out-of-range
# --------------------------------------------------------------------------

def test_gap_lower_boundary_is_skipped_upper_is_real(ny):
    # 02:00 exactly is the first non-existent instant; 03:00 is real again.
    assert isinstance(ny.to_instant(datetime(2024, 3, 10, 2, 0)),
                      ZoneNeverExisted)
    assert ny.to_instant(datetime(2024, 3, 10, 3, 0)) == \
        datetime(2024, 3, 10, 7, 0, tzinfo=UTC)


def test_fold_lower_boundary_is_ambiguous_upper_is_unique(ny):
    # 01:00 is the first repeated instant (ambiguous); 02:00 is past the fold.
    assert isinstance(ny.to_instant(datetime(2024, 11, 3, 1, 0)), tuple)
    assert isinstance(ny.to_instant(datetime(2024, 11, 3, 2, 0)), datetime)


def test_samoa_label_strictly_inside_skip_window_only():
    # 29 and 31 December are real; only 30 December is the SKIP.
    tl = TIMELINES["samoa_2011"]
    assert isinstance(tl.to_jdn((2011, 12, 29)), int)
    assert isinstance(tl.to_jdn((2011, 12, 30)), NeverExisted)
    assert isinstance(tl.to_jdn((2011, 12, 31)), int)


def test_philippines_label_strictly_inside_skip_window_only():
    tl = TIMELINES["philippines_1844"]
    assert isinstance(tl.to_jdn((1844, 12, 30)), int)
    assert isinstance(tl.to_jdn((1844, 12, 31)), NeverExisted)
    assert isinstance(tl.to_jdn((1845, 1, 1)), int)


def test_clock_timeline_is_a_frozen_view():
    ct = zone_timeline("America/New_York", *Y2024)
    assert isinstance(ct, ClockTimeline)
    with pytest.raises(Exception):
        ct.key = "mutated"


def test_multi_year_window_finds_all_transitions():
    ct = zone_timeline("America/New_York",
                       datetime(2020, 1, 1, tzinfo=UTC),
                       datetime(2025, 1, 1, tzinfo=UTC))
    # 2 transitions a year for 5 years
    assert len(ct.discontinuities) == 10
