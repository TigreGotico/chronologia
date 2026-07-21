"""Tests for mean-lunation moon-phase arithmetic.

Gold new/full moon instants are the US Naval Observatory's published 2024
phase table (``papers/standards/moon_phases_usno_2024.json``, USNO
Astronomical Applications API, downloaded 2026-07-21) -- real published
astronomical events, cross-checked against this module's mean-arithmetic
model within :data:`~chronologia.moon.MOON_PHASE_ACCURACY`. The Meeus
Lunation Number epoch and the Brown Lunation Number epoch/offset trace to
Wikipedia's "Lunation Number" article (``moon_lunation_number_wikipedia.html``,
quoted verbatim in ``chronologia/moon.py``).
"""
import unittest
from datetime import datetime, timedelta

from chronologia.astrodate import AstroDate, DateSpan
from chronologia.moon import (EPOCH_NEW_MOON, MEAN_SYNODIC_MONTH_DAYS,
                              MOON_PHASE_ACCURACY, lunation_number, moon_phase,
                              next_phase, previous_phase)

# Gold: USNO 2024 API (moon_phases_usno_2024.json), all times UTC.
USNO_NEW_MOONS_2024 = [
    datetime(2024, 1, 11, 11, 57),
    datetime(2024, 2, 9, 22, 59),
    datetime(2024, 3, 10, 9, 0),
]
USNO_FULL_MOONS_2024 = [
    datetime(2024, 1, 25, 17, 54),
    datetime(2024, 2, 24, 12, 30),
    datetime(2024, 3, 25, 7, 0),
]


class TestMoonPhaseGold(unittest.TestCase):
    """Mean-arithmetic phase fraction vs published new/full moon instants."""

    def test_gold_new_moons_are_phase_zero(self):
        for inst in USNO_NEW_MOONS_2024:
            frac = moon_phase(inst)
            # phase 0 wraps at 1.0; a true new moon is within the accuracy
            # bound of the mean instant, i.e. a small fraction of a lunation.
            wrapped = min(frac, 1.0 - frac)
            hours = wrapped * MEAN_SYNODIC_MONTH_DAYS * 24
            self.assertLessEqual(
                hours, MOON_PHASE_ACCURACY.total_seconds() / 3600,
                f"{inst} not within accuracy of mean new moon (phase={frac})")

    def test_gold_full_moons_are_phase_half(self):
        for inst in USNO_FULL_MOONS_2024:
            frac = moon_phase(inst)
            hours = abs(frac - 0.5) * MEAN_SYNODIC_MONTH_DAYS * 24
            self.assertLessEqual(
                hours, MOON_PHASE_ACCURACY.total_seconds() / 3600,
                f"{inst} not within accuracy of mean full moon (phase={frac})")

    def test_epoch_new_moon_is_phase_zero_exactly(self):
        self.assertEqual(moon_phase(EPOCH_NEW_MOON), 0.0)

    def test_next_phase_new_moon_gold(self):
        for inst in USNO_NEW_MOONS_2024:
            span = next_phase(inst - timedelta(days=25), "new")
            self.assertTrue(span.start <= AstroDate.from_datetime(inst) < span.end,
                            f"USNO new moon {inst} outside predicted span {span}")

    def test_next_phase_full_moon_gold(self):
        for inst in USNO_FULL_MOONS_2024:
            span = next_phase(inst - timedelta(days=25), "full")
            self.assertTrue(span.start <= AstroDate.from_datetime(inst) < span.end,
                            f"USNO full moon {inst} outside predicted span {span}")

    def test_previous_phase_new_moon_gold(self):
        for inst in USNO_NEW_MOONS_2024:
            span = previous_phase(inst + timedelta(days=25), "new")
            self.assertTrue(span.start <= AstroDate.from_datetime(inst) < span.end,
                            f"USNO new moon {inst} outside reconstructed span {span}")


class TestMoonPhaseMonotonicity(unittest.TestCase):
    def test_phase_increases_across_a_lunation(self):
        start = EPOCH_NEW_MOON
        samples = [moon_phase(start + timedelta(days=d))
                   for d in range(0, 29)]
        for a, b in zip(samples, samples[1:]):
            self.assertLess(a, b)

    def test_phase_wraps_at_next_new_moon(self):
        just_before = moon_phase(EPOCH_NEW_MOON + timedelta(
            days=MEAN_SYNODIC_MONTH_DAYS - 0.01))
        just_after = moon_phase(EPOCH_NEW_MOON + timedelta(
            days=MEAN_SYNODIC_MONTH_DAYS + 0.01))
        self.assertGreater(just_before, 0.99)
        self.assertLess(just_after, 0.01)

    def test_quarters_ordered_within_a_lunation(self):
        new = moon_phase(EPOCH_NEW_MOON + timedelta(hours=1))
        fq = moon_phase(EPOCH_NEW_MOON + timedelta(
            days=MEAN_SYNODIC_MONTH_DAYS * 0.25))
        full = moon_phase(EPOCH_NEW_MOON + timedelta(
            days=MEAN_SYNODIC_MONTH_DAYS * 0.5))
        lq = moon_phase(EPOCH_NEW_MOON + timedelta(
            days=MEAN_SYNODIC_MONTH_DAYS * 0.75))
        self.assertTrue(new < fq < full < lq)


class TestNextPreviousPhaseInverse(unittest.TestCase):
    def test_next_then_previous_from_after_recovers_same_span(self):
        anchor = datetime(2024, 6, 15)
        fwd = next_phase(anchor, "full")
        back = previous_phase(fwd.end + timedelta(hours=1), "full")
        self.assertEqual(fwd.start, back.start)
        self.assertEqual(fwd.end, back.end)

    def test_previous_then_next_from_before_recovers_same_span(self):
        anchor = datetime(2024, 6, 15)
        back = previous_phase(anchor, "new")
        fwd = next_phase(back.start - timedelta(hours=1), "new")
        self.assertEqual(back.start, fwd.start)
        self.assertEqual(back.end, fwd.end)

    def test_next_phase_is_strictly_after_anchor(self):
        anchor = AstroDate.from_datetime(datetime(2024, 6, 15))
        for phase in ("new", "first_quarter", "full", "last_quarter"):
            span = next_phase(anchor, phase)
            self.assertGreater(span.start, anchor)

    def test_previous_phase_is_strictly_before_anchor(self):
        anchor = AstroDate.from_datetime(datetime(2024, 6, 15))
        for phase in ("new", "first_quarter", "full", "last_quarter"):
            span = previous_phase(anchor, phase)
            self.assertLess(span.end, anchor)


class TestLunationNumber(unittest.TestCase):
    def test_epoch_lunation_is_953_brown(self):
        # Meeus LN 0 (this module's epoch) == BLN 953 (Wikipedia,
        # "Lunation Number": BLN = LN + 953).
        self.assertEqual(lunation_number(EPOCH_NEW_MOON), 953)

    def test_lunation_number_increments_each_synodic_month(self):
        n0 = lunation_number(EPOCH_NEW_MOON)
        n1 = lunation_number(EPOCH_NEW_MOON + timedelta(
            days=MEAN_SYNODIC_MONTH_DAYS + 1))
        self.assertEqual(n1, n0 + 1)

    def test_lunation_number_stable_within_a_lunation(self):
        n_start = lunation_number(EPOCH_NEW_MOON + timedelta(hours=1))
        n_mid = lunation_number(EPOCH_NEW_MOON + timedelta(days=14))
        self.assertEqual(n_start, n_mid)

    def test_lunation_number_far_future(self):
        # 100 years and ~1237 lunations ahead of the epoch; must not raise.
        far = EPOCH_NEW_MOON + timedelta(days=365.2425 * 100)
        self.assertGreater(lunation_number(far), lunation_number(EPOCH_NEW_MOON))


class TestSpanWidthAndBasis(unittest.TestCase):
    def test_span_width_is_twice_accuracy(self):
        span = next_phase(datetime(2024, 1, 1), "new")
        self.assertEqual(span.width, 2 * MOON_PHASE_ACCURACY)

    def test_future_phase_is_predicted(self):
        span = next_phase(datetime(2024, 1, 1), "new")
        self.assertEqual(span.basis, "predicted")

    def test_past_phase_is_reconstructed(self):
        span = previous_phase(datetime(2024, 6, 1), "full")
        self.assertEqual(span.basis, "reconstructed")

    def test_result_is_a_dataspan(self):
        self.assertIsInstance(next_phase(datetime(2024, 1, 1), "new"),
                              DateSpan)


class TestFarPastAndFuture(unittest.TestCase):
    """Mean arithmetic is just multiplication -- must work far outside
    ``datetime``'s year range (see the module docstring's no-ephemeris,
    AstroDate-native design)."""

    def test_far_past_year(self):
        far_past = AstroDate(-3760, 9, 7)  # long before datetime's range
        frac = moon_phase(far_past)
        self.assertTrue(0.0 <= frac < 1.0)

    def test_far_future_year(self):
        far_future = AstroDate(12000, 1, 1)
        frac = moon_phase(far_future)
        self.assertTrue(0.0 <= frac < 1.0)

    def test_next_phase_far_future_anchor(self):
        span = next_phase(AstroDate(12000, 1, 1), "new")
        self.assertGreater(span.start.year, 11999)

    def test_previous_phase_far_past_anchor(self):
        span = previous_phase(AstroDate(-3760, 9, 7), "full")
        self.assertLessEqual(span.end.year, -3759)

    def test_lunation_number_far_past(self):
        n = lunation_number(AstroDate(-3760, 9, 7))
        self.assertIsInstance(n, int)


class TestAdversarial(unittest.TestCase):
    def test_unknown_phase_name_raises(self):
        with self.assertRaises(ValueError):
            next_phase(datetime(2024, 1, 1), "waning_gibbous")

    def test_unknown_phase_name_raises_for_previous(self):
        with self.assertRaises(ValueError):
            previous_phase(datetime(2024, 1, 1), "banana")

    def test_empty_phase_name_raises(self):
        with self.assertRaises(ValueError):
            next_phase(datetime(2024, 1, 1), "")

    def test_case_sensitive_phase_name_raises(self):
        # Names are lowercase snake_case only -- "New" is not "new".
        with self.assertRaises(ValueError):
            next_phase(datetime(2024, 1, 1), "New")

    def test_moon_phase_rejects_bad_type(self):
        with self.assertRaises(TypeError):
            moon_phase("2024-01-01")


if __name__ == "__main__":
    unittest.main()
