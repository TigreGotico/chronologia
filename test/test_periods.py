"""Named-period registry: ICS chart, archaeological set, subdivision, IntCal20.

Gold values are the published ICS 2023/09 chart boundaries (Jurassic
201.4→143.1 Ma, Phanerozoic base 538.8 Ma, Holocene base 11.7 ka) and the
conventional archaeological chronologies; the arithmetic is asserted against
those, not against any library.
"""
import unittest
from datetime import timedelta

from chronologia import (AstroDate, DateSpan, DateTimeResolution as R,
                         WideDuration, AmbiguousPeriodError, ICS_CHART_VERSION,
                         INTCAL20_COARSE, NamedPeriod, PERIODS, calibrate_c14,
                         candidates, children, lookup, subdivide)

BP_EPOCH = 1950


def _ma(period):
    """(base_Ma, top_Ma) of a period's span on the Before-Present axis."""
    return ((BP_EPOCH - period.span.start.year) / 1e6,
            (BP_EPOCH - period.span.end.year) / 1e6)


# --------------------------------------------------------------------------
# Registry shape & lookup
# --------------------------------------------------------------------------
class TestRegistry(unittest.TestCase):
    def test_chart_version_embedded(self):
        self.assertEqual(ICS_CHART_VERSION, "2023/09")

    def test_entry_count_per_level(self):
        from collections import Counter
        ics = [p for p in PERIODS.values() if p.region is None]
        counts = Counter(p.level for p in ics)
        # the full ICS 2023/09 international chart
        self.assertEqual(counts["eon"], 3)
        self.assertEqual(counts["era"], 10)
        self.assertEqual(counts["period"], 22)
        self.assertEqual(counts["epoch"], 34)
        self.assertEqual(counts["age"], 101)
        self.assertEqual(sum(counts.values()), 170)

    def test_entries_are_frozen_namedperiods(self):
        j = lookup("jurassic")
        self.assertIsInstance(j, NamedPeriod)
        with self.assertRaises(Exception):
            j.name = "nope"

    def test_lookup_by_name_and_by_key(self):
        self.assertIs(lookup("Late Jurassic"), lookup("late_jurassic"))
        self.assertIs(lookup("late jurassic"), PERIODS["late_jurassic"])

    def test_lookup_unknown_raises_keyerror(self):
        with self.assertRaises(KeyError):
            lookup("Cambrian Explosion of Mammals")

    def test_all_spans_are_datespans_with_declared_basis(self):
        for p in PERIODS.values():
            self.assertIsInstance(p.span, DateSpan)
            self.assertIn(p.span.basis, ("tabulated", "reconstructed"))


# --------------------------------------------------------------------------
# Gold spans (ICS chart)
# --------------------------------------------------------------------------
class TestGoldSpans(unittest.TestCase):
    def test_jurassic_span(self):
        base, top = _ma(lookup("jurassic"))
        # base folds in the +/-0.2 Ma GSSP uncertainty -> 201.6; top 143.1
        self.assertAlmostEqual(base, 201.6, places=3)
        self.assertAlmostEqual(top, 143.1, places=3)

    def test_jurassic_derives_geological_period_resolution(self):
        self.assertEqual(lookup("jurassic").span.resolution,
                         R.PERIOD_GEOLOGICAL)

    def test_phanerozoic_base(self):
        base, _ = _ma(lookup("phanerozoic"))
        self.assertAlmostEqual(base, 539.0, places=3)  # 538.8 + 0.2 unc

    def test_holocene_starts_11700_yr_bp(self):
        h = lookup("holocene")
        self.assertEqual(BP_EPOCH - h.span.start.year, 11_700)

    def test_late_jurassic_is_a_chart_entry(self):
        lj = lookup("late jurassic")
        self.assertEqual(lj.level, "epoch")
        base, top = _ma(lj)
        self.assertAlmostEqual(base, 161.5, places=3)
        self.assertAlmostEqual(top, 143.1, places=3)

    def test_uncertainty_folded_outward_widens_span(self):
        # Triassic base 251.902 +/- 0.024 Ma -> start pushed OLDER by 0.024 Ma
        base, _ = _ma(lookup("triassic"))
        self.assertAlmostEqual(base, 251.926, places=3)

    def test_boundaries_without_published_unc_are_bare(self):
        # 143.1 Ma (base Cretaceous / top Jurassic) carries no chart +/-
        _, top = _ma(lookup("jurassic"))
        self.assertAlmostEqual(top, 143.1, places=6)


# --------------------------------------------------------------------------
# Width / WideDuration on geological entries
# --------------------------------------------------------------------------
class TestGeologicalWidth(unittest.TestCase):
    def test_jurassic_width_is_wideduration(self):
        w = lookup("jurassic").span.width
        self.assertIsInstance(w, WideDuration)
        # 201.6 - 143.1 = 58.5 Myr (base folded +0.2)
        self.assertAlmostEqual(w.years / 1e6, 58.5, places=1)

    def test_phanerozoic_width_exceeds_timedelta_ceiling(self):
        w = lookup("phanerozoic").span.width
        self.assertIsInstance(w, WideDuration)
        self.assertGreater(w, timedelta(days=999_999_999))

    def test_holocene_width_fits_plain_timedelta(self):
        w = lookup("holocene").span.width
        self.assertIsInstance(w, timedelta)


# --------------------------------------------------------------------------
# Hierarchy / parent walks
# --------------------------------------------------------------------------
class TestHierarchy(unittest.TestCase):
    def test_late_jurassic_parent_is_jurassic(self):
        self.assertEqual(lookup("late jurassic").parent, "jurassic")

    def test_jurassic_parent_is_mesozoic(self):
        self.assertEqual(lookup("jurassic").parent, "mesozoic")

    def test_eons_have_no_parent(self):
        self.assertIsNone(lookup("phanerozoic").parent)

    def test_parent_walk_to_root(self):
        chain = []
        cur = lookup("late jurassic")
        while cur is not None:
            chain.append(cur.key)
            cur = lookup(cur.parent) if cur.parent else None
        self.assertEqual(chain,
                         ["late_jurassic", "jurassic", "mesozoic", "phanerozoic"])

    def test_children_of_jurassic_are_its_epochs(self):
        kids = {p.key for p in children("jurassic")}
        self.assertEqual(kids,
                         {"early_jurassic", "middle_jurassic", "late_jurassic"})

    def test_every_non_eon_ics_entry_has_a_parent(self):
        for p in PERIODS.values():
            if p.region is None and p.level != "eon":
                self.assertIsNotNone(p.parent, f"{p.key} has no parent")
                self.assertIn(p.parent, PERIODS)


# --------------------------------------------------------------------------
# Region disambiguation (archaeological set)
# --------------------------------------------------------------------------
class TestRegionDisambiguation(unittest.TestCase):
    def test_candidates_lists_both_regions(self):
        regions = sorted(p.region for p in candidates("bronze age"))
        self.assertEqual(regions, ["GB", "MESO"])

    def test_bare_ambiguous_name_raises(self):
        with self.assertRaises(AmbiguousPeriodError):
            lookup("bronze age")
        with self.assertRaises(AmbiguousPeriodError):
            lookup("late bronze age")

    def test_region_resolves_to_distinct_spans(self):
        gb = lookup("late bronze age", region="GB")
        meso = lookup("late bronze age", region="MESO")
        self.assertNotEqual(gb.span, meso.span)
        # GB LBA 1150-800 BC; MESO LBA 1550-1200 BC (astronomical 1-Y)
        self.assertEqual((gb.span.start.year, gb.span.end.year), (-1149, -799))
        self.assertEqual((meso.span.start.year, meso.span.end.year),
                         (-1549, -1199))

    def test_region_lookup_unknown_raises(self):
        with self.assertRaises(KeyError):
            lookup("bronze age", region="ATLANTIS")

    def test_archaeo_basis_is_reconstructed(self):
        self.assertEqual(lookup("bronze age", region="GB").span.basis,
                         "reconstructed")

    def test_archaeo_parent_walk(self):
        lba = lookup("late bronze age", region="GB")
        self.assertEqual(lba.parent, "bronze_age_gb")
        self.assertEqual(lookup(lba.parent).name, "Bronze Age")

    def test_candidates_unknown_is_empty(self):
        self.assertEqual(candidates("space age"), [])


# --------------------------------------------------------------------------
# subdivide: precedence, thirds arithmetic, basis propagation
# --------------------------------------------------------------------------
class TestSubdivide(unittest.TestCase):
    def test_chart_defined_late_wins_over_arithmetic(self):
        j = lookup("jurassic")
        late = subdivide(j, "late")
        # equals the Late Jurassic entry, NOT the arithmetic last third
        self.assertEqual(late, lookup("late jurassic").span)
        arithmetic_third = _third(j.span, 2)
        self.assertNotEqual(late, arithmetic_third)

    def test_chart_defined_early_and_mid(self):
        j = lookup("jurassic")
        self.assertEqual(subdivide(j, "early"), lookup("early jurassic").span)
        self.assertEqual(subdivide(j, "mid"), lookup("middle jurassic").span)
        self.assertEqual(subdivide(j, "middle"), lookup("middle jurassic").span)

    def test_arithmetic_thirds_on_bare_span(self):
        span = DateSpan(AstroDate(2000, 1, 1), AstroDate(2030, 1, 1))
        early = subdivide(span, "early")
        mid = subdivide(span, "mid")
        late = subdivide(span, "late")
        self.assertEqual(early.start, span.start)
        self.assertEqual(late.end, span.end)
        # thirds tile with no gaps or overlaps
        self.assertEqual(early.end, mid.start)
        self.assertEqual(mid.end, late.start)
        self.assertEqual(early.start.year, 2000)
        # thirds of 30 years land near the decade marks (leap days shift the
        # microsecond split off an exact Jan 1)
        self.assertIn(early.end.year, (2009, 2010))
        self.assertIn(mid.end.year, (2019, 2020))

    def test_halves(self):
        span = DateSpan(AstroDate(2000, 1, 1), AstroDate(2020, 1, 1))
        first = subdivide(span, "first-half")
        second = subdivide(span, "second-half")
        self.assertEqual(first.start, span.start)
        self.assertEqual(first.end, second.start)
        self.assertEqual(second.end, span.end)
        self.assertIn(first.end.year, (2009, 2010))

    def test_authority_subdivision_wins_for_archaeo_too(self):
        # "Late Bronze Age" MESO is itself a registered child of Bronze Age
        # MESO, so it wins over an arithmetic third (precedence is general)
        meso = lookup("bronze age", region="MESO")
        self.assertEqual(subdivide(meso, "late"),
                         lookup("late bronze age", region="MESO").span)
        self.assertNotEqual(subdivide(meso, "late"), _third(meso.span, 2))

    def test_subdivide_without_chart_entry_falls_back_to_arithmetic(self):
        # a period with no early/mid/late named children -> arithmetic thirds
        neo = lookup("neolithic", region="GB")
        self.assertEqual(children(neo.key), [])
        self.assertEqual(subdivide(neo, "late"), _third(neo.span, 2))

    def test_basis_propagates_via_combine_basis(self):
        # reconstructed span stays reconstructed through arithmetic subdivision
        meso = lookup("bronze age", region="MESO")
        self.assertEqual(subdivide(meso, "early").basis, "reconstructed")
        # chart-defined: tabulated parent ∘ tabulated child -> tabulated
        self.assertEqual(subdivide(lookup("jurassic"), "late").basis,
                         "tabulated")

    def test_subdivide_on_geological_span_no_overflow(self):
        # thirds of a Phanerozoic-wide span must not OverflowError
        span = lookup("phanerozoic").span
        early = subdivide(span, "early")
        self.assertIsInstance(early, DateSpan)
        self.assertEqual(early.start, span.start)

    def test_unknown_part_rejected(self):
        with self.assertRaises(ValueError):
            subdivide(lookup("jurassic"), "penultimate")

    def test_bad_target_type_rejected(self):
        with self.assertRaises(TypeError):
            subdivide("jurassic", "late")


def _third(span, idx):
    start_us = span.start._total_us()
    total = span._delta_us
    a = span.start if idx == 0 else AstroDate._from_total_us(
        start_us + total * idx // 3)
    b = span.end if idx == 2 else AstroDate._from_total_us(
        start_us + total * (idx + 1) // 3)
    return DateSpan(a, b, basis=span.basis)


# --------------------------------------------------------------------------
# IntCal20 radiocarbon calibration (coarse)
# --------------------------------------------------------------------------
class TestCalibrate(unittest.TestCase):
    def test_curve_loaded_coarse(self):
        self.assertGreater(len(INTCAL20_COARSE), 500)
        # 100-yr grid
        self.assertEqual(INTCAL20_COARSE[0][0] % 100, 0)

    def test_calibrate_returns_reconstructed_span(self):
        span = calibrate_c14(3000)
        self.assertIsInstance(span, DateSpan)
        self.assertEqual(span.basis, "reconstructed")

    def test_calibrate_places_on_cal_bp_axis(self):
        # ~3000 14C BP calibrates to roughly ~3200 cal BP; assert it lands in a
        # sane calendar window (demonstrative, not OxCal-exact)
        span = calibrate_c14(3000)
        cal_start = BP_EPOCH - span.start.year   # older, larger cal BP
        cal_end = BP_EPOCH - span.end.year
        self.assertGreater(cal_start, cal_end)   # start is older
        self.assertTrue(2800 <= cal_start <= 3600)

    def test_calibrate_modern_is_near_present(self):
        span = calibrate_c14(200)
        self.assertLess(BP_EPOCH - span.start.year, 1000)

    def test_out_of_range_rejected(self):
        with self.assertRaises(ValueError):
            calibrate_c14(200_000)
        with self.assertRaises(ValueError):
            calibrate_c14(-500)

    def test_span_has_positive_width(self):
        span = calibrate_c14(5000)
        self.assertLess(span.start, span.end)


if __name__ == "__main__":
    unittest.main()
