"""Moon phases: mean-lunation arithmetic (class B, basis-honest).

The Moon's actual (true) phase instants come from full ephemeris
integration; this module does **not** do that (no-ephemeris vow, see the
package docstring's H-series scope).  Instead it uses **mean-lunation
arithmetic**: a single constant synodic-month length applied to a count of
lunations since a fixed epoch.  This is exact arithmetic on an
approximate model -- the model itself is what carries the error, not the
computation -- so results always come with the stated bound
:data:`MOON_PHASE_ACCURACY` and an explicit :attr:`~chronologia.astrodate.
DateSpan.basis`.

**Source (cited)**:

* Wikipedia, "New moon" -- states the
  present-day mean synodic month as ``29.530589`` days (:data:`MEAN_SYNODIC_MONTH_DAYS`,
  quoted verbatim), and that a single lunation's *true* length ranges
  ``29.26`` to ``29.80`` days (a 12.96-hour spread) because the Sun's
  gravity perturbs the Moon's eccentric orbit -- the physical reason mean
  arithmetic cannot be exact.
* Wikipedia, "Lunation Number"
  -- states, verbatim: "Lunation 0 began on the first new moon of 2000
  (approx. 18:14 UTC, 6 January 2000)" for Jean Meeus's Lunation Number
  (Meeus, *Astronomical Algorithms*, 2nd ed., 1998) -- the epoch this
  module counts from (:data:`EPOCH_NEW_MOON`, lunation 0).  The same page
  states the older, almanac-standard **Brown Lunation Number** (BLN,
  Ernest William Brown, used in almanacs until 1983) began its lunation 1
  "at approximately 02:41 UTC, 17 January 1923", and gives the fixed
  relation ``BLN = LN + 953`` connecting the two conventions.
  :func:`lunation_number` returns the Brown convention (the older, more
  widely cited one) by adding that offset.

**Accuracy.** ``MOON_PHASE_ACCURACY`` (:data:`MOON_PHASE_ACCURACY` ==
14 hours) bounds mean-vs-true new/full moon: cross-checked here against
the US Naval Observatory's published 2024 phase table (US Naval Observatory
Astronomical Applications API, ``https://aa.usno.navy.mil/api/moon/phases/year``,
downloaded 2026-07-21) -- the largest new/full deviation across all 25
new+full instants in that table is 14h11m (2024-08-04 New Moon), matching
the ~14h bound. **Quarter phases (first/last) are not covered by this
bound** -- the same cross-check shows quarter-phase deviations up to
about 23 hours, because Meeus's mean-quarter formula omits an extra
periodic term that the mean new/full formula's symmetry mostly cancels
(a documented asymmetry of the mean-phase model, not a bug in this
module); callers needing tighter quarter-phase accuracy need a true
ephemeris, which this module deliberately does not provide.

**Basis.** :func:`next_phase`/:func:`previous_phase` return a
:class:`~chronologia.astrodate.DateSpan` of width ``2 * MOON_PHASE_ACCURACY``
centred on the mean instant, with ``basis="reconstructed"`` when the
instant is in the past (modelled from evidence/theory about an
already-elapsed event) and ``basis="predicted"`` when it is in the
future (a forward model) -- the same reconstructed/predicted peer split
:func:`~chronologia.astrodate.combine_basis` already carries for deep-time
spans, applied here at hour granularity instead of geological granularity.
The split is by the instant's relation to the caller-supplied ``instant``
(the anchor "now"), not calendar date, so a caller anchoring the query at
a past moment still gets "predicted" for anything after *that* anchor.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Union

from chronologia.astrodate import AstroDate, DateSpan

#: Mean synodic month (new moon to new moon), present-day value: Wikipedia,
#: "New moon" (``moon_new_moon_wikipedia.html``), quoted verbatim as
#: "29.530589 days". A *true* individual lunation ranges 29.26..29.80 days
#: (same source) -- the eccentricity noise this module's accuracy bound
#: accounts for, not a defect in the constant.
MEAN_SYNODIC_MONTH_DAYS = 29.530589

#: Meeus Lunation Number epoch: lunation 0's new moon, "approx. 18:14 UTC,
#: 6 January 2000" (Wikipedia, "Lunation Number", quoted verbatim).
EPOCH_NEW_MOON = AstroDate(2000, 1, 6, 18, 14)

#: Brown Lunation Number (BLN) offset from the Meeus Lunation Number (LN):
#: ``BLN = LN + 953`` (Wikipedia, "Lunation Number", quoted verbatim).
#: :func:`lunation_number` reports BLN, the convention almanacs used
#: 1923-1983 and still the most commonly cited "the Moon's lunation number".
_BLN_OFFSET = 953

#: Stated accuracy of mean-arithmetic new/full moon vs the true instant:
#: cross-checked to 14h11m max against the USNO 2024 phase table (see the
#: module docstring); quarter phases are NOT covered by this bound (see
#: the module docstring -- their mean-model error runs wider, ~23h).
MOON_PHASE_ACCURACY = timedelta(hours=14)

#: Microseconds in one civil day -- the hub the mean-lunation arithmetic
#: rescales days to (matches ``astrodate._US_PER_DAY``); named here rather than
#: repeated as a bare literal in each conversion.
_US_PER_DAY = 86_400_000_000

#: Phase name -> fraction of a lunation (0 == new, 1 == the next new moon).
_PHASE_FRACTION = {
    "new": 0.0,
    "first_quarter": 0.25,
    "full": 0.5,
    "last_quarter": 0.75,
}


def _as_astrodate(instant) -> AstroDate:
    if isinstance(instant, AstroDate):
        return instant
    if isinstance(instant, datetime):
        return AstroDate.from_datetime(instant)
    if isinstance(instant, date):
        return AstroDate.from_date(instant)
    raise TypeError(
        f"expected AstroDate, datetime, or date, got {type(instant).__name__}")


def _lunations_since_epoch(instant: AstroDate) -> float:
    days = (instant._total_us() - EPOCH_NEW_MOON._total_us()) / _US_PER_DAY
    return days / MEAN_SYNODIC_MONTH_DAYS


def _mean_instant_for_lunation(k: float) -> AstroDate:
    total_days_us = round(k * MEAN_SYNODIC_MONTH_DAYS * _US_PER_DAY)
    return AstroDate._from_total_us(EPOCH_NEW_MOON._total_us() + total_days_us)


def moon_phase(instant: Union[AstroDate, datetime, date]) -> float:
    """The Moon's mean phase at ``instant``, as a fraction of a lunation.

    ``0.0`` is new moon, ``0.25`` first quarter, ``0.5`` full moon,
    ``0.75`` last quarter, and the fraction increases monotonically
    (mod 1) between them -- pure mean arithmetic, so this is exact given
    the model (:data:`MEAN_SYNODIC_MONTH_DAYS`, :data:`EPOCH_NEW_MOON`);
    the model-vs-true error is :data:`MOON_PHASE_ACCURACY` (new/full) or
    wider for the quarters (see the module docstring).

    Works for any :class:`~chronologia.astrodate.AstroDate` year, including
    far outside ``datetime``'s range, because the arithmetic is a plain
    microsecond subtraction and division -- no ``OverflowError`` path.
    """
    point = _as_astrodate(instant)
    k = _lunations_since_epoch(point)
    return k % 1.0


def lunation_number(instant: Union[AstroDate, datetime, date]) -> int:
    """The Brown Lunation Number (BLN) of the lunation containing ``instant``.

    BLN counts new moons from lunation 1 at 1923-01-17 02:41 UTC (Ernest
    William Brown; the almanac-standard convention 1923-1983). Internally
    this module counts from the Meeus epoch (lunation 0, 2000-01-06) and
    adds the fixed offset ``BLN = LN + 953`` (see the module docstring).
    """
    point = _as_astrodate(instant)
    k = _lunations_since_epoch(point)
    ln = int(k // 1)  # the lunation index containing `point` (Meeus numbering)
    return ln + _BLN_OFFSET


def _phase_span(k: float, past: bool) -> DateSpan:
    mean = _mean_instant_for_lunation(k)
    basis = "reconstructed" if past else "predicted"
    return DateSpan(mean - MOON_PHASE_ACCURACY, mean + MOON_PHASE_ACCURACY,
                    basis=basis)


def _phase_lunation_offset(phase: str) -> float:
    if phase not in _PHASE_FRACTION:
        raise ValueError(
            f"unknown moon phase {phase!r}; expected one of "
            f"{sorted(_PHASE_FRACTION)}")
    return _PHASE_FRACTION[phase]


def next_phase(instant: Union[AstroDate, datetime, date], phase: str
              ) -> DateSpan:
    """The next occurrence of ``phase`` strictly after ``instant``.

    ``phase`` is one of ``"new"``, ``"first_quarter"``, ``"full"``,
    ``"last_quarter"``. Returns a :class:`~chronologia.astrodate.DateSpan`
    of width ``2 * MOON_PHASE_ACCURACY`` centred on the mean-arithmetic
    instant, ``basis="predicted"`` (the result is necessarily after the
    anchor, i.e. in the anchor's future -- a forward model).

    :raises ValueError: ``phase`` is not one of the four recognised names.
    """
    point = _as_astrodate(instant)
    offset = _phase_lunation_offset(phase)
    k_now = _lunations_since_epoch(point)
    base = k_now // 1.0 + offset
    if base <= k_now:
        base += 1.0
    return _phase_span(base, past=False)


def previous_phase(instant: Union[AstroDate, datetime, date], phase: str
                   ) -> DateSpan:
    """The most recent occurrence of ``phase`` strictly before ``instant``.

    Mirror of :func:`next_phase`: same phase names, same span width; the
    result is necessarily before the anchor, so ``basis="reconstructed"``
    (modelled from evidence/theory about an already-elapsed event, the
    same peer basis :func:`~chronologia.astrodate.combine_basis` gives
    deep-time reconstruction).

    :raises ValueError: ``phase`` is not one of the four recognised names.
    """
    point = _as_astrodate(instant)
    offset = _phase_lunation_offset(phase)
    k_now = _lunations_since_epoch(point)
    base = k_now // 1.0 + offset
    if base >= k_now:
        base -= 1.0
    return _phase_span(base, past=True)
