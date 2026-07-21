"""Timezones as timelines: a materialized view over zoneinfo's transitions.

A timezone *is* the :mod:`~chronologia.timelines` mechanism at clock
granularity — a jurisdiction's history of civil label-mappings, where the
"label" is a wall-clock reading and the "reform" is a daylight-saving or
standard-offset jump.  But the two layers store fundamentally different things:

* ``tzdb`` (what :mod:`zoneinfo` reads) stores **rules** — intensional,
  recurring law: "spring forward on the second Sunday of March, forever".
* a :class:`~chronologia.timelines.Timeline` stores **events** — extensional,
  one-time facts: "on this JDN a pope skipped ten days".

So this module is an **adapter, not a copy**.  It does not re-encode any zone
rule; it *materializes* a zone's rule into the extensional event vocabulary
over a finite ``[start, end)`` window — enumerating the actual UTC transitions
in range and emitting one :class:`ZoneDiscontinuity` per transition, reusing
the day-level :class:`~chronologia.timelines.DiscontinuityKind` vocabulary:

* a **fall-back** (offset *decreases*, e.g. UTC-4 → UTC-5) re-lives a wall-clock
  window → :attr:`DiscontinuityKind.REPEAT`;
* a **spring-forward** (offset *increases*) deletes one → :attr:`DiscontinuityKind.SKIP`.

Why a parallel :class:`ClockTimeline` instead of reusing :class:`Timeline`
-------------------------------------------------------------------------
:class:`~chronologia.timelines.Timeline` is **day-granular by construction**:
its segments and its ``to_jdn`` / ``from_jdn`` speak Julian Day *Numbers*,
whole days with no time-of-day.  A zone transition happens at a specific
*minute*, and its REPEAT/SKIP windows are sub-day (one wall-clock hour), so
forcing it into JDN space would discard exactly the information that makes it a
timezone.  Rather than break the day-level API, this module carries a minimal
parallel :class:`ClockTimeline` whose ``to_instant`` / ``from_instant`` are the
clock-granular analogues of ``to_jdn`` / ``from_jdn`` (returning aware
``datetime`` instants), while borrowing the same discontinuity *vocabulary*.

Enumeration method and resolution
---------------------------------
:mod:`zoneinfo` exposes **no public list of transitions**, so
:func:`zone_timeline` finds them by observation: it walks ``[start, end)`` at
**day resolution**, comparing the zone's UTC offset one day to the next, and
whenever the offset changes it **bisects that day down to the minute** to locate
the transition instant.  The resolution is therefore **one minute** (real IANA
transitions land on minute boundaries, usually the whole hour); a hypothetical
transition shorter than a day that both began and ended between two sampled days
could be missed, but no real civil zone has one.  :func:`zone_history_start`
uses the same walk-then-bisect over historical years.

The pre-1970 caveat (documented in ``docs/timezones.md``): IANA states its
pre-1970 data is *not reliable*.  :func:`zone_history_start` reports what
``zoneinfo`` actually returns and cites ``tzdb`` as the source of record — it is
a faithful surfacing of the database, not an independent historical claim.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple, Union, cast

from chronologia.timelines import DiscontinuityKind

try:  # zoneinfo is stdlib on 3.9+; tzdata supplies the data where the OS lacks it
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover - Python < 3.9 not supported
    ZoneInfo = None  # type: ignore

_UTC = timezone.utc
_DAY = timedelta(days=1)
_MINUTE = timedelta(minutes=1)


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def _as_tz(tz):
    """Coerce a zone name or ``tzinfo`` to a ``tzinfo``."""
    if isinstance(tz, str):
        if ZoneInfo is None:  # pragma: no cover
            raise RuntimeError("zoneinfo unavailable; install tzdata")
        return ZoneInfo(tz)
    return tz


def _as_utc(dt: datetime) -> datetime:
    """A naive ``datetime`` is read as UTC; an aware one is converted to UTC."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=_UTC)
    return dt.astimezone(_UTC)


def _offset_at(tz, instant_utc: datetime) -> timedelta:
    """The zone's UTC offset in force at a UTC instant."""
    return cast(timedelta, instant_utc.astimezone(tz).utcoffset())


def _fmt_offset(td: timedelta) -> str:
    """Render an offset as ``UTC-5`` / ``UTC+5:30`` / ``UTC+0`` for a citation."""
    total = int(td.total_seconds())
    sign = "-" if total < 0 else "+"
    total = abs(total)
    hours, rem = divmod(total, 3600)
    minutes = rem // 60
    return f"UTC{sign}{hours}" + (f":{minutes:02d}" if minutes else "")


def _bisect_transition(tz, lo: datetime, hi: datetime,
                       off_lo: timedelta) -> datetime:
    """First UTC instant in ``(lo, hi]`` whose offset differs from ``off_lo``.

    Both bounds are UTC; ``off_lo`` is the offset at ``lo``.  Narrows to the
    minute, then reports the minute boundary the new offset first holds.
    """
    while hi - lo > _MINUTE:
        mid = lo + (hi - lo) / 2
        if _offset_at(tz, mid) == off_lo:
            lo = mid
        else:
            hi = mid
    return hi.replace(second=0, microsecond=0)


# --------------------------------------------------------------------------
# the clock-granular view
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class ZoneNeverExisted:
    """Typed result: a wall-clock reading a spring-forward gap deleted.

    The clock-granular sibling of :class:`chronologia.timelines.NeverExisted`,
    carrying the :class:`ZoneDiscontinuity` responsible.
    """
    wall: datetime
    discontinuity: "ZoneDiscontinuity"


@dataclass(frozen=True)
class ZoneDiscontinuity:
    """One UTC transition, in the day-level :class:`DiscontinuityKind` vocabulary.

    ``instant`` is the aware-UTC moment the offset changes; ``offset_before`` /
    ``offset_after`` are the UTC offsets straddling it.  ``before_wall`` and
    ``after_wall`` are the *naive* wall-clock readings of that instant under the
    two offsets — the two faces of the seam.  ``kind`` is REPEAT for a fall-back
    (offset decrease) and SKIP for a spring-forward (offset increase).
    ``citation`` names the offsets and the zone.
    """
    instant: datetime
    kind: DiscontinuityKind
    offset_before: timedelta
    offset_after: timedelta
    citation: str

    @property
    def before_wall(self) -> datetime:
        """Naive wall reading of :attr:`instant` under the outgoing offset."""
        return (self.instant + self.offset_before).replace(tzinfo=None)

    @property
    def after_wall(self) -> datetime:
        """Naive wall reading of :attr:`instant` under the incoming offset."""
        return (self.instant + self.offset_after).replace(tzinfo=None)


@dataclass(frozen=True)
class ClockSegment:
    """A stretch of constant UTC offset: from :attr:`start` (aware UTC) onward."""
    start: datetime
    offset: timedelta


@dataclass(frozen=True)
class ClockTimeline:
    """A zone's ``[start, end)`` history as an ordered clock-granular view.

    The clock-granular analogue of :class:`chronologia.timelines.Timeline`:
    :meth:`from_instant` (instant → wall reading) mirrors ``from_jdn`` and
    :meth:`to_instant` (wall reading → instant, a pair, or a
    :class:`ZoneNeverExisted`) mirrors ``to_jdn`` — at clock, not day, grain.
    """
    key: str
    start: datetime
    end: datetime
    segments: Tuple[ClockSegment, ...]
    discontinuities: Tuple[ZoneDiscontinuity, ...] = ()

    def offset_at(self, instant: datetime) -> timedelta:
        """The UTC offset in force at a UTC instant."""
        instant = _as_utc(instant)
        found = self.segments[0].offset
        for seg in self.segments:
            if seg.start <= instant:
                found = seg.offset
            else:
                break
        return found

    def from_instant(self, instant: datetime) -> datetime:
        """Naive wall-clock reading of an instant (Seam 2 — never ambiguous)."""
        instant = _as_utc(instant)
        return (instant + self.offset_at(instant)).replace(tzinfo=None)

    def to_instant(self, wall: datetime
                   ) -> Union[datetime, Tuple[datetime, datetime],
                              ZoneNeverExisted]:
        """Instant(s) a naive wall reading maps to (Seam 1 — the honest answer).

        One aware-UTC ``datetime`` for the ordinary case, an ``(earlier,
        later)`` pair across a REPEAT (fall-back fold), or a
        :class:`ZoneNeverExisted` inside a SKIP (spring-forward gap).
        """
        wall = wall.replace(tzinfo=None)
        for d in self.discontinuities:
            if d.kind is DiscontinuityKind.SKIP:
                if d.before_wall <= wall < d.after_wall:
                    return ZoneNeverExisted(wall, d)
            else:  # REPEAT
                if d.after_wall <= wall < d.before_wall:
                    earlier = (wall - d.offset_before).replace(tzinfo=_UTC)
                    later = (wall - d.offset_after).replace(tzinfo=_UTC)
                    return earlier, later
        # unique: find the segment whose wall-interval contains this reading
        offset = self.segments[0].offset
        for seg in self.segments:
            if seg.start + seg.offset <= wall.replace(tzinfo=_UTC):
                offset = seg.offset
            else:
                break
        return (wall - offset).replace(tzinfo=_UTC)


# --------------------------------------------------------------------------
# the adapter
# --------------------------------------------------------------------------

def zone_timeline(tz, start: datetime, end: datetime) -> ClockTimeline:
    """Materialize a zone's transitions over ``[start, end)`` as a view.

    Walks the window at day resolution, bisecting each offset change to the
    minute (see the module docstring), and returns a :class:`ClockTimeline`
    whose segments carry the offset in force and whose discontinuities are one
    :class:`ZoneDiscontinuity` per transition (REPEAT for a fall-back, SKIP for
    a spring-forward), the offsets recorded in each citation.

    ``tz`` is a zone name or any ``tzinfo``; ``start`` / ``end`` are treated as
    UTC (naive is read as UTC, aware is converted).
    """
    tzinfo = _as_tz(tz)
    name = str(tz) if isinstance(tz, str) else getattr(tzinfo, "key", str(tzinfo))
    start_u, end_u = _as_utc(start), _as_utc(end)

    off0 = _offset_at(tzinfo, start_u)
    segments: List[ClockSegment] = [ClockSegment(start_u, off0)]
    discontinuities: List[ZoneDiscontinuity] = []

    cur, prev_off = start_u, off0
    while cur < end_u:
        nxt = min(cur + _DAY, end_u)
        off = _offset_at(tzinfo, nxt)
        if off != prev_off:
            instant = _bisect_transition(tzinfo, cur, nxt, prev_off)
            # ``off`` is the post-transition offset (one day past ``cur``, no
            # civil zone has two transitions in a day); re-reading at the
            # minute-rounded ``instant`` would misfire for odd-second LMT seams.
            after = off
            kind = (DiscontinuityKind.REPEAT if after < prev_off
                    else DiscontinuityKind.SKIP)
            citation = (f"{_fmt_offset(prev_off)} -> {_fmt_offset(after)} "
                        f"({name})")
            discontinuities.append(ZoneDiscontinuity(
                instant, kind, prev_off, after, citation))
            segments.append(ClockSegment(instant, after))
            prev_off = after
        cur = nxt

    return ClockTimeline(f"zone:{name}", start_u, end_u,
                         tuple(segments), tuple(discontinuities))


def zone_history_start(tz, search_from: int = 1800, search_to: int = 1970
                       ) -> Optional[Tuple[datetime, timedelta, timedelta]]:
    """The zone's first transition out of Local Mean Time.

    Every ``tzdb`` zone opens with an LMT offset (raw longitude, odd-minute) and
    a first transition to a rounded standard offset when the jurisdiction
    adopted standard time.  Returns ``(instant, lmt_offset, first_standard_offset)``
    for that first transition, or ``None`` if none is found in the search range.

    Found by the same walk-then-bisect as :func:`zone_timeline`, at monthly
    resolution over ``[search_from, search_to)`` then bisected to the minute.
    The values are **whatever ``zoneinfo`` reports** — cite ``tzdb``, and heed
    its own warning that pre-1970 data is not reliable (see ``docs/timezones.md``).
    """
    tzinfo = _as_tz(tz)
    cur = datetime(search_from, 1, 1, tzinfo=_UTC)
    end = datetime(search_to, 1, 1, tzinfo=_UTC)
    step = timedelta(days=30)
    prev_off = _offset_at(tzinfo, cur)
    lmt = prev_off
    while cur < end:
        nxt = min(cur + step, end)
        off = _offset_at(tzinfo, nxt)
        if off != prev_off:
            instant = _bisect_transition(tzinfo, cur, nxt, prev_off)
            return instant, lmt, off
        prev_off = off
        cur = nxt
    return None
