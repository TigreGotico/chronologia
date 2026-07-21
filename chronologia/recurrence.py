"""RFC 5545 recurrence rules (RRULE) over the Julian-Day-Number hub.

A calendar-recurrence engine — "every third Tuesday", "the last Monday of
May", "Friday the 13th" — expressed with the vocabulary of
:rfc:`5545#section-3.3.10` (the iCalendar ``RECUR`` value type) and evaluated
by pure integer arithmetic on :class:`~chronologia.astrodate.AstroDate` /
:class:`~chronologia.astrodate.DateSpan`.  Because expansion is nothing but
Julian-Day-Number math, a yearly rule iterates just as happily from the year
-500 as from 2025: there is no ``datetime`` window and nothing overflows.

Scope — **date-level recurrence only**
--------------------------------------
This engine implements the *date*-generating rule parts of RFC 5545:

    ``FREQ`` (``DAILY`` / ``WEEKLY`` / ``MONTHLY`` / ``YEARLY``), ``INTERVAL``,
    ``COUNT``, ``UNTIL``, ``BYMONTH``, ``BYWEEKNO``, ``BYYEARDAY``,
    ``BYMONTHDAY``, ``BYDAY`` (including ordinals such as ``1MO`` / ``-1FR``),
    ``BYSETPOS`` and ``WKST``.

The **sub-day** rule parts — ``FREQ=SECONDLY`` / ``MINUTELY`` / ``HOURLY`` and
``BYHOUR`` / ``BYMINUTE`` / ``BYSECOND`` — are deliberately **out of scope**.
Each occurrence is a whole day (a day-wide :class:`DateSpan`), so a within-day
recurrence has no meaning here.  Parsing any of those parts raises
``ValueError`` rather than silently dropping them.  A future revision may layer
a time-of-day expansion on top; the date engine comes first because every
civil recurring rule (holidays, elections, "the last working day of the
month") is date-level.

DTSTART semantics — **strict RFC, not dateutil-compatible**
-----------------------------------------------------------
The recurrence set contains ``DTSTART`` **only if ``DTSTART`` itself matches
the rule**.  This is the strict reading of RFC 5545 (§3.8.5.3: "The recurrence
set ... is the complete set of recurrence instances for a calendar component,
as defined by the ... 'RRULE' ... The 'DTSTART' property ... MUST be
synchronized with the recurrence rule, if specified.").  It differs from
``python-dateutil``, which unconditionally prepends ``DTSTART`` even when it
does not satisfy the rule.  Concretely, with ``DTSTART`` on a Wednesday and
``FREQ=WEEKLY;BYDAY=MO`` this engine yields only Mondays; dateutil would emit
the seed Wednesday first.  ``DTSTART`` is still the anchor that fixes the
interval phase and supplies defaults for absent rule parts — it just is not
force-included.

Unbounded rules
---------------
:func:`occurrences` refuses to enumerate an unbounded set: if neither the rule
(``COUNT`` / ``UNTIL``) nor the call (``count=`` / ``until=``) bounds it, it
raises ``ValueError``.  An infinite ``for`` loop over a "forever" rule is
therefore impossible by accident; ask for a ``count`` or an ``until``.

Citations
---------
IETF RFC 5545 §3.3.10 (RECUR grammar, the expand/limit dependency table and the
BYDAY notes) and §3.8.5.3 (the worked example corpus).  A downloaded copy lives
at ``~/AgentWorkspaces/papers/standards/rfc5545_icalendar_recurrence.txt``;
the enumerated example dates seed the gold test suite.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, Optional, Tuple, Union

from chronologia.astrodate import AstroDate, DateSpan, is_leap_year
from chronologia.calendars import (gregorian_to_jdn, iso_week_from_jdn,
                                   jdn_to_gregorian)

__all__ = [
    "Recurrence",
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

# A legitimate rule may skip many periods before it hits (a leap-day yearly
# rule skips three years in four); an *impossible* one (BYMONTH=2;BYMONTHDAY=30)
# never hits at all.  This bound distinguishes the two so a count-limited call
# on an impossible rule raises instead of spinning forever.
_MAX_EMPTY_PERIODS = 20_000


# --------------------------------------------------------------------------
# Small JDN helpers (Monday == 0 weekday convention, matching AstroDate).
# --------------------------------------------------------------------------
def _days_in_month(year: int, month: int) -> int:
    if month == 2 and is_leap_year(year):
        return 29
    return _MONTH_LEN[month - 1]


def _days_in_year(year: int) -> int:
    return 366 if is_leap_year(year) else 365


def _jdn(year: int, month: int, day: int) -> int:
    return gregorian_to_jdn(year, month, day)


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
    """JDN of the ``wkst``-day that begins week 1 of ``cal_year`` — the first
    week carrying at least four days of the year (the ISO 8601 rule,
    generalized to an arbitrary week-start)."""
    jan1 = _jdn(cal_year, 1, 1)
    ws = _week_start(jan1, wkst)
    return ws if jan1 - ws <= 3 else ws + 7


def _week_of(jdn: int, wkst: int) -> Tuple[int, int, int]:
    """``(week_year, week_number, weeks_in_week_year)`` for ``jdn``.

    For the default ``WKST=MO`` this is exactly the ISO week, so it defers to
    the registered ``iso_week`` calendar (:func:`iso_week_from_jdn`); other
    week-starts use the generalized four-day rule above.
    """
    if wkst == 0:
        iso_year, week, _ = iso_week_from_jdn(jdn)
        total = iso_week_from_jdn(_jdn(iso_year, 12, 28))[1]
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
    """A frozen, hashable RFC 5545 recurrence rule (date-level parts only).

    Build one with :func:`parse_rrule` (from an ``RRULE`` string), with the
    pythonic :func:`every` constructor, or with the
    :func:`nth_weekday_of_month` / :func:`last_weekday_of_month` conveniences.
    Evaluate it with :func:`occurrences`.

    ``byday`` is a tuple of ``(ordinal_or_None, weekday)`` pairs with weekday in
    Monday==0..Sunday==6.  ``wkst`` is a weekday index (default Monday).  All
    ``by*`` collections are tuples so the whole object stays hashable.
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
        if self.bymonth:
            parts.append("BYMONTH=" + ",".join(map(str, self.bymonth)))
        if self.byweekno:
            parts.append("BYWEEKNO=" + ",".join(map(str, self.byweekno)))
        if self.byyearday:
            parts.append("BYYEARDAY=" + ",".join(map(str, self.byyearday)))
        if self.bymonthday:
            parts.append("BYMONTHDAY=" + ",".join(map(str, self.bymonthday)))
        if self.byday:
            parts.append("BYDAY=" + ",".join(
                (("" if o is None else str(o)) + _WD_CODE[w])
                for o, w in self.byday))
        if self.bysetpos:
            parts.append("BYSETPOS=" + ",".join(map(str, self.bysetpos)))
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
    if rec.wkst not in range(7):
        raise ValueError(f"WKST must be a weekday 0..6, got {rec.wkst}")
    for m in rec.bymonth:
        if not 1 <= m <= 12:
            raise ValueError(f"BYMONTH values must be 1..12, got {m}")
    for d in rec.bymonthday:
        if d == 0 or not -31 <= d <= 31:
            raise ValueError(f"BYMONTHDAY values must be -31..-1 or 1..31, got {d}")
    for d in rec.byyearday:
        if d == 0 or not -366 <= d <= 366:
            raise ValueError(f"BYYEARDAY values must be -366..-1 or 1..366, got {d}")
    for w in rec.byweekno:
        if w == 0 or not -53 <= w <= 53:
            raise ValueError(f"BYWEEKNO values must be -53..-1 or 1..53, got {w}")
    for p in rec.bysetpos:
        if p == 0 or not -366 <= p <= 366:
            raise ValueError(f"BYSETPOS values must be -366..-1 or 1..366, got {p}")
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
    # ``UNTIL`` is a DATE (``YYYYMMDD``) or DATE-TIME (``YYYYMMDDTHHMMSS`` with
    # an optional trailing ``Z``).  This date-level engine keeps the wall-clock
    # time but treats the value as NAIVE — the ``Z`` / any zone offset is not
    # converted (the cutoff is a wall-clock comparison against DTSTART's own
    # time-of-day; see :func:`occurrences`).
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
    """Parse an RFC 5545 ``RRULE`` string into a :class:`Recurrence`.

    Accepts an optional ``RRULE:`` prefix.  Rule parts are ``KEY=VALUE`` pairs
    separated by ``;`` in any order (the RFC does not order them).  Raises
    ``ValueError`` on an unknown part, a duplicated part, a malformed value, or
    a sub-day / contradictory rule (see :func:`_validate`).

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
    if "BYMONTH" in fields:
        kwargs["bymonth"] = _ints(fields.pop("BYMONTH"))
    if "BYMONTHDAY" in fields:
        kwargs["bymonthday"] = _ints(fields.pop("BYMONTHDAY"))
    if "BYYEARDAY" in fields:
        kwargs["byyearday"] = _ints(fields.pop("BYYEARDAY"))
    if "BYWEEKNO" in fields:
        kwargs["byweekno"] = _ints(fields.pop("BYWEEKNO"))
    if "BYSETPOS" in fields:
        kwargs["bysetpos"] = _ints(fields.pop("BYSETPOS"))
    if "BYDAY" in fields:
        kwargs["byday"] = tuple(_parse_weekdaynum(t)
                                for t in fields.pop("BYDAY").split(","))
    for bad in ("BYHOUR", "BYMINUTE", "BYSECOND"):
        if bad in fields:
            raise ValueError(
                f"{bad} is a sub-day rule part, out of scope for this "
                "date-level engine (see module docstring)")
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
    """Pythonic :class:`Recurrence` builder.

    ``freq`` is case-insensitive (``"yearly"``).  Keyword arguments map onto
    the rule parts: ``interval``, ``count``, ``until``, ``bymonth``,
    ``bymonthday``, ``byyearday``, ``byweekno``, ``bysetpos``, ``wkst`` and
    ``byday``.  ``byday`` accepts ``"1MO"``, ``"MO,WE"``, ``["1MO", "-1FR"]``,
    or ``(ordinal, weekday)`` tuples; ``wkst`` accepts a code or an int.

    >>> # U.S. Labor Day: the first Monday of September.
    >>> labor_day = every("yearly", bymonth=9, byday="1MO")
    >>> labor_day.to_string()
    'FREQ=YEARLY;BYMONTH=9;BYDAY=1MO'
    """
    kwargs: Dict[str, Any] = {"freq": freq.upper()}

    def _tup(v):
        return (v,) if isinstance(v, int) else tuple(v)

    for name in ("interval", "count", "until"):
        if name in by:
            kwargs[name] = by.pop(name)
    for name in ("bymonth", "bymonthday", "byyearday", "byweekno", "bysetpos"):
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

    With ``month`` given, it becomes a yearly rule restricted to that month
    (Thanksgiving = ``nth_weekday_of_month(4, "TH", month=11)``); without it,
    a monthly rule (the ``n``-th weekday of *every* month).  Extra keyword
    arguments (``count``, ``until``, ``interval`` ...) pass through to
    :func:`every`.
    """
    wd = _coerce_weekday(weekday)
    if month is not None:
        return every("yearly", bymonth=month, byday=((n, wd),), **extra)
    return every("monthly", byday=((n, wd),), **extra)


def last_weekday_of_month(weekday: Union[int, str],
                          month: Optional[int] = None, **extra) -> Recurrence:
    """The last ``weekday`` of the month — ``nth_weekday_of_month(-1, ...)``.

    UK spring bank holiday = ``last_weekday_of_month("MO", month=5)``.
    """
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
    if rec.byweekno:
        wy, wn, total = _week_of(jdn, rec.wkst)
        if wy != y or not any(_signed(x, wn, total) for x in rec.byweekno):
            return False
    if rec.byyearday:
        yd = jdn - _jdn(y, 1, 1) + 1
        ytot = _days_in_year(y)
        if not any(_signed(x, yd, ytot) for x in rec.byyearday):
            return False
    if rec.bymonthday:
        dim = _days_in_month(y, m)
        if not any(_signed(x, d, dim) for x in rec.bymonthday):
            return False
    if rec.byday and not _byday_match(rec, jdn, y, m, wd):
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
        finer = (rec.byweekno or rec.byyearday or rec.bymonthday or rec.byday)
        if not finer:
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
            first, last = _jdn(y, 1, 1), _jdn(y, 12, 31)
        else:
            first = _jdn(y, m, 1)
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


def _period_iter(rec: Recurrence, dtstart: AstroDate):
    """Yield ``(period_start_jdn, sorted_matching_jdns)`` for each interval,
    forever.  The caller bounds it with count/until."""
    freq = rec.freq
    start_jdn = _jdn(dtstart.year, dtstart.month, dtstart.day)

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
            days = [_jdn(y, m, d) for d in range(1, _days_in_month(y, m) + 1)]
            yield _jdn(y, m, 1), _keep(days)
            total = (y * 12 + (m - 1)) + rec.interval
            y, m = total // 12, total % 12 + 1
    else:  # YEARLY
        y = dtstart.year
        while True:
            jan1 = _jdn(y, 1, 1)
            days = list(range(jan1, jan1 + _days_in_year(y)))
            yield jan1, _keep(days)
            y += rec.interval


def _day_span(jdn: int) -> DateSpan:
    start = AstroDate(*jdn_to_gregorian(jdn))
    end = AstroDate(*jdn_to_gregorian(jdn + 1))
    return DateSpan(start, end)


def occurrences(rec: Recurrence, dtstart, until=None,
                count: Optional[int] = None) -> Iterator[DateSpan]:
    """Expand ``rec`` from ``dtstart``, yielding day-wide :class:`DateSpan`\\ s.

    ``dtstart`` is the anchor (an :class:`AstroDate`, ``date``, or
    ``datetime``): it fixes the interval phase and supplies defaults for absent
    rule parts, and — per this engine's **strict-RFC** policy — is emitted only
    if it actually matches the rule (unlike ``dateutil``; see the module
    docstring).

    A call-level ``until`` (inclusive, date-level) or ``count`` overrides the
    rule's own ``UNTIL`` / ``COUNT`` for this expansion.  If the expansion is
    unbounded on **both** sides — the rule has no ``COUNT``/``UNTIL`` *and* the
    call passes neither — it raises ``ValueError`` rather than looping forever.

    Occurrences come out in strict chronological order.
    """
    dtstart = _as_astro(dtstart)
    eff_until = _as_astro(until) if until is not None else rec.until
    eff_count = count if count is not None else rec.count
    if eff_until is None and eff_count is None:
        raise ValueError(
            "unbounded recurrence: neither the rule nor the call bounds the "
            "set. Pass count=... or until=..., or use a rule with COUNT/UNTIL.")

    start_jdn = _jdn(dtstart.year, dtstart.month, dtstart.day)
    # Each occurrence inherits DTSTART's time-of-day; the UNTIL cutoff is a
    # wall-clock comparison of that instant against UNTIL's own time (both
    # naive — see the module and _parse_until docstrings).
    start_tod = (dtstart.hour, dtstart.minute, dtstart.second,
                 dtstart.microsecond)
    until_jdn = None
    until_key = None
    if eff_until is not None:
        until_jdn = _jdn(eff_until.year, eff_until.month, eff_until.day)
        until_key = (until_jdn, (eff_until.hour, eff_until.minute,
                                 eff_until.second, eff_until.microsecond))

    emitted = 0
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
            yield _day_span(jdn)
            produced = True
            emitted += 1
            if eff_count is not None and emitted >= eff_count:
                return
        if produced:
            empty_streak = 0
        else:
            empty_streak += 1
            if empty_streak > _MAX_EMPTY_PERIODS:
                raise ValueError(
                    f"rule produced nothing in {_MAX_EMPTY_PERIODS} "
                    "consecutive periods; it appears never to occur "
                    f"(rule: {rec.to_string()})")


def _as_astro(value) -> AstroDate:
    if isinstance(value, AstroDate):
        return value
    # date / datetime duck-typing: read the calendar fields.
    try:
        return AstroDate(value.year, value.month, value.day)
    except AttributeError:
        raise TypeError(
            f"expected AstroDate/date/datetime, got {type(value).__name__}")
