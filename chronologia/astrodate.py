"""AstroDate: a datetime-compatible point with an unbounded year.

``datetime`` only represents years 1..9999 — its C-level bounds are hard.
Phrases like "44 BC", "the year 12000" or "5 Tishrei 5785" name instants
outside that window, so this module provides a frozen, tz-naive **point**
that carries the full ``year..microsecond`` field set of ``datetime`` but
lets the year be any integer (astronomical numbering: 1 BC == year 0,
proleptic Gregorian).

Subclassing ``datetime`` is impossible (the year bounds are exactly what is
being escaped), so compatibility is protocol-based: AstroDate duck-types
``datetime``'s public API — ``replace``/``weekday``/``isoweekday``/
``isocalendar``/``toordinal``/``date``/``time``/``isoformat``/``strftime``,
``timedelta`` arithmetic, and comparisons **and equality** that interoperate
with ``date``/``datetime`` (equal instant ⇒ equal, hash-consistent with
``datetime`` for in-range values).  A test walks ``datetime``'s public API
and asserts AstroDate answers every member.

AstroDate carries no imprecision: there are no optional calendar fields and
no resolution tag — referential width lives in :class:`DateSpan`, not here.

The proleptic-Gregorian ordinal / weekday math routes through
``calendars.gregorian_to_jdn`` / ``jdn_to_gregorian`` (the JDN hub), so this
module and the calendar layer never disagree.  ``date.toordinal()`` uses
RD (Rata Die, 0001-01-01 == 1); JDN(0001-01-01) == 1721426, hence
``ordinal == jdn - 1721425``.
"""
from __future__ import annotations

from dataclasses import dataclass, replace as _dc_replace
from datetime import date, datetime, time, timedelta, timezone, tzinfo
from typing import Optional, Tuple, Union

from chronologia.calendars import gregorian_to_jdn, jdn_to_gregorian
from chronologia.resolution import DateTimeResolution
from chronologia.timelines import (CivilLabel, Discontinuity,
                                   DiscontinuityKind, NeverExisted)

# Sentinel so ``replace(tzinfo=None)`` can *clear* the zone (as ``datetime``
# does) while an omitted ``tzinfo`` argument leaves it untouched.
_KEEP = object()

# JDN of RD 1 (proleptic Gregorian 0001-01-01); ordinal = jdn - this.
_RD_TO_JDN = 1721425
_US_PER_DAY = 86_400_000_000

_DAYS_IN_MONTH = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)


def is_leap_year(year: int) -> bool:
    """Proleptic Gregorian leap rule, valid for any year including <= 0.

    ``calendar.isleap`` implements the same formula but is documented for the
    stdlib range only; this spelling makes the negative-year contract explicit.
    """
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def _days_in_month(year: int, month: int) -> int:
    if month == 2 and is_leap_year(year):
        return 29
    return _DAYS_IN_MONTH[month - 1]


def _td_us(td: timedelta) -> int:
    """A ``timedelta`` as a signed microsecond count (unbounded int)."""
    return td.days * _US_PER_DAY + td.seconds * 1_000_000 + td.microseconds


@dataclass(frozen=True, slots=True, eq=False)
class AstroDate:
    """A frozen, tz-naive point in time with an unbounded (astronomical) year.

    Fields mirror ``datetime``: ``year`` (any int), ``month``/``day``
    (default 1), ``hour``/``minute``/``second``/``microsecond`` (default 0),
    and an optional ``tzinfo`` (default ``None`` => naive).  Fully duck-typed
    to ``datetime``'s public API; see the module docstring.

    **Aware/naive semantics mirror ``datetime`` exactly.**  A naive AstroDate
    (``tzinfo is None``) compares by wall-clock fields; an aware one compares
    by the instant it names (wall minus ``utcoffset()``).  Mixing the two
    never compares equal and raises ``TypeError`` on ordering, precisely as
    ``datetime`` does.  ``utcoffset()``/``tzname()``/``dst()`` delegate to the
    attached ``tzinfo``.  Because the year may fall outside ``datetime``'s
    1..9999 window (where a ``zoneinfo`` zone has no tabulated data), those
    lookups use a **proxy year** ``2000 + (year % 400)`` — the proleptic
    Gregorian calendar (and therefore every recurring DST rule keyed to a
    month/weekday) repeats with a 400-year period, so the proxy shares the
    real year's leap status and weekday pattern.  This *extrapolates the
    zone's current recurring rule* across all of time; it does not and cannot
    reconstruct historical offset changes (a zone's pre-1970 data is used
    as-is by ``zoneinfo`` where the real year is in range, with the usual
    caveats about its reliability, and is simply unavailable out of range).
    """
    year: int
    month: int = 1
    day: int = 1
    hour: int = 0
    minute: int = 0
    second: int = 0
    microsecond: int = 0
    tzinfo: Optional[tzinfo] = None

    def __post_init__(self):
        if self.month is None or not 1 <= self.month <= 12:
            raise ValueError(f"month must be in 1..12, got {self.month}")
        limit = _days_in_month(self.year, self.month)
        if self.day is None or not 1 <= self.day <= limit:
            raise ValueError(f"day must be in 1..{limit} for "
                             f"year={self.year} month={self.month}, "
                             f"got {self.day}")
        if not 0 <= self.hour <= 23:
            raise ValueError(f"hour must be in 0..23, got {self.hour}")
        if not 0 <= self.minute <= 59:
            raise ValueError(f"minute must be in 0..59, got {self.minute}")
        if not 0 <= self.second <= 59:
            raise ValueError(f"second must be in 0..59, got {self.second}")
        if not 0 <= self.microsecond <= 999_999:
            raise ValueError(f"microsecond must be in 0..999999, "
                             f"got {self.microsecond}")

    # -- era conveniences (not part of the datetime API) -------------------
    @property
    def is_bc(self) -> bool:
        """True for years before the common era (astronomical year <= 0)."""
        return self.year <= 0

    @property
    def bc_year(self) -> int:
        """The year in BC counting (1 BC = year 0, so BC = 1 - year)."""
        if not self.is_bc:
            raise ValueError(f"year {self.year} is not BC")
        return 1 - self.year

    @property
    def in_datetime_range(self) -> bool:
        return date.min.year <= self.year <= date.max.year

    # -- tz-aware duck-typing ---------------------------------------------
    def _proxy_datetime(self) -> datetime:
        """A naive ``datetime`` for handing to ``tzinfo`` offset lookups.

        In-range years pass through unchanged; out-of-range years map to
        ``2000 + (year % 400)`` (see the class docstring) so a ``zoneinfo``
        zone's recurring rule is still evaluable.  The proxy shares the real
        year's leap status, so 29 February is preserved.
        """
        if self.in_datetime_range:
            py = self.year
        else:
            py = 2000 + (self.year % 400)
        return datetime(py, self.month, self.day, self.hour, self.minute,
                        self.second, self.microsecond)

    def utcoffset(self) -> Optional[timedelta]:
        """The offset from UTC, or ``None`` when naive (``tzinfo`` protocol)."""
        if self.tzinfo is None:
            return None
        return self.tzinfo.utcoffset(self._proxy_datetime())

    def tzname(self) -> Optional[str]:
        """The zone's name for this instant, or ``None`` when naive."""
        if self.tzinfo is None:
            return None
        return self.tzinfo.tzname(self._proxy_datetime())

    def dst(self) -> Optional[timedelta]:
        """The daylight-saving adjustment, or ``None`` when naive."""
        if self.tzinfo is None:
            return None
        return self.tzinfo.dst(self._proxy_datetime())

    @property
    def _is_aware(self) -> bool:
        return self.tzinfo is not None and self.utcoffset() is not None

    def astimezone(self, tz: tzinfo) -> "AstroDate":
        """Return the same instant expressed in ``tz`` (aware -> aware).

        A **naive** AstroDate raises ``ValueError`` — a documented deviation
        from modern ``datetime.astimezone`` (which assumes the system local
        zone).  That assumption is a well-known footgun; requiring an explicit
        ``replace(tzinfo=...)`` first makes the intended zone unambiguous.
        """
        if not self._is_aware:
            raise ValueError(
                "astimezone() cannot convert a naive AstroDate: it has no "
                "zone to convert from. Attach one with replace(tzinfo=...) "
                "first (AstroDate does not assume a system-local zone).")
        # Shift the wall clock by (target_offset - self_offset) at this
        # instant; the instant itself is preserved.  The delta is read from a
        # proxy-year round trip so it works identically in and out of range.
        proxy_self = self._proxy_datetime().replace(tzinfo=self.tzinfo)
        proxy_target = proxy_self.astimezone(tz)
        delta = (proxy_target.replace(tzinfo=None)
                 - proxy_self.replace(tzinfo=None))
        shifted = AstroDate._from_total_us(self._total_us() + _td_us(delta))
        return shifted.replace(tzinfo=tz)

    # -- datetime duck-typing ---------------------------------------------
    def replace(self, year=None, month=None, day=None, hour=None,
                minute=None, second=None, microsecond=None,
                tzinfo=_KEEP) -> "AstroDate":
        """Return a copy with the given fields replaced (like ``datetime``).

        ``replace(tzinfo=...)`` is **label-preserving**: it re-labels the same
        wall-clock reading with a new zone, it does not convert the instant
        (that is :meth:`astimezone`).  Passing ``tzinfo=None`` clears the zone.
        """
        changes = {k: v for k, v in dict(
            year=year, month=month, day=day, hour=hour, minute=minute,
            second=second, microsecond=microsecond).items()
            if v is not None}
        if tzinfo is not _KEEP:
            changes["tzinfo"] = tzinfo
        return _dc_replace(self, **changes)

    def toordinal(self) -> int:
        """Proleptic Gregorian ordinal (0001-01-01 == 1), a plain int.

        Consistent with ``date.toordinal`` for in-range values; negative and
        huge values are just integers.
        """
        return gregorian_to_jdn(self.year, self.month, self.day) - _RD_TO_JDN

    @classmethod
    def fromordinal(cls, ordinal: int) -> "AstroDate":
        y, m, d = jdn_to_gregorian(ordinal + _RD_TO_JDN)
        return cls(y, m, d)

    def weekday(self) -> int:
        """Monday == 0 .. Sunday == 6 (like ``date.weekday``)."""
        return (self.toordinal() - 1) % 7

    def isoweekday(self) -> int:
        """Monday == 1 .. Sunday == 7 (like ``date.isoweekday``)."""
        return self.weekday() + 1

    def isocalendar(self) -> Tuple[int, int, int]:
        """(ISO year, ISO week, ISO weekday), computed for any year."""
        ordinal = self.toordinal()
        iso_weekday = self.isoweekday()
        thursday = ordinal - iso_weekday + 4
        iso_year = AstroDate.fromordinal(thursday).year
        jan1 = AstroDate(iso_year, 1, 1).toordinal()
        week = (thursday - jan1) // 7 + 1
        return (iso_year, week, iso_weekday)

    def date(self) -> Optional[date]:
        """The equivalent ``datetime.date``, or ``None`` when out of range."""
        if not self.in_datetime_range:
            return None
        return date(self.year, self.month, self.day)

    def time(self) -> time:
        """The time-of-day component as a ``datetime.time``."""
        return time(self.hour, self.minute, self.second, self.microsecond)

    def datetime(self) -> Optional[datetime]:
        """The equivalent ``datetime``, or ``None`` when out of range.

        Carries ``tzinfo`` through, so an aware AstroDate yields an aware
        ``datetime`` (a naive one stays naive — byte-identical to before).
        """
        if not self.in_datetime_range:
            return None
        return datetime(self.year, self.month, self.day, self.hour,
                        self.minute, self.second, self.microsecond,
                        tzinfo=self.tzinfo)

    def _year_field(self) -> str:
        if 0 <= self.year <= 9999:
            return f"{self.year:04d}"
        return f"{self.year:+07d}"

    def isoformat(self, sep: str = "T") -> str:
        """ISO 8601 representation, matching ``datetime.isoformat`` exactly.

        The time part is **always** present (``datetime`` never omits it):
        ``2020-01-01T00:00:00``, with microseconds appended only when nonzero,
        exactly as ``datetime``/``time`` do.  Years outside 0..9999 carry an
        explicit sign and >=6 digits (``-003760-09-07T00:00:00``).  When aware,
        the UTC-offset suffix is appended just as ``datetime`` does
        (``...T12:00:00-04:00``).
        """
        off = self.utcoffset()
        suffix = ""
        if off is not None:
            total = _td_us(off) // 1_000_000
            sign = "+" if total >= 0 else "-"
            total = abs(total)
            hh, rem = divmod(total, 3600)
            mm, ss = divmod(rem, 60)
            suffix = f"{sign}{hh:02d}:{mm:02d}" + (f":{ss:02d}" if ss else "")
        return (f"{self._year_field()}-{self.month:02d}-{self.day:02d}"
                f"{sep}{self.time().isoformat()}{suffix}")

    def __str__(self) -> str:
        return self.isoformat()

    @classmethod
    def fromisoformat(cls, s: str) -> "AstroDate":
        """Parse the year-expanded ISO form produced by :meth:`isoformat`."""
        import re
        m = re.match(
            r"^([+-]?\d{4,})-(\d{2})-(\d{2})"
            r"(?:[T ](\d{2}):(\d{2}):(\d{2})(?:\.(\d{1,6}))?)?"
            r"(Z|[+-]\d{2}:\d{2}(?::\d{2})?)?$", s)
        if not m:
            raise ValueError(f"invalid AstroDate isoformat: {s!r}")
        y, mo, d, hh, mm, ss, us, tz = m.groups()
        micro = int((us or "0").ljust(6, "0")) if us else 0
        zone = None
        if tz == "Z":
            zone = timezone.utc
        elif tz:
            osign = -1 if tz[0] == "-" else 1
            parts = [int(p) for p in tz[1:].split(":")]
            osecs = parts[0] * 3600 + parts[1] * 60 + (parts[2] if len(parts) > 2 else 0)
            zone = timezone(timedelta(seconds=osign * osecs))
        return cls(int(y), int(mo), int(d),
                   int(hh or 0), int(mm or 0), int(ss or 0), micro, tzinfo=zone)

    @classmethod
    def from_date(cls, d: date) -> "AstroDate":
        """Build from a ``datetime.date`` (date fields only)."""
        return cls(d.year, d.month, d.day)

    @classmethod
    def from_datetime(cls, dt: datetime) -> "AstroDate":
        """Build from a ``datetime`` (all fields; tzinfo is dropped)."""
        return cls(dt.year, dt.month, dt.day, dt.hour, dt.minute,
                   dt.second, dt.microsecond)

    def strftime(self, fmt: str) -> str:
        """Format the year-width-safe directive subset of ``strftime``.

        Supports ``%Y %m %d %H %M %S %f %j %W`` (and ``%%``); every other
        directive is rejected, because C ``strftime`` truncates or refuses
        the out-of-range years this type exists to carry.
        """
        out = []
        i = 0
        while i < len(fmt):
            ch = fmt[i]
            if ch != "%":
                out.append(ch)
                i += 1
                continue
            if i + 1 >= len(fmt):
                raise ValueError("dangling % in format string")
            code = fmt[i + 1]
            i += 2
            if code == "%":
                out.append("%")
            elif code == "Y":
                out.append(self._year_field())
            elif code == "m":
                out.append(f"{self.month:02d}")
            elif code == "d":
                out.append(f"{self.day:02d}")
            elif code == "H":
                out.append(f"{self.hour:02d}")
            elif code == "M":
                out.append(f"{self.minute:02d}")
            elif code == "S":
                out.append(f"{self.second:02d}")
            elif code == "f":
                out.append(f"{self.microsecond:06d}")
            elif code == "j":
                doy = self.toordinal() - AstroDate(self.year, 1, 1).toordinal() + 1
                out.append(f"{doy:03d}")
            elif code == "W":
                doy = self.toordinal() - AstroDate(self.year, 1, 1).toordinal() + 1
                jan1_wd = AstroDate(self.year, 1, 1).weekday()
                out.append(f"{(doy + jan1_wd - 1) // 7:02d}")
            else:
                raise ValueError(
                    f"strftime directive %{code} is not year-width-safe; "
                    f"AstroDate supports %Y %m %d %H %M %S %f %j %W")
        return "".join(out)

    # -- arithmetic --------------------------------------------------------
    def _total_us(self) -> int:
        return (self.toordinal() * _US_PER_DAY
                + ((self.hour * 3600 + self.minute * 60 + self.second)
                   * 1_000_000) + self.microsecond)

    @classmethod
    def _from_total_us(cls, total: int) -> "AstroDate":
        us = total % 1_000_000
        secs = total // 1_000_000
        sec_of_day = secs % 86_400
        ordinal = secs // 86_400
        base = cls.fromordinal(ordinal)
        return cls(base.year, base.month, base.day,
                   sec_of_day // 3600, (sec_of_day % 3600) // 60,
                   sec_of_day % 60, us)

    @staticmethod
    def _operand_key(other) -> Optional[Tuple[bool, int]]:
        """``(is_aware, key_us)`` for a date-like operand, else ``None``.

        ``key_us`` is the wall-clock microsecond count for a naive operand and
        the **instant** (wall minus ``utcoffset``) for an aware one, so aware
        values compare and subtract by the moment they name.
        """
        if isinstance(other, AstroDate):
            wall = other._total_us()
            off = other.utcoffset()
        elif isinstance(other, datetime):
            wall = AstroDate.from_datetime(other)._total_us()
            off = other.utcoffset()
        elif isinstance(other, date):
            wall = AstroDate.from_date(other)._total_us()
            off = None
        else:
            return None
        if off is None:
            return (False, wall)
        return (True, wall - _td_us(off))

    def __add__(self, other):
        if isinstance(other, timedelta):
            return (AstroDate._from_total_us(self._total_us() + _td_us(other))
                    .replace(tzinfo=self.tzinfo))
        return NotImplemented

    __radd__ = __add__

    def __sub__(self, other):
        if isinstance(other, timedelta):
            return (AstroDate._from_total_us(self._total_us() - _td_us(other))
                    .replace(tzinfo=self.tzinfo))
        right = self._operand_key(other)
        if right is None:
            return NotImplemented
        left = self._operand_key(self)
        if left[0] != right[0]:
            raise TypeError("can't subtract offset-naive and offset-aware "
                            "AstroDate/datetime values")
        return timedelta(microseconds=left[1] - right[1])

    def __rsub__(self, other):
        right = self._operand_key(other)
        if right is None:
            return NotImplemented
        left = self._operand_key(self)
        if left[0] != right[0]:
            raise TypeError("can't subtract offset-naive and offset-aware "
                            "AstroDate/datetime values")
        return timedelta(microseconds=right[1] - left[1])

    # -- comparison & equality --------------------------------------------
    def __eq__(self, other):
        right = self._operand_key(other)
        if right is None:
            return NotImplemented
        left = self._operand_key(self)
        if left[0] != right[0]:
            return False  # naive and aware are never equal (datetime parity)
        return left[1] == right[1]

    def __ne__(self, other):
        result = self.__eq__(other)
        return result if result is NotImplemented else not result

    def _order(self, other):
        """Shared ordering key pair, raising like ``datetime`` on mismatch."""
        right = self._operand_key(other)
        if right is None:
            return None
        left = self._operand_key(self)
        if left[0] != right[0]:
            raise TypeError("can't compare offset-naive and offset-aware "
                            "AstroDate/datetime values")
        return (left[1], right[1])

    def __lt__(self, other):
        keys = self._order(other)
        return NotImplemented if keys is None else keys[0] < keys[1]

    def __le__(self, other):
        keys = self._order(other)
        return NotImplemented if keys is None else keys[0] <= keys[1]

    def __gt__(self, other):
        keys = self._order(other)
        return NotImplemented if keys is None else keys[0] > keys[1]

    def __ge__(self, other):
        keys = self._order(other)
        return NotImplemented if keys is None else keys[0] >= keys[1]

    def __hash__(self):
        # Hash-consistent with ``datetime``: an in-range AstroDate hashes as
        # the equal ``datetime`` (naive by wall, aware by instant), so the two
        # collide in dicts/sets.  Out of range there is no datetime, so the
        # (awareness, key) pair is hashed instead — still eq-consistent.
        if self.in_datetime_range:
            return hash(self.datetime())
        aware, key = self._operand_key(self)
        return hash((aware, key))


# --------------------------------------------------------------------------
# Wall-clock resolution against a zone: fold (REPEAT) and gap (SKIP).
# --------------------------------------------------------------------------

def _fold_offsets(y, m, d, h, mi, zone):
    """``(off0, off1)`` — the ``fold=0`` / ``fold=1`` offsets of a wall time.

    Evaluated at a proxy year when ``y`` is outside ``datetime``'s range, so a
    ``zoneinfo`` zone's recurring rule still resolves (see AstroDate docstring).
    """
    py = y if date.min.year <= y <= date.max.year else 2000 + (y % 400)
    off0 = datetime(py, m, d, h, mi, tzinfo=zone, fold=0).utcoffset()
    off1 = datetime(py, m, d, h, mi, tzinfo=zone, fold=1).utcoffset()
    return off0, off1


def resolve_wall_clock(y: int, m: int, d: int, h: int, mi: int, zone: tzinfo
                       ) -> Union["AstroDate", Tuple["AstroDate", "AstroDate"],
                                  NeverExisted]:
    """Resolve a civil wall-clock reading against a DST-bearing ``zone``.

    Three outcomes, following PEP 495's fold model:

    * **unique** — the wall time occurs exactly once: an aware
      :class:`AstroDate` in ``zone``.
    * **REPEAT** (fall-back fold — the offset *shrinks*, so the clock repeats
      an hour): a ``(earlier, later)`` tuple of the two real instants.  Each is
      carried in a **fixed-offset** zone (the offset actually in force for that
      occurrence), because AstroDate has no fold bit — this keeps the identical
      wall reading yet gives the pair distinct, comparable instants.
    * **SKIP** (spring-forward gap — the offset *grows*, so the clock jumps and
      the reading never happens): a :class:`~chronologia.timelines.NeverExisted`
      carrying a synthetic :class:`~chronologia.timelines.Discontinuity` of kind
      ``SKIP`` — a real "never existed + why" answer, never an error.
    """
    off0, off1 = _fold_offsets(y, m, d, h, mi, zone)
    if off0 == off1:
        return AstroDate(y, m, d, h, mi, tzinfo=zone)
    if off0 > off1:  # fall back: two occurrences of one wall time
        earlier = AstroDate(y, m, d, h, mi, tzinfo=timezone(off0))
        later = AstroDate(y, m, d, h, mi, tzinfo=timezone(off1))
        return (earlier, later)
    # off0 < off1: spring-forward gap -- this wall time never existed
    jdn = AstroDate(y, m, d).toordinal() + _RD_TO_JDN
    disc = Discontinuity(
        jdn, DiscontinuityKind.SKIP,
        (y, m, d), (y, m, d),
        f"DST spring-forward gap at {h:02d}:{mi:02d} in zone "
        f"{getattr(zone, 'key', zone)!r}: the local clock jumps from "
        f"UTC{off0} to UTC{off1}, so this wall-clock reading never occurred")
    return NeverExisted(CivilLabel(y, m, d), disc)


# --------------------------------------------------------------------------
# Dual arithmetic: civil (calendar/zone/timeline-aware) vs absolute (+delta).
# --------------------------------------------------------------------------

def civil_add(point_or_span, *, years: int = 0, months: int = 0, days: int = 0,
              zone: Optional[tzinfo] = None, timeline=None):
    """Calendar-aware **civil** arithmetic — the counterpart to ``+ timedelta``.

    Absolute arithmetic (``point + timedelta``) always advances a real
    duration.  ``civil_add`` instead walks the *civil* calendar:

    * ``years`` / ``months`` shift the calendar fields and **clamp** the day of
      month (31 Jan + 1 month -> 28/29 Feb — the last valid day, never spilling
      into March), like ``dateutil.relativedelta`` and most calendar UIs.
    * ``days`` add whole calendar days preserving the wall-clock time.  With a
      DST ``zone`` the real elapsed time across a transition is 23 or 25 hours,
      not 24 (the result is aware in ``zone``; subtract two aware points to see
      the true duration).  Without a zone it is a plain field shift.
    * ``timeline`` routes the day step through civil labels: the point's
      ``(year, month, day)`` is read as a civil label, converted to JDN, the
      days added there, and converted back — so adding one day to Julian
      ``1582-10-04`` under ``rome_1582`` lands on Gregorian ``1582-10-15``,
      crossing the reform seam.

    ``point_or_span`` may be an :class:`AstroDate` (returns an AstroDate) or a
    :class:`DateSpan` (shifts both endpoints, returns a DateSpan).
    """
    if isinstance(point_or_span, DateSpan):
        span = point_or_span
        return DateSpan(
            civil_add(span.start, years=years, months=months, days=days,
                      zone=zone, timeline=timeline),
            civil_add(span.end, years=years, months=months, days=days,
                      zone=zone, timeline=timeline),
            basis=span.basis)

    pt = point_or_span
    y, m, d = pt.year, pt.month, pt.day
    if years or months:
        total = (y * 12 + (m - 1)) + years * 12 + months
        y, nm0 = divmod(total, 12)
        m = nm0 + 1
        d = min(d, _days_in_month(y, m))

    if days and timeline is not None:
        jdn = timeline.to_jdn((y, m, d))
        if not isinstance(jdn, int):
            raise ValueError(
                f"civil_add: label {(y, m, d)} is not a single JDN on "
                f"timeline {getattr(timeline, 'key', timeline)!r} "
                f"(got {jdn!r}); cannot step days across it")
        label = timeline.from_jdn(jdn + days)
        return AstroDate(label.year, label.month, label.day,
                         pt.hour, pt.minute, pt.second, pt.microsecond,
                         tzinfo=pt.tzinfo)

    if days:
        base = AstroDate(y, m, d)
        shifted = AstroDate.fromordinal(base.toordinal() + days)
        y, m, d = shifted.year, shifted.month, shifted.day

    tz = zone if zone is not None else pt.tzinfo
    return AstroDate(y, m, d, pt.hour, pt.minute, pt.second, pt.microsecond,
                     tzinfo=tz)


# --------------------------------------------------------------------------
# WideDuration: a span width that overflows ``timedelta``.
# --------------------------------------------------------------------------

# Mean Gregorian year, in microseconds: 365.2425 days.  Used only to split a
# geological span into a whole-year count plus a sub-year remainder — never in
# ``AstroDate`` field math, which stays exact and calendar-based.
_MEAN_YEAR_US = 365_2425 * 86_400 * 1_000_000 // 10_000  # 365.2425 days in us


@dataclass(frozen=True, slots=True)
class WideDuration:
    """A signed duration too large for :class:`datetime.timedelta`.

    ``timedelta`` caps at ``±999_999_999`` days (~2.74 million years), so the
    width of a geological span (a Jurassic interval is tens of millions of
    years) cannot be represented as one.  :attr:`DateSpan.width` returns a
    plain ``timedelta`` whenever the span fits — byte-identical to
    ``end - start`` — and a ``WideDuration`` only when it would otherwise
    ``OverflowError``.

    The value is stored as a whole number of **mean Gregorian years**
    (365.2425 days) plus a ``remainder`` ``timedelta`` strictly smaller than
    one such year, so ``remainder`` always fits.  The split is a *reporting*
    convenience — the authoritative magnitude is the total microsecond count
    the two encode, exposed by :meth:`total_seconds` and used for all
    comparisons.  ``WideDuration`` is orderable and equality-comparable
    against both other ``WideDuration`` values and ``timedelta`` (a
    ``timedelta`` is simply a magnitude that happens to be small enough to fit
    one), so a geological width and an ordinary width compare cleanly.
    """
    years: int
    remainder: timedelta

    @classmethod
    def _from_us(cls, total_us: int) -> "WideDuration":
        years = total_us // _MEAN_YEAR_US
        return cls(years, timedelta(microseconds=total_us - years * _MEAN_YEAR_US))

    def _total_us(self) -> int:
        rem_us = (self.remainder.days * _US_PER_DAY
                  + self.remainder.seconds * 1_000_000
                  + self.remainder.microseconds)
        return self.years * _MEAN_YEAR_US + rem_us

    def total_seconds(self) -> float:
        """Total length in seconds (mirrors ``timedelta.total_seconds``)."""
        return self._total_us() / 1_000_000

    @staticmethod
    def _other_us(other) -> Optional[int]:
        if isinstance(other, WideDuration):
            return other._total_us()
        if isinstance(other, timedelta):
            return (other.days * _US_PER_DAY + other.seconds * 1_000_000
                    + other.microseconds)
        return None

    def __eq__(self, other):
        us = self._other_us(other)
        return NotImplemented if us is None else self._total_us() == us

    def __ne__(self, other):
        result = self.__eq__(other)
        return result if result is NotImplemented else not result

    def __lt__(self, other):
        us = self._other_us(other)
        return NotImplemented if us is None else self._total_us() < us

    def __le__(self, other):
        us = self._other_us(other)
        return NotImplemented if us is None else self._total_us() <= us

    def __gt__(self, other):
        us = self._other_us(other)
        return NotImplemented if us is None else self._total_us() > us

    def __ge__(self, other):
        us = self._other_us(other)
        return NotImplemented if us is None else self._total_us() >= us

    def __hash__(self):
        return hash(self._total_us())


# --------------------------------------------------------------------------
# DateSpan: the primitive result of the engine.
# --------------------------------------------------------------------------

# Basis lattice: how the endpoints of a span were established, worst-of.  See
# :func:`combine_basis`.
BASIS_EXACT = "exact"
BASIS_TABULATED = "tabulated"
BASIS_RECONSTRUCTED = "reconstructed"
BASIS_PREDICTED = "predicted"

# Certainty rank, ascending imprecision.  ``exact`` is the bottom (identity)
# element; ``reconstructed`` and ``predicted`` are *peers* at the same rank —
# both are modelled rather than observed, one from evidence about the past,
# one from a forward model — so neither is "worse" than the other.
_BASIS_RANK = {
    BASIS_EXACT: 0,
    BASIS_TABULATED: 1,
    BASIS_RECONSTRUCTED: 2,
    BASIS_PREDICTED: 2,
}


def combine_basis(*bases: str) -> str:
    """Worst-of over the basis lattice ``exact < tabulated < {reconstructed,
    predicted}``.

    Combining the bases of several inputs yields the *least certain* — a span
    built from an exact endpoint and a tabulated one is only as trustworthy as
    the tabulated one.  The lattice is a total order except for the top pair:
    ``reconstructed`` and ``predicted`` are peers (equal rank).  When a
    combination mixes exactly those two differing peers, the result is
    ``reconstructed`` — an arbitrary but stable tie-break (documented, not
    meaningful: neither peer is more certain, so the lattice needs a canonical
    representative and the past-facing label is chosen).

    Properties (exercised by the tests): idempotent, commutative, associative,
    monotone worst-of; ``exact`` is the identity, so ``combine_basis()`` and
    ``combine_basis("exact", x)`` both reduce cleanly.
    """
    worst = BASIS_EXACT
    for b in bases:
        if b not in _BASIS_RANK:
            raise ValueError(f"unknown basis {b!r}; expected one of "
                             f"{sorted(_BASIS_RANK)}")
        if _BASIS_RANK[b] > _BASIS_RANK[worst]:
            worst = b
        elif _BASIS_RANK[b] == _BASIS_RANK[worst] and b != worst \
                and _BASIS_RANK[b] == 2:
            # two differing peers -> canonical representative
            worst = BASIS_RECONSTRUCTED
    return worst


# Canonical width (in days) of each derivable resolution class, ascending.
# Referential width IS the uncertainty; ``resolution`` is derived from it and
# never asserted, removing the tag-vs-value inconsistency class.  The tail
# (millennium and up) carries the deep-time tiers; see
# :class:`~chronologia.resolution.DateTimeResolution` for the threshold
# rationale.  ``EON`` is the open-topped fallback.
_RESOLUTION_BY_WIDTH = (
    (1.0, DateTimeResolution.DAY),
    (7.0, DateTimeResolution.WEEK),
    (31.0, DateTimeResolution.MONTH),
    (366.0, DateTimeResolution.YEAR),
    (3653.0, DateTimeResolution.DECADE),
    (36525.0, DateTimeResolution.CENTURY),
    (3_652_500.0, DateTimeResolution.MILLENNIUM),          # up to ~10 kyr
    (3_652_500_000.0, DateTimeResolution.EPOCH_GEOLOGICAL),  # ~10 kyr..10 Myr
    (36_525_000_000.0, DateTimeResolution.PERIOD_GEOLOGICAL),  # ..100 Myr
    (182_625_000_000.0, DateTimeResolution.ERA_GEOLOGICAL),  # ..~500 Myr
)


@dataclass(frozen=True, slots=True)
class DateSpan:
    """A frozen half-open interval ``[start, end)`` of :class:`AstroDate`.

    Width IS the uncertainty/error bar: a point is a minimal-width span
    ("3 pm" == ``[15:00, 15:01)``), "june" is a month-wide span ending exactly
    where "july" begins.  Points, imprecise references, durations, seasons,
    eras and explicit ranges all unify under this one type.  The span answers
    *which stretch of time was referred to*, never parser confidence.
    ``DateTimeResolution`` is derived from :attr:`width`, never stored.

    :attr:`basis` records *how* the endpoints were established — ``exact``
    (default, so every existing construction is unchanged), ``tabulated`` (a
    deterministic table that may differ from observation, e.g. the tabular
    Hijri), ``reconstructed`` (modelled from evidence about the past, e.g. a
    radiometric deep-time date) or ``predicted`` (a forward model).  It rides
    alongside width and never affects it; :func:`combine_basis` is the
    worst-of rule for propagating it when spans are combined.
    """
    start: AstroDate
    end: AstroDate
    basis: str = BASIS_EXACT

    def __post_init__(self):
        if not isinstance(self.start, AstroDate) \
                or not isinstance(self.end, AstroDate):
            raise TypeError("DateSpan endpoints must be AstroDate")
        if self.start > self.end:
            raise ValueError(
                f"DateSpan start {self.start} must be <= end {self.end}")
        if self.basis not in _BASIS_RANK:
            raise ValueError(f"unknown basis {self.basis!r}; expected one of "
                             f"{sorted(_BASIS_RANK)}")

    @property
    def _delta_us(self) -> int:
        """Total width in microseconds as an unbounded int (never overflows)."""
        return self.end._total_us() - self.start._total_us()

    @property
    def width(self):
        """The span's width.

        Returns a plain ``datetime.timedelta`` whenever the interval fits one
        (byte-identical to ``end - start``); for a geological span that would
        overflow ``timedelta`` it returns a :class:`WideDuration` instead.
        """
        try:
            return timedelta(microseconds=self._delta_us)
        except OverflowError:
            return WideDuration._from_us(self._delta_us)

    @property
    def start_datetime(self) -> Optional[datetime]:
        """The start as a real ``datetime``, or ``None`` when out of range."""
        return self.start.datetime()

    @property
    def end_datetime(self) -> Optional[datetime]:
        """The end as a real ``datetime``, or ``None`` when out of range."""
        return self.end.datetime()

    @property
    def resolution(self) -> DateTimeResolution:
        """The ``DateTimeResolution`` derived from the span's width.

        Computed straight from the microsecond delta so a geological width
        (which has no ``timedelta``) is classified without overflow; ``EON``
        is the open-topped fallback above the largest threshold.
        """
        days = self._delta_us / float(_US_PER_DAY)
        for limit, res in _RESOLUTION_BY_WIDTH:
            if days <= limit:
                return res
        return DateTimeResolution.EON

    def contains(self, point) -> bool:
        """True when ``point`` (AstroDate/date/datetime) is in ``[start, end)``."""
        return self.start <= point < self.end

    def overlaps(self, other: "DateSpan") -> bool:
        """True when two half-open spans share any instant."""
        return self.start < other.end and other.start < self.end
