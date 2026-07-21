"""Reckoning on Mars: Mars Sol Date, Coordinated Mars Time, the Darian calendar.

Everything here rides the ``mars_sol`` axis of :mod:`chronologia.axes` — a unit
of one Martian solar day (a *sol*, :data:`~chronologia.axes.MARS_SOL_SECONDS` ==
88,775.244 s) counted from an epoch fixed on Terrestrial Time.  The friendly,
object-in/object-out surface is :class:`MarsDate` (an MSD sol plus a Coordinated
Mars Time reading) with :meth:`MarsDate.to_earth` / :func:`to_mars` converters,
and the :class:`DarianCalendar` (``darian``) whose ``date(year, month, sol)``
places a civil Mars date on the same axis.  The low-level plumbing —
:func:`msd_from_tt` / :func:`tt_from_msd` on bare MSD floats — is documented but
callers should prefer the objects.

Mars Sol Date
-------------
MSD counts sols continuously from a fictitious midnight at the Airy-0 meridian
near 1873-12-29.  Per Allison & McEwen (2000), via the NASA GISS Mars24
algorithm notes (papers ``standards/mars24_allison_mcewen_2000_algorithm.html``):

    MSD = (JD_TT − 2451549.5) / 1.0274912517 + 44796.0 − 0.0009626

which is the consolidated single-constant form

    MSD = (JD_TT − 2405522.0028779) / 1.0274912517

and *that* subtraction-and-divide is exactly what the ``mars_sol``
:class:`~chronologia.axes.TimeAxis` computes (epoch JD_TT 2405522.0028779, unit
88,775.244 s), so the axis and this module share one constant.  JD_TT is the
Julian Date on Terrestrial Time; a civil UTC instant reaches it through
:func:`chronologia.leapseconds.utc_to_tt` (``TT = TAI + 32.184 s``, TAI − UTC
from the leap-second table).

Coordinated Mars Time
---------------------
MTC is mean solar time at Airy-0: the sol split into **24 stretched hours**, each
60 minutes of 60 seconds, exactly as an Earth clock splits a day — only the day
is a sol.  So ``MTC = 24 h × frac(MSD)`` and one MTC hour is 1/24 sol ≈ 61.65
civil minutes.  This mirrors :class:`chronologia.cycles.DaySubdivision` (which
rescales one *civil day* into alternative fixed units, e.g. French decimal time's
10 hours); MTC is the same rescaling applied to the *sol* instead of the day, so
the mechanism is reused conceptually while the arithmetic lives cleanly on the
sol axis.  Note MTC is **not** the Mars24 "Mean Solar Time" figure, which carries
an additional −0.0009626 sol prime-meridian offset (~83 s); MTC here is the pure
sol fraction.

Relativity stance
-----------------
Conversions are stated in TT and are accurate to the sub-millisecond floor set
by the periodic TDB−TT terms (~1.6 ms, Allison & McEwen 2000).  Light-time
delay is representable as :class:`~chronologia.astrodate.DateSpan` width, not
folded into an instant.  General-relativistic proper-time transport (a Mars
clock's own rate) is out of scope.  See :mod:`chronologia.axes`.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

from chronologia.astrodate import AstroDate, DateSpan
from chronologia.axes import AXES, MARS_SOL_SECONDS
from chronologia.leapseconds import tt_to_utc, utc_to_tt

__all__ = [
    "msd_from_tt",
    "tt_from_msd",
    "MarsDate",
    "to_mars",
    "DarianCalendar",
    "DarianDate",
    "darian",
    "DARIAN_MONTHS",
    "DARIAN_WEEKDAYS",
    "DARIAN_EPOCH_MSD",
    "Mission",
    "MISSION_ERAS",
    "mission_sol",
]

_MTC_SECONDS_PER_SOL = 86400          # 24 * 60 * 60 stretched clock seconds
_US_PER_MTC_SOL = _MTC_SECONDS_PER_SOL * 1_000_000


# -- Mars Sol Date <-> Terrestrial Time (low-level plumbing) ----------------

def msd_from_tt(instant: AstroDate) -> float:
    """Mars Sol Date of a Terrestrial-Time instant.

    Plumbing: this is ``AXES["mars_sol"].count_from_tt(instant)``, i.e. the
    cited ``(JD_TT − 2405522.0028779) / 1.0274912517`` formula.  Prefer
    :meth:`MarsDate.from_earth` / :func:`to_mars` for civil UTC input.
    """
    return AXES["mars_sol"].count_from_tt(instant)


def tt_from_msd(msd: float) -> AstroDate:
    """The Terrestrial-Time instant of a Mars Sol Date (inverse of :func:`msd_from_tt`)."""
    return AXES["mars_sol"].tt_from_count(msd)


# -- MarsDate: MSD sol + Coordinated Mars Time ------------------------------

@dataclass(frozen=True)
class MarsDate:
    """A civil instant on Mars: an MSD sol number plus a Coordinated Mars Time.

    ``sol`` is the integer Mars Sol Date; ``hour``/``minute``/``second``/
    ``microsecond`` are the MTC reading (24 stretched hours over the sol).  The
    fractional MSD is ``sol + (mtc seconds)/86400``.  Construct one from a real
    Earth instant with :meth:`from_earth`, or from a bare MSD with
    :meth:`from_msd`; go back with :meth:`to_earth`.
    """
    sol: int
    hour: int = 0
    minute: int = 0
    second: int = 0
    microsecond: int = 0

    def __post_init__(self):
        if not (0 <= self.hour < 24 and 0 <= self.minute < 60
                and 0 <= self.second < 60 and 0 <= self.microsecond < 1_000_000):
            raise ValueError(
                f"MTC reading out of range: "
                f"{self.hour:02d}:{self.minute:02d}:{self.second:02d}")

    @property
    def msd(self) -> float:
        """The fractional Mars Sol Date this reading names."""
        frac_us = ((self.hour * 3600 + self.minute * 60 + self.second)
                   * 1_000_000 + self.microsecond)
        return self.sol + frac_us / _US_PER_MTC_SOL

    @classmethod
    def from_msd(cls, msd: float) -> "MarsDate":
        """The :class:`MarsDate` for a (fractional) Mars Sol Date."""
        sol = int(msd // 1)
        frac = msd - sol
        us = int(round(frac * _US_PER_MTC_SOL))
        if us >= _US_PER_MTC_SOL:                 # frac rounded up to a full sol
            sol += 1
            us -= _US_PER_MTC_SOL
        micro = us % 1_000_000
        secs = us // 1_000_000
        return cls(sol, secs // 3600, (secs % 3600) // 60, secs % 60, micro)

    @classmethod
    def from_earth(cls, instant: AstroDate) -> "MarsDate":
        """The Mars time for an Earth **UTC** instant (``AstroDate``/``datetime``).

        The instant is lifted to TT (:func:`chronologia.leapseconds.utc_to_tt`)
        and read off the ``mars_sol`` axis.
        """
        if not isinstance(instant, AstroDate):
            instant = AstroDate.from_datetime(instant)
        return cls.from_msd(msd_from_tt(utc_to_tt(instant)))

    def to_earth(self) -> AstroDate:
        """The Earth **UTC** instant of this Mars time (inverse of :meth:`from_earth`).

        Raises ``ValueError`` for sols whose UTC instant falls before 1972 (the
        leap-second table's floor); MSD arithmetic itself has no such limit — use
        :func:`tt_from_msd` for the raw TT instant across all time.
        """
        return tt_to_utc(tt_from_msd(self.msd))

    def __str__(self) -> str:
        return (f"MSD {self.sol} "
                f"{self.hour:02d}:{self.minute:02d}:{self.second:02d} MTC")

    def to_json(self) -> dict:
        """A ``json.dumps``-ready dict envelope (see :meth:`from_json`)."""
        return {"type": "MarsDate", "sol": self.sol, "hour": self.hour,
                "minute": self.minute, "second": self.second,
                "microsecond": self.microsecond}

    @classmethod
    def from_json(cls, data: dict) -> "MarsDate":
        """Rebuild a :class:`MarsDate` from a :meth:`to_json` envelope."""
        if data.get("type") != "MarsDate":
            raise ValueError(f"not a MarsDate envelope: {data.get('type')!r}")
        return cls(data["sol"], data.get("hour", 0), data.get("minute", 0),
                   data.get("second", 0), data.get("microsecond", 0))


def to_mars(instant: AstroDate) -> MarsDate:
    """Module-level converter: an Earth UTC instant to a :class:`MarsDate`.

    A pure converter — no wall-clock ``now``; the caller supplies the instant.
    Equivalent to :meth:`MarsDate.from_earth`.
    """
    return MarsDate.from_earth(instant)


# -- Darian calendar (Gangale) on the sol axis ------------------------------

#: The 24 Darian months, in order (Latin zodiac name then Sanskrit equivalent,
#: alternating).  Source: Gangale, "The Darian Calendar for Mars"
#: (papers ``standards/darian_calendar_gangale_ops-alaska.html``) and Wikipedia
#: "Darian calendar".  Mina is month 8, Virgo month 19.
DARIAN_MONTHS: Tuple[str, ...] = (
    "Sagittarius", "Dhanus", "Capricornus", "Makara", "Aquarius", "Kumbha",
    "Pisces", "Mina", "Aries", "Mesha", "Taurus", "Rishabha",
    "Gemini", "Mithuna", "Cancer", "Karka", "Leo", "Simha",
    "Virgo", "Kanya", "Libra", "Tula", "Scorpius", "Vrishika",
)

#: The seven Darian weekday names; the week restarts at sol 1 of each month.
DARIAN_WEEKDAYS: Tuple[str, ...] = (
    "Sol Solis", "Sol Lunae", "Sol Martis", "Sol Mercurii",
    "Sol Jovis", "Sol Veneris", "Sol Saturni",
)

#: MSD of Darian year 1, month 1 (Sagittarius), sol 1.
#:
#: **Pinned to a gold correspondence, not to a bare epoch constant.**  The cited
#: sources fix the Darian calendar's *structure* unambiguously (month lengths,
#: leap rule, week) but do not state a numeric MSD for the Telescopic epoch
#: (1609).  So the alignment is derived from the one clean, doubly-cited
#: correspondence — Viking 1 landed at MSD 36455 (Wikipedia "Timekeeping on
#: Mars") on 14 Mina 195 (Wikipedia "Darian calendar") — giving this constant.
#: A Darian sol is assumed to share the MSD integer-sol boundary (both are mean
#: solar time at Airy-0, which the calendar's use of MTC supports).  This is the
#: documented gap: the absolute year-numbering follows from the leap rule
#: applied outward from this anchor, not from an independently published epoch.
DARIAN_EPOCH_MSD = -93460

_QUARTER_SOLS = (28, 28, 28, 28, 28, 27)      # months within a quarter
_COMMON_YEAR_SOLS = 668
_LEAP_YEAR_SOLS = 669


def _darian_leap(year: int) -> bool:
    """Darian intercalation: a 669-sol year.

    Rule (Gangale, papers ``standards/darian_calendar_gangale_ops-alaska.html``):
    leap if the year is odd or divisible by 10; cancelled if divisible by 100,
    unless also divisible by 500.  The extra sol lengthens month 24 to 28 sols.
    """
    leap = (year % 2 != 0) or (year % 10 == 0)
    if year % 100 == 0:
        leap = False
    if year % 500 == 0:
        leap = True
    return leap


def _darian_year_sols(year: int) -> int:
    return _LEAP_YEAR_SOLS if _darian_leap(year) else _COMMON_YEAR_SOLS


def _cumleap(n: int) -> int:
    """Leap years in 1..n (closed form of the intercalation)."""
    if n <= 0:
        return 0
    return (n + 1) // 2 + n // 10 - n // 100 + n // 500


def _sols_before_year(year: int) -> int:
    """Sols elapsed from Darian 1/1/1 up to (not including) year *year* sol 1."""
    y = year - 1
    return _COMMON_YEAR_SOLS * y + _cumleap(y)


def _month_length(year: int, month: int) -> int:
    base = _QUARTER_SOLS[(month - 1) % 6]
    if month == 24 and base == 27 and _darian_leap(year):
        return 28
    return base


def _sol_of_year(month: int, sol: int) -> int:
    """1-indexed sol-of-year for (month, sol), ignoring the leap sol (only month
    24 can carry it, which does not shift any earlier month)."""
    before = sum(_QUARTER_SOLS[(m - 1) % 6] for m in range(1, month))
    return before + sol


@dataclass(frozen=True)
class DarianDate:
    """A civil Darian calendar date (year, month 1..24, sol 1..28).

    Friendly object: :meth:`to_mars` places it on the sol axis (MTC 00:00:00 of
    that sol), :meth:`to_earth` gives the Earth UTC instant, and
    :attr:`month_name` / :attr:`weekday_name` label it.
    """
    year: int
    month: int
    sol: int

    def __post_init__(self):
        if not 1 <= self.month <= 24:
            raise ValueError(f"Darian month must be 1..24, got {self.month}")
        length = _month_length(self.year, self.month)
        if not 1 <= self.sol <= length:
            raise ValueError(
                f"sol {self.sol} out of range for {self.month_name} "
                f"{self.year} (1..{length})")

    @property
    def month_name(self) -> str:
        return DARIAN_MONTHS[self.month - 1]

    @property
    def weekday_name(self) -> str:
        """The Darian weekday; the seven-sol week restarts each month."""
        return DARIAN_WEEKDAYS[(self.sol - 1) % 7]

    @property
    def msd(self) -> int:
        """The integer MSD of this Darian sol."""
        idx = _sols_before_year(self.year) + _sol_of_year(self.month, self.sol) - 1
        return idx + DARIAN_EPOCH_MSD

    def to_mars(self) -> MarsDate:
        """This Darian sol as a :class:`MarsDate` at MTC 00:00:00."""
        return MarsDate(self.msd)

    def to_earth(self) -> AstroDate:
        """The Earth UTC instant of this Darian sol's start."""
        return self.to_mars().to_earth()

    def __str__(self) -> str:
        return f"{self.sol} {self.month_name} {self.year}"

    def to_json(self) -> dict:
        """A ``json.dumps``-ready dict envelope (see :meth:`from_json`)."""
        return {"type": "DarianDate", "year": self.year, "month": self.month,
                "sol": self.sol}

    @classmethod
    def from_json(cls, data: dict) -> "DarianDate":
        """Rebuild a :class:`DarianDate` from a :meth:`to_json` envelope."""
        if data.get("type") != "DarianDate":
            raise ValueError(
                f"not a DarianDate envelope: {data.get('type')!r}")
        return cls(data["year"], data["month"], data["sol"])


class DarianCalendar:
    """The Darian calendar as a Calendar-style object on the sol axis.

    ``darian.date(year, month, sol)`` yields the :class:`MarsDate` of that civil
    date (MTC 00:00:00); ``darian.from_mars`` / ``darian.from_msd`` invert it to
    a :class:`DarianDate`.  Objects in, objects out.
    """

    def date(self, year: int, month: int, sol: int) -> MarsDate:
        """The :class:`MarsDate` (MTC 00:00:00) of a Darian ``(year, month, sol)``."""
        return DarianDate(year, month, sol).to_mars()

    def from_msd(self, msd: float) -> DarianDate:
        """The :class:`DarianDate` containing integer sol ``floor(msd)``."""
        idx = int(msd // 1) - DARIAN_EPOCH_MSD
        year = idx // _COMMON_YEAR_SOLS + 1        # estimate, then correct
        while _sols_before_year(year) > idx:
            year -= 1
        while _sols_before_year(year + 1) <= idx:
            year += 1
        soy = idx - _sols_before_year(year) + 1    # 1-indexed sol-of-year
        month = 1
        while soy > _month_length(year, month):
            soy -= _month_length(year, month)
            month += 1
        return DarianDate(year, month, soy)

    def from_mars(self, mars: MarsDate) -> DarianDate:
        """The :class:`DarianDate` of a :class:`MarsDate`'s sol."""
        return self.from_msd(mars.sol)


#: The Darian calendar singleton.
darian = DarianCalendar()


# -- Mission sol-count eras -------------------------------------------------

@dataclass(frozen=True)
class Mission:
    """A landed Mars mission's sol-count era.

    :param key: mission identifier.
    :param landing_utc: touchdown instant, UTC.
    :param landing_sol: the sol number the mission assigns to its landing sol —
        **0** for Viking/Curiosity/Perseverance, **1** for Pathfinder and the
        Mars Exploration Rovers (Spirit, Opportunity).  This is the mission's own
        convention, not MSD; see :func:`mission_sol`.
    :param source: cited landing-time / convention source.
    """
    key: str
    landing_utc: AstroDate
    landing_sol: int
    source: str


_SRC = ("landing times & sol-count conventions: papers "
        "standards/timekeeping_on_mars_wikipedia.html (NASA mission pages)")

#: Landed-mission sol-count eras.  Sol-numbering convention per mission is the
#: source's (Viking/Curiosity/Perseverance: landing == Sol 0; Pathfinder and the
#: Mars Exploration Rovers Spirit & Opportunity: landing == Sol 1).
MISSION_ERAS: Dict[str, Mission] = {
    "viking_1": Mission(
        "viking_1", AstroDate(1976, 7, 20, 11, 53, 6), 0, _SRC),
    "viking_2": Mission(
        "viking_2", AstroDate(1976, 9, 3, 22, 37, 50), 0, _SRC),
    "pathfinder": Mission(
        "pathfinder", AstroDate(1997, 7, 4, 16, 56, 55), 1, _SRC),
    "spirit": Mission(
        "spirit", AstroDate(2004, 1, 4, 4, 35, 0), 1, _SRC),
    "opportunity": Mission(
        "opportunity", AstroDate(2004, 1, 25, 5, 5, 0), 1, _SRC),
    "curiosity": Mission(
        "curiosity", AstroDate(2012, 8, 6, 5, 17, 57), 0, _SRC),
    "perseverance": Mission(
        "perseverance", AstroDate(2021, 2, 18, 20, 55, 0), 0, _SRC),
}


def mission_sol(mission: str, sol: int) -> DateSpan:
    """The one-sol-wide Earth (UTC) :class:`DateSpan` of a mission sol.

    Mission sols are counted in local solar time at the rover; the landing sol is
    ``mission.landing_sol`` (0 or 1 per the mission's convention).  This models a
    mission sol as one :data:`~chronologia.axes.MARS_SOL_SECONDS`-wide window
    anchored at the touchdown instant — sol ``landing_sol`` begins at landing and
    each later sol one sol on — so ``width`` is exactly one sol and "Sol N (Earth
    date …)" press correspondences reproduce (e.g. Curiosity Sol 1000 spans
    2015-05-30/31).  The sub-sol phase offset from true local mean midnight is
    not modelled (a documented approximation; the landing-time anchor is what the
    published correspondences are consistent with).

    Raises ``KeyError`` for an unknown mission and ``ValueError`` for a sol below
    the mission's landing sol (mission sols do not run before touchdown).
    """
    m = MISSION_ERAS[mission]
    if sol < m.landing_sol:
        raise ValueError(
            f"{mission} has no sol {sol}: its landing sol is {m.landing_sol} "
            f"(sols do not run before touchdown)")
    offset = sol - m.landing_sol
    start = m.landing_utc + _sols_timedelta(offset)
    end = m.landing_utc + _sols_timedelta(offset + 1)
    return DateSpan(start, end)


def _sols_timedelta(n_sols: float):
    from datetime import timedelta
    return timedelta(seconds=n_sols * MARS_SOL_SECONDS)
