"""AstroDate is protocol-compatible with datetime.

Subclassing ``datetime`` is impossible (its C-level year bounds are exactly
what AstroDate escapes), so compatibility is enforced here: a test that walks
``datetime``'s public API and asserts AstroDate answers every width-relevant
member, plus exact-value tests for the arithmetic and formatting that has to
stay correct across year 0 and far outside the ``datetime`` range.
"""
import unittest
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from chronologia.astrodate import AstroDate, resolve_wall_clock, civil_add
from chronologia.timelines import NeverExisted, DiscontinuityKind


# datetime members AstroDate deliberately does NOT provide, with the reason:
#   * factory / "now" constructors -- there is no civil clock outside range
#   * class constants and stdlib/locale helpers that assume the datetime range
# The tz-aware members that AstroDate DOES honour are now in _COVERED.
_EXCLUDED = {
    # tz-aware members AstroDate cannot honour width-safely
    "timetz", "utctimetuple", "fold",
    # factory / clock constructors
    "now", "today", "utcnow", "fromtimestamp", "utcfromtimestamp",
    "combine", "strptime", "fromisocalendar",
    # class constants
    "min", "max", "resolution",
    # locale / stdlib helpers tied to the in-range calendar
    "ctime", "timetuple", "timestamp",
}

# The width-relevant public API AstroDate must implement.
_COVERED = {
    "year", "month", "day", "hour", "minute", "second", "microsecond",
    "date", "time", "weekday", "isoweekday", "isocalendar", "toordinal",
    "fromordinal", "isoformat", "fromisoformat", "strftime", "replace",
    # aware members (Z1): optional-aware, delegating to tzinfo
    "tzinfo", "utcoffset", "tzname", "dst", "astimezone",
}

_KEY_DUNDERS = {
    "__eq__", "__ne__", "__lt__", "__le__", "__gt__", "__ge__", "__hash__",
    "__add__", "__sub__", "__radd__", "__rsub__", "__str__",
}


class TestDatetimeProtocolCoverage(unittest.TestCase):
    def test_every_public_datetime_member_is_covered_or_excluded(self):
        public = {n for n in dir(datetime) if not n.startswith("_")}
        for name in public:
            with self.subTest(member=name):
                self.assertTrue(
                    name in _COVERED or name in _EXCLUDED,
                    f"datetime.{name} is neither implemented nor explicitly "
                    f"excluded -- decide and update the protocol test")

    def test_covered_members_exist_on_astrodate(self):
        for name in _COVERED:
            with self.subTest(member=name):
                self.assertTrue(hasattr(AstroDate, name),
                                f"AstroDate is missing datetime.{name}")

    def test_key_dunders_are_defined(self):
        for name in _KEY_DUNDERS:
            with self.subTest(dunder=name):
                self.assertTrue(hasattr(AstroDate, name))


class TestExactValues(unittest.TestCase):
    def test_weekday_matches_datetime_in_range(self):
        for d in (date(2000, 1, 1), date(2017, 6, 27), date(1, 1, 1),
                  date(9999, 12, 31), date(1969, 7, 20)):
            a = AstroDate(d.year, d.month, d.day)
            self.assertEqual(a.weekday(), d.weekday())
            self.assertEqual(a.isoweekday(), d.isoweekday())
            self.assertEqual(a.isocalendar(), tuple(d.isocalendar()))
            self.assertEqual(a.toordinal(), d.toordinal())

    def test_weekday_out_of_range(self):
        # 1 Tishrei AM 1 in the cited Hebrew arithmetic falls on -3760-09-07
        # (proleptic Gregorian); its weekday is a plain int, computed via JDN
        a = AstroDate(-3760, 9, 7)
        # cross-check against the ordinal/weekday identity
        self.assertEqual(a.weekday(), (a.toordinal() - 1) % 7)
        # round-trips through the ordinal
        self.assertEqual(AstroDate.fromordinal(a.toordinal()), a)

    def test_isoformat_round_trips(self):
        for a in (AstroDate(2020, 6, 15),
                  AstroDate(-3760, 9, 7),
                  AstroDate(12000, 1, 1),
                  AstroDate(50, 3, 2, 13, 4, 5, 678901),
                  AstroDate(-44, 3, 15, 9, 30)):
            self.assertEqual(AstroDate.fromisoformat(a.isoformat()), a)

    def test_isoformat_expanded_examples(self):
        # the time part is ALWAYS present, exactly like datetime.isoformat()
        self.assertEqual(AstroDate(-3760, 9, 7).isoformat(),
                         "-003760-09-07T00:00:00")
        self.assertEqual(AstroDate(2020, 1, 1, 3, 4, 5).isoformat(),
                         "2020-01-01T03:04:05")

    def test_isoformat_matches_datetime_literally(self):
        # in-range values must be byte-identical to datetime.isoformat(),
        # including the T00:00:00 at midnight and microseconds only when nonzero
        for dt in (datetime(2020, 1, 1),                       # midnight
                   datetime(2020, 6, 15, 13, 4, 5),            # with seconds
                   datetime(2020, 6, 15, 13, 4, 5, 678901),    # with micros
                   datetime(50, 3, 2)):                        # 4-digit pad
            a = AstroDate.from_datetime(dt)
            self.assertEqual(a.isoformat(), dt.isoformat())
            # sep argument parity too (datetime.__str__ uses a space sep)
            self.assertEqual(a.isoformat(sep=" "), dt.isoformat(sep=" "))
            self.assertEqual(a.isoformat(sep=" "), str(dt))

    def test_str_delegates_to_isoformat(self):
        self.assertEqual(str(AstroDate(-3760, 9, 7)), "-003760-09-07T00:00:00")

    def test_timedelta_arithmetic_across_year_zero(self):
        # 1 CE minus one day crosses into year 0 (1 BC)
        a = AstroDate(1, 1, 1)
        self.assertEqual(a - timedelta(days=1), AstroDate(0, 12, 31))
        self.assertEqual(AstroDate(0, 12, 31) + timedelta(days=1), a)
        # difference is a timedelta
        self.assertEqual(AstroDate(1, 1, 1) - AstroDate(0, 12, 31),
                         timedelta(days=1))
        # sub-day arithmetic
        self.assertEqual(AstroDate(2020, 1, 1, 0, 0, 0)
                         + timedelta(hours=25, minutes=1),
                         AstroDate(2020, 1, 2, 1, 1))

    def test_cross_type_eq_and_ordering(self):
        self.assertEqual(AstroDate(2020, 6, 15), date(2020, 6, 15))
        self.assertEqual(AstroDate(2020, 6, 15, 0, 0),
                         datetime(2020, 6, 15))
        self.assertNotEqual(AstroDate(2020, 6, 15, 1), datetime(2020, 6, 15))
        self.assertTrue(AstroDate(-1) < date(1, 1, 1))
        self.assertTrue(AstroDate(12000) > datetime(9999, 12, 31))
        # datetime.__eq__ yields NotImplemented for a non-date, so Python
        # falls back to our reflected __eq__
        self.assertEqual(datetime(2020, 6, 15), AstroDate(2020, 6, 15, 0))

    def test_hash_matches_datetime_in_range(self):
        self.assertEqual(hash(AstroDate(2020, 1, 1)),
                         hash(datetime(2020, 1, 1)))
        self.assertEqual(hash(AstroDate(2020, 6, 15, 13, 4)),
                         hash(datetime(2020, 6, 15, 13, 4)))
        # out-of-range values are still hashable
        self.assertIsInstance(hash(AstroDate(-3760, 9, 7)), int)

    def test_replace_and_accessors(self):
        a = AstroDate(2020, 6, 15, 13, 4, 5)
        self.assertEqual(a.replace(year=-44), AstroDate(-44, 6, 15, 13, 4, 5))
        self.assertEqual(a.date(), date(2020, 6, 15))
        self.assertEqual(a.time(), time(13, 4, 5))

    def test_strftime_subset(self):
        a = AstroDate(-3760, 9, 7)
        self.assertEqual(a.strftime("%Y-%m-%d"), "-003760-09-07")
        b = AstroDate(2020, 1, 3)
        self.assertEqual(b.strftime("%Y-%m-%d"), "2020-01-03")
        self.assertEqual(b.strftime("%j"), "003")
        self.assertEqual(b.strftime("%W"), datetime(2020, 1, 3).strftime("%W"))
        # %A/%B are computed from AstroDate's own weekday/month arithmetic,
        # so they are supported even out of datetime's range.
        self.assertEqual(a.strftime("%A"),
                         ("Monday", "Tuesday", "Wednesday", "Thursday",
                          "Friday", "Saturday", "Sunday")[a.weekday()])
        with self.assertRaises(ValueError):
            a.strftime("%Q")   # not a supported directive


class TestAwareSemantics(unittest.TestCase):
    """Z1: aware-optional AstroDate mirrors datetime's tz semantics."""

    def setUp(self):
        self.NY = ZoneInfo("America/New_York")
        self.UTC = timezone.utc

    def test_naive_by_default(self):
        a = AstroDate(2024, 1, 1)
        self.assertIsNone(a.tzinfo)
        self.assertIsNone(a.utcoffset())
        self.assertIsNone(a.tzname())
        self.assertIsNone(a.dst())

    def test_utcoffset_tzname_dst_delegate(self):
        summer = AstroDate(2024, 7, 1, 12, tzinfo=self.NY)   # EDT
        winter = AstroDate(2024, 1, 1, 12, tzinfo=self.NY)   # EST
        self.assertEqual(summer.utcoffset(), timedelta(hours=-4))
        self.assertEqual(winter.utcoffset(), timedelta(hours=-5))
        self.assertEqual(summer.tzname(), "EDT")
        self.assertEqual(winter.dst(), timedelta(0))
        self.assertEqual(summer.dst(), timedelta(hours=1))

    def test_utcoffset_out_of_range_via_proxy(self):
        # year 12000 is out of datetime range; the recurring rule still resolves
        far = AstroDate(12000, 7, 1, 12, tzinfo=self.NY)
        self.assertEqual(far.utcoffset(), timedelta(hours=-4))
        self.assertIsNone(far.datetime())          # no real datetime out of range
        self.assertIsInstance(hash(far), int)

    def test_mixed_naive_aware_never_equal(self):
        self.assertNotEqual(AstroDate(2024, 1, 1),
                            AstroDate(2024, 1, 1, tzinfo=self.UTC))
        # and vs a real datetime, both directions
        self.assertNotEqual(AstroDate(2024, 1, 1),
                            datetime(2024, 1, 1, tzinfo=self.UTC))
        self.assertNotEqual(datetime(2024, 1, 1),
                            AstroDate(2024, 1, 1, tzinfo=self.UTC))

    def test_mixed_ordering_raises_typeerror(self):
        for op in ("__lt__", "__le__", "__gt__", "__ge__"):
            with self.subTest(op=op):
                with self.assertRaises(TypeError):
                    getattr(AstroDate(2024, 1, 1), op)(
                        AstroDate(2024, 1, 1, tzinfo=self.UTC))
        with self.assertRaises(TypeError):
            AstroDate(2024, 1, 1) < datetime(2024, 1, 1, tzinfo=self.UTC)

    def test_mixed_subtraction_raises(self):
        with self.assertRaises(TypeError):
            AstroDate(2024, 1, 1, tzinfo=self.UTC) - AstroDate(2024, 1, 1)

    def test_aware_eq_and_hash_by_instant(self):
        # same instant, two zones -> equal and hash-equal
        u = AstroDate(2024, 6, 1, 16, 0, tzinfo=self.UTC)      # 16:00Z
        n = AstroDate(2024, 6, 1, 12, 0, tzinfo=self.NY)       # 12:00 EDT == 16:00Z
        self.assertEqual(u, n)
        self.assertEqual(hash(u), hash(n))
        # and equal to the equivalent aware datetime, hash-consistent
        self.assertEqual(u, datetime(2024, 6, 1, 16, tzinfo=self.UTC))
        self.assertEqual(hash(u), hash(datetime(2024, 6, 1, 16, tzinfo=self.UTC)))

    def test_aware_ordering_by_instant(self):
        # 12:00 EDT (=16:00Z) is later than 15:00Z
        self.assertTrue(AstroDate(2024, 6, 1, 15, tzinfo=self.UTC)
                        < AstroDate(2024, 6, 1, 12, tzinfo=self.NY))

    def test_aware_subtraction_is_instant_difference(self):
        u = AstroDate(2024, 6, 1, 16, tzinfo=self.UTC)
        n = AstroDate(2024, 6, 1, 12, tzinfo=self.NY)
        self.assertEqual(u - n, timedelta(0))

    def test_astimezone_converts_instant(self):
        a = AstroDate(2024, 6, 1, 12, tzinfo=self.UTC).astimezone(self.NY)
        self.assertEqual(a, AstroDate(2024, 6, 1, 12, tzinfo=self.UTC))
        self.assertEqual(a.hour, 8)                 # 12:00Z == 08:00 EDT
        self.assertEqual(a.utcoffset(), timedelta(hours=-4))

    def test_astimezone_matches_datetime_in_range(self):
        for dt in (datetime(2024, 6, 1, 12, tzinfo=self.UTC),
                   datetime(2024, 1, 1, 3, 30, tzinfo=self.UTC)):
            a = AstroDate.from_datetime(dt).replace(tzinfo=self.UTC)
            self.assertEqual(a.astimezone(self.NY).isoformat(),
                             dt.astimezone(self.NY).isoformat())

    def test_astimezone_naive_raises(self):
        with self.assertRaises(ValueError):
            AstroDate(2024, 1, 1).astimezone(self.NY)

    def test_replace_tzinfo_is_label_preserving(self):
        a = AstroDate(2024, 6, 1, 12)
        aware = a.replace(tzinfo=self.NY)
        self.assertEqual((aware.hour, aware.minute), (12, 0))   # wall unchanged
        self.assertEqual(aware.utcoffset(), timedelta(hours=-4))
        self.assertIsNone(aware.replace(tzinfo=None).tzinfo)     # can clear

    def test_aware_isoformat_and_roundtrip(self):
        a = AstroDate(2024, 6, 1, 12, tzinfo=self.NY)
        self.assertEqual(a.isoformat(), "2024-06-01T12:00:00-04:00")
        # in-range parity with datetime
        self.assertEqual(a.isoformat(),
                         datetime(2024, 6, 1, 12, tzinfo=self.NY).isoformat())
        # round-trips to a fixed-offset equivalent
        back = AstroDate.fromisoformat(a.isoformat())
        self.assertEqual(back, a)
        self.assertEqual(AstroDate.fromisoformat("2024-06-01T16:00:00Z"),
                         AstroDate(2024, 6, 1, 16, tzinfo=self.UTC))

    def test_aware_add_timedelta_keeps_zone(self):
        a = AstroDate(2024, 6, 1, 12, tzinfo=self.NY) + timedelta(hours=1)
        self.assertEqual((a.hour, a.tzinfo), (13, self.NY))


class TestFoldGapResolution(unittest.TestCase):
    """Z1: resolve_wall_clock -- fold (REPEAT) and gap (SKIP)."""

    def setUp(self):
        self.NY = ZoneInfo("America/New_York")

    def test_unique_wall_clock(self):
        r = resolve_wall_clock(2024, 6, 1, 12, 0, self.NY)
        self.assertIsInstance(r, AstroDate)
        self.assertEqual(r.utcoffset(), timedelta(hours=-4))

    def test_fall_back_returns_two_instants(self):
        # 2024-11-03 01:30 occurs twice in America/New_York
        r = resolve_wall_clock(2024, 11, 3, 1, 30, self.NY)
        self.assertIsInstance(r, tuple)
        earlier, later = r
        self.assertEqual(earlier.utcoffset(), timedelta(hours=-4))   # EDT
        self.assertEqual(later.utcoffset(), timedelta(hours=-5))     # EST
        self.assertTrue(earlier < later)                             # distinct
        self.assertEqual(later - earlier, timedelta(hours=1))
        # both read the same wall clock
        self.assertEqual((earlier.hour, earlier.minute), (1, 30))
        self.assertEqual((later.hour, later.minute), (1, 30))

    def test_spring_forward_gap_never_existed(self):
        # 2024-03-10 02:30 does not exist in America/New_York
        r = resolve_wall_clock(2024, 3, 10, 2, 30, self.NY)
        self.assertIsInstance(r, NeverExisted)
        self.assertEqual(r.discontinuity.kind, DiscontinuityKind.SKIP)
        self.assertEqual(r.label.as_tuple(), (2024, 3, 10))


class TestCivilArithmetic(unittest.TestCase):
    """Z2: civil_add -- calendar/zone/timeline-aware, vs absolute +timedelta."""

    def setUp(self):
        self.NY = ZoneInfo("America/New_York")

    def test_day_add_across_spring_forward_is_23h(self):
        start = AstroDate(2024, 3, 9, 12, 0, tzinfo=self.NY)
        res = civil_add(start, days=1, zone=self.NY)
        self.assertEqual((res.year, res.month, res.day, res.hour), (2024, 3, 10, 12))
        self.assertEqual(res - start, timedelta(hours=23))     # real duration

    def test_day_add_across_fall_back_is_25h(self):
        start = AstroDate(2024, 11, 2, 12, 0, tzinfo=self.NY)
        res = civil_add(start, days=1, zone=self.NY)
        self.assertEqual((res.month, res.day, res.hour), (11, 3, 12))
        self.assertEqual(res - start, timedelta(hours=25))

    def test_absolute_add_stays_real_duration(self):
        # + timedelta is untouched: exactly 24h of wall shift, zone preserved
        start = AstroDate(2024, 3, 9, 12, 0, tzinfo=self.NY)
        self.assertEqual(start + timedelta(days=1),
                         AstroDate(2024, 3, 10, 12, 0, tzinfo=self.NY))

    def test_month_add_clamps_day_of_month(self):
        self.assertEqual(civil_add(AstroDate(2024, 1, 31), months=1),
                         AstroDate(2024, 2, 29))     # 2024 is a leap year
        self.assertEqual(civil_add(AstroDate(2023, 1, 31), months=1),
                         AstroDate(2023, 2, 28))
        self.assertEqual(civil_add(AstroDate(2024, 1, 31), years=1, months=1),
                         AstroDate(2025, 2, 28))

    def test_timeline_day_add_crosses_reform_seam(self):
        from chronologia.timelines import TIMELINES
        res = civil_add(AstroDate(1582, 10, 4), days=1,
                        timeline=TIMELINES["rome_1582"])
        self.assertEqual((res.year, res.month, res.day), (1582, 10, 15))

    def test_span_shifts_both_endpoints(self):
        from chronologia.astrodate import DateSpan
        span = DateSpan(AstroDate(2024, 1, 31), AstroDate(2024, 3, 31))
        out = civil_add(span, months=1)
        self.assertEqual(out.start, AstroDate(2024, 2, 29))
        self.assertEqual(out.end, AstroDate(2024, 4, 30))


if __name__ == "__main__":
    unittest.main()
