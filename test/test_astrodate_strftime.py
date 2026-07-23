"""``format(astrodate, spec)`` / ``AstroDate.__format__`` -- strftime-style.

Regression coverage for the bug where ``format(astrodate, "%Y-%m-%d")``
raised ``TypeError`` (the default ``object.__format__`` only accepts an
empty spec).  ``__format__`` must route non-empty specs through
:meth:`AstroDate.strftime`, which computes every field from AstroDate's own
year/month/day/hour/minute/second -- never from a real ``datetime`` -- so it
must not raise for years outside 1..9999 (69, 200000, negative/BC years).
"""
import unittest
from datetime import datetime

from chronologia.astrodate import AstroDate


class TestFormatEmptySpec(unittest.TestCase):
    def test_empty_spec_matches_str(self):
        a = AstroDate(2024, 3, 6, 13, 4, 5)
        self.assertEqual(format(a, ""), str(a))
        self.assertEqual(f"{a}", str(a))

    def test_empty_spec_unchanged_out_of_range(self):
        a = AstroDate(-3760, 9, 7)
        self.assertEqual(format(a, ""), str(a))
        self.assertEqual(format(a, ""), "-003760-09-07T00:00:00")


class TestFormatStrftimeSpec(unittest.TestCase):
    def test_basic_date(self):
        self.assertEqual(format(AstroDate(2024, 3, 6), "%Y-%m-%d"),
                         "2024-03-06")

    def test_time_fields(self):
        a = AstroDate(2024, 3, 6, 13, 4, 5)
        self.assertEqual(format(a, "%H:%M:%S"), "13:04:05")

    def test_weekday_and_month_name(self):
        # 2024-03-06 is a Wednesday in March.
        a = AstroDate(2024, 3, 6)
        self.assertEqual(format(a, "%A"), "Wednesday")
        self.assertEqual(format(a, "%a"), "Wed")
        self.assertEqual(format(a, "%B"), "March")
        self.assertEqual(format(a, "%b"), "Mar")
        # cross-check against real datetime for an in-range value
        dt = datetime(2024, 3, 6)
        self.assertEqual(format(a, "%A"), dt.strftime("%A"))
        self.assertEqual(format(a, "%B"), dt.strftime("%B"))

    def test_two_digit_year(self):
        self.assertEqual(format(AstroDate(2024, 3, 6), "%y"), "24")

    def test_percent_literal(self):
        self.assertEqual(format(AstroDate(2024, 3, 6), "100%%"), "100%")

    def test_am_pm(self):
        self.assertEqual(format(AstroDate(2024, 3, 6, 9), "%p"), "AM")
        self.assertEqual(format(AstroDate(2024, 3, 6, 21), "%p"), "PM")

    def test_full_spec_matches_datetime_in_range(self):
        dt = datetime(2024, 3, 6, 13, 4, 5)
        a = AstroDate.from_datetime(dt)
        spec = "%Y-%m-%d %H:%M:%S %A %B %y %p"
        self.assertEqual(format(a, spec), dt.strftime(spec))


class TestFormatOutOfRangeYears(unittest.TestCase):
    """The whole point of AstroDate: years datetime cannot hold, no crash."""

    def test_small_out_of_range_year_69(self):
        # zero-padded to (at least) 4 digits, matching strftime's %Y convention
        self.assertEqual(format(AstroDate(69, 6, 1), "%Y"), "0069")

    def test_large_year_200000(self):
        result = format(AstroDate(200000, 6, 1), "%Y-%m-%d")
        self.assertEqual(result, "+200000-06-01")

    def test_negative_bc_year(self):
        # 44 BC (astronomical year -43), the Ides of March
        result = format(AstroDate(-43, 3, 15), "%Y-%m-%d")
        self.assertEqual(result, "-000043-03-15")

    def test_weekday_and_month_name_out_of_range_do_not_raise(self):
        a = AstroDate(-3760, 9, 7)
        # must not construct a real datetime (which would raise for this year)
        name = format(a, "%A %B")
        self.assertIn(name.split()[0],
                     ("Monday", "Tuesday", "Wednesday", "Thursday",
                      "Friday", "Saturday", "Sunday"))
        self.assertEqual(name.split()[1], "September")

    def test_huge_year_no_datetime_constructed(self):
        # Patch datetime() constructor calls would be overkill; instead
        # assert the operation simply succeeds where a real datetime
        # would raise ValueError constructing itself.
        with self.assertRaises(ValueError):
            datetime(200000, 6, 1)
        # AstroDate's formatting must not hit that path.
        self.assertEqual(format(AstroDate(200000, 6, 1), "%Y"), "+200000")


if __name__ == "__main__":
    unittest.main()
