"""Public ``extract_timespan`` edge: DateSpan-native extraction.

Only languages with engine locale data (``locale/<code>/lang.json``) are
supported for now -- ar and he ship the nongregorian/reckoned data.  Every
Gregorian value is the same one hand-checked in test_engine_nongregorian.py.
"""
import unittest
from datetime import date, datetime, timedelta

from chronologia import extract_timespan, DateSpan, AstroDate
from chronologia.resolution import DateTimeResolution

ANCHOR = datetime(2017, 6, 27, 13, 4)


class TestExtractTimespan(unittest.TestCase):
    def test_ar_day_wide_span(self):
        span, rem = extract_timespan("15 ramadan 1446", "ar", ANCHOR)
        self.assertIsInstance(span, DateSpan)
        self.assertEqual(span.start, AstroDate(2025, 3, 15))
        self.assertEqual(span.end, AstroDate(2025, 3, 16))
        self.assertEqual(span.width, timedelta(days=1))
        self.assertEqual(span.resolution, DateTimeResolution.DAY)
        self.assertEqual(rem, "")

    def test_he_month_wide_span(self):
        # a bare month + year is month-wide: [1 Tishri, 1 Heshvan)
        span, _ = extract_timespan("tishrei 5785", "he", ANCHOR)
        self.assertEqual(span.start, AstroDate(2024, 10, 3))
        self.assertEqual(span.resolution, DateTimeResolution.MONTH)

    def test_start_datetime_conveniences(self):
        span, _ = extract_timespan("15 ramadan 1446", "ar", ANCHOR)
        self.assertEqual(span.start_datetime, datetime(2025, 3, 15))
        self.assertEqual(span.end_datetime, datetime(2025, 3, 16))

    def test_contains_and_overlaps(self):
        span, _ = extract_timespan("tishrei 5785", "he", ANCHOR)
        self.assertTrue(span.contains(date(2024, 10, 15)))
        self.assertFalse(span.contains(date(2024, 11, 3)))  # half-open end

    def test_no_match_returns_none(self):
        self.assertIsNone(extract_timespan("just some words", "ar", ANCHOR))

    def test_unsupported_language_raises(self):
        # a language with no engine locale data (locale/<code>/lang.json)
        with self.assertRaises(NotImplementedError):
            extract_timespan("june 2027", "zu", ANCHOR)


class TestDateSpanValidation(unittest.TestCase):
    def test_start_after_end_rejected(self):
        with self.assertRaises(ValueError):
            DateSpan(AstroDate(2020, 2, 1), AstroDate(2020, 1, 1))

    def test_out_of_range_endpoint_datetime_is_none(self):
        span = DateSpan(AstroDate(-44, 1, 1), AstroDate(-44, 12, 31))
        self.assertIsNone(span.start_datetime)


if __name__ == "__main__":
    unittest.main()
