"""Interplanetary reckoning: TimeAxis, Mars Sol Date, MTC, Darian, mission eras.

Golds trace to the cited sources in the papers library:
- ``standards/mars24_allison_mcewen_2000_algorithm.html`` (Allison & McEwen 2000)
  — the MSD formula and the 2000-01-06 worked example.
- ``standards/timekeeping_on_mars_wikipedia.html`` — Viking 1 at MSD 36455,
  mission landing times and sol-count conventions.
- ``standards/darian_calendar_gangale_*.html`` — Darian structure, leap rule,
  and the Viking 1 correspondence 14 Mina 195.
"""
import math
from datetime import timedelta

import pytest

from chronologia.astrodate import AstroDate
from chronologia.axes import (AXES, EARTH_DAY_SECONDS, MARS_SOL_RATIO,
                              MARS_SOL_SECONDS, astro_from_jd, jd_of)
from chronologia.leapseconds import TT_MINUS_TAI, tt_to_utc, utc_to_tt
from chronologia.mars import (DARIAN_EPOCH_MSD, DARIAN_MONTHS, MISSION_ERAS,
                              DarianDate, MarsDate, darian, mission_sol,
                              msd_from_tt, tt_from_msd, to_mars)


# -- TimeAxis: Earth axis is byte-identical to the JDN hub -------------------

def test_earth_axis_count_is_julian_date():
    # JD of 2000-01-01 12:00 TT is 2451545.0 (the J2000.0 epoch).
    assert AXES["earth_day"].count_from_tt(AstroDate(2000, 1, 1, 12)) == 2451545.0


def test_earth_axis_unit_is_86400_seconds():
    assert AXES["earth_day"].unit_seconds == EARTH_DAY_SECONDS == 86400.0


@pytest.mark.parametrize("inst", [
    AstroDate(1, 1, 1),
    AstroDate(1969, 7, 20),
    AstroDate(2027, 6, 5),
    AstroDate(-4713, 11, 24, 12),
    AstroDate(9999, 12, 31),
    AstroDate(2000, 1, 1, 12),          # J2000, exactly representable
    AstroDate(2000, 1, 1, 6),           # quarter-day fraction, exact
])
def test_earth_axis_round_trip_byte_identical(inst):
    # Day-granular (and dyadic-fraction) instants round-trip byte-identically;
    # this is the JDN-hub equivalence the Earth axis restates.
    axis = AXES["earth_day"]
    assert axis.tt_from_count(axis.count_from_tt(inst)) == inst


def test_earth_axis_sub_second_within_sub_ms():
    # A JD is a float, so a far-from-J2000 sub-second instant round-trips only to
    # the library's stated sub-millisecond floor, not to the microsecond.
    axis = AXES["earth_day"]
    inst = AstroDate(9999, 12, 31, 23, 59, 59, 999999)
    back = axis.tt_from_count(axis.count_from_tt(inst))
    assert abs((back - inst).total_seconds()) < 1e-3


def test_jd_of_and_astro_from_jd_invert():
    for jd in (0.0, 1721425.5, 2451545.0, 2405522.0028779):
        assert abs(jd_of(astro_from_jd(jd)) - jd) < 1e-6


def test_earth_axis_count_matches_toordinal_midnight():
    # Midnight of a date is JDN - 0.5; JDN = toordinal + 1721425.
    d = AstroDate(2020, 2, 29)
    assert AXES["earth_day"].count_from_tt(d) == d.toordinal() + 1721425 - 0.5


# -- Mars sol axis + MSD formula --------------------------------------------

def test_mars_sol_unit_seconds_is_cited_value():
    assert MARS_SOL_RATIO == 1.0274912517
    # 88,775.244 s to the cited 3 decimals.
    assert round(MARS_SOL_SECONDS, 3) == 88775.244


def test_mars_sol_axis_epoch_is_msd_zero():
    # The axis epoch is JD_TT 2405522.0028779, i.e. MSD 0 by construction.
    assert abs(AXES["mars_sol"].count_from_tt(astro_from_jd(2405522.0028779))) < 1e-6


def test_msd_gold_2000_01_06():
    # Mars24 worked example: 2000-01-06 00:00 UTC -> MSD ~44796 (MST 23:59:39).
    md = MarsDate.from_earth(AstroDate(2000, 1, 6, 0, 0, 0))
    assert md.sol == 44795
    assert (md.hour, md.minute, md.second) == (23, 59, 39)
    assert abs(md.msd - 44795.99976) < 1e-4


def test_msd_gold_viking1_landing_is_36455():
    # Wikipedia "Timekeeping on Mars": Viking 1 landed at MSD 36455.
    md = MarsDate.from_earth(AstroDate(1976, 7, 20, 11, 53, 6))
    assert md.sol == 36455


def test_msd_from_tt_matches_cited_formula():
    tt = AstroDate(2020, 1, 1, 0, 0, 0)
    expected = (jd_of(tt) - 2405522.0028779) / 1.0274912517
    assert abs(msd_from_tt(tt) - expected) < 1e-9


# -- TT <-> MSD round-trips across centuries --------------------------------

@pytest.mark.parametrize("msd", [0.0, 100.0, 12345.6789, 44796.0, 66000.5,
                                 -5000.0, 250000.0])
def test_tt_msd_round_trip(msd):
    assert abs(msd_from_tt(tt_from_msd(msd)) - msd) < 1e-6


@pytest.mark.parametrize("year", [1700, 1800, 1900, 2000, 2100, 2200, 2300])
def test_tt_from_msd_round_trip_across_centuries(year):
    tt = AstroDate(year, 6, 15, 12, 30, 45)
    assert abs(msd_from_tt(tt_from_msd(msd_from_tt(tt))) - msd_from_tt(tt)) < 1e-6


def test_utc_to_tt_offset_is_leap_plus_32184():
    # 2000: TAI-UTC = 32 s, so TT-UTC = 64.184 s.
    utc = AstroDate(2000, 6, 1, 0, 0, 0)
    tt = utc_to_tt(utc)
    assert abs((tt - utc).total_seconds() - (32 + TT_MINUS_TAI)) < 1e-9


def test_tt_to_utc_inverts_utc_to_tt():
    utc = AstroDate(2015, 3, 10, 8, 45, 12)
    assert tt_to_utc(utc_to_tt(utc)) == utc


# -- MarsDate: fields, str, MTC arithmetic, Earth round-trip ----------------

def test_marsdate_str_format():
    assert str(MarsDate(52123, 4, 31, 12)) == "MSD 52123 04:31:12 MTC"


def test_marsdate_from_msd_fields():
    md = MarsDate.from_msd(1000.5)              # half a sol == MTC noon
    assert md.sol == 1000
    assert (md.hour, md.minute, md.second) == (12, 0, 0)


def test_mtc_sol_fraction_round_trip():
    # A stretched-clock reading -> sol fraction -> back.
    md = MarsDate(2000, 6, 30, 15, 500000)
    assert MarsDate.from_msd(md.msd) == md


def test_mtc_quarter_sol_is_six_hours():
    assert MarsDate.from_msd(10.25).hour == 6
    assert MarsDate.from_msd(10.75).hour == 18


def test_marsdate_to_earth_round_trip():
    utc = AstroDate(2018, 11, 26, 19, 52, 59)   # ~InSight landing era
    md = to_mars(utc)
    back = md.to_earth()
    # within one MTC second (rounding of the stretched clock)
    assert abs((back - utc).total_seconds()) < 2.0


def test_marsdate_rejects_bad_mtc():
    with pytest.raises(ValueError):
        MarsDate(1, 24, 0, 0)
    with pytest.raises(ValueError):
        MarsDate(1, 0, 60, 0)


def test_to_mars_matches_from_earth():
    utc = AstroDate(2005, 5, 5, 5, 5, 5)
    assert to_mars(utc) == MarsDate.from_earth(utc)


# -- Darian calendar: structure, golds, leap, round-trip sweep --------------

def test_darian_has_24_months_named():
    assert len(DARIAN_MONTHS) == 24
    assert DARIAN_MONTHS[7] == "Mina"          # month 8 (0-indexed 7)
    assert DARIAN_MONTHS[18] == "Virgo"        # month 19


def test_darian_gold_viking1():
    # Viking 1 (MSD 36455) == 14 Mina 195 (Wikipedia "Darian calendar").
    dd = darian.from_msd(36455)
    assert (dd.year, dd.month, dd.sol) == (195, 8, 14)
    assert dd.month_name == "Mina"
    assert str(dd) == "14 Mina 195"


def test_darian_epoch_constant():
    assert DARIAN_EPOCH_MSD == -93460
    assert DarianDate(1, 1, 1).msd == DARIAN_EPOCH_MSD


def test_darian_common_year_has_668_sols():
    # Year 4: even, not div by 10 -> common (668).
    assert DarianDate(5, 1, 1).msd - DarianDate(4, 1, 1).msd == 668


def test_darian_leap_year_has_669_sols():
    # Year 3: odd -> leap (669).
    assert DarianDate(4, 1, 1).msd - DarianDate(3, 1, 1).msd == 669


def test_darian_leap_month24_gains_a_sol():
    # Month 24 is 27 sols in a common year (year 4), 28 in a leap year (year 3).
    with pytest.raises(ValueError):
        DarianDate(4, 24, 28)                  # no sol 28 in common year
    assert DarianDate(3, 24, 28).sol == 28     # leap year has it


@pytest.mark.parametrize("year,leap", [
    (1, True),     # odd
    (2, False),    # even, not div 10
    (10, True),    # div 10
    (100, False),  # div 100 cancels
    (200, False),  # div 100, not div 500 -> cancelled
    (500, True),   # div 500 restores
    (1000, True),  # div 100 but also div 500 -> restored
    (999, True),   # odd
])
def test_darian_leap_rule(year, leap):
    length = DarianDate(year + 1, 1, 1).msd - DarianDate(year, 1, 1).msd
    assert (length == 669) == leap


def test_darian_month_quarter_lengths():
    # Within a quarter: five 28-sol months then a 27-sol month.
    for m in (1, 2, 3, 4, 5):
        with pytest.raises(ValueError):
            DarianDate(2, m, 29)
        assert DarianDate(2, m, 28).sol == 28
    with pytest.raises(ValueError):
        DarianDate(2, 6, 28)                   # month 6 has only 27 sols


def test_darian_weekday_restarts_each_month():
    assert DarianDate(50, 1, 1).weekday_name == "Sol Solis"
    assert DarianDate(50, 2, 1).weekday_name == "Sol Solis"  # week restarts
    assert DarianDate(50, 1, 8).weekday_name == "Sol Solis"  # 7-sol cycle


def test_darian_round_trip_sweep_over_10k_sols():
    for msd in range(20000, 30001):            # 10001 consecutive sols
        dd = darian.from_msd(msd)
        assert dd.msd == msd
        # date() is the inverse: same sol back
        assert darian.date(dd.year, dd.month, dd.sol).sol == msd


def test_darian_date_returns_marsdate_at_midnight():
    m = darian.date(200, 12, 5)
    assert isinstance(m, MarsDate)
    assert (m.hour, m.minute, m.second) == (0, 0, 0)


def test_darian_rejects_bad_month_and_sol():
    with pytest.raises(ValueError):
        DarianDate(100, 0, 1)
    with pytest.raises(ValueError):
        DarianDate(100, 25, 1)
    with pytest.raises(ValueError):
        DarianDate(100, 1, 0)


# -- Mission sol-count eras --------------------------------------------------

def test_mission_sol_width_is_one_sol():
    span = mission_sol("curiosity", 500)
    assert abs(span.width.total_seconds() - MARS_SOL_SECONDS) < 1e-3


def test_curiosity_sol1000_gold_spans_2015_05_31():
    # NASA/JPL: Curiosity's 1,000th sol fell on Earth date 2015-05-31.
    span = mission_sol("curiosity", 1000)
    assert span.contains(AstroDate(2015, 5, 31, 0, 0, 0))


def test_curiosity_counts_from_sol_zero():
    # Sol 0 is the landing sol -> begins at touchdown.
    assert MISSION_ERAS["curiosity"].landing_sol == 0
    assert mission_sol("curiosity", 0).start == MISSION_ERAS["curiosity"].landing_utc


def test_mer_and_pathfinder_count_from_sol_one():
    for m in ("spirit", "opportunity", "pathfinder"):
        assert MISSION_ERAS[m].landing_sol == 1
        assert mission_sol(m, 1).start == MISSION_ERAS[m].landing_utc


def test_viking_and_perseverance_count_from_sol_zero():
    for m in ("viking_1", "viking_2", "perseverance"):
        assert MISSION_ERAS[m].landing_sol == 0


def test_opportunity_sol1_gold_is_landing_date():
    # Opportunity (MER-B) Sol 1 == landing, 2004-01-25 UTC.
    span = mission_sol("opportunity", 1)
    assert span.contains(AstroDate(2004, 1, 25, 6, 0, 0))


def test_consecutive_mission_sols_tile():
    a = mission_sol("perseverance", 10)
    b = mission_sol("perseverance", 11)
    assert a.end == b.start                    # half-open spans tile gap-free


# -- Adversarial -------------------------------------------------------------

def test_mission_sol_unknown_mission_raises():
    with pytest.raises(KeyError):
        mission_sol("sojourner", 5)


def test_mission_sol_below_landing_sol_raises():
    # Curiosity has no sol -1; MER has no sol 0 (they count from 1).
    with pytest.raises(ValueError):
        mission_sol("curiosity", -1)
    with pytest.raises(ValueError):
        mission_sol("spirit", 0)


def test_darian_from_msd_handles_pre_epoch_sols():
    # Sols before the Darian epoch (MSD < DARIAN_EPOCH_MSD) still decode.
    dd = darian.from_msd(DARIAN_EPOCH_MSD - 1)
    assert dd.msd == DARIAN_EPOCH_MSD - 1
    assert dd.year < 1


def test_msd_is_monotonic_in_time():
    earlier = msd_from_tt(AstroDate(2001, 1, 1))
    later = msd_from_tt(AstroDate(2001, 1, 2))
    assert math.isclose(later - earlier, EARTH_DAY_SECONDS / MARS_SOL_SECONDS,
                        rel_tol=1e-9)
