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
from datetime import date, datetime, time, timedelta
from typing import Optional, Tuple, Union

from chronologia.calendars import gregorian_to_jdn, jdn_to_gregorian
from chronologia.resolution import DateTimeResolution

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


@dataclass(frozen=True, slots=True, eq=False)
class AstroDate:
    """A frozen, tz-naive point in time with an unbounded (astronomical) year.

    Fields mirror ``datetime``: ``year`` (any int), ``month``/``day``
    (default 1), ``hour``/``minute``/``second``/``microsecond`` (default 0).
    Fully duck-typed to ``datetime``'s public API; see the module docstring.
    """
    year: int
    month: int = 1
    day: int = 1
    hour: int = 0
    minute: int = 0
    second: int = 0
    microsecond: int = 0

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

    # -- datetime duck-typing ---------------------------------------------
    def replace(self, year=None, month=None, day=None, hour=None,
                minute=None, second=None, microsecond=None) -> "AstroDate":
        """Return a copy with the given fields replaced (like ``datetime``)."""
        return _dc_replace(
            self,
            **{k: v for k, v in dict(
                year=year, month=month, day=day, hour=hour, minute=minute,
                second=second, microsecond=microsecond).items()
               if v is not None})

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
        """The equivalent ``datetime``, or ``None`` when out of range."""
        if not self.in_datetime_range:
            return None
        return datetime(self.year, self.month, self.day, self.hour,
                        self.minute, self.second, self.microsecond)

    def _year_field(self) -> str:
        if 0 <= self.year <= 9999:
            return f"{self.year:04d}"
        return f"{self.year:+07d}"

    def isoformat(self, sep: str = "T") -> str:
        """ISO 8601 representation, matching ``datetime.isoformat`` exactly.

        The time part is **always** present (``datetime`` never omits it):
        ``2020-01-01T00:00:00``, with microseconds appended only when nonzero,
        exactly as ``datetime``/``time`` do.  Years outside 0..9999 carry an
        explicit sign and >=6 digits (``-003760-09-07T00:00:00``).
        """
        return (f"{self._year_field()}-{self.month:02d}-{self.day:02d}"
                f"{sep}{self.time().isoformat()}")

    def __str__(self) -> str:
        return self.isoformat()

    @classmethod
    def fromisoformat(cls, s: str) -> "AstroDate":
        """Parse the year-expanded ISO form produced by :meth:`isoformat`."""
        import re
        m = re.match(
            r"^([+-]?\d{4,})-(\d{2})-(\d{2})"
            r"(?:[T ](\d{2}):(\d{2}):(\d{2})(?:\.(\d{1,6}))?)?$", s)
        if not m:
            raise ValueError(f"invalid AstroDate isoformat: {s!r}")
        y, mo, d, hh, mm, ss, us = m.groups()
        micro = int((us or "0").ljust(6, "0")) if us else 0
        return cls(int(y), int(mo), int(d),
                   int(hh or 0), int(mm or 0), int(ss or 0), micro)

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
    def _as_total_us(other) -> Optional[int]:
        if isinstance(other, AstroDate):
            return other._total_us()
        if isinstance(other, datetime):
            return AstroDate.from_datetime(other)._total_us()
        if isinstance(other, date):
            return AstroDate.from_date(other)._total_us()
        return None

    def __add__(self, other):
        if isinstance(other, timedelta):
            delta = (other.days * _US_PER_DAY
                     + other.seconds * 1_000_000 + other.microseconds)
            return AstroDate._from_total_us(self._total_us() + delta)
        return NotImplemented

    __radd__ = __add__

    def __sub__(self, other):
        if isinstance(other, timedelta):
            delta = (other.days * _US_PER_DAY
                     + other.seconds * 1_000_000 + other.microseconds)
            return AstroDate._from_total_us(self._total_us() - delta)
        us = self._as_total_us(other)
        if us is None:
            return NotImplemented
        return timedelta(microseconds=self._total_us() - us)

    def __rsub__(self, other):
        us = self._as_total_us(other)
        if us is None:
            return NotImplemented
        return timedelta(microseconds=us - self._total_us())

    # -- comparison & equality --------------------------------------------
    def __eq__(self, other):
        us = self._as_total_us(other)
        return NotImplemented if us is None else self._total_us() == us

    def __ne__(self, other):
        result = self.__eq__(other)
        return result if result is NotImplemented else not result

    def __lt__(self, other):
        us = self._as_total_us(other)
        return NotImplemented if us is None else self._total_us() < us

    def __le__(self, other):
        us = self._as_total_us(other)
        return NotImplemented if us is None else self._total_us() <= us

    def __gt__(self, other):
        us = self._as_total_us(other)
        return NotImplemented if us is None else self._total_us() > us

    def __ge__(self, other):
        us = self._as_total_us(other)
        return NotImplemented if us is None else self._total_us() >= us

    def __hash__(self):
        # Hash-consistent with ``datetime`` for in-range values so that an
        # AstroDate and the equal ``datetime`` collide in dicts/sets.
        if self.in_datetime_range:
            return hash(self.datetime())
        return hash((self.year, self.month, self.day, self.hour,
                     self.minute, self.second, self.microsecond))


# --------------------------------------------------------------------------
# DateSpan: the primitive result of the engine.
# --------------------------------------------------------------------------

# Canonical width (in days) of each derivable resolution class, ascending.
# Referential width IS the uncertainty; ``resolution`` is derived from it and
# never asserted, removing the tag-vs-value inconsistency class.
_RESOLUTION_BY_WIDTH = (
    (1.0, DateTimeResolution.DAY),
    (7.0, DateTimeResolution.WEEK),
    (31.0, DateTimeResolution.MONTH),
    (366.0, DateTimeResolution.YEAR),
    (3653.0, DateTimeResolution.DECADE),
    (36525.0, DateTimeResolution.CENTURY),
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
    """
    start: AstroDate
    end: AstroDate

    def __post_init__(self):
        if not isinstance(self.start, AstroDate) \
                or not isinstance(self.end, AstroDate):
            raise TypeError("DateSpan endpoints must be AstroDate")
        if self.start > self.end:
            raise ValueError(
                f"DateSpan start {self.start} must be <= end {self.end}")

    @property
    def width(self) -> timedelta:
        return self.end - self.start

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
        """The ``DateTimeResolution`` derived from the span's width."""
        days = self.width.total_seconds() / 86400.0
        for limit, res in _RESOLUTION_BY_WIDTH:
            if days <= limit:
                return res
        return DateTimeResolution.MILLENNIUM

    def contains(self, point) -> bool:
        """True when ``point`` (AstroDate/date/datetime) is in ``[start, end)``."""
        return self.start <= point < self.end

    def overlaps(self, other: "DateSpan") -> bool:
        """True when two half-open spans share any instant."""
        return self.start < other.end and other.start < self.end
