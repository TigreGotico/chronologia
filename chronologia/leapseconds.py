"""Leap seconds: UTC <-> TAI <-> GPS conversions on the real (non-POSIX) timescales.

UTC keeps pace with the earth's uneven rotation by inserting occasional
whole leap seconds; TAI (International Atomic Time) and GPS time do not —
they tick continuously from their own epochs. The cumulative offset between
UTC and TAI is therefore not a formula, it is *history*: a tabulated,
periodically-updated fact published by the IERS (Bulletin C) and mirrored
by IANA/IETF as ``leap-seconds.list``. This module ships a parsed copy of
that table (:mod:`chronologia.data`, ``leap_seconds.tab``) with a provenance
header, exposes it as :data:`LEAP_SECONDS`, and provides the conversions.

POSIX/unix time (``chronologia.eras``' ``"unix"`` era, ``time.time()``,
``datetime.timestamp()``) counts **86400 seconds per day, every day** — it
never sees a leap second and is not "smeared" or corrected here in any way.
Unix time and its era in :mod:`chronologia.eras` are simply a different,
leap-second-*agnostic* timescale from the ones in this module; converting
between them and TAI/GPS is out of scope (POSIX itself does not define
what a unix timestamp means across a leap second, so no such conversion
would be well-defined without picking a smearing scheme, e.g. Google/AWS
"leap smear", which this module does not implement or endorse).

Naive-input convention: a naive ``datetime``/``date``/:class:`AstroDate`
passed to any function here is treated as already being UTC (this mirrors
the convention used elsewhere in ``chronologia``, e.g. ``eras.py``'s
"unix" era). An aware ``datetime`` is converted to UTC first via
``astimezone``.

Scope boundaries:

- **Pre-1972**: out of scope. Before 1972-01-01 UTC ran on the "rubber
  second" system (fractional, continuously-adjusted UTC-UT1 corrections,
  not whole leap seconds) — a fundamentally different mechanism that would
  need its own cited table. Calling any function here with an instant
  before 1972-01-01 raises ``ValueError``.
- **Beyond the table**: the table is complete only through
  :data:`TABLE_VALID_UNTIL` (the source list's stated expiry — IERS
  Bulletin C announces a new leap second roughly six months ahead of it,
  so the table can always be trusted at least that far past "today").
  Instants beyond that date are still accepted, but the offset returned
  for them is a **predicted basis**: the last known cumulative offset,
  assumed constant (i.e. "no further leap second has been announced yet"),
  not a guarantee that none will occur.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from importlib import resources
from typing import Tuple, Union

from chronologia.astrodate import AstroDate

__all__ = [
    "LEAP_SECONDS",
    "TABLE_VALID_UNTIL",
    "table_valid_until",
    "utc_tai_offset",
    "utc_to_tai",
    "tai_to_utc",
    "utc_to_gps",
    "gps_to_utc",
    "utc_to_tt",
    "tt_to_utc",
    "is_leap_second_day",
    "GPS_EPOCH",
    "TAI_MINUS_GPS",
    "TT_MINUS_TAI",
]

Instant = Union[date, datetime, AstroDate]

# TAI - GPS is a fixed constant: GPS time was set to equal TAI - 19s at the
# GPS epoch and has never itself stepped for leap seconds since.
TAI_MINUS_GPS = 19

# GPS epoch: 1980-01-06T00:00:00 UTC == 1980-01-06T00:00:00 GPS (offset 0).
GPS_EPOCH = date(1980, 1, 6)

_DATA_PACKAGE = "chronologia.data"
_DATA_FILE = "leap_seconds.tab"

# First tabulated date; before this UTC used fractional "rubber seconds",
# not whole leap seconds, and is out of scope for this module.
_TABLE_START = date(1972, 1, 1)


@dataclass(frozen=True, slots=True)
class _LeapSecondsTable:
    entries: Tuple[Tuple[date, int], ...]
    valid_until: date


def _parse_table(text: str) -> _LeapSecondsTable:
    entries = []
    valid_until = None
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            if "table_valid_until:" in stripped:
                token = stripped.split("table_valid_until:", 1)[1].strip()
                valid_until = date.fromisoformat(token.split()[0])
            continue
        date_str, offset_str = stripped.split("\t")
        entries.append((date.fromisoformat(date_str), int(offset_str)))
    if valid_until is None:
        raise ValueError(
            f"{_DATA_FILE}: missing '# table_valid_until: YYYY-MM-DD' "
            "provenance header")
    return _LeapSecondsTable(entries=tuple(entries), valid_until=valid_until)


def _load_table() -> _LeapSecondsTable:
    text = resources.files(_DATA_PACKAGE).joinpath(_DATA_FILE).read_text()
    return _parse_table(text)


_TABLE = _load_table()

#: Tuple of ``(utc_date, cumulative_utc_tai_offset_seconds)`` pairs, one per
#: row of the source table: the initial 1972-01-01 baseline (offset 10) plus
#: all 27 leap seconds inserted 1972-06-30 through 2016-12-31 (each row's
#: date is the day the *new* offset takes effect, i.e. one day after the
#: leap second itself). Sorted ascending by date.
LEAP_SECONDS: Tuple[Tuple[date, int], ...] = _TABLE.entries

#: The date through which :data:`LEAP_SECONDS` is confirmed complete absent
#: a further IERS Bulletin C announcement (the source list's stated
#: expiry). See the module docstring's "beyond the table" scope note.
TABLE_VALID_UNTIL: date = _TABLE.valid_until


def table_valid_until() -> date:
    """Return :data:`TABLE_VALID_UNTIL` (the table's confirmed-complete date)."""
    return TABLE_VALID_UNTIL


def _as_ymd(instant: Instant) -> Tuple[int, int, int]:
    if isinstance(instant, AstroDate):
        return instant.year, instant.month, instant.day
    if isinstance(instant, datetime):
        if instant.tzinfo is not None:
            instant = instant.astimezone(timezone.utc)
        return instant.year, instant.month, instant.day
    if isinstance(instant, date):
        return instant.year, instant.month, instant.day
    raise TypeError(
        f"expected date, datetime or AstroDate, got {type(instant).__name__}")


def utc_tai_offset(instant: Instant) -> int:
    """Cumulative UTC-TAI offset (whole seconds, TAI ahead of UTC) at *instant*.

    *instant* may be a naive or aware ``datetime``, a ``date``, or an
    :class:`AstroDate` (see the module docstring's naive-input convention).
    Raises ``ValueError`` for any instant before 1972-01-01 (the rubber-second
    era, out of scope). For instants beyond :data:`TABLE_VALID_UNTIL` the last
    tabulated offset is returned as a predicted basis (assumed constant).
    """
    ymd = _as_ymd(instant)
    if ymd < (_TABLE_START.year, _TABLE_START.month, _TABLE_START.day):
        raise ValueError(
            f"{ymd[0]:04d}-{ymd[1]:02d}-{ymd[2]:02d} is before 1972-01-01: "
            "pre-1972 UTC used fractional 'rubber second' corrections, not "
            "whole leap seconds, and is out of scope for chronologia.leapseconds")
    offset = LEAP_SECONDS[0][1]
    for effective_date, cumulative_offset in LEAP_SECONDS:
        key = (effective_date.year, effective_date.month, effective_date.day)
        if ymd >= key:
            offset = cumulative_offset
        else:
            break
    return offset


def is_leap_second_day(day: Instant) -> bool:
    """True if *day* is a UTC calendar date on which a leap second (23:59:60)
    was inserted, i.e. the day immediately before one of :data:`LEAP_SECONDS`'
    dates (excluding the initial 1972-01-01 baseline row, which is not itself
    a leap-second insertion).
    """
    ymd = _as_ymd(day)
    for effective_date, _ in LEAP_SECONDS[1:]:
        preceding = effective_date - timedelta(days=1)
        if ymd == (preceding.year, preceding.month, preceding.day):
            return True
    return False


def utc_to_tai(instant: datetime) -> datetime:
    """Convert a UTC ``datetime`` to the equivalent TAI ``datetime``.

    TAI is ahead of UTC by :func:`utc_tai_offset` whole seconds. The
    naive-input convention applies; the result is naive and represents TAI.
    """
    offset = utc_tai_offset(instant)
    return instant + timedelta(seconds=offset)


def tai_to_utc(instant: datetime) -> datetime:
    """Convert a TAI ``datetime`` to the equivalent UTC ``datetime``.

    Approximates by first estimating the UTC offset from *instant* treated
    as if it were UTC (off by at most the offset itself, never enough to
    cross a table boundary in practice), then re-checks against the
    resulting UTC date so a same-day round trip with :func:`utc_to_tai` is
    always exact.
    """
    offset = utc_tai_offset(instant)
    candidate = instant - timedelta(seconds=offset)
    offset2 = utc_tai_offset(candidate)
    if offset2 != offset:
        candidate = instant - timedelta(seconds=offset2)
    return candidate


def utc_to_gps(instant: datetime) -> datetime:
    """Convert a UTC ``datetime`` to the equivalent GPS-time ``datetime``.

    GPS - UTC = (TAI - UTC) - (TAI - GPS) = :func:`utc_tai_offset` -
    :data:`TAI_MINUS_GPS`. Before the GPS epoch (1980-01-06) this is
    well-defined but GPS time did not yet exist as a broadcast signal.
    """
    offset = utc_tai_offset(instant) - TAI_MINUS_GPS
    return instant + timedelta(seconds=offset)


def gps_to_utc(instant: datetime) -> datetime:
    """Convert a GPS-time ``datetime`` to the equivalent UTC ``datetime``."""
    offset = utc_tai_offset(instant) - TAI_MINUS_GPS
    candidate = instant - timedelta(seconds=offset)
    offset2 = utc_tai_offset(candidate) - TAI_MINUS_GPS
    if offset2 != offset:
        candidate = instant - timedelta(seconds=offset2)
    return candidate


# TT - TAI is a defining constant: Terrestrial Time runs 32.184 s ahead of TAI
# for all time (the offset that made TT continuous with the older Ephemeris
# Time at 1977-01-01).  Unlike the UTC-TAI offset it is never tabulated and
# never steps.
TT_MINUS_TAI = 32.184


def utc_to_tt(instant: Instant) -> Instant:
    """Convert a UTC instant to Terrestrial Time (``TT = TAI + 32.184 s``).

    TT is the smooth timescale on which every :class:`~chronologia.axes.TimeAxis`
    epoch is fixed, so this is the bridge from civil UTC into axis space (Mars
    Sol Date and friends).  ``TT - UTC = utc_tai_offset(instant) + 32.184 s``.
    *instant* may be an :class:`AstroDate`, ``datetime`` or ``date`` (naive-input
    convention as elsewhere in this module); the result is the same type, naive,
    and represents TT.  Raises ``ValueError`` before 1972 (out of the
    leap-second table's scope).
    """
    seconds = utc_tai_offset(instant) + TT_MINUS_TAI
    return instant + timedelta(seconds=seconds)


def tt_to_utc(instant: Instant) -> Instant:
    """Convert a Terrestrial Time instant to the equivalent UTC instant.

    Inverse of :func:`utc_to_tt`.  Estimates the offset from *instant* treated
    as UTC (never enough off to cross a table boundary in practice), then
    re-checks against the resulting UTC date so a same-instant round trip with
    :func:`utc_to_tt` is exact.
    """
    seconds = utc_tai_offset(instant) + TT_MINUS_TAI
    candidate = instant - timedelta(seconds=seconds)
    seconds2 = utc_tai_offset(candidate) + TT_MINUS_TAI
    if seconds2 != seconds:
        candidate = instant - timedelta(seconds=seconds2)
    return candidate
