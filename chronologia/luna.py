"""Lunar time: the natural cycle registered, the civil standard withheld.

Two very different things share the word "lunar time", and this module keeps
them apart on purpose.

The **natural** lunar cycle is a fact of orbital mechanics and needs no
committee: because the Moon is tidally locked, a mean **lunar (solar) day** for
a surface observer equals one mean **synodic month** — new moon to new moon,
:data:`~chronologia.moon.MEAN_SYNODIC_MONTH_DAYS` (29.530589 days).  The Sun
returns to the same place in the lunar sky once per lunation.  That cycle is
registered here as a :class:`~chronologia.axes.TimeAxis` (``AXES["lunar"]``),
byte-consistent with the mean-lunation arithmetic in :mod:`chronologia.moon`,
so "the natural lunar day" is a first-class reckoning like the Mars sol.

The **civil** standard — Coordinated Lunar Time (LTC/LunarTC), a UTC-analogue
for the Moon — does **not** exist yet, and this library refuses to invent one.
On 2 April 2024 the US White House OSTP issued a policy directive tasking NASA
with defining such a standard by the end of 2026, precisely because clocks on
the Moon do not tick at Earth's rate: a lunar clock runs about **58.7
microseconds per Earth-day faster** than one on Earth's surface (general- and
special-relativistic terms combined), plus smaller periodic variations
(Wikipedia, "Coordinated Lunar Time", quoted verbatim).
Until the standard publishes there is no defensible zero point and no adopted
rate convention, so :func:`ltc_offset` raises :class:`NotImplementedError`
rather than ship a fabricated civil offset.  :data:`LTC_STATUS` records the
mandate, its source, and the drift figure as citable data.

This is the same stance the rest of the package takes toward things it cannot
compute honestly (the no-ephemeris vow, the reconstructed/predicted basis
split): a placeholder that documents *what is known and what is pending*, never
a plausible-looking number with no authority behind it.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from datetime import date, datetime

from chronologia.astrodate import AstroDate
from chronologia.axes import AXES, EARTH_DAY_SECONDS, TimeAxis
from chronologia.moon import EPOCH_NEW_MOON, MEAN_SYNODIC_MONTH_DAYS

__all__ = [
    "LUNAR_DAY_SECONDS",
    "LTC_DRIFT_MICROSECONDS_PER_DAY",
    "LTC_STATUS",
    "LunarTimeStandardStatus",
    "ltc_offset",
]

#: SI seconds in a mean lunar (solar) day.  The Moon is tidally locked, so a
#: surface observer's mean solar day equals one mean synodic month:
#: ``MEAN_SYNODIC_MONTH_DAYS * 86400`` == 2,551,442.9 s (29.530589 days;
#: Wikipedia, "New moon", for the month length).
#: This is the natural lunar cycle the ``lunar`` axis counts — a documented
#: astronomical fact, not a civil convention.
LUNAR_DAY_SECONDS = MEAN_SYNODIC_MONTH_DAYS * EARTH_DAY_SECONDS

#: Relativistic drift of a lunar-surface clock relative to an Earth-surface
#: clock: **58.7 microseconds per Earth-day faster** (Wikipedia, "Coordinated
#: Lunar Time", quoted verbatim: "24 hours on the Moon being 58.7 microseconds ...
#: faster").  The value the spec rounds to "~56 µs/day"; the cited source
#: figure is 58.7, which is the number used here.  This is *why* a lunar time
#: standard is needed and *why* no naive Earth-clock offset is correct.
LTC_DRIFT_MICROSECONDS_PER_DAY = 58.7


@dataclass(frozen=True)
class LunarTimeStandardStatus:
    """The publication status of a lunar civil time standard, as citable data.

    A deliberately inert record: it asserts no clock reading, only *what has
    been mandated, by whom, when, and on what physical grounds* — so a consumer
    can display or reason about the pending standard without the library
    pretending the standard exists.
    """
    key: str
    #: human-facing name of the standard ("Coordinated Lunar Time").
    name: str
    #: lifecycle state — ``"mandated_unpublished"`` here (directed, not yet
    #: defined).  There is intentionally no ``"published"`` value in this
    #: module; when the standard exists it becomes an implemented axis, not a
    #: status record.
    status: str
    #: the mandating instrument (the 2024 US OSTP policy directive).
    mandate: str
    #: date the mandate was issued.
    mandate_date: date
    #: relativistic drift figure, µs per Earth-day (:data:`LTC_DRIFT_MICROSECONDS_PER_DAY`).
    drift_microseconds_per_day: float
    #: the downloaded, cited source backing every field above.
    source: str


#: The pending-standard record for Coordinated Lunar Time.  Fields are cited to
#: Wikipedia, "Coordinated Lunar Time": the White House OSTP directive of
#: 2 April 2024 tasking NASA
#: with a lunar time standard, and the 58.7 µs/Earth-day relativistic drift
#: that makes an Earth clock the wrong clock on the Moon.
LTC_STATUS = LunarTimeStandardStatus(
    key="coordinated_lunar_time",
    name="Coordinated Lunar Time",
    status="mandated_unpublished",
    mandate="US White House OSTP policy directive to NASA (Celestial Time "
            "Standardization), tasking a lunar time standard by end of 2026",
    mandate_date=date(2024, 4, 2),
    drift_microseconds_per_day=LTC_DRIFT_MICROSECONDS_PER_DAY,
    source="Wikipedia, 'Coordinated Lunar Time'",
)


def _register_lunar_axis() -> TimeAxis:
    """Register (idempotently) the natural lunar-cycle axis in ``AXES``.

    Epoch is the Meeus lunation-0 new moon (:data:`~chronologia.moon.
    EPOCH_NEW_MOON`, 2000-01-06 18:14), so ``count_from_tt`` counts natural
    lunar days == lunations from the same zero the moon-phase arithmetic uses.
    The count is the *natural* cycle only; it carries no civil LTC convention.
    """
    axis = TimeAxis("lunar", LUNAR_DAY_SECONDS, EPOCH_NEW_MOON)
    AXES.setdefault("lunar", axis)
    return AXES["lunar"]


#: The natural lunar-cycle axis (also installed into :data:`~chronologia.axes.AXES`).
LUNAR_AXIS = _register_lunar_axis()


def ltc_offset(instant: Union[AstroDate, datetime, date]) -> float:
    """The Coordinated Lunar Time offset from Earth time at ``instant``.

    **Not implemented, by design.** Coordinated Lunar Time has been *mandated*
    (the 2024 US OSTP directive, see :data:`LTC_STATUS`) but not yet *defined*:
    there is no published zero point and no adopted rate convention, and the
    lunar clock genuinely diverges from Earth's at
    :data:`LTC_DRIFT_MICROSECONDS_PER_DAY` µs/Earth-day, so no honest offset can
    be returned.  This function is the placeholder that names the pending
    standard instead of inventing a value.

    :raises NotImplementedError: always, with the pending standard and its
        cited source in the message.
    """
    raise NotImplementedError(
        f"Coordinated Lunar Time is mandated but not yet published "
        f"({LTC_STATUS.mandate}, {LTC_STATUS.mandate_date.isoformat()}); no "
        f"civil lunar time standard exists to offset against "
        f"(relativistic drift {LTC_DRIFT_MICROSECONDS_PER_DAY} "
        f"microseconds/Earth-day). Source: {LTC_STATUS.source}."
    )
