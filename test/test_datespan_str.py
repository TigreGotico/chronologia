"""``str(DateSpan(...))`` -- a compact, human-legible rendering.

Before this, ``str()`` fell back to the dataclass ``__repr__``, so even a
one-line log statement dumped the full ``DateSpan(start=AstroDate(...),
end=AstroDate(...), basis='exact')``.  ``__str__`` now collapses a whole
calendar day to just its date, keeps a same-day range to one date with a
time span, and only spells out both full timestamps when the endpoints
land on different days at different times.  ``__repr__`` is untouched --
these tests pin that it still round-trips through ``eval``-style detail.
"""
import unittest
from datetime import timedelta, timezone

from chronologia.astrodate import AstroDate, DateSpan


class TestDateSpanStr(unittest.TestCase):
    def test_whole_day_collapses_to_date(self):
        span = DateSpan(AstroDate(2020, 1, 1), AstroDate(2020, 1, 2))
        self.assertEqual(str(span), "2020-01-01")

    def test_whole_month_shows_date_range_without_time(self):
        span = DateSpan(AstroDate(2020, 1, 1), AstroDate(2020, 2, 1))
        self.assertEqual(str(span), "2020-01-01 - 2020-02-01")

    def test_same_day_time_range(self):
        span = DateSpan(AstroDate(2020, 1, 1, 9, 0), AstroDate(2020, 1, 1, 17, 0))
        self.assertEqual(str(span), "2020-01-01 09:00-17:00")

    def test_point_in_time(self):
        span = DateSpan(AstroDate(2020, 1, 1, 9, 30, 15),
                         AstroDate(2020, 1, 1, 9, 30, 15))
        self.assertEqual(str(span), "2020-01-01 09:30:15-09:30:15")

    def test_cross_day_with_times(self):
        span = DateSpan(AstroDate(2020, 1, 1, 22, 0), AstroDate(2020, 1, 2, 2, 0))
        self.assertEqual(str(span), "2020-01-01 22:00 - 2020-01-02 02:00")

    def test_aware_same_day_keeps_offset_on_each_side(self):
        tz = timezone(timedelta(hours=-4))
        span = DateSpan(AstroDate(2020, 1, 1, 9, 0, tzinfo=tz),
                         AstroDate(2020, 1, 1, 17, 0, tzinfo=tz))
        self.assertEqual(str(span), "2020-01-01 09:00-04:00 - 17:00-04:00")

    def test_repr_is_unchanged_dataclass_form(self):
        span = DateSpan(AstroDate(2020, 1, 1), AstroDate(2020, 2, 1))
        self.assertTrue(repr(span).startswith("DateSpan(start=AstroDate("))
        self.assertIn("basis='exact'", repr(span))
        self.assertNotEqual(repr(span), str(span))


if __name__ == "__main__":
    unittest.main()
