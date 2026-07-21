"""Time axes: the generalized reckoning hub, for Earth and beyond.

The Julian Day Number was never really about *Julian* or about *days*.  Strip
the Earth-specific labels and what remains is: **count a periodic unit from an
epoch on one shared instant line.**  A planet's day, a rover's sol, a pulsar's
period — anything that ticks a fixed length of proper time — is the same idea
with a different unit and a different zero.  :class:`TimeAxis` is that idea made
concrete: ``(key, unit_seconds, epoch_tt)`` — a unit measured in SI seconds,
counted from an epoch fixed on the **TT** (Terrestrial Time) scale.

Why TT, and the relativity stance
---------------------------------
Exchange between axes runs through TT, the smooth atomic timescale
(``TT = TAI + 32.184 s`` — the leap-second module,
:mod:`chronologia.leapseconds`, is the down payment on this).  Relativity is
handled **by declaration, not computation**: every conversion is stated in TT,
and the documented error from ignoring the periodic relativistic terms is
sub-millisecond.  TDB (Barycentric Dynamical Time) differs from TT by at most
~1.6 ms of periodic terms (Allison & McEwen 2000; IAU 2006 Resolution B3), and
that is the floor of accuracy claimed here.  Light-time delay between planets is
representable as *referential span width* (a :class:`~chronologia.astrodate.DateSpan`
carries its own uncertainty as width), never silently folded into an instant.
Full general-relativistic proper-time transport — a rover clock's own elapsed
time versus a barycentric coordinate — is **permanently out of scope** (it is
provider-hook territory, needing an ephemeris and a metric, not a calendar).

The Earth axis is descriptive, the others authoritative
-------------------------------------------------------
``AXES["earth_day"]`` exists so Earth is not a special case in the model, but it
changes nothing: Earth timekeeping remains :class:`~chronologia.astrodate.AstroDate`
and the JDN hub in :mod:`chronologia.calendars`.  The axis is **byte-identical**
to that machinery — :meth:`TimeAxis.count_from_tt` on ``earth_day`` returns the
Julian Date and round-trips an ``AstroDate`` exactly (integer-microsecond
arithmetic, no float drift) — so it is merely a *descriptive* restatement of
what Earth already does.  For ``mars_sol`` (and any future body) the axis is
**authoritative**: it is where the count is defined.

Plumbing note (low-level): :func:`jd_of` exposes the Julian Date of an
``AstroDate`` instant and :func:`astro_from_jd` its inverse; friendly,
object-returning surfaces (``SolDate``/``MarsDate`` and their ``.to_earth()`` /
``from_earth`` converters) live in :mod:`chronologia.mars` and should be
preferred over threading raw JD/MSD floats by hand.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from chronologia.astrodate import AstroDate, _RD_TO_JDN, _US_PER_DAY

__all__ = [
    "TimeAxis",
    "AXES",
    "EARTH_DAY_SECONDS",
    "MARS_SOL_SECONDS",
    "MARS_SOL_RATIO",
    "jd_of",
    "astro_from_jd",
]

#: SI seconds in a mean Earth solar day — the JDN unit, by definition exact.
EARTH_DAY_SECONDS = 86400.0

#: Ratio of a mean Martian solar day (sol) to an Earth day, from Allison &
#: McEwen (2000) via the Mars24 algorithm notes — the divisor in the MSD
#: formula.  A sol is 1.0274912517 Earth days.
MARS_SOL_RATIO = 1.0274912517

#: SI seconds in a mean Martian solar day: ``MARS_SOL_RATIO * 86400`` ==
#: 88775.2442..., i.e. the commonly cited **88,775.244 s** (39 min 35.244 s
#: longer than an Earth day; Allison & McEwen 2000; Wikipedia "Timekeeping on
#: Mars").  Kept as the ratio product so the axis and the MSD formula share one
#: constant and cannot drift apart.
MARS_SOL_SECONDS = MARS_SOL_RATIO * EARTH_DAY_SECONDS


def jd_of(instant: AstroDate) -> float:
    """The Julian Date of an :class:`AstroDate` instant (astronomical JD).

    JDN counts from noon, so an instant's JD is ``toordinal + 1721425 +
    day_fraction - 0.5`` (midnight of a date is ``JDN - 0.5``).  Whatever
    timescale *instant* is expressed in (UTC, TT, ...) is the timescale of the
    returned JD; the caller is responsible for having put it on TT before
    feeding an axis (see :func:`chronologia.leapseconds.utc_to_tt`).
    """
    return instant._total_us() / _US_PER_DAY + _RD_TO_JDN - 0.5


def astro_from_jd(jd: float) -> AstroDate:
    """The :class:`AstroDate` instant of a Julian Date (inverse of :func:`jd_of`).

    Rounds to the nearest microsecond — the sub-microsecond tail of a JD float
    is below every precision this library claims (see the module's relativity
    note).
    """
    us = round((jd - _RD_TO_JDN + 0.5) * _US_PER_DAY)
    return AstroDate._from_total_us(us)


@dataclass(frozen=True)
class TimeAxis:
    """A periodic unit counted from an epoch on the TT scale.

    :param key: registry key (``"earth_day"``, ``"mars_sol"``).
    :param unit_seconds: the unit's length in SI seconds.
    :param epoch_tt: the instant (as a TT :class:`AstroDate`) where the count is
        zero.

    :meth:`count_from_tt` maps a TT instant to a (fractional) unit count;
    :meth:`tt_from_count` is its inverse.  The count arithmetic is done in
    integer microseconds so that an integer-unit axis (``earth_day``) round-trips
    an ``AstroDate`` with no floating-point drift — the byte-identical guarantee
    the Earth axis makes.
    """
    key: str
    unit_seconds: float
    epoch_tt: AstroDate

    def count_from_tt(self, instant: AstroDate) -> float:
        """Units elapsed from :attr:`epoch_tt` to *instant* (a TT instant).

        For ``earth_day`` this is exactly the Julian Date of *instant*; for
        ``mars_sol`` it is exactly the Mars Sol Date (the MSD formula is this
        subtraction and division — see :mod:`chronologia.mars`).
        """
        diff_us = instant._total_us() - self.epoch_tt._total_us()
        return diff_us / (self.unit_seconds * 1_000_000)

    def tt_from_count(self, count: float) -> AstroDate:
        """The TT instant *count* units after :attr:`epoch_tt` (inverse)."""
        us = self.epoch_tt._total_us() + round(count * self.unit_seconds * 1_000_000)
        return AstroDate._from_total_us(us)


#: Registry of known time axes.
#:
#: ``earth_day`` — the JDN axis: unit 86400 s, epoch the Julian Day zero
#: (proleptic-Gregorian −4713-11-24 12:00, i.e. JD 0.0).  Descriptive only;
#: Earth timekeeping stays on :class:`AstroDate` / the JDN hub, to which this is
#: byte-identical.
#:
#: ``mars_sol`` — the Mars Sol Date axis: unit :data:`MARS_SOL_SECONDS`, epoch
#: the TT instant of MSD 0 (JD_TT 2405522.0028779; Allison & McEwen 2000 via the
#: Mars24 algorithm notes).  Authoritative — this is where MSD is defined.
AXES: Dict[str, TimeAxis] = {
    "earth_day": TimeAxis("earth_day", EARTH_DAY_SECONDS, astro_from_jd(0.0)),
    "mars_sol": TimeAxis(
        "mars_sol", MARS_SOL_SECONDS, astro_from_jd(2405522.0028779)),
}
