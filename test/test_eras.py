"""Tests for chronologia.eras — AstroDate, year ranges, era resolution.

Reference values are cited to the canonical sources saved under
``~/AgentWorkspaces/papers/calendars/`` (see the module docstrings in
eras.py); nothing here is pinned to another library's output.
"""
import logging
import unittest
from datetime import date, datetime, timezone

from chronologia import DateTimeResolution
from chronologia import eras as eras_mod
from chronologia.eras import (AstroDate, ERAS, ERA_ALIASES, HEAT_DEATH_YEAR,
                                   astro_year_range, is_leap_year,
                                   julian_day_to_date, resolve_era)


class TestAstroDateBasics(unittest.TestCase):
    def test_bc_mapping(self):
        # astronomical numbering: X BC = 1 - X
        self.assertEqual(AstroDate(0).bc_year, 1)
        self.assertEqual(AstroDate(-4712).bc_year, 4713)
        self.assertTrue(AstroDate(0).is_bc)
        self.assertFalse(AstroDate(1).is_bc)
        with self.assertRaises(ValueError):
            AstroDate(1).bc_year

    def test_date_interop(self):
        self.assertEqual(AstroDate(2020, 6, 15).date(), date(2020, 6, 15))
        self.assertEqual(AstroDate(2020).date(), date(2020, 1, 1))
        self.assertIsNone(AstroDate(-50).date())
        self.assertIsNone(AstroDate(10000).date())
        self.assertTrue(AstroDate(9999, 12, 31).in_datetime_range)
        self.assertFalse(AstroDate(0).in_datetime_range)
        d = AstroDate.from_datetime(datetime(1999, 12, 31, 23, 59))
        self.assertEqual((d.year, d.month, d.day), (1999, 12, 31))
        self.assertEqual((d.hour, d.minute), (23, 59))

    def test_validation(self):
        with self.assertRaises(ValueError):
            AstroDate(2020, 13)
        with self.assertRaises(ValueError):
            AstroDate(2020, 0)
        with self.assertRaises(ValueError):
            AstroDate(2020, None, 5)      # None month rejected
        with self.assertRaises(ValueError):
            AstroDate(2021, 2, 29)        # not a leap year
        AstroDate(2020, 2, 29)            # leap year: fine

    def test_leap_rule_is_proleptic_gregorian_for_bc(self):
        # proleptic Gregorian: year 0 (1 BC) and -400 are leap;
        # -100 (101 BC) is not (century rule applies before CE too)
        self.assertTrue(is_leap_year(0))
        self.assertTrue(is_leap_year(-400))
        self.assertFalse(is_leap_year(-100))
        AstroDate(0, 2, 29)
        with self.assertRaises(ValueError):
            AstroDate(-100, 2, 29)

    def test_str_iso8601_expanded(self):
        # str delegates to isoformat, which always carries the time part
        # (datetime parity); years outside 0..9999 carry a sign and >=6 digits
        self.assertEqual(str(AstroDate(2020, 6, 15)), "2020-06-15T00:00:00")
        self.assertEqual(str(AstroDate(-4712, 1, 1)), "-004712-01-01T00:00:00")
        self.assertEqual(str(AstroDate(12000)), "+012000-01-01T00:00:00")
        self.assertEqual(str(AstroDate(50, 3)), "0050-03-01T00:00:00")


class TestAstroDateOrdering(unittest.TestCase):
    def test_orders_against_astrodate_and_date(self):
        self.assertLess(AstroDate(-3000), AstroDate(-2999))
        self.assertLess(AstroDate(-1), date(1, 1, 1))
        self.assertGreater(AstroDate(12000), date(9999, 12, 31))
        self.assertLess(AstroDate(2020, 5), date(2020, 6, 1))
        self.assertLessEqual(AstroDate(2020, 6, 1), date(2020, 6, 1))
        self.assertGreaterEqual(date(2020, 6, 2), AstroDate(2020, 6, 1).date())

    def test_eq_and_hash_interoperate_with_date(self):
        # cross-type == holds for equal instants; hashing is consistent with
        # datetime for in-range values so dict/set use is safe
        self.assertEqual(AstroDate(2020, 1, 1), AstroDate(2020, 1, 1))
        self.assertEqual(AstroDate(2020, 1, 1), date(2020, 1, 1))
        self.assertEqual(AstroDate(2020, 1, 1), datetime(2020, 1, 1))
        self.assertEqual(hash(AstroDate(2020, 1, 1)),
                         hash(datetime(2020, 1, 1)))
        self.assertEqual(len({AstroDate(0), AstroDate(0)}), 1)

    def test_unrelated_types_raise(self):
        with self.assertRaises(TypeError):
            AstroDate(0) < "0"


class TestAstroYearRange(unittest.TestCase):
    def test_ad_buckets_match_ranges_module_convention(self):
        start, end = astro_year_range(1984, DateTimeResolution.DECADE)
        self.assertEqual((start.year, end.year), (1980, 1989))
        start, end = astro_year_range(2026, DateTimeResolution.CENTURY)
        self.assertEqual((start.year, end.year), (2000, 2099))
        start, end = astro_year_range(2026, DateTimeResolution.MILLENNIUM)
        self.assertEqual((start.year, end.year), (2000, 2999))

    def test_bc_buckets_floor_correctly(self):
        # century containing 2999 BC (astronomical -2998) is -3000..-2901
        start, end = astro_year_range(-2998, DateTimeResolution.CENTURY)
        self.assertEqual((start.year, end.year), (-3000, -2901))
        start, end = astro_year_range(-1, DateTimeResolution.DECADE)
        self.assertEqual((start.year, end.year), (-10, -1))
        start, end = astro_year_range(0, DateTimeResolution.MILLENNIUM)
        self.assertEqual((start.year, end.year), (0, 999))

    def test_unsupported_resolution(self):
        with self.assertRaises(ValueError):
            astro_year_range(2020, DateTimeResolution.MONTH)


class TestJulianDay(unittest.TestCase):
    def test_epoch(self):
        # JD 0 begins 1 January 4713 BC proleptic Julian = 24 November
        # 4714 BC proleptic Gregorian = astronomical -4713-11-24
        # (USNO, papers/calendars/usno_julian_date.html)
        d = julian_day_to_date(0)
        self.assertIsInstance(d, AstroDate)
        self.assertEqual((d.year, d.month, d.day), (-4713, 11, 24))

    def test_known_modern_values(self):
        # 2000-01-01 begins JD 2451545 (the J2000.0 day); unix epoch is
        # JD 2440588 (both derivable from the USNO conversion rules)
        self.assertEqual(julian_day_to_date(2451545), date(2000, 1, 1))
        self.assertEqual(julian_day_to_date(2440588), date(1970, 1, 1))

    def test_returns_plain_date_in_range(self):
        self.assertIsInstance(julian_day_to_date(2451545), date)
        self.assertNotIsInstance(julian_day_to_date(2451545), AstroDate)

    def test_consecutive_days_are_consecutive(self):
        for jd in (-10, 0, 1721424, 2451544):
            a, b = (julian_day_to_date(j) for j in (jd, jd + 1))
            self.assertLess(AstroDate(a.year, a.month, a.day),
                            AstroDate(b.year, b.month, b.day))
            if isinstance(a, date) and isinstance(b, date):
                self.assertEqual((b - a).days, 1)


class TestResolveEra(unittest.TestCase):
    def test_before_christ(self):
        d = resolve_era("before_christ", 3000)
        self.assertEqual(d, AstroDate(-2999, 1, 1))
        # 1 BC = astronomical 0; still out of datetime range
        self.assertEqual(resolve_era("before_christ", 1), AstroDate(0))

    def test_common_era_in_range_returns_plain_date(self):
        d = resolve_era("common_era", 2026)
        self.assertEqual(d, date(2026, 1, 1))
        self.assertNotIsInstance(d, AstroDate)

    def test_before_present(self):
        # present = AD 1950 (Stuiver & Polach 1977)
        self.assertEqual(resolve_era("before_present", 100), date(1850, 1, 1))
        self.assertEqual(resolve_era("before_present", 10000),
                         AstroDate(-8050))

    def test_unix_seconds(self):
        d = resolve_era("unix", 0)
        self.assertEqual(d, datetime(1970, 1, 1, tzinfo=timezone.utc))
        self.assertEqual(resolve_era("unix", 1000000000),
                         datetime(2001, 9, 9, 1, 46, 40,
                                  tzinfo=timezone.utc))

    def test_holocene(self):
        # HE 1 = 10000 BC = astronomical -9999, so HE 12025 = CE 2025
        self.assertEqual(resolve_era("holocene", 12025), date(2025, 1, 1))
        self.assertEqual(resolve_era("holocene", 1), AstroDate(-9999))

    def test_anno_mundi(self):
        # Anno Mundi is the Hebrew calendar's own numbering: AM N resolves
        # EXACTLY to 1 Tishri of Hebrew year N (Rosh HaShanah), via calendars
        self.assertEqual(resolve_era("anno_mundi", 5786), date(2025, 9, 23))
        self.assertEqual(resolve_era("anno_mundi", 1), AstroDate(-3760, 9, 7))

    def test_buddhist(self):
        # BE = CE + 543 (Thai 1941 act): BE 2569 = CE 2026
        self.assertEqual(resolve_era("buddhist", 2569), date(2026, 1, 1))

    def test_julian_day_era(self):
        d = resolve_era("julian_day", 0)
        self.assertEqual((d.year, d.month, d.day), (-4713, 11, 24))
        self.assertEqual(resolve_era("julian_day", 2451545), date(2000, 1, 1))

    def test_deep_future_never_overflows(self):
        self.assertEqual(resolve_era("common_era", 100000), AstroDate(100000))
        self.assertEqual(resolve_era("before_present", -1000000),
                         AstroDate(1001950))

    def test_unknown_era_raises_keyerror(self):
        with self.assertRaises(KeyError):
            resolve_era("jurassic", 1)

    def test_era_epochs_registry_consistency(self):
        for key, era in ERAS.items():
            self.assertEqual(key, era.key)


#: One gold "year-1 (or day-1) epoch" per registered era, each value taken from
#: the citation in its ``eras.py`` comment.  Calendar-backed eras resolve
#: EXACTLY through calendars.py; offset eras land on 1 January proleptically;
#: day-count eras give their day-1 civil date.  Keyed by era key -> expected
#: ``resolve_era(key, 1)`` result.
GOLD_ERA_EPOCHS = {
    # already-existing eras (regression anchors)
    "common_era": date(1, 1, 1),
    "before_christ": AstroDate(0),
    "before_present": AstroDate(1949),
    "holocene": AstroDate(-9999),
    "anno_mundi": AstroDate(-3760, 9, 7),
    "buddhist": AstroDate(-542),
    "ab_urbe_condita": AstroDate(-752),
    # calendar-backed additions (exact, proleptic Gregorian)
    "armenian": AstroDate(552, 7, 13),
    "diocletian": AstroDate(284, 8, 29),
    "amete_mihret": AstroDate(8, 8, 27),
    "hijri": AstroDate(622, 7, 19),
    "solar_hijri": AstroDate(622, 3, 21),
    "nabonassar": AstroDate(-746, 2, 18),
    # day-count additions (day 1)
    "rata_die": date(1, 1, 1),
    "lilian": date(1582, 10, 15),
    "julian_day": AstroDate(-4713, 11, 25),  # JD 1 = day after JD 0
    # year-count offsets — Gregorian/tropical-year-aligned, at the era's TRUE
    # civil new-year (month, day), NOT a lazy 1 January
    "julian_period": AstroDate(-4712, 1, 1),
    "assyrian": AstroDate(-4749, 4, 1),          # Kha b-Nisan, 1 April
    "anno_lucis": AstroDate(-3999, 1, 1),
    "spanish_era": AstroDate(-37, 1, 1),
    "saka": date(78, 3, 22),                     # Chaitra 1
    "discordian": AstroDate(-1165, 1, 1),
    "positivist": date(1789, 1, 1),
    "rattanakosin": date(1782, 4, 6),            # founding of Bangkok
    "era_fascista": date(1922, 10, 28),          # March on Rome
    "minguo": date(1912, 1, 1),
    "juche": date(1912, 1, 1),
    "after_dianetics": date(1950, 1, 1),
}


class TestEraGoldEpochs(unittest.TestCase):
    def test_every_era_has_a_gold_epoch(self):
        # parametrized-over-the-registry: a newly added era cannot skip a gold
        # assertion.  ``unix`` is second-counted (tested separately), so it is
        # the one deliberate exemption.
        missing = set(ERAS) - set(GOLD_ERA_EPOCHS) - {"unix",
                                                       "byzantine_am",
                                                       "french_republican",
                                                       "bahai", "olympiad"}
        self.assertEqual(missing, set(),
                         f"eras with no gold epoch: {sorted(missing)}")

    def test_gold_epochs_resolve(self):
        for key, expected in GOLD_ERA_EPOCHS.items():
            with self.subTest(era=key):
                self.assertEqual(resolve_era(key, 1), expected)

    def test_calendar_backed_current_year_samples(self):
        # a second point each for the calendar-backed additions, to guard the
        # offset as well as the epoch (values via calendars.py)
        self.assertEqual(resolve_era("hijri", 1447), date(2025, 6, 27))
        self.assertEqual(resolve_era("solar_hijri", 1404), date(2025, 3, 20))

    def test_rata_die_matches_gregorian_ordinal(self):
        # R.D. n == proleptic Gregorian ordinal n (Reingold & Dershowitz)
        self.assertEqual(resolve_era("rata_die", date(2025, 7, 25).toordinal()),
                         date(2025, 7, 25))

    def test_lilian_reform_day(self):
        self.assertEqual(resolve_era("lilian", 1), date(1582, 10, 15))
        self.assertEqual(resolve_era("lilian", 2), date(1582, 10, 16))

    def test_offset_eras_use_true_civil_new_year(self):
        # not a lazy 1 January: each begins at its cited civil new-year and the
        # next era year is exactly one Gregorian year later (fixed offset)
        self.assertEqual(resolve_era("saka", 1949), date(2026, 3, 22))
        self.assertEqual(resolve_era("assyrian", 6776), date(2026, 4, 1))
        self.assertEqual(resolve_era("era_fascista", 104), date(2025, 10, 28))
        self.assertEqual(resolve_era("rattanakosin", 245), date(2026, 4, 6))

    def test_drifting_lunisolar_eras_are_not_registered(self):
        # applied consistently with Yazdegerd: a lunisolar/sidereal era whose
        # year drifts against the Gregorian year is NOT a fixed-offset era
        for key in ("vikrama", "kali_yuga", "seleucid", "bengali_san",
                    "burmese", "kollam", "nepal_sambat", "yazdegerd"):
            with self.subTest(era=key):
                self.assertNotIn(key, ERAS)
                with self.assertRaises(KeyError):
                    resolve_era(key, 1)


class TestEraAliases(unittest.TestCase):
    def test_aliases_resolve_to_common_era(self):
        for alias in ERA_ALIASES:
            with self.subTest(alias=alias):
                self.assertEqual(ERA_ALIASES[alias], "common_era")
                self.assertEqual(resolve_era(alias, 2026),
                                 resolve_era("common_era", 2026))
        # spot-check the returned value is the plain date, not a duplicate epoch
        self.assertEqual(resolve_era("anno_domini", 2026), date(2026, 1, 1))
        self.assertEqual(resolve_era("ce", 1), date(1, 1, 1))


class TestHeatDeath(unittest.TestCase):
    def setUp(self):
        # the warning is single-fire per process; reset so this test controls it
        eras_mod._heat_death_warned = False

    def tearDown(self):
        eras_mod._heat_death_warned = False

    def test_date_past_heat_death_warns_once(self):
        past = HEAT_DEATH_YEAR + 10 ** 50
        with self.assertLogs("chronologia.eras", level="WARNING") as cm:
            result = resolve_era("common_era", past)
        self.assertEqual(result, AstroDate(past))
        self.assertEqual(len(cm.output), 1)
        self.assertIn("heat death", cm.output[0].lower())
        self.assertIn("Adams", cm.output[0])
        # single-fire: a second resolution past the bound stays silent
        logger = logging.getLogger("chronologia.eras")
        with self.assertRaises(AssertionError):
            with self.assertLogs("chronologia.eras", level="WARNING"):
                resolve_era("common_era", past + 1)

    def test_normal_date_does_not_warn(self):
        logger = logging.getLogger("chronologia.eras")
        with self.assertRaises(AssertionError):
            with self.assertLogs("chronologia.eras", level="WARNING"):
                resolve_era("common_era", 12025)
        # even a very large but pre-heat-death year stays silent
        with self.assertRaises(AssertionError):
            with self.assertLogs("chronologia.eras", level="WARNING"):
                resolve_era("common_era", 10 ** 90)


if __name__ == "__main__":
    unittest.main()
