"""Tests for the RFC 5545 recurrence engine.

The bulk of the gold suite is harvested verbatim from RFC 5545 section 3.8.5.3
(the "RRULE" examples, each with its enumerated expected dates) — only the
date-level examples, since sub-day recurrence is out of scope.  Civic golds
(Labor Day, Thanksgiving, the UK spring bank holiday, Friday the 13th) are
enumerated independently and cross-checked against ``datetime`` where the years
fall in range.  Adversarial cases cover malformed and contradictory rules.
"""
from datetime import date, timedelta

import pytest

from chronologia.astrodate import AstroDate, DateSpan
from chronologia.recurrence import (Recurrence, every, last_weekday_of_month,
                                     nth_weekday_of_month, occurrences,
                                     parse_rrule)


def ymd(rec, start, **kw):
    return [(s.start.year, s.start.month, s.start.day)
            for s in occurrences(rec, start, **kw)]


def ad(y, m, d):
    return AstroDate(y, m, d)


# --------------------------------------------------------------------------
# RFC 5545 section 3.8.5.3 gold corpus (date-level examples).
# --------------------------------------------------------------------------
def test_rfc_daily_count():
    r = parse_rrule("FREQ=DAILY;COUNT=10")
    assert ymd(r, ad(1997, 9, 2)) == [(1997, 9, d) for d in range(2, 12)]


def test_rfc_daily_until():
    r = parse_rrule("FREQ=DAILY;UNTIL=19971224T000000Z")
    got = ymd(r, AstroDate(1997, 9, 2, 9, 0, 0))
    assert got[0] == (1997, 9, 2)
    assert got[-1] == (1997, 12, 23)
    assert len(got) == 113


def test_rfc_every_other_day():
    r = parse_rrule("FREQ=DAILY;INTERVAL=2")
    got = ymd(r, ad(1997, 9, 2), count=12)
    assert got[:6] == [(1997, 9, 2), (1997, 9, 4), (1997, 9, 6),
                       (1997, 9, 8), (1997, 9, 10), (1997, 9, 12)]


def test_rfc_every_10_days_5_occ():
    r = parse_rrule("FREQ=DAILY;INTERVAL=10;COUNT=5")
    assert ymd(r, ad(1997, 9, 2)) == [(1997, 9, 2), (1997, 9, 12),
                                      (1997, 9, 22), (1997, 10, 2),
                                      (1997, 10, 12)]


def test_rfc_every_day_in_january_yearly_and_daily_agree():
    a = parse_rrule("FREQ=YEARLY;UNTIL=20000131T140000Z;"
                    "BYMONTH=1;BYDAY=SU,MO,TU,WE,TH,FR,SA")
    b = parse_rrule("FREQ=DAILY;UNTIL=20000131T140000Z;BYMONTH=1")
    ga, gb = ymd(a, ad(1998, 1, 1)), ymd(b, ad(1998, 1, 1))
    assert ga == gb
    assert len(ga) == 31 * 3
    assert ga[0] == (1998, 1, 1) and ga[-1] == (2000, 1, 31)


def test_rfc_weekly_count():
    r = parse_rrule("FREQ=WEEKLY;COUNT=10")
    assert ymd(r, ad(1997, 9, 2)) == [
        (1997, 9, 2), (1997, 9, 9), (1997, 9, 16), (1997, 9, 23),
        (1997, 9, 30), (1997, 10, 7), (1997, 10, 14), (1997, 10, 21),
        (1997, 10, 28), (1997, 11, 4)]


def test_rfc_every_other_week():
    r = parse_rrule("FREQ=WEEKLY;INTERVAL=2;WKST=SU")
    got = ymd(r, ad(1997, 9, 2), count=8)
    assert got[:5] == [(1997, 9, 2), (1997, 9, 16), (1997, 9, 30),
                       (1997, 10, 14), (1997, 10, 28)]


def test_rfc_weekly_tu_th_five_weeks():
    r = parse_rrule("FREQ=WEEKLY;UNTIL=19971007T000000Z;WKST=SU;BYDAY=TU,TH")
    assert ymd(r, AstroDate(1997, 9, 2, 9, 0, 0)) == [
        (1997, 9, 2), (1997, 9, 4), (1997, 9, 9), (1997, 9, 11),
        (1997, 9, 16), (1997, 9, 18), (1997, 9, 23), (1997, 9, 25),
        (1997, 9, 30), (1997, 10, 2)]


def test_rfc_every_other_week_mwf():
    r = parse_rrule("FREQ=WEEKLY;INTERVAL=2;UNTIL=19971224T000000Z;WKST=SU;"
                    "BYDAY=MO,WE,FR")
    got = ymd(r, AstroDate(1997, 9, 1, 9, 0, 0))
    assert got[:7] == [(1997, 9, 1), (1997, 9, 3), (1997, 9, 5),
                       (1997, 9, 15), (1997, 9, 17), (1997, 9, 19),
                       (1997, 9, 29)]
    assert got[-1] == (1997, 12, 22)


def test_rfc_every_other_week_tu_th_8():
    r = parse_rrule("FREQ=WEEKLY;INTERVAL=2;COUNT=8;WKST=SU;BYDAY=TU,TH")
    assert ymd(r, ad(1997, 9, 2)) == [
        (1997, 9, 2), (1997, 9, 4), (1997, 9, 16), (1997, 9, 18),
        (1997, 9, 30), (1997, 10, 2), (1997, 10, 14), (1997, 10, 16)]


def test_rfc_monthly_first_friday_10():
    r = parse_rrule("FREQ=MONTHLY;COUNT=10;BYDAY=1FR")
    assert ymd(r, ad(1997, 9, 5)) == [
        (1997, 9, 5), (1997, 10, 3), (1997, 11, 7), (1997, 12, 5),
        (1998, 1, 2), (1998, 2, 6), (1998, 3, 6), (1998, 4, 3),
        (1998, 5, 1), (1998, 6, 5)]


def test_rfc_monthly_first_and_last_sunday():
    r = parse_rrule("FREQ=MONTHLY;INTERVAL=2;COUNT=10;BYDAY=1SU,-1SU")
    assert ymd(r, ad(1997, 9, 7)) == [
        (1997, 9, 7), (1997, 9, 28), (1997, 11, 2), (1997, 11, 30),
        (1998, 1, 4), (1998, 1, 25), (1998, 3, 1), (1998, 3, 29),
        (1998, 5, 3), (1998, 5, 31)]


def test_rfc_monthly_second_to_last_monday():
    r = parse_rrule("FREQ=MONTHLY;COUNT=6;BYDAY=-2MO")
    assert ymd(r, ad(1997, 9, 22)) == [
        (1997, 9, 22), (1997, 10, 20), (1997, 11, 17), (1997, 12, 22),
        (1998, 1, 19), (1998, 2, 16)]


def test_rfc_monthly_third_to_last_day():
    r = parse_rrule("FREQ=MONTHLY;BYMONTHDAY=-3")
    assert ymd(r, ad(1997, 9, 28), count=6) == [
        (1997, 9, 28), (1997, 10, 29), (1997, 11, 28), (1997, 12, 29),
        (1998, 1, 29), (1998, 2, 26)]


def test_rfc_monthly_2nd_and_15th():
    r = parse_rrule("FREQ=MONTHLY;COUNT=10;BYMONTHDAY=2,15")
    assert ymd(r, ad(1997, 9, 2)) == [
        (1997, 9, 2), (1997, 9, 15), (1997, 10, 2), (1997, 10, 15),
        (1997, 11, 2), (1997, 11, 15), (1997, 12, 2), (1997, 12, 15),
        (1998, 1, 2), (1998, 1, 15)]


def test_rfc_monthly_first_and_last_day():
    r = parse_rrule("FREQ=MONTHLY;COUNT=10;BYMONTHDAY=1,-1")
    assert ymd(r, ad(1997, 9, 30)) == [
        (1997, 9, 30), (1997, 10, 1), (1997, 10, 31), (1997, 11, 1),
        (1997, 11, 30), (1997, 12, 1), (1997, 12, 31), (1998, 1, 1),
        (1998, 1, 31), (1998, 2, 1)]


def test_rfc_every_18_months_10th_to_15th():
    r = parse_rrule("FREQ=MONTHLY;INTERVAL=18;COUNT=10;"
                    "BYMONTHDAY=10,11,12,13,14,15")
    assert ymd(r, ad(1997, 9, 10)) == [
        (1997, 9, 10), (1997, 9, 11), (1997, 9, 12), (1997, 9, 13),
        (1997, 9, 14), (1997, 9, 15), (1999, 3, 10), (1999, 3, 11),
        (1999, 3, 12), (1999, 3, 13)]


def test_rfc_every_tuesday_every_other_month():
    r = parse_rrule("FREQ=MONTHLY;INTERVAL=2;BYDAY=TU")
    got = ymd(r, ad(1997, 9, 2), count=9)
    assert got == [(1997, 9, 2), (1997, 9, 9), (1997, 9, 16), (1997, 9, 23),
                   (1997, 9, 30), (1997, 11, 4), (1997, 11, 11),
                   (1997, 11, 18), (1997, 11, 25)]


def test_rfc_yearly_june_july():
    r = parse_rrule("FREQ=YEARLY;COUNT=10;BYMONTH=6,7")
    assert ymd(r, ad(1997, 6, 10)) == [
        (1997, 6, 10), (1997, 7, 10), (1998, 6, 10), (1998, 7, 10),
        (1999, 6, 10), (1999, 7, 10), (2000, 6, 10), (2000, 7, 10),
        (2001, 6, 10), (2001, 7, 10)]


def test_rfc_every_other_year_jan_feb_mar():
    r = parse_rrule("FREQ=YEARLY;INTERVAL=2;COUNT=10;BYMONTH=1,2,3")
    assert ymd(r, ad(1997, 3, 10)) == [
        (1997, 3, 10), (1999, 1, 10), (1999, 2, 10), (1999, 3, 10),
        (2001, 1, 10), (2001, 2, 10), (2001, 3, 10), (2003, 1, 10),
        (2003, 2, 10), (2003, 3, 10)]


def test_rfc_every_third_year_byyearday():
    r = parse_rrule("FREQ=YEARLY;INTERVAL=3;COUNT=10;BYYEARDAY=1,100,200")
    assert ymd(r, ad(1997, 1, 1)) == [
        (1997, 1, 1), (1997, 4, 10), (1997, 7, 19), (2000, 1, 1),
        (2000, 4, 9), (2000, 7, 18), (2003, 1, 1), (2003, 4, 10),
        (2003, 7, 19), (2006, 1, 1)]


def test_rfc_every_20th_monday_of_year():
    r = parse_rrule("FREQ=YEARLY;BYDAY=20MO")
    assert ymd(r, ad(1997, 5, 19), count=3) == [
        (1997, 5, 19), (1998, 5, 18), (1999, 5, 17)]


def test_rfc_monday_of_week_20():
    r = parse_rrule("FREQ=YEARLY;BYWEEKNO=20;BYDAY=MO")
    assert ymd(r, ad(1997, 5, 12), count=3) == [
        (1997, 5, 12), (1998, 5, 11), (1999, 5, 17)]


def test_rfc_every_thursday_in_march():
    r = parse_rrule("FREQ=YEARLY;BYMONTH=3;BYDAY=TH")
    got = ymd(r, ad(1997, 3, 13), count=11)
    assert got[:3] == [(1997, 3, 13), (1997, 3, 20), (1997, 3, 27)]
    assert got[3:7] == [(1998, 3, 5), (1998, 3, 12), (1998, 3, 19),
                        (1998, 3, 26)]


def test_rfc_every_thursday_jun_jul_aug():
    r = parse_rrule("FREQ=YEARLY;BYDAY=TH;BYMONTH=6,7,8")
    got = ymd(r, ad(1997, 6, 5), count=13)
    assert got[0] == (1997, 6, 5)
    assert (1997, 7, 3) in got and (1997, 8, 28) in got


def test_rfc_friday_the_13th():
    r = parse_rrule("FREQ=MONTHLY;BYDAY=FR;BYMONTHDAY=13")
    got = ymd(r, ad(1997, 9, 2), count=5)
    assert got == [(1998, 2, 13), (1998, 3, 13), (1998, 11, 13),
                   (1999, 8, 13), (2000, 10, 13)]


def test_rfc_first_saturday_following_first_sunday():
    r = parse_rrule("FREQ=MONTHLY;BYDAY=SA;BYMONTHDAY=7,8,9,10,11,12,13")
    got = ymd(r, ad(1997, 9, 13), count=8)
    assert got == [(1997, 9, 13), (1997, 10, 11), (1997, 11, 8),
                   (1997, 12, 13), (1998, 1, 10), (1998, 2, 7),
                   (1998, 3, 7), (1998, 4, 11)]


def test_rfc_us_presidential_election_day():
    r = parse_rrule("FREQ=YEARLY;INTERVAL=4;BYMONTH=11;BYDAY=TU;"
                    "BYMONTHDAY=2,3,4,5,6,7,8")
    assert ymd(r, ad(1996, 11, 5), count=3) == [
        (1996, 11, 5), (2000, 11, 7), (2004, 11, 2)]


def test_rfc_bysetpos_third_instance():
    r = parse_rrule("FREQ=MONTHLY;COUNT=3;BYDAY=TU,WE,TH;BYSETPOS=3")
    assert ymd(r, ad(1997, 9, 4)) == [
        (1997, 9, 4), (1997, 10, 7), (1997, 11, 6)]


def test_rfc_bysetpos_second_to_last_weekday():
    r = parse_rrule("FREQ=MONTHLY;BYDAY=MO,TU,WE,TH,FR;BYSETPOS=-2")
    assert ymd(r, ad(1997, 9, 29), count=6) == [
        (1997, 9, 29), (1997, 10, 30), (1997, 11, 27), (1997, 12, 30),
        (1998, 1, 29), (1998, 2, 26)]


def test_rfc_wkst_matters_mo():
    r = parse_rrule("FREQ=WEEKLY;INTERVAL=2;COUNT=4;BYDAY=TU,SU;WKST=MO")
    assert ymd(r, ad(1997, 8, 5)) == [
        (1997, 8, 5), (1997, 8, 10), (1997, 8, 19), (1997, 8, 24)]


def test_rfc_wkst_matters_su():
    r = parse_rrule("FREQ=WEEKLY;INTERVAL=2;COUNT=4;BYDAY=TU,SU;WKST=SU")
    assert ymd(r, ad(1997, 8, 5)) == [
        (1997, 8, 5), (1997, 8, 17), (1997, 8, 19), (1997, 8, 31)]


def test_rfc_invalid_date_feb30_ignored():
    r = parse_rrule("FREQ=MONTHLY;BYMONTHDAY=15,30;COUNT=5")
    assert ymd(r, ad(2007, 1, 15)) == [
        (2007, 1, 15), (2007, 1, 30), (2007, 2, 15), (2007, 3, 15),
        (2007, 3, 30)]


# --------------------------------------------------------------------------
# Civic-rule golds (independently enumerated, cross-checked vs datetime).
# --------------------------------------------------------------------------
def _weekday_ref(y, m, d):
    return date(y, m, d).weekday()


def test_us_labor_day():
    r = every("yearly", bymonth=9, byday="1MO")
    assert ymd(r, ad(2023, 1, 1), count=3) == [
        (2023, 9, 4), (2024, 9, 2), (2025, 9, 1)]
    for y, m, d in ymd(r, ad(2023, 1, 1), count=3):
        assert _weekday_ref(y, m, d) == 0 and d <= 7


def test_us_thanksgiving():
    r = nth_weekday_of_month(4, "TH", month=11)
    assert ymd(r, ad(2023, 1, 1), count=3) == [
        (2023, 11, 23), (2024, 11, 28), (2025, 11, 27)]
    for y, m, d in ymd(r, ad(2023, 1, 1), count=3):
        assert _weekday_ref(y, m, d) == 3 and 22 <= d <= 28


def test_uk_spring_bank_holiday():
    r = last_weekday_of_month("MO", month=5)
    assert ymd(r, ad(2023, 1, 1), count=3) == [
        (2023, 5, 29), (2024, 5, 27), (2025, 5, 26)]
    for y, m, d in ymd(r, ad(2023, 1, 1), count=3):
        assert _weekday_ref(y, m, d) == 0 and d >= 25


def test_australia_day_observed_fixed_date():
    # Australia Day is the fixed 26 January; a plain yearly rule reproduces it.
    r = every("yearly", bymonth=1, bymonthday=26)
    assert ymd(r, ad(2024, 1, 1), count=3) == [
        (2024, 1, 26), (2025, 1, 26), (2026, 1, 26)]


def test_friday_13th_2024_2026():
    r = parse_rrule("FREQ=MONTHLY;BYDAY=FR;BYMONTHDAY=13")
    got = ymd(r, ad(2024, 1, 1), until=ad(2026, 12, 31))
    assert got == [(2024, 9, 13), (2024, 12, 13), (2025, 6, 13),
                   (2026, 2, 13), (2026, 3, 13), (2026, 11, 13)]
    for y, m, d in got:
        assert _weekday_ref(y, m, d) == 4 and d == 13


def test_nth_weekday_cross_check_vs_datetime():
    # Differential: our "first Monday of every month" vs a datetime scan.
    r = nth_weekday_of_month(1, "MO")
    ours = ymd(r, ad(2020, 1, 1), until=ad(2021, 12, 31))
    ref = []
    for month_start_ord in range(date(2020, 1, 1).toordinal(),
                                 date(2022, 1, 1).toordinal()):
        dd = date.fromordinal(month_start_ord)
        if dd.weekday() == 0 and dd.day <= 7:
            ref.append((dd.year, dd.month, dd.day))
    assert ours == ref


# --------------------------------------------------------------------------
# Edge cases.
# --------------------------------------------------------------------------
def test_jan31_monthly_skips_short_months():
    r = parse_rrule("FREQ=MONTHLY;COUNT=4")
    assert ymd(r, ad(2023, 1, 31)) == [
        (2023, 1, 31), (2023, 3, 31), (2023, 5, 31), (2023, 7, 31)]


def test_leap_day_yearly_only_in_leap_years():
    r = parse_rrule("FREQ=YEARLY;COUNT=3")
    assert ymd(r, ad(2024, 2, 29)) == [
        (2024, 2, 29), (2028, 2, 29), (2032, 2, 29)]


def test_bysetpos_last_workday_of_month():
    r = parse_rrule("FREQ=MONTHLY;BYDAY=MO,TU,WE,TH,FR;BYSETPOS=-1")
    got = ymd(r, ad(2023, 1, 1), count=3)
    # Jan 2023 ends Tue 31; Feb ends Tue 28; Mar 31 is Friday.
    assert got == [(2023, 1, 31), (2023, 2, 28), (2023, 3, 31)]


def test_count_and_until_call_overrides_narrow():
    r = parse_rrule("FREQ=DAILY;COUNT=100")
    # A call-level until can cut a COUNT rule short.
    got = ymd(r, ad(2023, 1, 1), until=ad(2023, 1, 5))
    assert got == [(2023, 1, d) for d in range(1, 6)]


def test_dtstart_not_matching_is_excluded_strict_rfc():
    # DTSTART is a Wednesday; a Monday rule must NOT emit it (unlike dateutil).
    r = parse_rrule("FREQ=WEEKLY;BYDAY=MO;COUNT=2")
    got = ymd(r, ad(2023, 6, 7))  # 2023-06-07 is a Wednesday
    assert got == [(2023, 6, 12), (2023, 6, 19)]
    assert all(_weekday_ref(*t) == 0 for t in got)


def test_dtstart_matching_is_included():
    r = parse_rrule("FREQ=WEEKLY;BYDAY=MO;COUNT=2")
    got = ymd(r, ad(2023, 6, 12))  # a Monday
    assert got == [(2023, 6, 12), (2023, 6, 19)]


def test_wkst_effect_on_weekly_interval():
    a = parse_rrule("FREQ=WEEKLY;INTERVAL=2;COUNT=4;BYDAY=TU,SU;WKST=MO")
    b = parse_rrule("FREQ=WEEKLY;INTERVAL=2;COUNT=4;BYDAY=TU,SU;WKST=SU")
    assert ymd(a, ad(1997, 8, 5)) != ymd(b, ad(1997, 8, 5))


def test_negative_byweekno_last_week():
    r = parse_rrule("FREQ=YEARLY;BYWEEKNO=-1;BYDAY=MO")
    got = ymd(r, ad(2023, 1, 1), count=2)
    # Monday of the last ISO week of each year.
    for y, m, d in got:
        assert _weekday_ref(y, m, d) == 0


def test_until_is_inclusive():
    r = parse_rrule("FREQ=DAILY")
    got = ymd(r, ad(2023, 1, 1), until=ad(2023, 1, 3))
    assert got == [(2023, 1, 1), (2023, 1, 2), (2023, 1, 3)]


def test_occurrences_yield_day_wide_spans():
    r = parse_rrule("FREQ=DAILY;COUNT=1")
    span = next(iter(occurrences(r, ad(2023, 3, 1))))
    assert isinstance(span, DateSpan)
    assert span.start == ad(2023, 3, 1)
    assert span.end == ad(2023, 3, 2)
    assert span.width == timedelta(days=1)


# --------------------------------------------------------------------------
# Deep-time / unbounded-year differentiator.
# --------------------------------------------------------------------------
def test_yearly_rule_from_deep_past():
    r = every("yearly", bymonth=9, byday="1MO")
    got = ymd(r, ad(-500, 1, 1), count=3)
    assert got[0][0] == -500 and got[0][1] == 9
    # every occurrence is the first Monday of September (day <= 7).
    for y, m, d in got:
        assert m == 9 and d <= 7


def test_daily_across_year_zero():
    r = parse_rrule("FREQ=YEARLY;COUNT=3")
    assert ymd(r, ad(-1, 3, 15)) == [(-1, 3, 15), (0, 3, 15), (1, 3, 15)]


def test_far_future_yearly_no_overflow():
    r = every("yearly", bymonth=7, bymonthday=4)
    got = ymd(r, ad(50000, 1, 1), count=2)
    assert got == [(50000, 7, 4), (50001, 7, 4)]


# --------------------------------------------------------------------------
# Friendly constructors & round-trip.
# --------------------------------------------------------------------------
def test_every_builds_and_round_trips():
    r = every("yearly", bymonth=9, byday="1MO")
    assert r.to_string() == "FREQ=YEARLY;BYMONTH=9;BYDAY=1MO"
    assert parse_rrule(r.to_string()) == r


def test_to_string_round_trip_complex():
    s = "FREQ=MONTHLY;INTERVAL=2;COUNT=5;BYMONTHDAY=1,-1;BYSETPOS=-1;WKST=SU"
    assert parse_rrule(s).to_string() == s


def test_rrule_prefix_accepted():
    r = parse_rrule("RRULE:FREQ=DAILY;COUNT=2")
    assert r.freq == "DAILY" and r.count == 2


def test_recurrence_is_frozen_and_hashable():
    r = parse_rrule("FREQ=DAILY;COUNT=2")
    assert hash(r) == hash(parse_rrule("FREQ=DAILY;COUNT=2"))
    with pytest.raises(Exception):
        r.freq = "WEEKLY"


def test_nth_weekday_of_month_monthly_variant():
    r = nth_weekday_of_month(2, "TU")
    assert r.freq == "MONTHLY"
    assert r.byday == ((2, 1),)


# --------------------------------------------------------------------------
# Adversarial: malformed / contradictory / out-of-scope rules.
# --------------------------------------------------------------------------
@pytest.mark.parametrize("bad", [
    "",
    "RRULE:",
    "INTERVAL=2",                       # no FREQ
    "FREQ=WEEKLY;FREQ=DAILY",           # duplicate
    "FREQ=DAILY;COUNT=5;UNTIL=20200101",  # COUNT and UNTIL together
    "FREQ=HOURLY;COUNT=3",              # sub-day frequency
    "FREQ=SECONDLY",                    # sub-day frequency
    "FREQ=DAILY;BYSECOND=0",            # sub-second BY part (out of scope)
    "FREQ=DAILY;BYHOUR=24",             # hour out of range
    "FREQ=DAILY;BYMINUTE=30",           # BYMINUTE without BYHOUR
    "FREQ=BOGUS",                       # unknown freq
    "FREQ=WEEKLY;BYDAY=1MO",            # ordinal BYDAY with WEEKLY
    "FREQ=DAILY;BYDAY=1MO",             # ordinal BYDAY with DAILY
    "FREQ=WEEKLY;BYMONTHDAY=1",         # BYMONTHDAY N/A for WEEKLY
    "FREQ=DAILY;BYYEARDAY=1",           # BYYEARDAY N/A for DAILY
    "FREQ=MONTHLY;BYWEEKNO=2",          # BYWEEKNO only YEARLY
    "FREQ=YEARLY;BYSETPOS=1",           # BYSETPOS without other BY part
    "FREQ=DAILY;INTERVAL=0",            # interval must be >= 1
    "FREQ=YEARLY;BYMONTH=13",           # month out of range
    "FREQ=MONTHLY;BYMONTHDAY=0",        # zero monthday
    "FREQ=WEEKLY;BYDAY=XX",             # bad weekday code
    "FREQ=DAILY;NOPE=1",                # unknown part
    "FREQ=DAILY;GARBAGE",               # no '='
])
def test_parse_rejects_malformed(bad):
    with pytest.raises(ValueError):
        parse_rrule(bad)


def test_parse_rejects_non_string():
    with pytest.raises(TypeError):
        parse_rrule(123)


def test_unbounded_rule_without_limit_raises():
    r = parse_rrule("FREQ=DAILY")
    with pytest.raises(ValueError, match="unbounded"):
        list(occurrences(r, ad(2023, 1, 1)))


def test_bounded_rule_iterates_without_call_limit():
    r = parse_rrule("FREQ=DAILY;COUNT=3")
    assert len(ymd(r, ad(2023, 1, 1))) == 3


def test_impossible_rule_with_count_raises():
    # Feb never has a 30th: the statically-impossible month/day pair is now
    # rejected up front at construction (was only caught after scanning tens of
    # thousands of empty periods).
    with pytest.raises(ValueError, match="never"):
        parse_rrule("FREQ=YEARLY;BYMONTH=2;BYMONTHDAY=30;COUNT=1")


def test_abusive_count_is_refused_at_construction():
    # An untrusted RRULE (e.g. from from_ical) with a huge COUNT would enumerate
    # for hours; it must be rejected when the Recurrence is built, before any
    # expansion, so no abusive rule can exist to be enumerated later.
    import time
    t0 = time.monotonic()
    with pytest.raises(ValueError, match="ceiling"):
        parse_rrule("FREQ=DAILY;COUNT=1000000000")
    assert time.monotonic() - t0 < 1.0
    # the ceiling itself is a legal value; one above it is not
    assert parse_rrule("FREQ=DAILY;COUNT=100000").count == 100000
    with pytest.raises(ValueError, match="ceiling"):
        parse_rrule("FREQ=DAILY;COUNT=100001")


def test_far_until_with_no_count_trips_emission_cap_not_count_check():
    # A count-field pre-check alone would wave this through: no COUNT is
    # declared at all.  It is the far UNTIL that makes materialisation
    # expensive, and only a during-generation counter catches it.
    from chronologia.recurrence import _MAX_EMITTED_OCCURRENCES
    r = parse_rrule("FREQ=DAILY;UNTIL=99991231T000000Z")
    assert r.count is None
    with pytest.raises(ValueError, match="ceiling"):
        list(occurrences(r, ad(2023, 1, 1)))


def test_unbounded_rule_succeeds_when_windowed():
    # The same "forever" rule that test_unbounded_rule_without_limit_raises
    # refuses to fully materialise succeeds once the caller supplies an
    # explicit window.
    r = parse_rrule("FREQ=DAILY")
    got = ymd(r, ad(2023, 1, 1), until=ad(2023, 1, 10))
    assert got == [(2023, 1, d) for d in range(1, 11)]


def test_call_level_count_at_emission_cap_succeeds_one_over_raises():
    # A caller-supplied count= is not validated at construction (only the
    # rule's own declared COUNT is), so the during-generation counter is the
    # only thing standing between this and an abusive materialisation.
    from chronologia.recurrence import _MAX_EMITTED_OCCURRENCES
    r = parse_rrule("FREQ=DAILY")
    got = ymd(r, ad(2023, 1, 1), count=_MAX_EMITTED_OCCURRENCES)
    assert len(got) == _MAX_EMITTED_OCCURRENCES
    with pytest.raises(ValueError, match="ceiling"):
        list(occurrences(r, ad(2023, 1, 1),
                         count=_MAX_EMITTED_OCCURRENCES + 1))


def test_occurrences_accepts_plain_date():
    r = parse_rrule("FREQ=DAILY;COUNT=2")
    got = [(s.start.year, s.start.month, s.start.day)
           for s in occurrences(r, date(2023, 5, 1))]
    assert got == [(2023, 5, 1), (2023, 5, 2)]


def test_generalized_weekno_matches_iso_calendar_for_monday_wkst():
    # BYWEEKNO with the default MO week-start must agree with AstroDate's own
    # ISO calendar across a range (reusing the iso_week hub).
    from chronologia.recurrence import _week_of
    for ord_ in range(date(2015, 1, 1).toordinal(),
                       date(2025, 1, 1).toordinal(), 7):
        dd = date.fromordinal(ord_)
        a = AstroDate(dd.year, dd.month, dd.day)
        jdn = a.toordinal() + 1721425  # RD -> JDN
        iso_y, iso_w, _ = a.isocalendar()
        wy, wn, _ = _week_of(jdn, 0)
        assert (wy, wn) == (iso_y, iso_w)


# --------------------------------------------------------------------------
# Clock pin (BYHOUR / BYMINUTE) and movable-feast HolidayRecurrence.
# --------------------------------------------------------------------------
from chronologia.recurrence import HolidayRecurrence   # noqa: E402


def test_byhour_expands_to_clocked_hour_span():
    rule = parse_rrule("FREQ=DAILY;BYHOUR=9")
    spans = list(occurrences(rule, AstroDate(2026, 1, 1), count=2))
    assert [(s.start.hour, s.start.minute) for s in spans] == [(9, 0), (9, 0)]
    # no BYMINUTE -> a one-hour span
    assert spans[0].end - spans[0].start == timedelta(hours=1)


def test_byhour_byminute_expands_to_minute_span():
    rule = every("weekly", byday="WE", byhour=9, byminute=30)
    assert rule.to_string() == "FREQ=WEEKLY;BYDAY=WE;BYHOUR=9;BYMINUTE=30"
    span = next(iter(occurrences(rule, AstroDate(2026, 1, 1), count=1)))
    assert (span.start.hour, span.start.minute) == (9, 30)
    assert span.end - span.start == timedelta(minutes=1)


def test_byhour_rrule_roundtrips():
    assert parse_rrule("FREQ=DAILY;BYHOUR=9;BYMINUTE=30").to_string() == (
        "FREQ=DAILY;BYHOUR=9;BYMINUTE=30")


def test_holiday_recurrence_expands_but_never_serializes():
    hr = HolidayRecurrence("easter")
    dates = [s.start for s in hr.occurrences(AstroDate(2026, 1, 1), count=2)]
    assert [d.year for d in dates] == [2026, 2027]
    assert dates[0].month == 4 and dates[0].day == 5   # Western Easter 2026
    with pytest.raises(ValueError):
        hr.to_string()


def test_holiday_recurrence_unbounded_raises():
    with pytest.raises(ValueError):
        list(HolidayRecurrence("easter").occurrences(AstroDate(2026, 1, 1)))


def test_holiday_recurrence_rejects_unknown_key():
    with pytest.raises(ValueError):
        HolidayRecurrence("not_a_real_holiday")


from chronologia.recurrence import JurisdictionHolidays   # noqa: E402


def test_jurisdiction_holidays_expands_but_never_serializes():
    jh = JurisdictionHolidays("PT")
    dates = [s.start for s in jh.occurrences(AstroDate(2026, 1, 1), count=14)]
    # 2026 Portuguese public holidays, chronologically, computed independently
    # of the parser: New Year, Carnival (moveable, not always public but
    # tabulated here), Good Friday (computus: Easter 2026 = 5 Apr -> Good
    # Friday = 3 Apr), Easter Sunday, Freedom Day, Labour Day, Corpus Christi
    # (Easter + 60 = 4 Jun), Portugal Day, Assumption, Republic Day, All
    # Saints, Restoration of Independence, Immaculate Conception, Christmas.
    assert (dates[0].year, dates[0].month, dates[0].day) == (2026, 1, 1)
    assert (2026, 4, 3) in [(d.year, d.month, d.day) for d in dates]   # Good Friday
    assert (2026, 4, 5) in [(d.year, d.month, d.day) for d in dates]   # Easter
    assert (2026, 12, 25) in [(d.year, d.month, d.day) for d in dates]  # Christmas
    # chronological order, never re-sorted across the boundary
    assert dates == sorted(dates)
    with pytest.raises(ValueError):
        jh.to_string()
    with pytest.raises(ValueError):
        str(jh)


def test_jurisdiction_holidays_spills_into_next_year():
    jh = JurisdictionHolidays("PT")
    dates = [s.start for s in jh.occurrences(AstroDate(2026, 1, 1), count=15)]
    assert dates[-1].year == 2027
    assert (dates[-1].year, dates[-1].month, dates[-1].day) == (2027, 1, 1)


def test_jurisdiction_holidays_unbounded_raises():
    with pytest.raises(ValueError):
        list(JurisdictionHolidays("PT").occurrences(AstroDate(2026, 1, 1)))


def test_jurisdiction_holidays_rejects_unknown_jurisdiction():
    with pytest.raises(ValueError):
        JurisdictionHolidays("ATLANTIS")


def test_jurisdiction_holidays_default_category_is_public():
    assert JurisdictionHolidays("PT").categories == ("public",)


def test_jurisdiction_holidays_categories_override():
    jh = JurisdictionHolidays("PT", categories=("public", "bank"))
    assert jh.categories == ("public", "bank")


def test_count_zero_yields_no_occurrences():
    """COUNT=0 is a legal value (distinct from unbounded) and means 'repeat zero
    times' -- it must yield an empty iterator, not the one occurrence a naive
    post-yield cutoff leaks."""
    from chronologia.recurrence import occurrences, every
    assert list(occurrences(every("daily", count=0), AstroDate(2024, 1, 1))) == []
    # sanity: COUNT=1 still yields exactly one
    assert len(list(occurrences(every("daily", count=1), AstroDate(2024, 1, 1)))) == 1


def test_extract_recurrence_every_zero_interval_returns_none_not_crash():
    """"every 0 <unit>" names no valid recurrence (an interval must be >= 1).
    It must return None, never let the 0 reach Recurrence's validator and raise
    -- extract_recurrence never raises on user text."""
    from chronologia import extract_recurrence
    from datetime import datetime
    A = datetime(2017, 6, 27, 13, 4)
    for text in ("every 0 days", "every 0 weeks", "every 0 months",
                 "every 0 years", "every 0 friday"):
        assert extract_recurrence(text, anchor=A) is None
    # a valid interval still parses
    r = extract_recurrence("every 2 weeks", anchor=A)
    assert r is not None and r.recurrence.interval == 2


def test_sparse_yearly_expansion_is_narrowed_not_brute_forced():
    """A sparse YEARLY rule ("every 29th of february") must expand by its own
    BY parts, not by scanning all 365 days per year -- otherwise a large COUNT
    within the sanity ceiling costs ~O(365 * count) wall time.  Correctness is
    the guard here (identical results); the narrowing is what makes it cheap."""
    from chronologia.recurrence import occurrences, every
    # leap day: only leap Februaries, non-leap years skipped (not fabricated)
    leaps = [o.start for o in occurrences(every("yearly", bymonth=2,
                                                bymonthday=29),
                                          AstroDate(2020, 1, 1), count=4)]
    assert [(d.year, d.month, d.day) for d in leaps] == [
        (2020, 2, 29), (2024, 2, 29), (2028, 2, 29), (2032, 2, 29)]
    # a large count that used to cost ~seconds now completes promptly and
    # returns exactly that many correct occurrences (functional bound on cost)
    got = list(occurrences(every("yearly", bymonth=2, bymonthday=29),
                           AstroDate(2020, 1, 1), count=1000))
    assert len(got) == 1000
    assert all(o.start.month == 2 and o.start.day == 29 for o in got)


@pytest.mark.parametrize("rec_kwargs,dtstart,first", [
    ({"freq": "yearly"}, (2020, 3, 4), (2020, 3, 4)),          # bare yearly
    ({"freq": "monthly"}, (2020, 1, 15), (2020, 1, 15)),        # bare monthly
    ({"freq": "yearly", "bymonthday": 29}, (2020, 1, 1), (2020, 1, 29)),
    ({"freq": "yearly", "bymonth": (3, 6, 9, 12), "bymonthday": 15},
     (2020, 1, 1), (2020, 3, 15)),
    ({"freq": "monthly", "bymonthday": -1}, (2020, 1, 1), (2020, 1, 31)),
])
def test_narrowed_yearly_monthly_first_occurrence(rec_kwargs, dtstart, first):
    # the DTSTART-default and bymonth/bymonthday narrowing must not shift the
    # first occurrence off its correct day.
    from chronologia.recurrence import occurrences, every
    o = next(iter(occurrences(every(**rec_kwargs), AstroDate(*dtstart), count=1)))
    assert (o.start.year, o.start.month, o.start.day) == first


def test_every_coerces_date_and_datetime_until():
    # every()'s until= must accept a plain date/datetime (a pythonic-constructor
    # convenience) and coerce to AstroDate, like parse_rrule/occurrences do.
    # Regression: a plain date reached to_string()/occurrences() and crashed on
    # the missing .hour.
    import datetime as _dt
    from chronologia.recurrence import every
    from chronologia.astrodate import AstroDate
    r = every("daily", until=_dt.date(2024, 1, 5))
    assert isinstance(r.until, AstroDate)
    assert r.to_string() == "FREQ=DAILY;UNTIL=20240105T000000"
    r2 = every("daily", until=_dt.datetime(2024, 1, 5, 9, 0))
    assert isinstance(r2.until, AstroDate)
    assert r2.to_string() == "FREQ=DAILY;UNTIL=20240105T090000"
