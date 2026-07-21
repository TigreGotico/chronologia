"""Leap-second table and UTC/TAI/GPS conversions.

Gold instants and the table itself are cited from the IANA/IETF
``leap-seconds.list`` mirror of the IERS Bulletin C series (see
``chronologia/data/leap_seconds.tab``'s provenance header and
``~/AgentWorkspaces/papers/standards/INDEX.md``).
"""
import unittest
from datetime import date, datetime, timedelta, timezone

from chronologia.eras import ERAS
from chronologia.leapseconds import (GPS_EPOCH, LEAP_SECONDS,
                                     TABLE_VALID_UNTIL, TAI_MINUS_GPS,
                                     gps_to_utc, is_leap_second_day,
                                     table_valid_until, tai_to_utc,
                                     utc_tai_offset, utc_to_gps, utc_to_tai)


class TestTableProvenance(unittest.TestCase):
    def test_table_has_28_rows(self):
        # initial 1972 baseline + 27 leap seconds through 2016-12-31.
        self.assertEqual(28, len(LEAP_SECONDS))

    def test_table_starts_at_initial_offset(self):
        self.assertEqual((date(1972, 1, 1), 10), LEAP_SECONDS[0])

    def test_table_ends_at_1972_2017_span(self):
        self.assertEqual(date(1972, 1, 1), LEAP_SECONDS[0][0])
        self.assertEqual(date(2017, 1, 1), LEAP_SECONDS[-1][0])
        self.assertEqual(37, LEAP_SECONDS[-1][1])

    def test_table_sorted_ascending(self):
        dates = [d for d, _ in LEAP_SECONDS]
        self.assertEqual(sorted(dates), dates)

    def test_offsets_strictly_increasing(self):
        offsets = [o for _, o in LEAP_SECONDS]
        self.assertEqual(sorted(offsets), offsets)
        self.assertEqual(len(set(offsets)), len(offsets))

    def test_table_valid_until_parsed(self):
        self.assertEqual(date(2027, 6, 28), TABLE_VALID_UNTIL)
        self.assertEqual(TABLE_VALID_UNTIL, table_valid_until())


class TestUtcTaiOffsetGoldInstants(unittest.TestCase):
    def test_1972_01_01(self):
        self.assertEqual(10, utc_tai_offset(date(1972, 1, 1)))

    def test_1999_01_01(self):
        self.assertEqual(32, utc_tai_offset(date(1999, 1, 1)))

    def test_2009_01_01(self):
        self.assertEqual(34, utc_tai_offset(date(2009, 1, 1)))

    def test_2017_01_01(self):
        self.assertEqual(37, utc_tai_offset(date(2017, 1, 1)))

    def test_today(self):
        # no leap second announced since 2016-12-31; predicted-constant basis.
        self.assertEqual(37, utc_tai_offset(date(2026, 7, 21)))

    def test_accepts_datetime(self):
        self.assertEqual(37, utc_tai_offset(datetime(2020, 6, 15, 12, 30)))

    def test_accepts_aware_utc_datetime(self):
        aware = datetime(2020, 6, 15, 12, 30, tzinfo=timezone.utc)
        self.assertEqual(37, utc_tai_offset(aware))

    def test_aware_non_utc_converted_first(self):
        # 2016-12-31T23:00 in UTC+2 == 2016-12-31T21:00 UTC -> offset 36
        tz = timezone(timedelta(hours=2))
        aware = datetime(2016, 12, 31, 23, 0, tzinfo=tz)
        self.assertEqual(36, utc_tai_offset(aware))

    def test_accepts_astrodate(self):
        from chronologia.astrodate import AstroDate
        self.assertEqual(32, utc_tai_offset(AstroDate(1999, 1, 1)))

    def test_pre_1972_raises(self):
        with self.assertRaises(ValueError):
            utc_tai_offset(date(1971, 12, 31))

    def test_far_pre_1972_astrodate_raises(self):
        from chronologia.astrodate import AstroDate
        with self.assertRaises(ValueError):
            utc_tai_offset(AstroDate(44, 1, 1))


class TestLeapSecondDayBoundary(unittest.TestCase):
    def test_2016_12_31_is_a_leap_second_day(self):
        self.assertTrue(is_leap_second_day(date(2016, 12, 31)))

    def test_offset_before_and_after_the_boundary(self):
        self.assertEqual(36, utc_tai_offset(date(2016, 12, 31)))
        self.assertEqual(37, utc_tai_offset(date(2017, 1, 1)))

    def test_1972_01_01_baseline_is_not_a_leap_second_day(self):
        # the initial offset fixing, not an inserted leap second.
        self.assertFalse(is_leap_second_day(date(1972, 1, 1)))

    def test_ordinary_day_is_not_a_leap_second_day(self):
        self.assertFalse(is_leap_second_day(date(2020, 3, 15)))

    def test_every_table_row_after_first_has_a_leap_second_day(self):
        for effective_date, _ in LEAP_SECONDS[1:]:
            preceding = effective_date - timedelta(days=1)
            self.assertTrue(is_leap_second_day(preceding))


class TestUtcTaiRoundTrip(unittest.TestCase):
    def test_round_trip(self):
        original = datetime(2020, 6, 15, 12, 0, 0)
        self.assertEqual(original, tai_to_utc(utc_to_tai(original)))

    def test_offset_applied(self):
        original = datetime(2020, 6, 15, 12, 0, 0)
        tai = utc_to_tai(original)
        self.assertEqual(original + timedelta(seconds=37), tai)

    def test_round_trip_across_leap_second_boundary(self):
        original = datetime(2016, 12, 31, 23, 59, 59)
        self.assertEqual(original, tai_to_utc(utc_to_tai(original)))


class TestGpsConversions(unittest.TestCase):
    def test_gps_epoch_offset_is_zero(self):
        # UTC - GPS == 0 at the GPS epoch (offset then was 19 == TAI_MINUS_GPS).
        epoch = datetime(1980, 1, 6)
        self.assertEqual(epoch, utc_to_gps(epoch))
        self.assertEqual(19, utc_tai_offset(epoch))

    def test_today_gps_minus_utc_is_18(self):
        today = datetime(2026, 7, 21)
        gps = utc_to_gps(today)
        self.assertEqual(18, int((gps - today).total_seconds()))

    def test_gps_round_trip(self):
        original = datetime(2020, 6, 15, 12, 0, 0)
        self.assertEqual(original, gps_to_utc(utc_to_gps(original)))

    def test_gps_round_trip_across_leap_second_boundary(self):
        original = datetime(2016, 12, 31, 23, 59, 59)
        self.assertEqual(original, gps_to_utc(utc_to_gps(original)))

    def test_tai_minus_gps_constant(self):
        self.assertEqual(19, TAI_MINUS_GPS)

    def test_gps_epoch_constant(self):
        self.assertEqual(date(1980, 1, 6), GPS_EPOCH)


class TestUnixEraUntouched(unittest.TestCase):
    """POSIX/unix time ignores leap seconds; this module must not change it."""

    def test_unix_era_epoch_unaffected(self):
        from chronologia.astrodate import AstroDate
        unix_era = ERAS["unix"]
        self.assertEqual(AstroDate(1970, 1, 1), unix_era.epoch)

    def test_unix_timestamp_86400_seconds_per_day_regardless_of_leap_seconds(self):
        # a day spanning a real leap second still advances by exactly 86400
        # unix seconds -- POSIX time is leap-second-agnostic by construction,
        # unrelated to the TAI/GPS conversions in this module.
        before = datetime(2016, 12, 31, tzinfo=timezone.utc)
        after = datetime(2017, 1, 1, tzinfo=timezone.utc)
        self.assertEqual(86400, int((after - before).total_seconds()))
        self.assertEqual(86400, after.timestamp() - before.timestamp())


if __name__ == "__main__":
    unittest.main()
