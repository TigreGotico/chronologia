"""Tests for historical local time: LMT zones and apparent solar time.

Gold values trace to Honsberg & Bowden, "Solar Time" (PVCDROM /
PVEducation), mirror of the NOAA/Woolf equation of time, stated accurate
to within half a minute -- so equation-of-time assertions use that
tolerance.  LMT offsets are exact (longitude times 4 minutes per degree);
documented historical meridian offsets (Paris mean time +9m21s, Lisbon
-36m34s) are checked against that arithmetic.
"""
import unittest
from datetime import date, datetime, timedelta

from chronologia.astrodate import AstroDate
from chronologia.localtime import (EOT_ACCURACY, LMTZone, apparent_solar_time,
                                    equation_of_time, local_mean_time)

TOL = EOT_ACCURACY  # half a minute, the source's stated bound


class TestLocalMeanTime(unittest.TestCase):
    def test_greenwich_is_zero(self):
        z = local_mean_time(0)
        self.assertEqual(z.offset, timedelta(0))
        self.assertEqual(z.utcoffset(), timedelta(0))
        self.assertIsNone(z.dst())

    def test_four_minutes_per_degree(self):
        # 1 degree east == exactly 4 minutes ahead of UTC.
        self.assertEqual(local_mean_time(1).offset, timedelta(minutes=4))
        self.assertEqual(local_mean_time(-1).offset, timedelta(minutes=-4))
        self.assertEqual(local_mean_time(15).offset, timedelta(hours=1))

    def test_lisbon_documented_offset(self):
        # Lisbon ~ 9.14 W: -9.14 * 240 s = -2194 s = -36m34s.
        z = local_mean_time(-9.14)
        self.assertEqual(z.offset, timedelta(seconds=-2194))
        self.assertEqual(z.offset, timedelta(minutes=-36, seconds=-34))

    def test_paris_mean_time_documented(self):
        # Paris mean time = +9m21s (Paris observatory meridian 2 deg 20' E,
        # 2.3372 E * 240 s = 561 s = 9m21s), the civil time of France
        # before the 1911 adoption of GMT.
        z = local_mean_time(2.3372)
        self.assertEqual(z.offset, timedelta(minutes=9, seconds=21))

    def test_east_positive_west_negative(self):
        self.assertGreater(local_mean_time(30).offset, timedelta(0))
        self.assertLess(local_mean_time(-30).offset, timedelta(0))

    def test_antimeridian_edges(self):
        # +180 -> +12h ahead, -180 -> -12h behind, both exactly half a day.
        self.assertEqual(local_mean_time(180).offset, timedelta(hours=12))
        self.assertEqual(local_mean_time(-180).offset, timedelta(hours=-12))

    def test_seconds_precision(self):
        # A fractional longitude resolves to whole seconds.
        z = local_mean_time(9.140)
        self.assertEqual(z.offset, timedelta(seconds=2194))

    def test_tzname_format(self):
        self.assertEqual(local_mean_time(0).tzname(),
                         "LMT+00:00:00(lambda=0.000E)")
        self.assertEqual(local_mean_time(-9.14).tzname(),
                         "LMT-00:36:34(lambda=9.140W)")
        self.assertEqual(local_mean_time(2.3372).tzname(),
                         "LMT+00:09:21(lambda=2.337E)")

    def test_is_frozen_dataclass(self):
        z = local_mean_time(10)
        with self.assertRaises(Exception):
            z.offset = timedelta(0)  # type: ignore[misc]

    def test_from_utc_shifts_by_offset(self):
        z = local_mean_time(15)  # +1h
        got = z.from_utc(datetime(2000, 1, 1, 12, 0, 0))
        self.assertEqual(got, AstroDate(2000, 1, 1, 13, 0, 0))


class TestEquationOfTime(unittest.TestCase):
    def _assert_close(self, got: timedelta, expect_minutes: float):
        expect = timedelta(minutes=expect_minutes)
        self.assertLessEqual(abs(got - expect), TOL,
                             f"{got} not within {TOL} of {expect}")

    def test_early_november_max_positive(self):
        # Sundial fastest: about +16.4 min in early November.
        self._assert_close(equation_of_time(date(2023, 11, 3)), 16.4)

    def test_mid_february_max_negative(self):
        # Sundial slowest: about -14.2 min in mid-February.
        self._assert_close(equation_of_time(date(2023, 2, 11)), -14.2)

    def test_near_zero_crossings(self):
        # Near-zero around mid-April, mid-June, and early September.
        for d in (date(2023, 4, 15), date(2023, 6, 13), date(2023, 9, 1)):
            self.assertLessEqual(abs(equation_of_time(d)), TOL,
                                 f"EoT at {d} should be near zero")

    def test_sign_convention_apparent_minus_mean(self):
        # Positive EoT == sundial ahead of the clock (apparent - mean > 0).
        self.assertGreater(equation_of_time(date(2023, 11, 3)),
                           timedelta(0))
        self.assertLess(equation_of_time(date(2023, 2, 11)), timedelta(0))

    def test_leap_year_day_of_year(self):
        # Feb 29 exists only in leap years; it must resolve without error
        # and land between the Feb 28 and Mar 1 values (monotone stretch).
        feb28 = equation_of_time(date(2024, 2, 28))
        feb29 = equation_of_time(date(2024, 2, 29))
        mar1 = equation_of_time(date(2024, 3, 1))
        self.assertTrue(feb28 < feb29 < mar1 or feb28 > feb29 > mar1)

    def test_leap_vs_common_year_march_shift(self):
        # A given calendar date has a slightly different day-of-year after
        # Feb 29, so the leap-year value differs but stays within tolerance.
        common = equation_of_time(date(2023, 6, 13))
        leap = equation_of_time(date(2024, 6, 13))
        self.assertLessEqual(abs(common - leap), TOL)

    def test_accepts_astrodate_and_datetime(self):
        d = date(2023, 11, 3)
        self.assertEqual(equation_of_time(d),
                         equation_of_time(AstroDate(2023, 11, 3)))
        self.assertEqual(equation_of_time(d),
                         equation_of_time(datetime(2023, 11, 3, 6, 30)))

    def test_out_of_datetime_range_year(self):
        # Range-safe: a far-past year still computes (the earthquake era and
        # beyond), because day-of-year uses the proleptic ordinal.
        got = equation_of_time(AstroDate(-3760, 11, 3))
        self.assertLessEqual(abs(got - timedelta(minutes=16.4)), TOL)


class TestApparentSolarTime(unittest.TestCase):
    def test_apparent_is_lmt_plus_eot(self):
        inst = datetime(1755, 11, 1, 12, 0, 0)
        lon = -9.14
        lmt = local_mean_time(lon).from_utc(inst)
        got = apparent_solar_time(inst, lon)
        self.assertEqual(got, lmt + equation_of_time(lmt))

    def test_composition_greenwich(self):
        # At Greenwich the LMT offset is zero, so apparent == UTC + EoT.
        inst = datetime(2023, 11, 3, 12, 0, 0)
        got = apparent_solar_time(inst, 0)
        self.assertEqual(got, AstroDate.from_datetime(inst)
                         + equation_of_time(date(2023, 11, 3)))

    def test_lisbon_earthquake_day(self):
        # 1755-11-01, the Lisbon earthquake: solar noon reads earlier than
        # noon because Lisbon is west of Greenwich, then apparent time adds
        # the (positive, early-November) equation of time.
        inst = datetime(1755, 11, 1, 12, 0, 0)
        lmt = local_mean_time(-9.14).from_utc(inst)
        app = apparent_solar_time(inst, -9.14)
        self.assertLess(lmt, AstroDate(1755, 11, 1, 12))  # west of UTC
        self.assertGreater(app, lmt)                      # EoT positive here

    def test_returns_astrodate(self):
        got = apparent_solar_time(datetime(2000, 6, 13, 12), 0)
        self.assertIsInstance(got, AstroDate)


if __name__ == "__main__":
    unittest.main()
