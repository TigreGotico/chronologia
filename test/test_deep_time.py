"""Deep-time reckoning: geological span widths, resolution tiers, the basis
lattice and scaled Before-Present units.

The gold values (K-Pg boundary, geological division magnitudes) are derived
from first principles here — the BP epoch is AD 1950 (Stuiver & Polach 1977,
as cited in ``eras.py``) — and the arithmetic is asserted against that
derivation, not against any library's output.
"""
import unittest
from datetime import timedelta
from decimal import Decimal

from chronologia import (AstroDate, DateSpan, DateTimeResolution as R,
                         WideDuration, combine_basis, resolve_bp)
from chronologia.calendars import CALENDARS


# --------------------------------------------------------------------------
# Item 1: width overflow -> WideDuration
# --------------------------------------------------------------------------
class TestWideDuration(unittest.TestCase):
    # a Jurassic-scale interval, far past timedelta's ~2.74-Myr ceiling
    JURASSIC = DateSpan(AstroDate(-201_400_000, 1, 1),
                        AstroDate(-143_100_000, 1, 1))

    def test_normal_width_is_plain_timedelta_byte_identical(self):
        span = DateSpan(AstroDate(2020, 6, 1), AstroDate(2020, 7, 1))
        self.assertIsInstance(span.width, timedelta)
        self.assertNotIsInstance(span.width, WideDuration)
        self.assertEqual(span.width, AstroDate(2020, 7, 1) - AstroDate(2020, 6, 1))
        self.assertEqual(span.width, timedelta(days=30))

    def test_boundary_just_under_timedelta_ceiling_is_timedelta(self):
        # ~2.7 Myr still fits a timedelta
        span = DateSpan(AstroDate(1, 1, 1), AstroDate(2_700_000, 1, 1))
        self.assertIsInstance(span.width, timedelta)

    def test_geological_width_is_wideduration_no_overflow(self):
        w = self.JURASSIC.width
        self.assertIsInstance(w, WideDuration)
        # 58.3 Myr, split into whole mean-years plus a sub-year remainder
        self.assertEqual(w.years, 58_300_000)
        self.assertLess(w.remainder, timedelta(days=366))

    def test_wideduration_orders_against_timedelta_and_peers(self):
        w = self.JURASSIC.width
        self.assertGreater(w, timedelta(days=999_999_999))
        self.assertGreater(w, timedelta(days=1))
        narrow = DateSpan(AstroDate(-201_400_000, 1, 1),
                          AstroDate(-201_300_000, 1, 1)).width  # 100 kyr
        self.assertLess(narrow, w)
        self.assertEqual(w, w)
        self.assertGreater(w.total_seconds(), 0)

    def test_no_method_overflows_on_geological_span(self):
        s = self.JURASSIC
        # width, resolution, contains, overlaps must all be overflow-free
        _ = s.width
        _ = s.resolution
        self.assertTrue(s.contains(AstroDate(-180_000_000, 1, 1)))
        self.assertFalse(s.contains(AstroDate(-100_000_000, 1, 1)))
        self.assertTrue(s.overlaps(s))
        other = DateSpan(AstroDate(-150_000_000, 1, 1),
                         AstroDate(-100_000_000, 1, 1))
        self.assertTrue(s.overlaps(other))
        self.assertFalse(s.overlaps(
            DateSpan(AstroDate(-50_000_000, 1, 1), AstroDate(-40_000_000, 1, 1))))

    def test_wideduration_is_hashable_and_frozen(self):
        w = self.JURASSIC.width
        self.assertEqual(hash(w), hash(w))
        with self.assertRaises(Exception):
            w.years = 0


# --------------------------------------------------------------------------
# Item 2: geological resolution tiers
# --------------------------------------------------------------------------
class TestGeologicalResolution(unittest.TestCase):
    def test_appended_members_have_new_values(self):
        # existing members untouched; new ones appended above MILLENNIUM
        self.assertEqual(R.MILLENNIUM.value, 26)
        self.assertEqual(R.EPOCH_GEOLOGICAL.value, 34)
        self.assertEqual(R.PERIOD_GEOLOGICAL.value, 35)
        self.assertEqual(R.ERA_GEOLOGICAL.value, 36)
        self.assertEqual(R.EON.value, 37)

    def _res(self, years):
        return DateSpan(AstroDate(0, 1, 1), AstroDate(years, 1, 1)).resolution

    def test_tier_thresholds(self):
        self.assertEqual(self._res(500), R.MILLENNIUM)        # < 10 kyr
        self.assertEqual(self._res(50_000), R.EPOCH_GEOLOGICAL)   # 10 kyr..10 Myr
        self.assertEqual(self._res(50_000_000), R.PERIOD_GEOLOGICAL)  # 10..100 Myr
        self.assertEqual(self._res(300_000_000), R.ERA_GEOLOGICAL)    # 100..500 Myr
        self.assertEqual(self._res(1_000_000_000), R.EON)     # > 500 Myr

    def test_jurassic_derives_period(self):
        s = DateSpan(AstroDate(-201_400_000, 1, 1), AstroDate(-143_100_000, 1, 1))
        self.assertEqual(s.resolution, R.PERIOD_GEOLOGICAL)

    def test_in_range_resolutions_unchanged(self):
        self.assertEqual(
            DateSpan(AstroDate(2020, 6, 1), AstroDate(2020, 7, 1)).resolution,
            R.MONTH)
        self.assertEqual(
            DateSpan(AstroDate(2020, 1, 1), AstroDate(2021, 1, 1)).resolution,
            R.YEAR)
        self.assertEqual(
            DateSpan(AstroDate(2000, 1, 1), AstroDate(2100, 1, 1)).resolution,
            R.CENTURY)


# --------------------------------------------------------------------------
# Item 3: basis lattice
# --------------------------------------------------------------------------
class TestBasisLattice(unittest.TestCase):
    BASES = ("exact", "tabulated", "reconstructed", "predicted")

    def test_default_basis_is_exact(self):
        self.assertEqual(DateSpan(AstroDate(2020), AstroDate(2021)).basis,
                         "exact")

    def test_invalid_basis_rejected(self):
        with self.assertRaises(ValueError):
            DateSpan(AstroDate(2020), AstroDate(2021), basis="guessed")

    def test_worst_of_total_order(self):
        self.assertEqual(combine_basis("exact", "tabulated"), "tabulated")
        self.assertEqual(combine_basis("exact", "reconstructed"), "reconstructed")
        self.assertEqual(combine_basis("tabulated", "predicted"), "predicted")
        self.assertEqual(combine_basis("exact", "exact"), "exact")

    def test_identity_element_is_exact(self):
        self.assertEqual(combine_basis(), "exact")
        for b in self.BASES:
            self.assertEqual(combine_basis("exact", b), b)
            self.assertEqual(combine_basis(b), b)

    def test_idempotent(self):
        for b in self.BASES:
            self.assertEqual(combine_basis(b, b), b)

    def test_commutative(self):
        for a in self.BASES:
            for b in self.BASES:
                self.assertEqual(combine_basis(a, b), combine_basis(b, a))

    def test_associative(self):
        for a in self.BASES:
            for b in self.BASES:
                for c in self.BASES:
                    self.assertEqual(
                        combine_basis(combine_basis(a, b), c),
                        combine_basis(a, combine_basis(b, c)))

    def test_peer_tiebreak_is_reconstructed(self):
        # reconstructed and predicted are equal-rank peers; a mix collapses to
        # the documented canonical representative
        self.assertEqual(combine_basis("reconstructed", "predicted"),
                         "reconstructed")
        self.assertEqual(combine_basis("predicted", "reconstructed"),
                         "reconstructed")

    def test_unknown_basis_rejected(self):
        with self.assertRaises(ValueError):
            combine_basis("exact", "nonsense")

    def test_calendar_basis_attribute(self):
        # plumbing only: default exact, tabular Hijri declares tabulated
        self.assertEqual(CALENDARS["julian"].basis, "exact")
        self.assertEqual(CALENDARS["hebrew"].basis, "exact")
        self.assertEqual(CALENDARS["islamic_civil"].basis, "exact")
        self.assertEqual(CALENDARS["umm_al_qura"].basis, "tabulated")


# --------------------------------------------------------------------------
# Item 4: scaled Before-Present units
# --------------------------------------------------------------------------
class TestResolveBP(unittest.TestCase):
    BP_EPOCH = 1950

    def test_kpg_boundary_start_year_from_first_principles(self):
        # 66 Ma before AD 1950 -> astronomical year 1950 - 66_000_000
        span = resolve_bp("66", "Ma")
        self.assertEqual(span.start.year, self.BP_EPOCH - 66_000_000)
        self.assertEqual(span.start.year, -65_998_050)

    @staticmethod
    def _width_years(w):
        """Width in whole years, whichever representation ``w`` uses (a 1-Ma
        or 100-ka width still fits a plain timedelta; only >~2.7 Myr widths
        become a WideDuration)."""
        if isinstance(w, WideDuration):
            return w.years
        return round(w.total_seconds() / (365.2425 * 86400))

    def test_width_reflects_significant_figures(self):
        # "66 Ma" -> 1 Ma wide; "66.0 Ma" -> 100 ka; "66.043 Ma" -> 1 ka
        self.assertEqual(self._width_years(resolve_bp("66", "Ma").width),
                         1_000_000)
        self.assertEqual(self._width_years(resolve_bp("66.0", "Ma").width),
                         100_000)
        self.assertEqual(self._width_years(resolve_bp("66.043", "Ma").width),
                         1_000)

    def test_string_vs_float_precision(self):
        # the string form carries precision a float has already lost
        self.assertEqual(self._width_years(resolve_bp("66.0", "Ma").width),
                         100_000)
        self.assertEqual(self._width_years(resolve_bp(Decimal("66.00"), "Ma").width),
                         10_000)

    def test_units(self):
        self.assertEqual(resolve_bp("12", "ka").start.year,
                         self.BP_EPOCH - 12_000)
        self.assertEqual(resolve_bp("1", "Ga").start.year,
                         self.BP_EPOCH - 1_000_000_000)
        self.assertEqual(resolve_bp("100", "a").start.year, self.BP_EPOCH - 100)

    def test_span_is_half_open_and_tiles(self):
        # consecutive Ma bins abut: "67 Ma" ends where "66 Ma" begins
        self.assertEqual(resolve_bp("67", "Ma").end.year,
                         resolve_bp("66", "Ma").start.year)
        # the stated value is the inclusive start
        span = resolve_bp("66", "Ma")
        self.assertTrue(span.contains(span.start))
        self.assertLess(span.start, span.end)

    def test_round_trip_years_before_present(self):
        for v, u, yr in [("66", "Ma", 66_000_000), ("125", "ka", 125_000),
                         ("4", "Ga", 4_000_000_000)]:
            span = resolve_bp(v, u)
            self.assertEqual(self.BP_EPOCH - span.start.year, yr)

    def test_basis_is_reconstructed(self):
        self.assertEqual(resolve_bp("66", "Ma").basis, "reconstructed")

    def test_resolution_derives_from_precision(self):
        # a 1-Ma-wide span is epoch-scale; a 1-Ga-wide span is an eon
        self.assertEqual(resolve_bp("66", "Ma").resolution, R.EPOCH_GEOLOGICAL)
        self.assertEqual(resolve_bp("5", "Ga").resolution, R.EON)

    def test_unknown_unit_rejected(self):
        with self.assertRaises(ValueError):
            resolve_bp("66", "My")

    def test_accepts_int_and_float_and_decimal(self):
        self.assertEqual(resolve_bp(66, "Ma").start.year, -65_998_050)
        self.assertEqual(resolve_bp(66.0, "Ma").start.year, -65_998_050)
        self.assertEqual(resolve_bp(Decimal("66"), "Ma").start.year, -65_998_050)


# --------------------------------------------------------------------------
# Deep-time arithmetic on AstroDate: subtraction overflow -> WideDuration,
# and AstroDate +/- WideDuration advancing an unbounded date.
# --------------------------------------------------------------------------
class TestAstroDateDeepTimeArithmetic(unittest.TestCase):
    A = AstroDate(-65_000_000, 1, 1)
    B = AstroDate(-45_000_000, 1, 1)

    def test_subtract_deep_time_dates_returns_wideduration(self):
        w = self.B - self.A
        self.assertIsInstance(w, WideDuration)
        # exact microsecond magnitude, independent of the mean-year split
        self.assertEqual(w._total_us(),
                         self.B._total_us() - self.A._total_us())

    def test_subtract_reversed_is_negative_wideduration(self):
        w = self.A - self.B
        self.assertIsInstance(w, WideDuration)
        self.assertEqual(w._total_us(),
                         self.A._total_us() - self.B._total_us())
        self.assertLess(w, timedelta(0))

    def test_add_wideduration_round_trips(self):
        w = self.B - self.A
        self.assertEqual(self.A + w, self.B)
        self.assertEqual(w + self.A, self.B)  # __radd__

    def test_subtract_wideduration_round_trips(self):
        w = self.B - self.A
        self.assertEqual(self.B - w, self.A)

    def test_add_wideduration_lands_far_outside_datetime_range(self):
        w = self.B - self.A
        result = AstroDate(-45_000_000, 1, 1) - w
        self.assertEqual(result.year, -65_000_000)
        self.assertFalse(result.in_datetime_range)

    def test_wideduration_arithmetic_preserves_tzinfo(self):
        from datetime import timezone
        aware = AstroDate(-65_000_000, 1, 1, tzinfo=timezone.utc)
        w = self.B - self.A
        self.assertEqual((aware + w).tzinfo, timezone.utc)
        self.assertEqual((aware - w).tzinfo, timezone.utc)

    # -- in-range behaviour must stay byte-identical -----------------------
    def test_in_range_subtraction_still_timedelta(self):
        d = AstroDate(2020, 1, 1) - AstroDate(2019, 1, 1)
        self.assertIsInstance(d, timedelta)
        self.assertNotIsInstance(d, WideDuration)
        self.assertEqual(d, timedelta(days=365))  # 2019 is not a leap year

    def test_in_range_timedelta_addition_unchanged(self):
        self.assertEqual(AstroDate(2020, 1, 1) + timedelta(days=1),
                         AstroDate(2020, 1, 2))
        self.assertEqual(AstroDate(2020, 1, 2) - timedelta(days=1),
                         AstroDate(2020, 1, 1))


if __name__ == "__main__":
    unittest.main()
