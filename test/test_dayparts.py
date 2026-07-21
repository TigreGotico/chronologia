"""Day-part registry and DateSpan algebra.

Boundary gold values are the Unicode CLDR 47 Day Period Rules (see
``chronologia/dayparts.py`` and the papers-library copy at
``standards/cldr47_day_period_rules.html``): en morning [06,12), afternoon
[12,18), evening [18,21), night [21,06); es tarde [12,20). The algebra section
asserts the interval-algebra identities (commutativity of intersect/union, the
half-open tiling law) directly, not against any library.
"""
import unittest
from datetime import date, datetime, time, timedelta

from chronologia import (AstroDate, DateSpan, DAY_PARTS, DayPart,
                         UnknownDayPartError, daypart_span)
from chronologia.dayparts import lookup


TUE = date(2027, 6, 8)   # a Tuesday
WED = date(2027, 6, 9)


def span(y1, m1, d1, y2, m2, d2):
    return DateSpan(AstroDate(y1, m1, d1), AstroDate(y2, m2, d2))


class TestDefaults(unittest.TestCase):
    def test_morning_boundaries(self):
        s = daypart_span(TUE, "morning")
        self.assertEqual(s.start, AstroDate(2027, 6, 8, 6))
        self.assertEqual(s.end, AstroDate(2027, 6, 8, 12))

    def test_afternoon_boundaries(self):
        s = daypart_span(TUE, "afternoon")
        self.assertEqual(s.start, AstroDate(2027, 6, 8, 12))
        self.assertEqual(s.end, AstroDate(2027, 6, 8, 18))

    def test_evening_boundaries(self):
        s = daypart_span(TUE, "evening")
        self.assertEqual(s.start, AstroDate(2027, 6, 8, 18))
        self.assertEqual(s.end, AstroDate(2027, 6, 8, 21))

    def test_afternoon_evening_tile(self):
        # half-open: afternoon ends exactly where evening begins.
        self.assertEqual(daypart_span(TUE, "afternoon").end,
                         daypart_span(TUE, "evening").start)

    def test_morning_afternoon_tile_at_noon(self):
        self.assertEqual(daypart_span(TUE, "morning").end,
                         daypart_span(TUE, "afternoon").start)

    def test_defaults_have_no_region(self):
        for name in ("morning", "afternoon", "evening", "night",
                     "noon", "midnight"):
            self.assertIsNone(lookup(name).region)

    def test_source_is_cited(self):
        self.assertIn("CLDR", lookup("morning").source)

    def test_registry_keys(self):
        self.assertIn("morning", DAY_PARTS)
        self.assertIn("tarde_es", DAY_PARTS)


class TestMidnightCrossing(unittest.TestCase):
    def test_night_crosses_into_next_day(self):
        s = daypart_span(TUE, "night")
        self.assertEqual(s.start, AstroDate(2027, 6, 8, 21))
        self.assertEqual(s.end, AstroDate(2027, 6, 9, 6))

    def test_night_end_lands_on_next_civil_day(self):
        s = daypart_span(TUE, "night")
        self.assertEqual(s.end.day, 9)
        self.assertNotEqual(s.start.day, s.end.day)

    def test_night_flag_set(self):
        self.assertTrue(lookup("night").crosses_midnight)

    def test_night_anchored_to_named_date(self):
        # "tuesday night" starts on Tuesday even though it ends on Wednesday.
        self.assertEqual(daypart_span(TUE, "night").start.day, 8)

    def test_night_crossing_a_month_boundary(self):
        s = daypart_span(date(2027, 6, 30), "night")
        self.assertEqual(s.start, AstroDate(2027, 6, 30, 21))
        self.assertEqual(s.end, AstroDate(2027, 7, 1, 6))

    def test_night_crossing_a_year_boundary(self):
        s = daypart_span(date(2027, 12, 31), "night")
        self.assertEqual(s.end, AstroDate(2028, 1, 1, 6))

    def test_non_crosser_flag_false(self):
        self.assertFalse(lookup("morning").crosses_midnight)


class TestAnchors(unittest.TestCase):
    def test_noon_minimal_width(self):
        s = daypart_span(TUE, "noon")
        self.assertEqual(s.start, AstroDate(2027, 6, 8, 12))
        self.assertEqual(s.width, timedelta(minutes=1))

    def test_midnight_minimal_width(self):
        s = daypart_span(TUE, "midnight")
        self.assertEqual(s.start, AstroDate(2027, 6, 8, 0, 0))
        self.assertEqual(s.width, timedelta(minutes=1))

    def test_midnight_does_not_cross(self):
        self.assertFalse(lookup("midnight").crosses_midnight)


class TestRegionVariant(unittest.TestCase):
    def test_tarde_boundaries(self):
        s = daypart_span(TUE, "tarde", region="es")
        self.assertEqual(s.start, AstroDate(2027, 6, 8, 12))
        self.assertEqual(s.end, AstroDate(2027, 6, 8, 20))

    def test_tarde_outspans_default_afternoon(self):
        # the lesson: es "tarde" covers English afternoon AND early evening.
        tarde = daypart_span(TUE, "tarde", region="es")
        afternoon = daypart_span(TUE, "afternoon")
        self.assertGreater(tarde.width, afternoon.width)
        self.assertTrue(tarde.contains(daypart_span(TUE, "evening").start))

    def test_region_falls_back_to_default(self):
        # es overrides "tarde", not "morning": morning resolves to the default.
        self.assertEqual(daypart_span(TUE, "morning", region="es"),
                         daypart_span(TUE, "morning"))

    def test_madrugada_is_small_hours_no_crossing(self):
        # madrugada [00:00,06:00) sits wholly before dawn; it does not wrap.
        mad = lookup("madrugada", region="es")
        self.assertFalse(mad.crosses_midnight)
        s = daypart_span(TUE, "madrugada", region="es")
        self.assertEqual(s.start, AstroDate(2027, 6, 8, 0))
        self.assertEqual(s.end, AstroDate(2027, 6, 8, 6))

    def test_region_case_insensitive(self):
        self.assertEqual(lookup("tarde", region="ES"),
                         lookup("tarde", region="es"))


class TestInputTypes(unittest.TestCase):
    def test_accepts_datetime(self):
        s = daypart_span(datetime(2027, 6, 8, 3, 0), "morning")
        self.assertEqual(s.start, AstroDate(2027, 6, 8, 6))

    def test_accepts_astrodate(self):
        s = daypart_span(AstroDate(2027, 6, 8), "morning")
        self.assertEqual(s.start, AstroDate(2027, 6, 8, 6))


class TestComposition(unittest.TestCase):
    def test_compose_with_full_day_span(self):
        tuesday = span(2027, 6, 8, 2027, 6, 9)
        s = daypart_span(tuesday, "morning")
        self.assertEqual(s, daypart_span(TUE, "morning"))

    def test_compose_clips_midnight_crosser(self):
        # night composed with the Tuesday day-span is clipped at Wed 00:00,
        # unlike the bare-date form which reaches into Wednesday.
        tuesday = span(2027, 6, 8, 2027, 6, 9)
        s = daypart_span(tuesday, "night")
        self.assertEqual(s.start, AstroDate(2027, 6, 8, 21))
        self.assertEqual(s.end, AstroDate(2027, 6, 9, 0, 0))

    def test_compose_with_partial_span(self):
        window = DateSpan(AstroDate(2027, 6, 8, 9), AstroDate(2027, 6, 8, 15))
        s = daypart_span(window, "morning")
        self.assertEqual(s.start, AstroDate(2027, 6, 8, 9))
        self.assertEqual(s.end, AstroDate(2027, 6, 8, 12))

    def test_compose_disjoint_raises(self):
        night_only = DateSpan(AstroDate(2027, 6, 8, 22),
                              AstroDate(2027, 6, 8, 23))
        with self.assertRaises(ValueError):
            daypart_span(night_only, "morning")


class TestAdversarial(unittest.TestCase):
    def test_unknown_name(self):
        with self.assertRaises(UnknownDayPartError):
            daypart_span(TUE, "brunch")

    def test_unknown_name_is_keyerror(self):
        self.assertTrue(issubclass(UnknownDayPartError, KeyError))

    def test_region_only_name_without_region_raises(self):
        # "tarde" is not a global name; asking for it with no region fails.
        with self.assertRaises(UnknownDayPartError):
            daypart_span(TUE, "tarde")

    def test_unknown_region_falls_back_to_default(self):
        self.assertEqual(daypart_span(TUE, "morning", region="zz"),
                         daypart_span(TUE, "morning"))

    def test_crosses_flag_must_match_endpoints(self):
        with self.assertRaises(ValueError):
            DayPart("bogus", time(6), time(12), None, "x",
                    crosses_midnight=True)

    def test_endpoints_must_be_time(self):
        with self.assertRaises(TypeError):
            DayPart("bogus", 6, 12, None, "x", crosses_midnight=False)


class TestSpanAlgebra(unittest.TestCase):
    def setUp(self):
        self.june = span(2027, 6, 1, 2027, 7, 1)
        self.july = span(2027, 7, 1, 2027, 8, 1)
        self.summer = span(2027, 6, 1, 2027, 9, 1)
        self.august = span(2027, 8, 1, 2027, 9, 1)

    # --- intersect ---
    def test_intersect_june_summer(self):
        self.assertEqual(self.june.intersect(self.summer), self.june)

    def test_intersect_disjoint_is_none(self):
        self.assertIsNone(self.june.intersect(self.july))

    def test_intersect_touching_is_none(self):
        # half-open: june and july merely touch, share no instant.
        self.assertIsNone(self.june.intersect(self.july))
        self.assertIsNone(self.july.intersect(self.june))

    def test_intersect_commutes(self):
        for a, b in [(self.june, self.summer), (self.summer, self.august),
                     (self.june, self.july)]:
            self.assertEqual(a.intersect(b), b.intersect(a))

    def test_intersect_partial(self):
        jul_aug = span(2027, 7, 1, 2027, 9, 1)
        jun_jul = span(2027, 6, 15, 2027, 7, 15)
        self.assertEqual(jul_aug.intersect(jun_jul),
                         span(2027, 7, 1, 2027, 7, 15))

    # --- union ---
    def test_union_tiling_two_months(self):
        u = self.june.union(self.july)
        self.assertEqual(u, span(2027, 6, 1, 2027, 8, 1))

    def test_union_commutes(self):
        self.assertEqual(self.june.union(self.july),
                         self.july.union(self.june))

    def test_union_overlapping(self):
        self.assertEqual(self.june.union(self.summer), self.summer)

    def test_union_disjoint_raises(self):
        with self.assertRaises(ValueError):
            self.june.union(self.august)

    # --- gap ---
    def test_gap_between_disjoint(self):
        self.assertEqual(self.june.gap(self.august), self.july)

    def test_gap_commutes(self):
        self.assertEqual(self.june.gap(self.august),
                         self.august.gap(self.june))

    def test_gap_adjacent_is_none(self):
        self.assertIsNone(self.june.gap(self.july))

    def test_gap_overlapping_is_none(self):
        self.assertIsNone(self.june.gap(self.summer))

    def test_basis_propagates_worst_of(self):
        recon = DateSpan(AstroDate(2027, 6, 1), AstroDate(2027, 9, 1),
                         basis="reconstructed")
        got = self.june.intersect(recon)
        self.assertEqual(got.basis, "reconstructed")


class TestAlgebraDaypartComposition(unittest.TestCase):
    def test_daypart_union_two_adjacent_parts(self):
        # morning ∪ afternoon tiles into one 06:00–18:00 span.
        u = daypart_span(TUE, "morning").union(daypart_span(TUE, "afternoon"))
        self.assertEqual(u.start, AstroDate(2027, 6, 8, 6))
        self.assertEqual(u.end, AstroDate(2027, 6, 8, 18))

    def test_daypart_gap_between_morning_and_evening(self):
        g = daypart_span(TUE, "morning").gap(daypart_span(TUE, "evening"))
        self.assertEqual(g, daypart_span(TUE, "afternoon"))


if __name__ == "__main__":
    unittest.main()
