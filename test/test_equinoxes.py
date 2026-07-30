"""Tests for Meeus equinox/solstice, astronomical seasons and solar terms.

Gold cardinal-event instants are Fred Espenak / AstroPixels' published
Universal-Time table (downloaded 2026-07-21) -- real published astronomical
events, cross-checked against the Meeus ch.27 arithmetic within
:data:`~chronologia.equinoxes.EQUINOX_ACCURACY`. Solar-term golds trace to the
conventional jieqi table (Wikipedia, "Solar term"; lichun ~ Feb 4). The Meeus
coefficients and their stated accuracy trace to the sources named in
``chronologia/equinoxes.py``.
"""
import unittest
from datetime import datetime, timedelta

from chronologia.astrodate import AstroDate, DateSpan
from chronologia.equinoxes import (EQUINOX_ACCURACY, SOLAR_TERM_ACCURACY,
                                   SOLAR_TERM_NAMES, VALID_YEAR_RANGE,
                                   astronomical_season_span, equinox,
                                   solar_term)


def _centre(span: DateSpan) -> AstroDate:
    return span.start + (span.end - span.start) / 2


# Gold: AstroPixels UTC table, 2024 (astropixels_soleq2001, all UT).
GOLD_2024 = {
    "march": datetime(2024, 3, 20, 3, 7),
    "june": datetime(2024, 6, 20, 20, 51),
    "september": datetime(2024, 9, 22, 12, 44),
    "december": datetime(2024, 12, 21, 9, 20),
}
# Gold: AstroPixels UTC table, 2025.
GOLD_2025 = {
    "march": datetime(2025, 3, 20, 9, 2),
    "june": datetime(2025, 6, 21, 2, 42),
    "september": datetime(2025, 9, 22, 18, 20),
    "december": datetime(2025, 12, 21, 15, 3),
}


class TestEquinoxGold(unittest.TestCase):
    """Cardinal-event instants vs the published AstroPixels UTC table."""

    def _assert_gold(self, year, table):
        for which, gold in table.items():
            centre = _centre(equinox(year, which))
            delta = abs(centre - gold)
            self.assertLessEqual(
                delta, EQUINOX_ACCURACY,
                f"{year} {which}: {centre} vs gold {gold} = {delta}")

    def test_gold_2024(self):
        self._assert_gold(2024, GOLD_2024)

    def test_gold_2025(self):
        self._assert_gold(2025, GOLD_2025)

    def test_march_equinox_lands_on_march_20(self):
        sp = equinox(2024, "march")
        self.assertEqual((sp.start.year, sp.start.month, sp.start.day),
                         (2024, 3, 20))

    def test_all_four_events_distinct_and_ordered(self):
        instants = [_centre(equinox(2024, w))
                    for w in ("march", "june", "september", "december")]
        self.assertEqual(instants, sorted(instants))


class TestEquinoxSpan(unittest.TestCase):
    """Span shape: width == 2*accuracy, reconstructed basis, UTC endpoints."""

    def test_span_width_is_twice_accuracy(self):
        sp = equinox(2024, "june")
        self.assertEqual(sp.end - sp.start, 2 * EQUINOX_ACCURACY)

    def test_basis_is_reconstructed(self):
        self.assertEqual(equinox(2024, "march").basis, "reconstructed")

    def test_endpoints_are_astrodate(self):
        sp = equinox(2024, "march")
        self.assertIsInstance(sp.start, AstroDate)
        self.assertIsInstance(sp.end, AstroDate)


class TestSolarConsistency(unittest.TestCase):
    """Weak invariant vs the arithmetic solar engine (solar.py)."""

    def test_march_equinox_greenwich_sunrise_near_six_lmt(self):
        # On the equinox the Sun rises ~due east near 06:00 local mean time
        # everywhere; at Greenwich (lon 0) local mean time == UTC, so the
        # computed sunrise clusters around 06:00 UTC (a weak cross-check that
        # the two independent modules agree on "which day is the equinox").
        from chronologia.solar import sun_events
        day = _centre(equinox(2024, "march"))
        ev = sun_events(AstroDate(day.year, day.month, day.day), 0.0, 0.0)
        minutes = ev.sunrise.hour * 60 + ev.sunrise.minute
        self.assertLess(abs(minutes - 360), 20)  # within 20 min of 06:00


class TestSweep(unittest.TestCase):
    """A 500-year sweep: monotonic instants, ~91-day equinox->solstice gaps."""

    YEARS = range(2000, 2500)

    def test_march_equinoxes_strictly_increasing(self):
        prev = None
        for y in self.YEARS:
            inst = _centre(equinox(y, "march"))
            if prev is not None:
                self.assertGreater(inst, prev, f"non-monotonic at {y}")
            prev = inst

    def test_consecutive_cardinal_gaps_are_about_91_days(self):
        order = ("march", "june", "september", "december")
        for y in self.YEARS:
            instants = [_centre(equinox(y, w)) for w in order]
            instants.append(_centre(equinox(y + 1, "march")))
            for a, b in zip(instants, instants[1:]):
                gap_days = (b - a).total_seconds() / 86400.0
                self.assertTrue(
                    88.0 <= gap_days <= 94.0,
                    f"{y} gap {gap_days:.2f}d outside 91+-3")

    def test_year_length_is_about_a_tropical_year(self):
        for y in (2000, 2200, 2499):
            span_days = ((_centre(equinox(y + 1, "march"))
                          - _centre(equinox(y, "march"))).total_seconds()
                         / 86400.0)
            self.assertTrue(365.0 <= span_days <= 365.5, span_days)


class TestAstronomicalSeasons(unittest.TestCase):
    """Equinox-to-solstice spans, north and south."""

    def test_north_spring_is_march_to_june(self):
        sp = astronomical_season_span(2024, "spring")
        self.assertEqual(_centre(equinox(2024, "march")), sp.start)
        self.assertEqual(_centre(equinox(2024, "june")), sp.end)

    def test_north_winter_crosses_new_year(self):
        sp = astronomical_season_span(2024, "winter")
        self.assertEqual(sp.start.year, 2024)
        self.assertEqual(sp.end.year, 2025)

    def test_fall_is_synonym_for_autumn(self):
        self.assertEqual(astronomical_season_span(2024, "fall"),
                         astronomical_season_span(2024, "autumn"))

    def test_hemisphere_flip_shares_solar_events(self):
        # The March equinox opens spring in the north but autumn in the south.
        north_spring = astronomical_season_span(2024, "spring", "north")
        south_autumn = astronomical_season_span(2024, "autumn", "south")
        self.assertEqual(north_spring, south_autumn)

    def test_south_summer_crosses_new_year(self):
        sp = astronomical_season_span(2024, "summer", "south")
        self.assertEqual(sp.start.year, 2024)
        self.assertEqual(sp.end.year, 2025)

    def test_season_span_is_about_91_days(self):
        sp = astronomical_season_span(2024, "summer")
        days = (sp.end - sp.start).total_seconds() / 86400.0
        self.assertTrue(88.0 <= days <= 95.0, days)

    def test_season_basis_is_reconstructed(self):
        self.assertEqual(
            astronomical_season_span(2024, "spring").basis, "reconstructed")


class TestSolarTerms(unittest.TestCase):
    """The 24 jieqi via Meeus ch.25 mean-longitude inversion."""

    def test_there_are_24_named_terms(self):
        self.assertEqual(len(SOLAR_TERM_NAMES), 24)
        self.assertEqual(len(set(SOLAR_TERM_NAMES)), 24)

    def test_lichun_near_feb_4(self):
        sp = solar_term(2024, "lichun")
        self.assertEqual(sp.start.month, 2)
        self.assertIn(_centre(sp).day, (3, 4, 5))

    def test_index_and_name_agree(self):
        self.assertEqual(solar_term(2024, 0), solar_term(2024, "lichun"))
        self.assertEqual(solar_term(2024, 3), solar_term(2024, "chunfen"))

    def test_chunfen_matches_march_equinox_within_term_accuracy(self):
        # chunfen (longitude 0) is the March equinox; the mean-longitude term
        # instant agrees with the accurate ch.27 equinox to well within the
        # solar-term bound (the class-B accuracy gap, documented).
        delta = abs(_centre(solar_term(2024, "chunfen"))
                    - _centre(equinox(2024, "march")))
        self.assertLessEqual(delta, SOLAR_TERM_ACCURACY)

    def test_dongzhi_near_winter_solstice(self):
        delta = abs(_centre(solar_term(2024, "dongzhi"))
                    - _centre(equinox(2024, "december")))
        self.assertLessEqual(delta, SOLAR_TERM_ACCURACY)

    def test_terms_are_ordered_within_the_solar_year(self):
        # Sweep lichun..dongzhi (indices 0..21); each falls strictly after the
        # previous within the same civil year (dahan/xiaohan wrap past it).
        instants = [_centre(solar_term(2024, i)) for i in range(22)]
        self.assertEqual(instants, sorted(instants))

    def test_term_span_width_is_twice_accuracy(self):
        sp = solar_term(2024, "qingming")
        self.assertEqual(sp.end - sp.start, 2 * SOLAR_TERM_ACCURACY)

    def test_term_basis_is_reconstructed(self):
        self.assertEqual(solar_term(2024, "guyu").basis, "reconstructed")

    def test_qingming_near_april_4_5(self):
        sp = solar_term(2024, "qingming")
        self.assertEqual(sp.start.month, 4)
        self.assertIn(_centre(sp).day, (3, 4, 5))


class TestTtUtcHandling(unittest.TestCase):
    """TT->UTC via leap seconds in range; TT returned unconverted before 1972."""

    def test_in_range_uses_leap_second_conversion(self):
        # 2024 is inside the leap-second table: the reported instant is civil
        # UTC and matches the published UTC gold within a minute.
        centre = _centre(equinox(2024, "june"))
        self.assertLessEqual(abs(centre - GOLD_2024["june"]), EQUINOX_ACCURACY)

    def test_pre_1972_returns_tt_but_still_lands_on_the_right_day(self):
        # Before 1972 the leap-second table is out of scope; the TT instant is
        # returned unconverted (documented). It must still be a valid span on
        # the expected calendar day (equinox of 1600 ~ March 19-20).
        sp = equinox(1600, "march")
        self.assertEqual(sp.start.month, 3)
        self.assertIn(_centre(sp).day, (18, 19, 20, 21))

    def test_boundary_years_1971_and_1972_are_close(self):
        # The ~1-minute timescale step at the 1972 boundary is far smaller than
        # the year-to-year drift, so consecutive years stay ordered across it.
        a = _centre(equinox(1971, "march"))
        b = _centre(equinox(1972, "march"))
        gap = (b - a).total_seconds() / 86400.0
        self.assertTrue(365.0 <= gap <= 365.6, gap)


class TestAdversarial(unittest.TestCase):
    """Bad inputs and out-of-range years -> documented ValueError/TypeError."""

    def test_unknown_event_name(self):
        with self.assertRaises(ValueError):
            equinox(2024, "spring")  # not a cardinal-event name

    def test_year_below_valid_range(self):
        with self.assertRaises(ValueError):
            equinox(VALID_YEAR_RANGE[0] - 1, "march")

    def test_year_above_valid_range(self):
        with self.assertRaises(ValueError):
            equinox(VALID_YEAR_RANGE[1] + 1, "march")

    def test_winter_end_year_pushed_out_of_range(self):
        # winter's end event is the following year's March equinox, so the
        # top valid year is out of range for winter (year+1 == 3001).
        with self.assertRaises(ValueError):
            astronomical_season_span(VALID_YEAR_RANGE[1], "winter")

    def test_unknown_season(self):
        with self.assertRaises(ValueError):
            astronomical_season_span(2024, "monsoon")

    def test_unknown_hemisphere(self):
        with self.assertRaises(ValueError):
            astronomical_season_span(2024, "spring", "eastern")

    def test_unknown_solar_term_name(self):
        with self.assertRaises(ValueError):
            solar_term(2024, "notaterm")

    def test_solar_term_index_out_of_range(self):
        with self.assertRaises(ValueError):
            solar_term(2024, 24)
        with self.assertRaises(ValueError):
            solar_term(2024, -1)

    def test_solar_term_bad_type(self):
        with self.assertRaises(TypeError):
            solar_term(2024, 3.5)
        with self.assertRaises(TypeError):
            solar_term(2024, True)  # bool is not a valid index

    def test_solar_term_year_out_of_range(self):
        with self.assertRaises(ValueError):
            solar_term(VALID_YEAR_RANGE[1] + 1, "lichun")


if __name__ == "__main__":
    unittest.main()
