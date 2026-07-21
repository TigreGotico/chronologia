"""AstroDate is protocol-compatible with datetime.

Subclassing ``datetime`` is impossible (its C-level year bounds are exactly
what AstroDate escapes), so compatibility is enforced here: a test that walks
``datetime``'s public API and asserts AstroDate answers every width-relevant
member, plus exact-value tests for the arithmetic and formatting that has to
stay correct across year 0 and far outside the ``datetime`` range.
"""
import unittest
from datetime import date, datetime, time, timedelta

from chronologia.astrodate import AstroDate


# datetime members AstroDate deliberately does NOT provide, with the reason:
#   * timezone-aware behaviour -- AstroDate is tz-naive by construction
#   * factory / "now" constructors -- there is no civil clock outside range
#   * class constants and stdlib/locale helpers that assume the datetime range
_EXCLUDED = {
    # tz-aware
    "astimezone", "dst", "tzinfo", "tzname", "utcoffset", "timetz",
    "utctimetuple", "fold",
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
        with self.assertRaises(ValueError):
            a.strftime("%A")   # weekday name is not year-width-safe


if __name__ == "__main__":
    unittest.main()
