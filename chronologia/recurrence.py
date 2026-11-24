"""RFC 5545 recurrence rules (RRULE) over the Julian-Day-Number hub.

A calendar-recurrence engine ("every third Tuesday", "the last Monday of May",
"Friday the 13th") that speaks the vocabulary of :rfc:`5545#section-3.3.10` and
expands rules with integer Julian-Day-Number arithmetic on
:class:`~chronologia.astrodate.AstroDate` / :class:`~chronologia.astrodate.DateSpan`.
There is no ``datetime`` window, so a yearly rule iterates from the year -500
as easily as from 2025.

Supported rule parts: ``FREQ`` (``DAILY`` / ``WEEKLY`` / ``MONTHLY`` /
``YEARLY``), ``INTERVAL``, ``COUNT``, ``UNTIL``, ``BYMONTH``, ``BYWEEKNO``,
``BYYEARDAY``, ``BYMONTHDAY``, ``BYDAY`` (with ordinals such as ``1MO`` /
``-1FR``), ``BYSETPOS`` and ``WKST``.  ``BYHOUR`` / ``BYMINUTE`` pin a clock
time: each matched day then expands to a one-hour span (one minute when
``BYMINUTE`` is given) instead of a day-wide :class:`DateSpan`.  The sub-day
frequencies ``SECONDLY`` / ``MINUTELY`` / ``HOURLY`` and ``BYSECOND`` raise
``ValueError``.

``DTSTART`` follows the strict reading of RFC 5545 section 3.8.5.3: the
recurrence set contains ``DTSTART`` only if it matches the rule.  This differs
from ``python-dateutil``, which always prepends it.  ``DTSTART`` still fixes
the interval phase and supplies defaults for absent rule parts.

:func:`occurrences` refuses an unbounded rule: either the rule (``COUNT`` /
``UNTIL``) or the call (``count=`` / ``until=``) must bound the set.

Sources: IETF RFC 5545 section 3.3.10 (RECUR grammar, the expand/limit
dependency table, the BYDAY notes) and section 3.8.5.3 (the worked examples
that seed the gold tests).
"""
from dataclasses import dataclass
from datetime import date as _date, datetime as _datetime, timedelta
from typing import Any, Dict, Iterator, Optional, Tuple, Union

from chronologia.astrodate import AstroDate, DateSpan, is_leap_year
from chronologia.calendars import (gregorian_to_jdn, iso_week_from_jdn,
                                   jdn_to_gregorian)

__all__ = [
    "Recurrence",
    "HolidayRecurrence",
    "parse_rrule",
    "occurrences",
    "every",
    "nth_weekday_of_month",
    "last_weekday_of_month",
    "WEEKDAYS",
]

# RFC weekday codes -> Python weekday index (Monday == 0 .. Sunday == 6).
WEEKDAYS = {"MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6}
_WD_CODE = {v: k for k, v in WEEKDAYS.items()}
_FREQS = ("DAILY", "WEEKLY", "MONTHLY", "YEARLY")
_SUBDAY_FREQS = ("SECONDLY", "MINUTELY", "HOURLY")
_MONTH_LEN = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)

# A leap-day yearly rule skips three years in four, so empty periods are
# normal; an impossible rule (BYMONTH=2;BYMONTHDAY=30) never hits.  This bound
# tells the two apart.
_MAX_EMPTY_PERIODS = 20_000


class RuleNeverOccursError(ValueError):
    """A rule produced no occurrence in :data:`_MAX_EMPTY_PERIODS` periods."""


#: Ceiling on a declared ``COUNT``, rejected at construction so an abusive
#: ``RRULE:...COUNT=1000000000`` never becomes a ``Recurrence``.  The binding
#: guard is :data:`_MAX_EMITTED_OCCURRENCES`, which also covers a far ``UNTIL``
#: and a call-level ``count=``.
_MAX_COUNT = 100_000

#: Ceiling on the occurrences one expansion emits, checked per occurrence by
#: :func:`occurrences` and by both holiday classes.
_MAX_EMITTED_OCCURRENCES = 100_000

#: Latest day of each month in any year (February 29).
_MAX_MONTH_DAYS = (31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)


# --------------------------------------------------------------------------
# Small JDN helpers (Monday == 0 weekday convention, matching AstroDate).
# --------------------------------------------------------------------------
def _days_in_month(year: int, month: int) -> int:
    if month == 2 and is_leap_year(year):
        return 29
    return _MONTH_LEN[month - 1]


def _weekday(jdn: int) -> int:
    """Monday == 0 .. Sunday == 6 (JDN 0 was a Monday)."""
    return jdn % 7


def _signed(spec: int, value: int, total: int) -> bool:
    """RFC signed-offset match: ``spec`` counts from the start (+n) or the
    end (-n) of a ``total``-long run.  ``value`` is 1-based from the start."""
    if spec > 0:
        return value == spec
    return value == total + spec + 1


def _week_start(jdn: int, wkst: int) -> int:
    """The JDN of the ``wkst``-day on or before ``jdn``."""
    return jdn - ((jdn - wkst) % 7)


def _week1_start(cal_year: int, wkst: int) -> int:
    """JDN of the ``wkst``-day that begins week 1 of ``cal_year``: the first
    week with at least four days of the year (ISO 8601 for ``wkst == 0``)."""
    jan1 = gregorian_to_jdn(cal_year, 1, 1)
    ws = _week_start(jan1, wkst)
    return ws if jan1 - ws <= 3 else ws + 7


def _week_of(jdn: int, wkst: int) -> Tuple[int, int, int]:
    """``(week_year, week_number, weeks_in_week_year)`` for ``jdn``."""
    if wkst == 0:
        iso_year, week, _ = iso_week_from_jdn(jdn)
        total = iso_week_from_jdn(gregorian_to_jdn(iso_year, 12, 28))[1]
        return iso_year, week, total
    year = jdn_to_gregorian(jdn)[0]
    w1 = _week1_start(year, wkst)
    if jdn < w1:
        wy, base = year - 1, _week1_start(year - 1, wkst)
    else:
        w_next = _week1_start(year + 1, wkst)
        if jdn >= w_next:
            wy, base = year + 1, w_next
        else:
            wy, base = year, w1
    week = (jdn - base) // 7 + 1
    total = (_week1_start(wy + 1, wkst) - _week1_start(wy, wkst)) // 7
    return wy, week, total


def _weekday_index(jdn: int, first: int, last: int) -> Tuple[int, int]:
    """1-based position of ``jdn`` among the days sharing its weekday in the
    inclusive JDN range ``[first, last]``, and the count of such days."""
    wd = _weekday(jdn)
    first_occ = first + ((wd - _weekday(first)) % 7)
    idx = (jdn - first_occ) // 7 + 1
    total = (last - first_occ) // 7 + 1
    return idx, total


# --------------------------------------------------------------------------
# The rule object.
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class Recurrence:
    """A frozen, hashable RFC 5545 recurrence rule.

    Build one with :func:`parse_rrule`, :func:`every`,
    :func:`nth_weekday_of_month` or :func:`last_weekday_of_month`; expand it
    with :func:`occurrences`.  ``byday`` holds ``(ordinal_or_None, weekday)``
    pairs with weekday in Monday==0..Sunday==6; ``wkst`` is a weekday index.
    """
    freq: str
    interval: int = 1
    count: Optional[int] = None
    until: Optional[AstroDate] = None
    byday: Tuple[Tuple[Optional[int], int], ...] = ()
    bymonth: Tuple[int, ...] = ()
    bymonthday: Tuple[int, ...] = ()
    byyearday: Tuple[int, ...] = ()
    byweekno: Tuple[int, ...] = ()
    bysetpos: Tuple[int, ...] = ()
    byhour: Tuple[int, ...] = ()
    byminute: Tuple[int, ...] = ()
    wkst: int = 0

    def __post_init__(self):
        _validate(self)

    @property
    def is_bounded(self) -> bool:
        """True when the rule itself limits the set (``COUNT`` or ``UNTIL``)."""
        return self.count is not None or self.until is not None

    def to_string(self) -> str:
        """Serialize back to a canonical ``FREQ=...;...`` RRULE string."""
        parts = [f"FREQ={self.freq}"]
        if self.interval != 1:
            parts.append(f"INTERVAL={self.interval}")
        if self.count is not None:
            parts.append(f"COUNT={self.count}")
        if self.until is not None:
            u = self.until
            stamp = f"{u.year:04d}{u.month:02d}{u.day:02d}"
            if (u.hour, u.minute, u.second):
                stamp += f"T{u.hour:02d}{u.minute:02d}{u.second:02d}"
            parts.append(f"UNTIL={stamp}")
        byday = [("" if o is None else str(o)) + _WD_CODE[w]
                 for o, w in self.byday]
        for key, values in (("BYMONTH", self.bymonth),
                            ("BYWEEKNO", self.byweekno),
                            ("BYYEARDAY", self.byyearday),
                            ("BYMONTHDAY", self.bymonthday),
                            ("BYDAY", byday),
                            ("BYSETPOS", self.bysetpos),
                            ("BYHOUR", self.byhour),
                            ("BYMINUTE", self.byminute)):
            if values:
                parts.append(f"{key}=" + ",".join(map(str, values)))
        if self.wkst != 0:
            parts.append(f"WKST={_WD_CODE[self.wkst]}")
        return ";".join(parts)

    def __str__(self) -> str:
        return self.to_string()

    def to_json(self) -> dict:
        """A ``json.dumps``-ready dict envelope carrying the RRULE string."""
        return {"type": "Recurrence", "rrule": self.to_string()}

    @classmethod
    def from_json(cls, data: dict) -> "Recurrence":
        """Rebuild a :class:`Recurrence` from a :meth:`to_json` envelope."""
        if data.get("type") != "Recurrence":
            raise ValueError(
                f"not a Recurrence envelope: {data.get('type')!r}")
        return parse_rrule(data["rrule"])


def _validate(rec: Recurrence) -> None:
    if rec.freq not in _FREQS:
        if rec.freq in _SUBDAY_FREQS:
            raise ValueError(
                f"FREQ={rec.freq} is a sub-day recurrence, which is out of "
                "scope for this date-level engine (see module docstring)")
        raise ValueError(f"FREQ must be one of {_FREQS}, got {rec.freq!r}")
    if rec.interval < 1:
        raise ValueError(f"INTERVAL must be >= 1, got {rec.interval}")
    if rec.count is not None and rec.until is not None:
        raise ValueError("COUNT and UNTIL MUST NOT both be present (RFC 5545)")
    if rec.count is not None and rec.count < 0:
        raise ValueError(f"COUNT must be >= 0, got {rec.count}")
    if rec.count is not None and rec.count > _MAX_COUNT:
        raise ValueError(
            f"COUNT={rec.count} exceeds the civil-recurrence ceiling "
            f"{_MAX_COUNT}; refusing a rule that would enumerate unboundedly")
    if rec.wkst not in range(7):
        raise ValueError(f"WKST must be a weekday 0..6, got {rec.wkst}")
    for m in rec.bymonth:
        if not 1 <= m <= 12:
            raise ValueError(f"BYMONTH values must be 1..12, got {m}")
    for d in rec.bymonthday:
        if d == 0 or not -31 <= d <= 31:
            raise ValueError(f"BYMONTHDAY values must be -31..-1 or 1..31, got {d}")
    # A rule whose month/day pairs can never occur (30 February) would scan
    # _MAX_EMPTY_PERIODS periods before failing; reject it up front.  A
    # negative day (-1 = last day) is always satisfiable.
    if rec.bymonth and rec.bymonthday:
        if not any(d < 0 or d <= _MAX_MONTH_DAYS[m - 1]
                   for m in rec.bymonth for d in rec.bymonthday):
            raise ValueError(
                f"BYMONTH={rec.bymonth} with BYMONTHDAY={rec.bymonthday} can "
                "never occur (e.g. 30 February); the rule matches no date")
    for d in rec.byyearday:
        if d == 0 or not -366 <= d <= 366:
            raise ValueError(f"BYYEARDAY values must be -366..-1 or 1..366, got {d}")
    for w in rec.byweekno:
        if w == 0 or not -53 <= w <= 53:
            raise ValueError(f"BYWEEKNO values must be -53..-1 or 1..53, got {w}")
    for p in rec.bysetpos:
        if p == 0 or not -366 <= p <= 366:
            raise ValueError(f"BYSETPOS values must be -366..-1 or 1..366, got {p}")
    for h in rec.byhour:
        if not 0 <= h <= 23:
            raise ValueError(f"BYHOUR values must be 0..23, got {h}")
    for mn in rec.byminute:
        if not 0 <= mn <= 59:
            raise ValueError(f"BYMINUTE values must be 0..59, got {mn}")
    if rec.byminute and not rec.byhour:
        raise ValueError("BYMINUTE requires BYHOUR (a bare minute pin is "
                         "ambiguous in this civil clock-pin engine)")
    for ordinal, wd in rec.byday:
        if wd not in range(7):
            raise ValueError(f"BYDAY weekday out of range: {wd}")
        if ordinal is not None and rec.freq not in ("MONTHLY", "YEARLY"):
            raise ValueError(
                "BYDAY with a numeric ordinal (e.g. 1MO) is only valid with "
                f"FREQ=MONTHLY or YEARLY, not {rec.freq}")
    # N/A combinations from the RFC dependency table.
    if rec.byweekno and rec.freq != "YEARLY":
        raise ValueError("BYWEEKNO is only valid with FREQ=YEARLY")
    if rec.byyearday and rec.freq in ("DAILY", "WEEKLY", "MONTHLY"):
        raise ValueError(f"BYYEARDAY MUST NOT be used with FREQ={rec.freq}")
    if rec.bymonthday and rec.freq == "WEEKLY":
        raise ValueError("BYMONTHDAY MUST NOT be used with FREQ=WEEKLY")
    if rec.bysetpos and not (rec.byday or rec.bymonth or rec.bymonthday
                             or rec.byyearday or rec.byweekno):
        raise ValueError("BYSETPOS MUST be used with another BYxxx rule part")


# --------------------------------------------------------------------------
# Parsing.
# --------------------------------------------------------------------------
def _parse_weekdaynum(token: str) -> Tuple[Optional[int], int]:
    code = token[-2:].upper()
    if code not in WEEKDAYS:
        raise ValueError(f"invalid weekday code in BYDAY: {token!r}")
    prefix = token[:-2]
    ordinal: Optional[int] = None
    if prefix not in ("", "+"):
        try:
            ordinal = int(prefix)
        except ValueError:
            raise ValueError(f"invalid BYDAY ordinal: {token!r}")
        if ordinal == 0:
            raise ValueError(f"BYDAY ordinal must be nonzero: {token!r}")
    return ordinal, WEEKDAYS[code]


def _parse_until(value: str) -> AstroDate:
    # A DATE (YYYYMMDD) or DATE-TIME (YYYYMMDDTHHMMSS[Z]).  The value is kept
    # naive: a trailing Z is dropped, not converted.
    date_part, _, time_part = value.partition("T")
    time_part = time_part.rstrip("Zz")
    if len(date_part) < 8 or not date_part.lstrip("+-").isdigit():
        raise ValueError(f"invalid UNTIL date: {value!r}")
    sign = -1 if date_part[0] == "-" else 1
    digits = date_part.lstrip("+-")
    y = sign * int(digits[:-4])
    mo = int(digits[-4:-2])
    d = int(digits[-2:])
    hh = mm = ss = 0
    if time_part:
        if len(time_part) != 6 or not time_part.isdigit():
            raise ValueError(f"invalid UNTIL time: {value!r}")
        hh, mm, ss = int(time_part[:2]), int(time_part[2:4]), int(time_part[4:])
    return AstroDate(y, mo, d, hh, mm, ss)


def parse_rrule(s: str) -> Recurrence:
    """Parse an RFC 5545 ``RRULE`` string (optional ``RRULE:`` prefix).

    Raises ``ValueError`` on an unknown or duplicated part, a malformed value,
    or a sub-day or contradictory rule.

    >>> parse_rrule("FREQ=MONTHLY;BYDAY=FR;BYMONTHDAY=13").freq
    'MONTHLY'
    """
    if not isinstance(s, str):
        raise TypeError(f"RRULE must be a string, got {type(s).__name__}")
    text = s.strip()
    if text.upper().startswith("RRULE:"):
        text = text[6:]
    if not text:
        raise ValueError("empty RRULE")
    fields = {}
    for chunk in text.split(";"):
        if not chunk:
            continue
        if "=" not in chunk:
            raise ValueError(f"malformed RRULE part (no '='): {chunk!r}")
        key, value = chunk.split("=", 1)
        key = key.strip().upper()
        if key in fields:
            raise ValueError(f"duplicate RRULE part: {key}")
        if value == "":
            raise ValueError(f"empty value for RRULE part {key}")
        fields[key] = value.strip()

    if "FREQ" not in fields:
        raise ValueError("RRULE is missing the required FREQ part")

    def _ints(v: str) -> Tuple[int, ...]:
        return tuple(int(x) for x in v.split(","))

    kwargs: Dict[str, Any] = {"freq": fields.pop("FREQ").upper()}
    if "INTERVAL" in fields:
        kwargs["interval"] = int(fields.pop("INTERVAL"))
    if "COUNT" in fields:
        kwargs["count"] = int(fields.pop("COUNT"))
    if "UNTIL" in fields:
        kwargs["until"] = _parse_until(fields.pop("UNTIL"))
    if "WKST" in fields:
        code = fields.pop("WKST").upper()
        if code not in WEEKDAYS:
            raise ValueError(f"invalid WKST: {code!r}")
        kwargs["wkst"] = WEEKDAYS[code]
    for key in ("BYMONTH", "BYMONTHDAY", "BYYEARDAY", "BYWEEKNO", "BYSETPOS"):
        if key in fields:
            kwargs[key.lower()] = _ints(fields.pop(key))
    if "BYDAY" in fields:
        kwargs["byday"] = tuple(_parse_weekdaynum(t)
                                for t in fields.pop("BYDAY").split(","))
    for key in ("BYHOUR", "BYMINUTE"):
        if key in fields:
            kwargs[key.lower()] = _ints(fields.pop(key))
    if "BYSECOND" in fields:
        raise ValueError(
            "BYSECOND is a sub-second rule part, out of scope for this "
            "date-plus-clock-pin engine (see module docstring)")
    if fields:
        raise ValueError(f"unknown RRULE part(s): {sorted(fields)}")
    return Recurrence(**kwargs)


# --------------------------------------------------------------------------
# Friendly constructors.
# --------------------------------------------------------------------------
def _coerce_weekday(value: Union[int, str]) -> int:
    if isinstance(value, int):
        if value not in range(7):
            raise ValueError(f"weekday int must be 0..6, got {value}")
        return value
    code = str(value)[:2].upper()
    if code not in WEEKDAYS:
        raise ValueError(f"unknown weekday: {value!r}")
    return WEEKDAYS[code]


def _coerce_byday(value) -> Tuple[Tuple[Optional[int], int], ...]:
    if isinstance(value, str):
        value = value.split(",")
    if isinstance(value, (tuple, list)):
        out = []
        for item in value:
            if isinstance(item, tuple):
                out.append((item[0], _coerce_weekday(item[1])))
            else:
                out.append(_parse_weekdaynum(str(item).strip()))
        return tuple(out)
    raise TypeError(f"cannot interpret byday={value!r}")


def every(freq: str, **by) -> Recurrence:
    """Pythonic :class:`Recurrence` builder; ``freq`` is case-insensitive.

    Keyword arguments are the lowercase rule parts.  ``byday`` accepts
    ``"1MO"``, ``"MO,WE"``, ``["1MO", "-1FR"]`` or ``(ordinal, weekday)``
    tuples; ``wkst`` accepts a code or an int.

    >>> # U.S. Labor Day: the first Monday of September.
    >>> labor_day = every("yearly", bymonth=9, byday="1MO")
    >>> labor_day.to_string()
    'FREQ=YEARLY;BYMONTH=9;BYDAY=1MO'
    """
    kwargs: Dict[str, Any] = {"freq": freq.upper()}

    def _tup(v):
        return (v,) if isinstance(v, int) else tuple(v)

    for name in ("interval", "count"):
        if name in by:
            kwargs[name] = by.pop(name)
    if "until" in by:
        kwargs["until"] = _as_astro(by.pop("until"))
    for name in ("bymonth", "bymonthday", "byyearday", "byweekno", "bysetpos",
                 "byhour", "byminute"):
        if name in by:
            kwargs[name] = _tup(by.pop(name))
    if "wkst" in by:
        kwargs["wkst"] = _coerce_weekday(by.pop("wkst"))
    if "byday" in by:
        kwargs["byday"] = _coerce_byday(by.pop("byday"))
    if by:
        raise TypeError(f"unexpected recurrence arguments: {sorted(by)}")
    return Recurrence(**kwargs)


def nth_weekday_of_month(n: int, weekday: Union[int, str],
                         month: Optional[int] = None, **extra) -> Recurrence:
    """The ``n``-th ``weekday`` of the month (``n`` may be negative).

    With ``month`` it is a yearly rule (Thanksgiving is
    ``nth_weekday_of_month(4, "TH", month=11)``); without, a monthly rule.
    Extra keyword arguments pass through to :func:`every`.
    """
    wd = _coerce_weekday(weekday)
    if month is not None:
        return every("yearly", bymonth=month, byday=((n, wd),), **extra)
    return every("monthly", byday=((n, wd),), **extra)


def last_weekday_of_month(weekday: Union[int, str],
                          month: Optional[int] = None, **extra) -> Recurrence:
    """The last ``weekday`` of the month: ``nth_weekday_of_month(-1, ...)``."""
    return nth_weekday_of_month(-1, weekday, month=month, **extra)


# --------------------------------------------------------------------------
# Evaluation.
# --------------------------------------------------------------------------
def _matches(rec: Recurrence, jdn: int, dtstart: AstroDate) -> bool:
    """True when the day ``jdn`` satisfies every present BY part and the
    DTSTART-derived defaults for the absent ones."""
    y, m, d = jdn_to_gregorian(jdn)
    wd = _weekday(jdn)

    if rec.bymonth and m not in rec.bymonth:
        return False
    if rec.bymonthday:
        dim = _days_in_month(y, m)
        if not any(_signed(x, d, dim) for x in rec.bymonthday):
            return False
    if rec.byday and not _byday_match(rec, jdn, y, m, wd):
        return False
    if rec.byyearday:
        yd = jdn - gregorian_to_jdn(y, 1, 1) + 1
        ytot = 366 if is_leap_year(y) else 365
        if not any(_signed(x, yd, ytot) for x in rec.byyearday):
            return False
    # The week number is the dearest test, so it runs last.
    if rec.byweekno:
        wy, wn, total = _week_of(jdn, rec.wkst)
        if wy != y or not any(_signed(x, wn, total) for x in rec.byweekno):
            return False

    # DTSTART-derived defaults for the parts the rule leaves unspecified.
    f = rec.freq
    if f == "WEEKLY":
        if not rec.byday and wd != dtstart.weekday():
            return False
    elif f == "MONTHLY":
        if not rec.bymonthday and not rec.byday and d != dtstart.day:
            return False
    elif f == "YEARLY":
        if not _has_finer_day_part(rec):
            if rec.bymonth:
                if d != dtstart.day:
                    return False
            elif m != dtstart.month or d != dtstart.day:
                return False
    return True


def _byday_match(rec: Recurrence, jdn: int, y: int, m: int, wd: int) -> bool:
    for ordinal, bwd in rec.byday:
        if bwd != wd:
            continue
        if ordinal is None:
            return True
        # Ordinal scope: within the month for MONTHLY (and for YEARLY when a
        # BYMONTH narrows it), within the whole year for a bare YEARLY.
        if rec.freq == "YEARLY" and not rec.bymonth:
            first = gregorian_to_jdn(y, 1, 1)
            last = gregorian_to_jdn(y, 12, 31)
        else:
            first = gregorian_to_jdn(y, m, 1)
            last = first + _days_in_month(y, m) - 1
        idx, total = _weekday_index(jdn, first, last)
        if _signed(ordinal, idx, total):
            return True
    return False


def _apply_setpos(rec: Recurrence, days: list) -> list:
    if not rec.bysetpos:
        return days
    n = len(days)
    picked = set()
    for p in rec.bysetpos:
        i = p - 1 if p > 0 else n + p
        if 0 <= i < n:
            picked.add(days[i])
    return sorted(picked)


def _has_finer_day_part(rec: Recurrence) -> bool:
    """Whether a BY part can select a day other than DTSTART's own, which rules
    out the DTSTART-default day/month narrowing."""
    return bool(rec.byweekno or rec.byyearday or rec.bymonthday or rec.byday)


def _candidate_months(rec: Recurrence, dtstart: AstroDate):
    """The months a YEARLY period must test, a superset of the matching ones."""
    if rec.bymonth:
        return sorted(rec.bymonth)
    if not _has_finer_day_part(rec):
        return [dtstart.month]
    return list(range(1, 13))


def _candidate_days_in_month(rec: Recurrence, y: int, m: int,
                             dtstart: AstroDate):
    """The day-of-month numbers to test in month ``(y, m)``, a superset of the
    matching ones: positive ``bymonthday`` alone limits them, a bare rule
    matches only DTSTART's day, anything else needs the whole month."""
    dim = _days_in_month(y, m)
    if (rec.bymonthday and all(x > 0 for x in rec.bymonthday)
            and not rec.byyearday and not rec.byweekno):
        return [x for x in rec.bymonthday if 1 <= x <= dim]
    if not _has_finer_day_part(rec):
        return [dtstart.day] if dtstart.day <= dim else []
    return list(range(1, dim + 1))


def _period_iter(rec: Recurrence, dtstart: AstroDate):
    """Yield ``(period_start_jdn, sorted_matching_jdns)`` for each interval,
    forever.  The caller bounds it with count/until."""
    freq = rec.freq
    start_jdn = gregorian_to_jdn(dtstart.year, dtstart.month, dtstart.day)

    def _keep(candidates):
        return [j for j in candidates if _matches(rec, j, dtstart)]

    if freq == "DAILY":
        cur = start_jdn
        while True:
            yield cur, _keep([cur])
            cur += rec.interval
    elif freq == "WEEKLY":
        cur = _week_start(start_jdn, rec.wkst)
        step = 7 * rec.interval
        while True:
            yield cur, _keep([cur + i for i in range(7)])
            cur += step
    elif freq == "MONTHLY":
        y, m = dtstart.year, dtstart.month
        while True:
            days = [gregorian_to_jdn(y, m, d)
                    for d in _candidate_days_in_month(rec, y, m, dtstart)]
            yield gregorian_to_jdn(y, m, 1), _keep(days)
            total = (y * 12 + (m - 1)) + rec.interval
            y, m = total // 12, total % 12 + 1
    else:  # YEARLY
        y = dtstart.year
        while True:
            # Test only candidate days: a sparse rule would otherwise scan a
            # whole year per hit.
            days = [gregorian_to_jdn(y, m, d)
                    for m in _candidate_months(rec, dtstart)
                    for d in _candidate_days_in_month(rec, y, m, dtstart)]
            yield gregorian_to_jdn(y, 1, 1), _keep(sorted(days))
            y += rec.interval


def _day_span(jdn: int) -> DateSpan:
    start = AstroDate(*jdn_to_gregorian(jdn))
    end = AstroDate(*jdn_to_gregorian(jdn + 1))
    return DateSpan(start, end)


def _spans_for_day(rec: Recurrence, jdn: int) -> Iterator[DateSpan]:
    """The span(s) a matched day contributes: the whole day, or one per pinned
    hour/minute in chronological order."""
    if not rec.byhour:
        yield _day_span(jdn)
        return
    y, m, d = jdn_to_gregorian(jdn)
    minutes = rec.byminute or (0,)
    width = timedelta(minutes=1) if rec.byminute else timedelta(hours=1)
    for h in sorted(rec.byhour):
        for mn in sorted(minutes):
            start = AstroDate(y, m, d, h, mn)
            yield DateSpan(start, start + width)


def occurrences(rec: Recurrence, dtstart, until=None,
                count: Optional[int] = None) -> Iterator[DateSpan]:
    """Expand ``rec`` from ``dtstart`` in chronological order.

    ``dtstart`` (an :class:`AstroDate`, ``date`` or ``datetime``) fixes the
    interval phase and is emitted only if it matches the rule.  A call-level
    ``until`` (inclusive) or ``count`` overrides the rule's own.  Raises
    ``ValueError`` when neither the rule nor the call bounds the expansion.
    """
    dtstart = _as_astro(dtstart)
    eff_until = _as_astro(until) if until is not None else rec.until
    eff_count = count if count is not None else rec.count
    if eff_until is None and eff_count is None:
        raise ValueError(
            "unbounded recurrence: neither the rule nor the call bounds the "
            "set. Pass count=... or until=..., or use a rule with COUNT/UNTIL.")

    start_jdn = gregorian_to_jdn(dtstart.year, dtstart.month, dtstart.day)
    # Each occurrence inherits DTSTART's time of day; UNTIL is compared as a
    # naive wall-clock instant.
    start_tod = (dtstart.hour, dtstart.minute, dtstart.second,
                 dtstart.microsecond)
    until_jdn = None
    until_key = None
    if eff_until is not None:
        until_jdn = gregorian_to_jdn(eff_until.year, eff_until.month,
                                     eff_until.day)
        until_key = (until_jdn, (eff_until.hour, eff_until.minute,
                                 eff_until.second, eff_until.microsecond))

    emitted = 0
    # COUNT=0 yields nothing; the cutoff below runs after a yield.
    if eff_count is not None and eff_count <= 0:
        return
    empty_streak = 0
    for period_start, day_set in _period_iter(rec, dtstart):
        if until_jdn is not None and period_start > until_jdn:
            return
        selected = _apply_setpos(rec, day_set)
        produced = False
        for jdn in selected:
            if jdn < start_jdn:
                continue
            if until_key is not None and (jdn, start_tod) > until_key:
                return
            for span in _spans_for_day(rec, jdn):
                emitted += 1
                if emitted > _MAX_EMITTED_OCCURRENCES:
                    raise ValueError(
                        f"recurrence exceeded the materialisation ceiling of "
                        f"{_MAX_EMITTED_OCCURRENCES} emitted occurrences "
                        "(bounded by the actual expansion, not just the "
                        f"declared COUNT); rule: {rec.to_string()}")
                yield span
                produced = True
                if eff_count is not None and emitted >= eff_count:
                    return
        if produced:
            empty_streak = 0
        else:
            empty_streak += 1
            if empty_streak > _MAX_EMPTY_PERIODS:
                raise RuleNeverOccursError(
                    f"rule produced nothing in {_MAX_EMPTY_PERIODS} "
                    "consecutive periods; it appears never to occur "
                    f"(rule: {rec.to_string()})")


def _as_astro(value) -> AstroDate:
    if isinstance(value, AstroDate):
        return value
    # datetime is a subclass of date, so it is tested first.
    if isinstance(value, _datetime):
        return AstroDate(value.year, value.month, value.day, value.hour,
                         value.minute, value.second, value.microsecond)
    if isinstance(value, _date):
        return AstroDate(value.year, value.month, value.day)
    raise TypeError(
        f"expected AstroDate/date/datetime, got {type(value).__name__}")


# --------------------------------------------------------------------------
# Movable-feast recurrence — a Recurrence variant an RRULE cannot express.
# --------------------------------------------------------------------------
#: Consecutive years without a holiday before the holiday ``occurrences``
#: methods stop.
_MAX_EMPTY_YEARS = 400


@dataclass(frozen=True)
class HolidayRecurrence:
    """The yearly recurrence of a **movable** holiday (Easter, Eid, Passover).

    Its date each year comes from the holiday engine, so no RFC 5545 rule can
    express it: :meth:`occurrences` expands the real dates through
    :data:`chronologia.civil_holidays.WELL_KNOWN_BY_KEY` and :meth:`to_string`
    raises.  ``holiday_key`` is a well-known key (``"easter"``); ``until`` is an
    optional inclusive bound that :meth:`occurrences` uses when the caller
    passes none.  A fixed-date
    holiday (Christmas) is a plain ``YEARLY`` :class:`Recurrence`.
    """

    holiday_key: str
    until: Optional[AstroDate] = None

    def __post_init__(self) -> None:
        from chronologia.civil_holidays import WELL_KNOWN_BY_KEY
        if self.holiday_key not in WELL_KNOWN_BY_KEY:
            raise ValueError(
                f"unknown well-known holiday key: {self.holiday_key!r}")
        if self.until is not None:
            object.__setattr__(self, "until", _as_astro(self.until))

    def occurrences(self, dtstart, until=None,
                    count: Optional[int] = None) -> Iterator[DateSpan]:
        """Yield the holiday's :class:`DateSpan` for each year on/after
        ``dtstart``, bounded by ``count``/``until``.

        A year the feast does not resolve in is skipped; after
        :data:`_MAX_EMPTY_YEARS` consecutive misses the iterator stops.
        """
        from chronologia.civil_holidays import WELL_KNOWN_BY_KEY
        wk = WELL_KNOWN_BY_KEY[self.holiday_key]
        dtstart = _as_astro(dtstart)
        eff_until = _as_astro(until) if until is not None else self.until
        if eff_until is None and count is None:
            raise ValueError(
                "unbounded holiday recurrence: pass count=... or until=...")
        emitted = 0
        empty = 0
        year = dtstart.year
        while True:
            got = wk.span_for(year)
            if got is None:
                empty += 1
                if empty > _MAX_EMPTY_YEARS:
                    return
            else:
                empty = 0
                span = got[0]
                if span.start >= dtstart:
                    if eff_until is not None and span.start > eff_until:
                        return
                    emitted += 1
                    if emitted > _MAX_EMITTED_OCCURRENCES:
                        raise ValueError(
                            "holiday recurrence exceeded the materialisation "
                            f"ceiling of {_MAX_EMITTED_OCCURRENCES} emitted "
                            f"occurrences (holiday: {self.holiday_key!r})")
                    yield span
                    if count is not None and emitted >= count:
                        return
            year += 1

    def to_string(self) -> str:
        raise ValueError(
            f"holiday recurrence {self.holiday_key!r} is a movable feast with "
            "no RFC 5545 RRULE (its civil date is computed by the holiday "
            "engine, not by BY* arithmetic); expand it with occurrences() "
            "instead of serializing it to a rule string")

    def __str__(self) -> str:  # pragma: no cover - mirrors to_string
        return self.to_string()

    def to_json(self) -> dict:
        """A ``json.dumps``-ready envelope carrying the holiday key and,
        when set, the ISO-8601 ``until`` bound."""
        data = {"type": "HolidayRecurrence", "holiday": self.holiday_key}
        if self.until is not None:
            data["until"] = self.until.isoformat()
        return data

    @classmethod
    def from_json(cls, data: dict) -> "HolidayRecurrence":
        """Rebuild a :class:`HolidayRecurrence` from a :meth:`to_json` envelope."""
        if data.get("type") != "HolidayRecurrence":
            raise ValueError(
                f"not a HolidayRecurrence envelope: {data.get('type')!r}")
        until = data.get("until")
        return cls(data["holiday"],
                   AstroDate.fromisoformat(until) if until else None)


# --------------------------------------------------------------------------
# Jurisdiction holiday sets ("every holiday in Portugal").
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class JurisdictionHolidays:
    """Every holiday a jurisdiction observes, as one chronological stream.

    Unlike :class:`HolidayRecurrence` (one named feast), the set is re-queried
    from :mod:`chronologia.civil_holidays` per year.  ``categories`` defaults to
    the public holidays; ``jurisdiction`` is an upper-cased ISO-3166-1 (or
    vacanza market) code and ``subdiv`` an optional subdivision (``"PT-LIS"``).
    It has no RFC 5545 rule, so :meth:`to_string` raises.
    """

    jurisdiction: str
    subdiv: Optional[str] = None
    categories: Optional[Tuple[str, ...]] = ("public",)

    def __post_init__(self) -> None:
        from chronologia.civil_holidays import registry
        code = self.jurisdiction.upper()
        object.__setattr__(self, "jurisdiction", code)
        # Fail at construction, not at the first occurrences() pull.
        try:
            registry._calendar_for(code)
        except KeyError as exc:
            raise ValueError(
                f"unknown jurisdiction: {self.jurisdiction!r}") from exc

    def occurrences(self, dtstart, until=None,
                    count: Optional[int] = None) -> Iterator[DateSpan]:
        """Yield every holiday's :class:`DateSpan` on/after ``dtstart``,
        chronologically, bounded by ``count``/``until``.  ``count`` counts
        holidays, not years.

        After :data:`_MAX_EMPTY_YEARS` consecutive years without a holiday the
        iterator stops.
        """
        from chronologia.civil_holidays import registry
        dtstart = _as_astro(dtstart)
        eff_until = _as_astro(until) if until is not None else None
        if eff_until is None and count is None:
            raise ValueError(
                "unbounded jurisdiction holiday recurrence: pass count=... "
                "or until=...")
        emitted = 0
        empty = 0
        year = dtstart.year
        while True:
            holidays = registry.holidays_for(
                self.jurisdiction, year, self.subdiv, self.categories)
            produced = False
            for holiday in holidays:
                span = holiday.span
                if span.start < dtstart:
                    continue
                if eff_until is not None and span.start > eff_until:
                    return
                emitted += 1
                if emitted > _MAX_EMITTED_OCCURRENCES:
                    raise ValueError(
                        "jurisdiction holiday recurrence exceeded the "
                        f"materialisation ceiling of {_MAX_EMITTED_OCCURRENCES} "
                        f"emitted occurrences (jurisdiction: "
                        f"{self.jurisdiction!r})")
                yield span
                produced = True
                if count is not None and emitted >= count:
                    return
            if produced:
                empty = 0
            else:
                empty += 1
                if empty > _MAX_EMPTY_YEARS:
                    return
            year += 1

    def to_string(self) -> str:
        raise ValueError(
            f"jurisdiction holiday set {self.jurisdiction!r} is not a "
            "single recurring date -- it is a whole calendar's worth of "
            "holidays per year, looked up from the civil-holidays engine, "
            "with no RFC 5545 RRULE; expand it with occurrences() instead "
            "of serializing it to a rule string")

    def __str__(self) -> str:  # pragma: no cover - mirrors to_string
        return self.to_string()

    def to_json(self) -> dict:
        """A ``json.dumps``-ready envelope carrying jurisdiction/subdiv/categories."""
        return {"type": "JurisdictionHolidays", "jurisdiction": self.jurisdiction,
                "subdiv": self.subdiv,
                "categories": (list(self.categories)
                              if self.categories is not None else None)}

    @classmethod
    def from_json(cls, data: dict) -> "JurisdictionHolidays":
        """Rebuild a :class:`JurisdictionHolidays` from a :meth:`to_json` envelope."""
        if data.get("type") != "JurisdictionHolidays":
            raise ValueError(
                f"not a JurisdictionHolidays envelope: {data.get('type')!r}")
        cats = data.get("categories")
        return cls(data["jurisdiction"], data.get("subdiv"),
                   tuple(cats) if cats is not None else None)
