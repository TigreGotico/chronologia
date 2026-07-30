"""EDTF (Extended Date/Time Format) <-> :class:`DateSpan`.

EDTF is the Library of Congress profile of ISO 8601-2:2019 — *the* standard
for the dates archives, libraries and museums have to write when they are **not
sure**: "sometime in the 1560s", "June 2004, approximately", "the year
170000002".  That is precisely what a :class:`~chronologia.astrodate.DateSpan`
already expresses (a half-open stretch of time whose *width is the
uncertainty*), so EDTF maps onto this engine almost one-to-one.

Reference: Library of Congress, "Extended Date/Time Format (EDTF)
Specification", https://www.loc.gov/standards/datetime/ (spec dated
2019-02-04).  Every example string in that
document is exercised by ``test/test_edtf.py`` and every design decision below
cites it.

Two entry points:

* :func:`parse_edtf` — an EDTF string to an :class:`EdtfDate` (a frozen wrapper
  carrying the resolved :class:`DateSpan` plus the EDTF *qualifier* flags).
* :func:`format_edtf` — the inverse: the tightest EDTF string for a span.


Design decisions (all documented against the spec)
--------------------------------------------------

**The qualifier wrapper.**  DateSpan's core is frozen and widely depended on,
so the EDTF qualifiers (``?`` uncertain, ``~`` approximate, ``%`` both) are not
new DateSpan fields.  Instead :func:`parse_edtf` returns an :class:`EdtfDate`
= ``(span, uncertain, approximate)``.  The qualifiers speak about the **claim**
("possibly 1984, but not definitely"), not about how we computed the endpoints,
so their effect on :attr:`DateSpan.basis` is: ``span.basis`` becomes
``"reconstructed"`` when either flag is set, and stays ``"exact"`` otherwise.
Width-based imprecision (reduced precision, unspecified ``X`` digits, seasons,
significant digits) never touches ``basis`` — there the endpoints *are* exact,
and the width already carries the uncertainty, matching this engine's rule that
"width IS the uncertainty; basis records how the endpoints were established".
EDTF Level-2 lets a qualifier scope a single component ("year uncertain; month
known"); we recognise and parse that placement but **collapse** it to the two
date-level flags (a documented lossiness — the per-component scope is not
retained).

**Open / unknown interval ends.**  EDTF L1 writes an unbounded interval end as
``..`` ("open", ongoing) or an empty string ("unknown").  A DateSpan cannot
bound infinity, so an open interval resolves to the **bounded** side's span with
:attr:`EdtfDate.open_start` / :attr:`EdtfDate.open_end` set.  ``1985/..``
becomes the 1985 year-span with ``open_end=True``.  EDTF's null-vs-``..``
distinction (don't-know versus ongoing) is *semantic only*; both collapse to the
same boolean here (documented).

**Seasons.**  EDTF assigns 21/22/23/24 to Spring/Summer/Autumn/Winter but
deliberately leaves the calendar boundaries undefined.  We adopt the
**meteorological** seasons of the **Northern Hemisphere** — three-month blocks
starting 1 March / 1 June / 1 September / 1 December — because they are exact
month boundaries (astronomical seasons would need per-year solstice
computation).  Generic seasons (21-24) and the explicit Northern-Hemisphere
codes (25-28) yield the same spans; Southern-Hemisphere codes (29-32) are
shifted six months.  Winter runs into the following year (Dec Y .. Mar Y+1).

**Sub-year groupings (L2 33-41).**  Quarters, quadrimesters and semesters map to
their exact month blocks (Q1 = Jan-Mar, ..., semester 2 = Jul-Dec).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import timedelta, timezone

from chronologia.astrodate import (AstroDate, BASIS_EXACT, BASIS_RECONSTRUCTED,
                                   DateSpan, _days_in_month)


class EdtfParseError(ValueError):
    """Raised for an EDTF string that is malformed or otherwise unparseable.

    A subclass of :class:`ValueError`, so callers that only catch ``ValueError``
    still work.  Never raised for a *valid but unsupported* construct — those
    raise :class:`NotImplementedError` (see :func:`parse_edtf`).
    """


# EDTF Level-1/2 season and sub-year grouping codes -> (start_month, end_month)
# where end_month is the FIRST month NOT covered; when end <= start the block
# wraps into the following year (e.g. Winter = Dec .. Mar of the next year).
# Northern-Hemisphere meteorological convention (see module docstring).
_SEASON_MONTHS = {
    21: (3, 6), 22: (6, 9), 23: (9, 12), 24: (12, 3),    # generic == NH
    25: (3, 6), 26: (6, 9), 27: (9, 12), 28: (12, 3),    # Northern Hemisphere
    29: (9, 12), 30: (12, 3), 31: (3, 6), 32: (6, 9),    # Southern Hemisphere
    33: (1, 4), 34: (4, 7), 35: (7, 10), 36: (10, 1),    # quarters (3 months)
    37: (1, 5), 38: (5, 9), 39: (9, 1),                  # quadrimesters (4 mo)
    40: (1, 7), 41: (7, 1),                              # semesters (6 months)
}


# --------------------------------------------------------------------------
# The wrapper.
# --------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class EdtfDate:
    """An EDTF value: a :class:`DateSpan` plus the EDTF qualifier flags.

    :attr:`span` is the resolved half-open interval — the whole point of the
    mapping.  :attr:`uncertain` / :attr:`approximate` record the EDTF ``?`` /
    ``~`` / ``%`` qualifiers (``%`` sets both).  :attr:`open_start` /
    :attr:`open_end` mark an unbounded interval end (see the module docstring);
    when set, :attr:`span` covers only the bounded side.

    ``span.basis`` is ``"reconstructed"`` whenever a qualifier is present and
    ``"exact"`` otherwise, so the qualifier's effect on downstream basis
    propagation is visible through the span alone.
    """
    span: DateSpan
    uncertain: bool = False
    approximate: bool = False
    open_start: bool = False
    open_end: bool = False

    @property
    def basis(self) -> str:
        """Shorthand for ``self.span.basis``."""
        return self.span.basis

    @property
    def qualifier(self) -> str:
        """The single EDTF qualifier character (``?``/``~``/``%``), or ``""``."""
        if self.uncertain and self.approximate:
            return "%"
        if self.uncertain:
            return "?"
        if self.approximate:
            return "~"
        return ""

    def to_json(self) -> dict:
        """A ``json.dumps``-ready dict envelope (see :meth:`from_json`)."""
        return {"type": "EdtfDate", "span": self.span.to_json(),
                "uncertain": self.uncertain, "approximate": self.approximate,
                "open_start": self.open_start, "open_end": self.open_end}

    @classmethod
    def from_json(cls, data: dict) -> "EdtfDate":
        """Rebuild an :class:`EdtfDate` from a :meth:`to_json` envelope."""
        if data.get("type") != "EdtfDate":
            raise ValueError(f"not an EdtfDate envelope: {data.get('type')!r}")
        return cls(DateSpan.from_json(data["span"]),
                   bool(data.get("uncertain", False)),
                   bool(data.get("approximate", False)),
                   bool(data.get("open_start", False)),
                   bool(data.get("open_end", False)))


# --------------------------------------------------------------------------
# Low-level span builders.
# --------------------------------------------------------------------------

def _next_month(y: int, m: int):
    return (y + 1, 1) if m == 12 else (y, m + 1)


def _year_span(lo: int, hi_exclusive: int) -> DateSpan:
    """Year-precision span ``[lo-01-01, hi-01-01)`` (hi is exclusive year)."""
    return DateSpan(AstroDate(lo, 1, 1), AstroDate(hi_exclusive, 1, 1))


def _month_range_span(y: int, m_lo: int, m_hi: int) -> DateSpan:
    """Span from the first of ``m_lo`` to the first after ``m_hi`` (same year)."""
    ey, em = _next_month(y, m_hi)
    return DateSpan(AstroDate(y, m_lo, 1), AstroDate(ey, em, 1))


def _day_range_span(y: int, m: int, d_lo: int, d_hi: int) -> DateSpan:
    """Span covering days ``d_lo..d_hi`` (inclusive) of one month."""
    start = AstroDate(y, m, d_lo)
    end = AstroDate.fromordinal(AstroDate(y, m, d_hi).toordinal() + 1)
    return DateSpan(start, end)


def _season_span(y: int, code: int) -> DateSpan:
    sm, em = _SEASON_MONTHS[code]
    start = AstroDate(y, sm, 1)
    end = AstroDate(y + 1 if em <= sm else y, em, 1)
    return DateSpan(start, end)


# --------------------------------------------------------------------------
# Field parsing: unspecified digits (X) and significant digits (S).
# --------------------------------------------------------------------------

def _x_range(field: str):
    """``(lo, hi)`` inclusive numeric range of a digit field containing ``X``.

    Only **trailing** ``X`` runs are contiguous (``156X`` == 1560..1569); an
    ``X`` followed by a real digit denotes a non-contiguous set (``1X23`` ==
    {1023,1123,...}) which no single span can hold, so that raises
    :class:`NotImplementedError`.  Returns ``None`` when the field has no ``X``.
    """
    if "X" not in field:
        return None
    first = field.index("X")
    if any(c != "X" for c in field[first:]):
        raise NotImplementedError(
            f"non-trailing unspecified digit in {field!r}: the value set is "
            f"non-contiguous and cannot be one DateSpan")
    return int(field.replace("X", "0")), int(field.replace("X", "9"))


def _sig_year_span(value: int, sig: int) -> DateSpan:
    """Significant-digits year span: all years sharing the top ``sig`` digits.

    ``1950S2`` -> [1900, 2000); ``Y171010000S3`` -> [171000000, 172000000).
    """
    if sig < 1:
        raise EdtfParseError(f"significant-digit count must be >= 1, got {sig}")
    digits = len(str(abs(value)))
    trailing = digits - sig
    if trailing <= 0:
        return _year_span(value, value + 1)
    p = 10 ** trailing
    lo = (value // p) * p
    return _year_span(lo, lo + p)


_YEAR_TOKEN = re.compile(r"^Y(-?\d+)(?:E(\d+))?(?:S(\d+))?$")
_PLAIN_SIG = re.compile(r"^(-?\d+)S(\d+)$")


def _parse_year_only(field: str) -> DateSpan:
    """A year-only EDTF component -> its year-precision (or wider) span.

    Handles: plain four-digit years, negative years (``-1985``), ``Y``-prefix
    big years (``Y170000002``), exponential years (``Y-17E7``), significant
    digits (``1950S2``, ``Y3388E2S3``) and unspecified digits (``156X``,
    ``20XX``).
    """
    if field.startswith("Y"):
        m = _YEAR_TOKEN.match(field)
        if not m:
            raise EdtfParseError(f"malformed Y-prefixed year: {field!r}")
        value = int(m.group(1)) * (10 ** int(m.group(2)) if m.group(2) else 1)
        if m.group(3):
            return _sig_year_span(value, int(m.group(3)))
        return _year_span(value, value + 1)

    sig = _PLAIN_SIG.match(field)
    if sig:
        return _sig_year_span(int(sig.group(1)), int(sig.group(2)))

    if "X" in field:
        if len(field.lstrip("-")) < 4:
            raise EdtfParseError(
                f"a bare EDTF year needs at least four digits, got {field!r}")
        lo, hi = _x_range(field)
        return _year_span(lo, hi + 1)

    if not re.match(r"^-?\d+$", field):
        raise EdtfParseError(f"malformed year: {field!r}")
    if len(field.lstrip("-")) < 4:
        raise EdtfParseError(
            f"a bare EDTF year needs at least four digits, got {field!r}")
    value = int(field)
    return _year_span(value, value + 1)


def _is_year_range(span: DateSpan) -> bool:
    return span.end.year - span.start.year > 1 or span.start.month != 1 \
        or span.start.day != 1


# --------------------------------------------------------------------------
# Datetime.
# --------------------------------------------------------------------------

_DATETIME = re.compile(
    r"^(-?\d{4,})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.(\d{1,6}))?"
    r"(Z|[+-]\d{2}(?::\d{2})?)?$")


def _parse_datetime(tok: str) -> DateSpan:
    m = _DATETIME.match(tok)
    if not m:
        raise EdtfParseError(f"malformed EDTF date/time: {tok!r}")
    y, mo, d, hh, mm, ss, frac, off = m.groups()
    micro = int((frac or "").ljust(6, "0")) if frac else 0
    zone = None
    if off == "Z":
        zone = timezone.utc
    elif off:
        sign = -1 if off[0] == "-" else 1
        parts = off[1:].split(":")
        secs = int(parts[0]) * 3600 + (int(parts[1]) * 60 if len(parts) > 1 else 0)
        zone = timezone(timedelta(seconds=sign * secs))
    start = AstroDate(int(y), int(mo), int(d), int(hh), int(mm), int(ss),
                      micro, tzinfo=zone)
    step = timedelta(microseconds=1) if frac else timedelta(seconds=1)
    return DateSpan(start, start + step)


# --------------------------------------------------------------------------
# The component parser (one endpoint, no qualifiers, no interval).
# --------------------------------------------------------------------------

def _month_bounds(field: str):
    """``(m_lo, m_hi, is_full_year)`` for a numeric month field (maybe with X).

    ``m_lo``/``m_hi`` are clamped to 1..12; ``is_full_year`` is True when the
    field covers every month (``XX``), which collapses to year precision.
    """
    x = _x_range(field)
    if x is None:
        m = int(field)
        return m, m, False
    lo, hi = x
    m_lo = max(lo, 1)
    m_hi = min(hi, 12)
    if m_hi < m_lo:
        raise EdtfParseError(f"month field {field!r} clamps to an empty range")
    return m_lo, m_hi, (m_lo == 1 and m_hi == 12)


def _parse_component(tok: str) -> DateSpan:
    if "T" in tok:
        return _parse_datetime(tok)

    if tok.startswith("Y"):
        return _parse_year_only(tok)

    negative = tok.startswith("-")
    body = tok[1:] if negative else tok
    if not body:
        raise EdtfParseError(f"empty date component: {tok!r}")
    parts = body.split("-")
    year_field = ("-" if negative else "") + parts[0]

    if len(parts) == 1:
        return _parse_year_only(year_field)

    if len(parts) == 2:
        return _parse_ym(year_field, parts[1])

    if len(parts) == 3:
        return _parse_ymd(year_field, parts[1], parts[2])

    raise EdtfParseError(f"too many '-' separated fields in {tok!r}")


def _check_two_digit(field: str, what: str):
    if len(field) != 2 or not re.match(r"^[\dX]{2}$", field):
        raise EdtfParseError(
            f"EDTF {what} field must be two digits/X, got {field!r}")


def _parse_ym(year_field: str, month_field: str) -> DateSpan:
    _check_two_digit(month_field, "month")
    year = _parse_year_only(year_field)
    # A season / sub-year grouping code occupies the month slot.
    if _x_range(month_field) is None and int(month_field) >= 13:
        code = int(month_field)
        if code not in _SEASON_MONTHS:
            raise EdtfParseError(
                f"month/season code {code} out of range (01-12 or 21-41)")
        if _is_year_range(year):
            raise NotImplementedError(
                "a season on a wildcarded/ranged year is a non-contiguous set")
        return _season_span(year.start.year, code)

    m_lo, m_hi, full = _month_bounds(month_field)
    if full:  # unspecified month == the whole year (single or ranged)
        return year
    if _is_year_range(year):
        raise NotImplementedError(
            f"specific month on a wildcarded/ranged year ({year_field!r}) is a "
            f"non-contiguous set of months")
    if not 1 <= m_lo <= 12 or not 1 <= m_hi <= 12:
        raise EdtfParseError(f"month field {month_field!r} out of range")
    return _month_range_span(year.start.year, m_lo, m_hi)


def _parse_ymd(year_field: str, month_field: str, day_field: str) -> DateSpan:
    _check_two_digit(month_field, "month")
    _check_two_digit(day_field, "day")
    year = _parse_year_only(year_field)
    m_lo, m_hi, month_full = _month_bounds(month_field)

    if month_full:
        # Unspecified month; a specific day would be non-contiguous.
        dx = _x_range(day_field)
        if dx is not None and dx[0] <= 1 and dx[1] >= 28:
            return year  # day also unspecified -> whole year
        raise NotImplementedError(
            "a specific day within an unspecified month is a non-contiguous set")

    if _is_year_range(year) or m_lo != m_hi:
        raise NotImplementedError(
            "a day within a wildcarded/ranged year or month is non-contiguous")

    y, m = year.start.year, m_lo
    limit = _days_in_month(y, m)
    dx = _x_range(day_field)
    if dx is None:
        d = int(day_field)
        if not 1 <= d <= limit:
            raise EdtfParseError(
                f"day {d} out of range 1..{limit} for {y}-{m:02d}")
        return _day_range_span(y, m, d, d)
    d_lo = max(dx[0], 1)
    d_hi = min(dx[1], limit)
    if d_hi < d_lo:
        raise EdtfParseError(f"day field {day_field!r} clamps to an empty range")
    return _day_range_span(y, m, d_lo, d_hi)


# --------------------------------------------------------------------------
# Qualifiers.
# --------------------------------------------------------------------------

_QUAL_CHARS = "?~%"


def _extract_qualifiers(tok: str):
    """``(clean_token, uncertain, approximate)`` — strip ``?``/``~``/``%``.

    L2 placement (left/right of a component) is recognised only by *presence*;
    the positional scope is collapsed to two date-level flags (documented).
    """
    uncertain = "?" in tok or "%" in tok
    approximate = "~" in tok or "%" in tok
    clean = "".join(c for c in tok if c not in _QUAL_CHARS)
    return clean, uncertain, approximate


def _parse_single(tok: str) -> EdtfDate:
    clean, unc, appr = _extract_qualifiers(tok)
    if not clean:
        raise EdtfParseError(f"no date content in {tok!r}")
    span = _parse_component(clean)
    basis = BASIS_RECONSTRUCTED if (unc or appr) else BASIS_EXACT
    return EdtfDate(DateSpan(span.start, span.end, basis), unc, appr)


# --------------------------------------------------------------------------
# Public: parse.
# --------------------------------------------------------------------------

_OPEN = ("", "..")


def parse_edtf(s: str) -> EdtfDate:
    """Parse an EDTF string into an :class:`EdtfDate`.

    Covers EDTF **Level 0** (dates, date/times with time-shift, intervals),
    **Level 1** (``?``/``~``/``%`` qualifiers, unspecified ``X`` digits,
    negative and ``Y``-prefix years, seasons, open/unknown interval ends) and
    the cleanly-mapping **Level 2** subset (exponential years, significant
    digits, sub-year groupings/quarters, component-level qualifiers).

    Raises :class:`EdtfParseError` (a :class:`ValueError`) for malformed input,
    and :class:`NotImplementedError` for a *valid* EDTF string whose meaning is
    a non-contiguous set of instants that no single :class:`DateSpan` can hold
    (an interior/partial unspecified digit combined with a more specific
    component, e.g. ``1XXX-12``; the set-notation ``[..]`` / ``{..}`` forms).
    """
    if not isinstance(s, str):
        raise EdtfParseError(f"expected str, got {type(s).__name__}")
    s = s.strip()
    if not s:
        raise EdtfParseError("empty EDTF string")
    if " " in s:
        raise EdtfParseError(f"EDTF forbids spaces within an expression: {s!r}")
    if s[0] in "[{":
        raise NotImplementedError(
            "EDTF set representation ([..] one-of, {..} all-members) is not "
            "mapped to a single DateSpan")

    if "/" in s:
        return _parse_interval(s)
    return _parse_single(s)


def _parse_interval(s: str) -> EdtfDate:
    parts = s.split("/")
    if len(parts) != 2:
        raise EdtfParseError(
            f"an EDTF interval has exactly one '/': {s!r}")
    left, right = parts

    if left in _OPEN and right in _OPEN:
        raise EdtfParseError(f"interval with both ends open: {s!r}")

    if left in _OPEN:  # open/unknown start
        ed = _parse_single(right)
        return EdtfDate(ed.span, ed.uncertain, ed.approximate, open_start=True)
    if right in _OPEN:  # open/unknown end
        ed = _parse_single(left)
        return EdtfDate(ed.span, ed.uncertain, ed.approximate, open_end=True)

    ledt = _parse_single(left)
    redt = _parse_single(right)
    unc = ledt.uncertain or redt.uncertain
    appr = ledt.approximate or redt.approximate
    basis = BASIS_RECONSTRUCTED if (unc or appr) else BASIS_EXACT
    span = DateSpan(ledt.span.start, redt.span.end, basis)
    return EdtfDate(span, unc, appr)


# --------------------------------------------------------------------------
# Public: format.
# --------------------------------------------------------------------------

def _year_str(y: int) -> str:
    if 0 <= y <= 9999:
        return f"{y:04d}"
    if -9999 <= y < 0:
        return f"-{-y:04d}"
    return f"Y{y}"


def _day_str(a: AstroDate) -> str:
    return f"{_year_str(a.year)}-{a.month:02d}-{a.day:02d}"


def _month_str(a: AstroDate) -> str:
    return f"{_year_str(a.year)}-{a.month:02d}"


def _is_midnight(a: AstroDate) -> bool:
    return not (a.hour or a.minute or a.second or a.microsecond)


def _span_token(span: DateSpan):
    """The single tightest EDTF token for ``span``, or ``None`` for an interval.

    Recognises day / month / year / decade / century precision (all aligned to
    the corresponding unit boundary).  ``None`` means no single token fits and
    the caller must emit an interval.
    """
    s, e = span.start, span.end
    if not (_is_midnight(s) and _is_midnight(e)):
        return None
    # day precision
    if AstroDate.fromordinal(s.toordinal() + 1) == e:
        return _day_str(s)
    if s.day != 1:
        return None
    # month precision
    ny, nm = _next_month(s.year, s.month)
    if s.month != 1:
        return _month_str(s) if e == AstroDate(ny, nm, 1) else None
    # year / decade / century (month == 1, day == 1)
    if e == AstroDate(s.year + 1, 1, 1):
        return _year_str(s.year)
    if 0 <= s.year <= 9999:
        if s.year % 10 == 0 and e == AstroDate(s.year + 10, 1, 1):
            return f"{s.year:04d}"[:3] + "X"
        if s.year % 100 == 0 and e == AstroDate(s.year + 100, 1, 1):
            return f"{s.year:04d}"[:2] + "XX"
    return None


def _format_span(span: DateSpan) -> str:
    token = _span_token(span)
    if token is not None:
        return token

    s, e = span.start, span.end
    if _is_midnight(s) and _is_midnight(e) and s.day == 1 and e.day == 1:
        # both endpoints on a month boundary -> tightest interval
        if s.month == 1 and e.month == 1:  # whole-year interval
            return f"{_year_str(s.year)}/{_year_str(e.year - 1)}"
        py, pm = (e.year - 1, 12) if e.month == 1 else (e.year, e.month - 1)
        return f"{_month_str(s)}/{_month_str(AstroDate(py, pm, 1))}"
    if _is_midnight(s) and _is_midnight(e):
        last = AstroDate.fromordinal(e.toordinal() - 1)
        return f"{_day_str(s)}/{_day_str(last)}"
    # a sub-day point: emit a date/time token
    if e == s + timedelta(seconds=1) or e == s + timedelta(microseconds=1):
        return _format_point(s)
    raise ValueError(
        f"span {span.start}..{span.end} has sub-day width but is not a single "
        f"instant; EDTF cannot express it")


def _format_point(a: AstroDate) -> str:
    if _is_midnight(a) and a.tzinfo is None:
        return _day_str(a)
    return a.isoformat()


def format_edtf(obj) -> str:
    """Emit the tightest EDTF string for a span, point, or :class:`EdtfDate`.

    Accepts a :class:`DateSpan`, an :class:`AstroDate` (a point), or an
    :class:`EdtfDate` (span + qualifier/open flags).  A recognised precision
    (day/month/year/decade/century) yields a single reduced-precision token;
    anything else yields an interval (``start/end``).

    **Lossiness (documented, honest).**  Format is not a perfect inverse of
    every EDTF string — it emits the *span*'s tightest form, so information that
    the span does not carry is dropped:

    * exponential years (``Y17E7``) come back as plain ``Y170000000``;
    * significant-digit and season/quarter spans come back as the equivalent
      reduced-precision token or bounded interval (``1950S2`` -> ``19XX``;
      Spring 2001 -> ``2001-03/2001-05``);
    * L2 per-component qualifier scope collapses to one trailing qualifier.

    The guarantee that *does* hold is a round trip on the **span**:
    ``parse_edtf(format_edtf(parse_edtf(x))).span == parse_edtf(x).span`` for
    every span this module can express.
    """
    unc = appr = open_start = open_end = False
    if isinstance(obj, EdtfDate):
        span = obj.span
        unc, appr = obj.uncertain, obj.approximate
        open_start, open_end = obj.open_start, obj.open_end
    elif isinstance(obj, AstroDate):
        return _format_point(obj)
    elif isinstance(obj, DateSpan):
        span = obj
    else:
        raise TypeError(
            f"format_edtf expects EdtfDate/DateSpan/AstroDate, got "
            f"{type(obj).__name__}")

    core = _format_span(span)
    qual = "%" if (unc and appr) else "?" if unc else "~" if appr else ""
    if open_start:
        return f"../{core}{qual}"
    if open_end:
        return f"{core}{qual}/.."
    return f"{core}{qual}"
