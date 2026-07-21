"""Match + anchor + Conventions -> Resolution.  All date math lives here.

Every construction's semantics are computed once, engine-side, shared by
every language.  Notably the *sign* of a ``relative_offset`` is read from
the marker's declared direction (``spec.directions``); a language cannot
get the ago/hence direction wrong because it never writes the sign.

Resolution conventions (chosen once, documented, asserted in tests):

* pure-calendar constructions (``named_day``, ``weekday_ref``,
  ``calendar_date``, ``iso_date``) return midnight of the resolved date;
* ``relative_offset`` shifts the full anchor datetime, preserving its
  time-of-day.

An impossible or unrepresentable date never raises: :meth:`resolve`
returns ``None`` (the matcher offered a span the calendar rejects, so the
construction simply did not fire).

The adopted-extension constructions land their resolvers here:
``clock_time`` (with date composition), ``subdivision_time`` (alternative
day subdivisions), ``scoped_ordinal``, ``season_ref``, ``cycle_ref``
(named day cycles), ``regnal_date`` and ``roman_date``.  ``era_date``
remains declared-but-unimplemented (era phrasing resolves through
``reckoned_date`` / the eras layer) and raises ``NotImplementedError``.
"""
from __future__ import annotations

import calendar
from datetime import date, datetime, timedelta
from typing import Optional

from chronologia.astrodate import AstroDate, DateSpan
from chronologia.calendars import (CALENDARS, gregorian_to_jdn,
                                        jdn_to_gregorian)
from chronologia.cycles import (DAY_CYCLES, DAY_SUBDIVISIONS, US_PER_DAY,
                                     resolve_cycle_day)
from chronologia.regnal import REGNAL_SEQUENCES
from chronologia.roman import roman_to_julian
from chronologia.extract.compiler import UNIMPLEMENTED
from chronologia.extract.model import (Conventions, LangSpec, Match,
                                           Resolution)
from chronologia.extract.ranges import (_ABSOLUTE, _UNIT_OF_CENTURY,
                                        _UNIT_OF_MILLENNIUM, _UNIT_OF_MONTH,
                                        _UNIT_OF_YEAR, DateTimeResolution,
                                        Hemisphere, Season, get_date_ordinal,
                                        last_season_date, next_season_date,
                                        season_to_date)


def _add_months(dt: datetime, months: int) -> datetime:
    total = dt.month - 1 + months
    year = dt.year + total // 12
    month = total % 12 + 1
    day = min(dt.day, calendar.monthrange(year, month)[1])
    return dt.replace(year=year, month=month, day=day)


def _midnight(dt: datetime) -> datetime:
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def _point_span(dt: datetime, unit: str) -> DateSpan:
    """Half-open span of one ``unit``'s width starting at ``dt``.

    Width is the offset unit's granularity: day/week are fixed timedeltas,
    month/year advance the calendar so the span tiles cleanly.
    """
    start = AstroDate.from_datetime(dt)
    if unit == "minute":
        end = AstroDate.from_datetime(dt + timedelta(minutes=1))
    elif unit == "hour":
        end = AstroDate.from_datetime(dt + timedelta(hours=1))
    elif unit == "day":
        end = AstroDate.from_datetime(dt + timedelta(days=1))
    elif unit == "week":
        end = AstroDate.from_datetime(dt + timedelta(days=7))
    elif unit == "fortnight":
        end = AstroDate.from_datetime(dt + timedelta(days=14))
    elif unit == "month":
        end = AstroDate.from_datetime(_add_months(dt, 1))
    elif unit == "year":
        end = AstroDate.from_datetime(_add_months(dt, 12))
    else:
        raise ValueError(f"unsupported offset unit {unit!r}")
    return DateSpan(start, end)


def _day_span(dt: datetime) -> DateSpan:
    """Day-wide span ``[midnight(dt), next midnight)``."""
    start = AstroDate.from_datetime(_midnight(dt))
    return DateSpan(start, start + timedelta(days=1))


#: constructions that name a *date* (a day or a wider calendar period); a
#: clock_time in the same text composes onto the day these select.
DATE_CONSTRUCTIONS = frozenset({
    "calendar_date", "reckoned_date", "nongregorian_date", "iso_date",
    "weekday_ref", "named_day", "season_ref", "scoped_ordinal",
    "scoped_bc", "scoped_ad",
    "regnal_date", "roman_date", "era_date",
    "era_bc", "era_ad", "era_bp", "deep_time", "named_period"})


def compose_date_clock(date_res: Resolution, clock_res: Resolution) -> Resolution:
    """Intersect a date span with a clock span: the minute-wide clock time
    placed on the day the date construction selected.

    The date span's ``start`` supplies the calendar day (its left edge is
    that day's midnight); the clock span's ``start`` supplies the
    time-of-day.  The result is the clock's minute-wide span on that day --
    "june 5 at half past ten" -> ``[2027-06-05 10:30, ...10:31)``.
    """
    d = date_res.value.start
    c = clock_res.value.start
    start = AstroDate(d.year, d.month, d.day,
                      c.hour, c.minute, c.second, c.microsecond)
    consumed = tuple(sorted(set(date_res.consumed) | set(clock_res.consumed)))
    return Resolution(DateSpan(start, start + timedelta(minutes=1)), consumed)


def _astro_add_years(start: AstroDate, years: int) -> AstroDate:
    """``start`` advanced by whole years (day/month preserved, Feb 29 clamped)."""
    day = 28 if (start.month == 2 and start.day == 29
                 and not _astro_is_leap(start.year + years)) else start.day
    return start.replace(year=start.year + years, day=day)


def _astro_is_leap(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def _unit_end(start: AstroDate, kind: str) -> AstroDate:
    """Half-open end of a one-``kind``-wide span starting at ``start``.

    The width IS the referential uncertainty; the derived resolution tiles
    with :class:`DateSpan`'s width thresholds (a week-wide span reads WEEK,
    a century-wide span reads CENTURY).
    """
    if kind == "day":
        return start + timedelta(days=1)
    if kind == "week":
        return start + timedelta(days=7)
    if kind == "month":
        nyear, nmonth = (start.year + 1, 1) if start.month == 12 \
            else (start.year, start.month + 1)
        return AstroDate(nyear, nmonth, 1)
    steps = {"year": 1, "decade": 10, "century": 100, "millennium": 1000}
    if kind in steps:
        return _astro_add_years(AstroDate(start.year, start.month, start.day),
                                steps[kind])
    raise ValueError(f"unsupported scoped unit {kind!r}")


def _gregorian_month_span(year: int, month: int) -> DateSpan:
    """Month-wide span ``[first of month, first of next month)``."""
    start = AstroDate(year, month, 1)
    nyear, nmonth = (year + 1, 1) if month == 12 else (year, month + 1)
    return DateSpan(start, AstroDate(nyear, nmonth, 1))


class Resolver:
    """Configured once from a :class:`LangSpec`."""

    def __init__(self, spec: LangSpec):
        self.spec = spec
        self.conventions: Conventions = spec.conventions

    def resolve(self, match: Match, anchor: datetime) -> Optional[Resolution]:
        if match.construction in UNIMPLEMENTED:
            raise NotImplementedError(
                f"construction {match.construction!r} is declared but not "
                f"resolved in the engine-core phase; it lands with its own "
                f"migration wave")
        handler = getattr(self, f"_resolve_{match.construction}", None)
        if handler is None:
            raise NotImplementedError(
                f"no resolver for construction {match.construction!r}")
        try:
            return handler(match, anchor)
        except (ValueError, OverflowError, KeyError):
            return None

    def _consumed(self, match: Match):
        return tuple(range(*match.span))

    # -- constructions -----------------------------------------------------

    def _offset_quantity(self, match):
        """The count of a relative offset: an explicit NUM, else a quantifier
        ("a"=1, "couple"=2, "half"=0.5), else an implicit 1 ("a week ago")."""
        num_tok = match.slots.get("NUM")
        if num_tok is not None:
            return float(num_tok.value)
        quant_tok = match.slots.get("QUANT")
        if quant_tok is not None:
            return self.spec.quantifiers[quant_tok.text]
        return 1.0

    def _resolve_relative_offset(self, match, anchor):
        qty = self._offset_quantity(match)
        unit = self.spec.units[match.slots["UNIT"].text]
        sign = self.spec.directions[match.slots["MARKER"].text]
        step = sign * qty
        if unit == "minute":
            value = anchor + timedelta(minutes=step)
        elif unit == "hour":
            value = anchor + timedelta(hours=step)
        elif unit == "day":
            value = anchor + timedelta(days=step)
        elif unit == "week":
            value = anchor + timedelta(weeks=step)
        elif unit == "fortnight":
            value = anchor + timedelta(weeks=2 * step)
        elif unit == "month":
            value = _add_months(anchor, int(step))
        elif unit == "year":
            value = _add_months(anchor, int(step) * 12)
        else:
            raise ValueError(f"unsupported offset unit {unit!r}")
        return Resolution(_point_span(value, unit), self._consumed(match))

    def _resolve_named_day(self, match, anchor):
        offset = self.spec.named_days[match.slots["DAY_WORD"].text]
        value = _midnight(anchor) + timedelta(days=offset)
        return Resolution(_day_span(value), self._consumed(match))

    def _named_day_offset(self, match, anchor, step):
        """"the day after/before <named day>": one day past/short of a named
        day ("the day after tomorrow" -> +2, "the day before yesterday" -> -2).
        Only the day unit shifts a named day by a whole day."""
        if self.spec.units[match.slots["UNIT"].text] != "day":
            return None
        offset = self.spec.named_days[match.slots["DAY_WORD"].text] + step
        return Resolution(_day_span(_midnight(anchor) + timedelta(days=offset)),
                          self._consumed(match))

    def _resolve_named_day_after(self, match, anchor):
        return self._named_day_offset(match, anchor, +1)

    def _resolve_named_day_before(self, match, anchor):
        return self._named_day_offset(match, anchor, -1)

    def _resolve_weekday_offset(self, match, anchor):
        """"a week from tuesday", "two weeks from monday": N weeks after the
        next occurrence (strictly future) of the named weekday."""
        if self.spec.units[match.slots["UNIT"].text] != "week":
            return None
        weeks = int(self._offset_quantity(match))
        target = self.spec.weekdays[match.slots["WEEKDAY"].text]
        ahead = (target - anchor.weekday()) % 7 or 7          # strictly future
        value = _midnight(anchor) + timedelta(days=ahead, weeks=weeks)
        return Resolution(_day_span(value), self._consumed(match))

    def _resolve_weekday_ref(self, match, anchor):
        target = self.spec.weekdays[match.slots["WEEKDAY"].text]
        rel = self.spec.rel_markers[match.slots["REL_MARKER"].text]
        base = _midnight(anchor)
        if rel > 0:      # next
            ahead = (target - anchor.weekday()) % 7 or 7
            value = base + timedelta(days=ahead)
        elif rel < 0:    # last
            back = (anchor.weekday() - target) % 7 or 7
            value = base - timedelta(days=back)
        else:            # this: within the current (monday-start) week
            week_start = base - timedelta(days=anchor.weekday())
            value = week_start + timedelta(days=target)
        return Resolution(_day_span(value), self._consumed(match))

    def _resolve_calendar_date(self, match, anchor):
        month = self.spec.months[match.slots["MONTH"].text]
        day_tok = match.slots.get("DAY")
        year_tok = match.slots.get("YEAR")
        day = int(day_tok.value) if day_tok else 1
        prefer_future = self.spec.construction_flags.get(
            "calendar_date", {}).get("prefer_future", False)
        if year_tok:
            year = int(year_tok.value)
        else:
            year = anchor.year
        value = datetime(year, month, day)          # raises on impossible
        if not year_tok and prefer_future and day_tok \
                and value < _midnight(anchor):
            value = value.replace(year=year + 1)
            year += 1
        span = _day_span(value) if day_tok \
            else _gregorian_month_span(year, month)
        return Resolution(span, self._consumed(match))

    def _resolve_reckoned_date(self, match, anchor):
        """Reckoned date over a registered calendar ("5 Tishrei 5785",
        "15 Sha'ban"): the unified family the design folds ``era_date`` and
        ``nongregorian_date`` into.  Resolved through JDN to a DateSpan --
        day-wide when a day is named, month-wide otherwise.
        """
        cal_key = match.calendar
        surface = match.slots["CAL_MONTH"].text
        month = self.spec.calendar_months[cal_key][surface]
        calendar = CALENDARS[cal_key]
        day_tok = match.slots.get("DAY")
        year_tok = match.slots.get("YEAR")
        day = int(day_tok.value) if day_tok else 1
        prefer_future = self.spec.construction_flags.get(
            match.construction, {}).get("prefer_future", False)
        anchor_jdn = gregorian_to_jdn(anchor.year, anchor.month, anchor.day)
        if year_tok:
            year = int(year_tok.value)
        else:
            year = calendar.from_jdn(anchor_jdn)[0]     # anchor's calendar year
        jdn = calendar.to_jdn(year, month, day)
        if not year_tok and prefer_future and day_tok and jdn < anchor_jdn:
            year += 1                                   # bump in calendar space
            jdn = calendar.to_jdn(year, month, day)
        if calendar.from_jdn(jdn) != (year, month, day):
            return None                                 # impossible day-in-month
        start = AstroDate(*jdn_to_gregorian(jdn))       # ValueError -> None
        if day_tok:
            span = DateSpan(start, start + timedelta(days=1))
        else:
            # month-wide: convert this month's first day AND next month's
            # first day through the calendar's own JDN hub, so the span tiles
            month_count = calendar.month_count
            nyear, nmonth = (year, month + 1) if month < month_count \
                else (year + 1, 1)
            end = AstroDate(*jdn_to_gregorian(calendar.to_jdn(nyear, nmonth, 1)))
            span = DateSpan(start, end)
        return Resolution(span, self._consumed(match))

    # ``nongregorian_date`` is the legacy construction name kept as an alias
    # for the unified ``reckoned_date`` family (zz/ar/he lang.json still use it)
    _resolve_nongregorian_date = _resolve_reckoned_date

    def _resolve_iso_date(self, match, anchor):
        y, m, d = (int(p) for p in match.slots["ISO"].text.split("-"))
        start = AstroDate(y, m, d)                       # ValueError -> None
        return Resolution(DateSpan(start, start + timedelta(days=1)),
                          self._consumed(match))

    def _resolve_hebrew_new_year(self, match, anchor):
        """"the hebrew new year N": Rosh Hashanah of Hebrew year N -- 1 Tishrei
        (month 7 in the Nisan-first month numbering this calendar uses),
        day-wide, converted through the Hebrew calendar's JDN hub."""
        year = int(match.slots["YEAR"].value)
        cal = CALENDARS["hebrew"]
        start = AstroDate(*jdn_to_gregorian(cal.to_jdn(year, 7, 1)))
        return Resolution(DateSpan(start, start + timedelta(days=1)),
                          self._consumed(match))

    def _resolve_year_ref(self, match, anchor):
        """A bare calendar year ("2027", "in 1995", "the year 2000"): a
        year-wide span ``[Jan 1 y, Jan 1 y+1)``.  The GYEAR slot only binds a
        bare 4-5 digit run, so plain small integers never read as years.  A
        spelled "year NUM SCALE" ("the year twelve thousand") multiplies the
        NUM by its scale word -- safe here because the scale word is reserved
        for deep time only in the "... years ago" framing."""
        gyear = match.slots.get("GYEAR")
        if gyear is not None:
            year = int(gyear.value)
        else:
            year = int(match.slots["NUM"].value) * self.spec.scales[
                match.slots["SCALE"].text]
        return Resolution(DateSpan(AstroDate(year, 1, 1), AstroDate(year + 1, 1, 1)),
                          self._consumed(match))

    def _decade_start(self, decade_tok, num_tok, anchor):
        """The Gregorian year a decade phrase begins on.

        Digit forms carry their own century: "1990s"/"2020s" -> that decade
        outright.  A bare tens ("the nineties", "the 90s") uses the
        *nearest-past* century convention -- the most recent decade with that
        tens digit that has already begun on the anchor date -- so in 2017
        "the twenties" is 1920 (2020 is still future) and "the nineties" is
        1990.  Returns None when the phrase names no whole-ten decade.
        """
        if decade_tok is not None:
            tens = self.spec.decade_words[decade_tok.text]
        else:
            n = int(num_tok.value)
            if n >= 1000:                       # explicit 4-digit decade
                return n - n % 10
            if n % 10 or not 0 <= n <= 90:      # a bare tens must be a multiple
                return None
            tens = n
        base = (anchor.year // 100) * 100 + tens
        return base - 100 if base > anchor.year else base

    def _resolve_decade_ref(self, match, anchor):
        """A decade span ("the 1990s", "the nineties", "the 90s"): ten years
        wide.  An optional early/mid/late PART slices it into thirds via
        :func:`chronologia.subdivide`."""
        base = self._decade_start(match.slots.get("DECADE"),
                                  match.slots.get("NUM"), anchor)
        if base is None:
            return None
        span = DateSpan(AstroDate(base, 1, 1), AstroDate(base + 10, 1, 1))
        part_tok = match.slots.get("PART")
        if part_tok is not None:
            from chronologia import subdivide
            span = subdivide(span, self.spec.period_parts[part_tok.text])
        return Resolution(DateSpan(span.start, span.end), self._consumed(match))

    def _resolve_month_fuzzy(self, match, anchor):
        """"early/mid/late <month>": the early/mid/late third of that month
        (this anchor year), sliced by :func:`chronologia.subdivide`."""
        from chronologia import subdivide
        month = self.spec.months[match.slots["MONTH"].text]
        part = self.spec.period_parts[match.slots["PART"].text]
        span = subdivide(_gregorian_month_span(anchor.year, month), part)
        return Resolution(DateSpan(span.start, span.end), self._consumed(match))

    def _resolve_month_day_ref(self, match, anchor):
        """"the first of the month": the Nth day of the current month, rolled
        to next month when that day has already passed (prefer_future)."""
        day = int(match.slots["ORD"].value)
        value = datetime(anchor.year, anchor.month, day)   # raises -> None
        prefer_future = self.spec.construction_flags.get(
            "month_day_ref", {}).get("prefer_future", False)
        if prefer_future and value < _midnight(anchor):
            value = _add_months(value, 1)
        return Resolution(_day_span(value), self._consumed(match))

    #: scope-word kind -> that period's length in whole years.
    _HALF_SCOPES = {"decade": 10, "century": 100, "millennium": 1000}

    def _resolve_half_period(self, match, anchor):
        """"the first/second half of <period>": the calendar half of a year,
        decade, century or millennium.  Halves are calendar-clean -- the year
        splits at July 1 (not the arithmetic mid-instant), a decade/century at
        its midpoint year -- so consecutive halves tile with no gap."""
        n = int(match.slots["NUM"].value)
        if n not in (1, 2):
            return None
        year_tok = match.slots.get("GYEAR")
        if year_tok is not None:
            y = int(year_tok.value)
            if n == 1:
                span = DateSpan(AstroDate(y, 1, 1), AstroDate(y, 7, 1))
            else:
                span = DateSpan(AstroDate(y, 7, 1), AstroDate(y + 1, 1, 1))
            return Resolution(span, self._consumed(match))
        length = self._HALF_SCOPES[self._scope_kind(match.slots["SCOPE_UNIT"])]
        base = (anchor.year // length) * length
        h = length // 2
        if n == 1:
            span = DateSpan(AstroDate(base, 1, 1), AstroDate(base + h, 1, 1))
        else:
            span = DateSpan(AstroDate(base + h, 1, 1),
                            AstroDate(base + length, 1, 1))
        return Resolution(span, self._consumed(match))

    # -- scoped_ordinal ----------------------------------------------------

    def _scope_kind(self, tok):
        return self.spec.scope_units.get(tok.text) or self.spec.units[tok.text]

    def _resolve_scoped_ordinal(self, match, anchor):
        """"Nth UNIT of SCOPE" nesting, absolute periods, last-ordinal (-1).

        Ports :func:`scoped_scan.extract_scoped_date` into the engine: the
        selected-unit width IS the span, resolved through
        :func:`ranges.get_date_ordinal` (reused verbatim, its scope/unit
        resolution tables imported).  Shapes are told apart by which slots
        the matcher bound:

        * ``ORD SCOPE_UNIT`` (no UNIT)              -> absolute period
          ("the 21st century");
        * ``ORD UNIT of SORD SCOPE_UNIT``           -> one nesting level
          ("the first decade of the 21st century");
        * ``ORD UNIT of MONTH [YEAR]``              -> month-scoped
          ("the 3rd week of june");
        * ``ORD UNIT of <year-word> [YEAR]``        -> year-scoped
          ("the 100th day of the year").

        ``last`` in place of the ordinal selects the final unit (-1).
        """
        ord_tok = match.slots.get("ORD")
        n = int(ord_tok.value) if ord_tok is not None else -1

        sord = match.slots.get("SORD")
        if sord is not None:                        # nested one level
            unit_kind = self._scope_kind(match.slots["SEL_UNIT"])
            scope_kind = self._scope_kind(match.slots["SCOPE_UNIT"])
            scope_ref = get_date_ordinal(int(sord.value),
                                         resolution=_ABSOLUTE[scope_kind])
            table = (_UNIT_OF_CENTURY if scope_kind == "century"
                     else _UNIT_OF_MILLENNIUM)
            res = table[unit_kind]
            value = get_date_ordinal(n, scope_ref, res)
            return self._ordinal_result(value, unit_kind, match)

        unit_tok = match.slots.get("UNIT")
        if unit_tok is None:                        # absolute period
            kind = self._scope_kind(match.slots["SCOPE_UNIT"])
            value = get_date_ordinal(n, resolution=_ABSOLUTE[kind])
            return self._ordinal_result(value, kind, match)

        unit_kind = self.spec.units[unit_tok.text]
        year_tok = match.slots.get("YEAR")
        year = int(year_tok.value) if year_tok else anchor.year
        month_tok = match.slots.get("MONTH")
        if month_tok is not None:                   # month-scoped
            month = self.spec.months[month_tok.text]
            res = _UNIT_OF_MONTH[unit_kind]
            value = get_date_ordinal(n, date(year, month, 1), res)
        else:                                       # year-scoped
            res = _UNIT_OF_YEAR[unit_kind]
            value = get_date_ordinal(n, date(year, 1, 1), res)
        return self._ordinal_result(value, unit_kind, match)

    def _ordinal_result(self, value, kind, match):
        start = value if isinstance(value, AstroDate) \
            else AstroDate.from_date(value)
        return Resolution(DateSpan(start, _unit_end(start, kind)),
                          self._consumed(match))

    # -- scoped period on an era axis ("the 3rd century bc", "2nd century ad")

    #: scope-word kind -> that period's length in whole years.  A scoped
    #: period ("century") is this many years wide on either axis.
    _SCOPE_YEARS = {"decade": 10, "century": 100, "millennium": 1000}

    def _resolve_scoped_ad(self, match, anchor):
        """"Nth SCOPE ad/ce": an explicit-AD scoped period.  Identical
        semantics to the plain absolute scoped period ("the 3rd century")
        -- the era marker only makes the AD axis explicit and consumes the
        marker token so it never leaks into the remainder."""
        n = int(match.slots["ORD"].value)
        kind = self._scope_kind(match.slots["SCOPE_UNIT"])
        value = get_date_ordinal(n, resolution=_ABSOLUTE[kind])
        return self._ordinal_result(value, kind, match)

    def _resolve_scoped_bc(self, match, anchor):
        """"Nth SCOPE bc/bce": a scoped period on the *BC axis*.

        The nth century BC spans the BC years ``(n-1)*100+1 .. n*100`` -- e.g.
        the 3rd century BC is 300 BC..201 BC, astronomically ``[-299, -199)``.
        Both edges are derived through the era registry (``before_christ``,
        which counts years backwards from AD 1): the older edge is the
        ``n*length``-th BC year, the younger edge the ``(n-1)*length``-th (the
        first year already in the next, more-recent period), so consecutive
        periods tile with no gap.  The span is one whole ``length`` wide.
        """
        from chronologia import resolve_era
        n = int(match.slots["ORD"].value)
        kind = self._scope_kind(match.slots["SCOPE_UNIT"])
        length = self._SCOPE_YEARS[kind]
        start = self._as_astro(resolve_era("before_christ", length * n))
        end = self._as_astro(resolve_era("before_christ", length * (n - 1)))
        return Resolution(DateSpan(start, end), self._consumed(match))

    @staticmethod
    def _as_astro(d) -> AstroDate:
        return d if isinstance(d, AstroDate) else AstroDate.from_date(d)

    # -- regnal_date -------------------------------------------------------

    def _resolve_regnal_date(self, match, anchor):
        """"<era-name> N" / "the Nth year of <era-name>" -> the Gregorian year
        span that regnal year occupies inside its reign segment.

        Delegates to :class:`~chronologia.regnal.RegnalSequence`, which
        clamps the year to the segment (Reiwa 1 begins at the 2019 accession,
        the last year of a closed era ends at the successor's accession).
        """
        seqkey, segname = self.spec.regnal_names[match.slots["ERANAME"].text]
        seq = REGNAL_SEQUENCES[seqkey]
        num_tok = match.slots.get("NUM") or match.slots.get("ORD")
        n = int(num_tok.value) if num_tok is not None else 1   # bare eponym
        span = seq.year_span(segname, n)
        if span is None:
            return None
        return Resolution(DateSpan(*span), self._consumed(match))

    # -- roman_date (Kalends / Nones / Ides) -------------------------------

    def _resolve_roman_date(self, match, anchor):
        """"a.d. III Kal. Apr." / "pridie Idus Martias" / "Idibus Martiis":
        inclusive backward counting from a monthly anchor, over the Julian
        calendar (see :mod:`chronologia.roman`).  Day-wide span; the
        ordinal-beyond-the-span case yields ``None``.
        """
        anchor_name = self.spec.roman_anchors[match.slots["ANCHOR_DAY"].text]
        month = self.spec.months[match.slots["MONTH"].text]
        if "ORD" in match.slots:
            count = int(match.slots["ORD"].value)
        elif "PRIDIE" in match.slots:
            count = 2
        else:
            count = 1                       # bare ablative: the anchor day
        ymd = roman_to_julian(anchor.year, month, anchor_name, count)
        if ymd is None:
            return None
        start = AstroDate(*ymd)             # Julian-calendar labels
        return Resolution(DateSpan(start, start + timedelta(days=1)),
                          self._consumed(match))

    # -- cycle_ref (generalised weekday over any named day cycle) ----------

    def _resolve_cycle_ref(self, match, anchor):
        """"next/last/this <cycle-day>" over an arbitrary named day cycle.

        The generalisation of ``weekday_ref``: the seven-day week is just the
        ``week`` cycle, so a bare-week query here lands the identical day the
        legacy weekday path returns.  Also resolves the French Republican
        décade (month-anchored) and the Roman nundinal cycle (free-running).
        Day-wide span; midnight of the resolved day.
        """
        surface = match.slots["CYCLE_DAY"].text
        cycle = DAY_CYCLES[self.spec.day_cycles[surface]]
        position = self.spec.cycle_positions[surface]
        rel_tok = match.slots.get("REL_MARKER")
        rel = self.spec.rel_markers[rel_tok.text] if rel_tok is not None else 0
        anchor_jdn = gregorian_to_jdn(anchor.year, anchor.month, anchor.day)
        target = resolve_cycle_day(cycle, position, rel, anchor_jdn)
        if target is None:
            return None
        start = AstroDate(*jdn_to_gregorian(target))
        return Resolution(DateSpan(start, start + timedelta(days=1)),
                          self._consumed(match))

    # -- season_ref --------------------------------------------------------

    def _resolve_season_ref(self, match, anchor):
        """Hemisphere-aware meteorological season, next/last/this, "of YYYY".

        Ports the season handling of :func:`scoped_scan.extract_scoped_date`
        into the engine, reusing ``ranges``'s season tables.  The width is a
        fixed **three months** (the meteorological season length) from the
        season's first day; the hemisphere is the language's ``hemisphere``
        convention (a fact), so the same vocabulary resolves correctly north
        and south of the equator.
        """
        season = Season[self.spec.seasons[match.slots["SEASON"].text].upper()]
        hemi = (Hemisphere.SOUTH if self.conventions.hemisphere == "south"
                else Hemisphere.NORTH)
        ref = anchor.date()
        year_tok = match.slots.get("YEAR")
        rel_tok = match.slots.get("REL_MARKER")
        if year_tok is not None:
            start = season_to_date(season, int(year_tok.value), hemi)
        elif rel_tok is not None and self.spec.rel_markers[rel_tok.text] > 0:
            start = next_season_date(season, ref, hemi)
        elif rel_tok is not None and self.spec.rel_markers[rel_tok.text] < 0:
            start = last_season_date(season, ref, hemi)
        else:                                       # this / bare
            start = season_to_date(season, ref, hemi)
        start_dt = datetime(start.year, start.month, start.day)
        span_start = AstroDate.from_datetime(start_dt)
        end = AstroDate.from_datetime(_add_months(start_dt, 3))
        return Resolution(DateSpan(span_start, end), self._consumed(match))

    # -- era_date family (BC / AD / before-present), year-wide -------------

    def _era_span(self, era, n):
        from chronologia import resolve_era
        d = resolve_era(era, n)
        start = d if isinstance(d, AstroDate) else AstroDate.from_date(d)
        end = AstroDate(start.year + 1, start.month, start.day)
        return DateSpan(start, end)

    def _resolve_era_bc(self, match, anchor):
        n = int(match.slots["NUM"].value)
        return Resolution(self._era_span("before_christ", n),
                          self._consumed(match))

    def _resolve_era_ad(self, match, anchor):
        n = int(match.slots["NUM"].value)
        return Resolution(self._era_span("common_era", n),
                          self._consumed(match))

    def _resolve_era_bp(self, match, anchor):
        n = int(match.slots["NUM"].value)
        return Resolution(self._era_span("before_present", n),
                          self._consumed(match))

    # -- deep_time ("66 million years ago", "4.5 billion years ago") ------

    #: scale multiplier -> chronologia SI-prefixed Before-Present unit.  The
    #: sig-fig precision rule lives *at the spoken unit*: "66 million" is
    #: 1-Ma-wide (one place of the "66"), not year-precise, so the value
    #: string and its scale unit -- not the pre-multiplied year count -- are
    #: what :func:`chronologia.resolve_bp` must see.
    _BP_SCALE_UNITS = {1_000: "ka", 1_000_000: "Ma", 1_000_000_000: "Ga"}

    def _resolve_deep_time(self, match, anchor):
        """Numeric deep time via the radiocarbon before-present convention.

        The value is ``NUM x SCALE`` years before present (1950).  The span's
        width is the *referential precision* read off the spoken value's last
        significant digit at its scale unit: "66 million" -> 1 Ma wide, "66.5
        million" -> 100 ka, "4.5 billion" -> 100 Ma.  We route the untouched
        value **string** and the SI unit through :func:`chronologia.resolve_bp`
        so the sig-fig rule applies before value x scale collapses to years.
        """
        from chronologia import resolve_bp
        num = match.slots["NUM"]
        factor = self.spec.scales[match.slots["SCALE"].text]
        unit = self._BP_SCALE_UNITS.get(factor)
        if unit is not None:
            span = resolve_bp(num.text, unit)
        else:  # scale word with no SI unit (e.g. "hundred"): fall back to years
            span = resolve_bp(num.value * factor, "a")
        return Resolution(DateSpan(span.start, span.end), self._consumed(match))

    # -- named_period ("during the jurassic", "the late cretaceous") ------

    def _resolve_named_period(self, match, anchor):
        from chronologia import PERIODS, subdivide
        key = self.spec.periods[match.slots["PERIOD"].text]
        period = PERIODS[key]
        part_tok = match.slots.get("PART")
        if part_tok is not None:
            span = subdivide(period, self.spec.period_parts[part_tok.text])
        else:
            span = period.span
        return Resolution(DateSpan(span.start, span.end), self._consumed(match))

    # -- clock_time --------------------------------------------------------

    def _resolve_clock_time(self, match, anchor):
        """Resolve a clock reference to a **minute-wide** span anchored on the
        resolved-or-anchor date.

        Three shapes, distinguished by which slots the matcher bound:

        * ``CLOCK`` -- a ``HH:MM[:SS]`` digit literal, taken verbatim;
        * ``FRACTION CLOCKDIR HOUR`` -- "half past ten", "quarter to five":
          the fraction's minutes are added on the *past* side and subtracted
          (rolling the hour back one) on the *to* side;
        * bare ``HOUR`` (from "at ten", "ten o'clock") -- minute 0.

        An optional ``MERIDIEM`` slot applies the language's am/pm policy
        (12h -> 24h).  ``prefer_future`` (a construction fact) rolls a time
        already past on the anchor day to the next day.
        """
        hms = self._clock_hms(match)
        if hms is None:
            return None
        hour, minute, second = hms
        if not (0 <= minute <= 59 and 0 <= second <= 59):
            return None
        if hour == 24 and minute == 0 and second == 0:
            hour = 0
        if not 0 <= hour <= 23:
            return None
        base = _midnight(anchor)
        dt = base.replace(hour=hour, minute=minute, second=second)
        prefer_future = self.spec.construction_flags.get(
            match.construction, {}).get("prefer_future", False)
        if prefer_future and dt < anchor:
            dt = dt + timedelta(days=1)
        start = AstroDate.from_datetime(dt)
        return Resolution(DateSpan(start, start + timedelta(minutes=1)),
                          self._consumed(match))

    #: military "HHMM hours" / bare "0600" reuse the clock resolver verbatim.
    _resolve_military_time = _resolve_clock_time

    def _resolve_subdivision_time(self, match, anchor):
        """A clock reading in an alternative day subdivision, rescaled to civil
        time by exact day-fraction arithmetic.

        French decimal time ("5 decimal hours" == exactly noon): the reading
        is converted through the subdivision's unit->day-fraction table to
        civil microseconds since midnight.  The span width is the smallest
        named subdivision unit's civil duration -- honest referential width,
        so "5 decimal hours" is a 2.4-civil-hour-wide span, not a false point.
        """
        sub = DAY_SUBDIVISIONS[self.spec.day_subdivision]
        subh = int(match.slots["SUBH"].value)
        subm_tok = match.slots.get("SUBM")
        subs_tok = match.slots.get("SUBS")
        subm = int(subm_tok.value) if subm_tok else 0
        subs = int(subs_tok.value) if subs_tok else 0
        start_us = sub.units_to_us(subh, subm, subs)
        if not 0 <= start_us < US_PER_DAY:
            return None
        smallest = "second" if subs_tok else "minute" if subm_tok else "hour"
        width_us = sub.unit_width_us(smallest)
        base = _midnight(anchor)
        start_dt = base + timedelta(microseconds=start_us)
        start = AstroDate.from_datetime(start_dt)
        end = start + timedelta(microseconds=width_us)
        return Resolution(DateSpan(start, end), self._consumed(match))

    def _clock_hms(self, match):
        clock = match.slots.get("CLOCK")
        miltime = match.slots.get("MILTIME") or match.slots.get("MILTIMEZ")
        landmark = match.slots.get("LANDMARK")
        if clock is not None:
            parts = [int(p) for p in clock.text.split(":")]
            hour, minute = parts[0], parts[1]
            second = parts[2] if len(parts) > 2 else 0
        elif miltime is not None:
            raw = miltime.raw.rstrip(".")
            hour, minute, second = int(raw[:2]), int(raw[2:]), 0
        else:
            second = 0
            # base hour/minute: a landmark ("midnight" 0, "noon" 720) or a
            # bare hour ("at ten") -- the fraction/minute offset applies on top
            if landmark is not None:
                hour, minute = divmod(self.spec.clock_landmarks[landmark.text], 60)
            else:
                hour, minute = int(match.slots["HOUR"].value), 0
            frac_tok = match.slots.get("FRACTION")
            min_tok = match.slots.get("MINUTE")
            dir_tok = match.slots.get("CLOCKDIR")
            if dir_tok is not None and (frac_tok is not None or min_tok is not None):
                offset = (self.spec.clock_fractions[frac_tok.text]
                          if frac_tok is not None else int(min_tok.value))
                if self.spec.clock_dirs[dir_tok.text] > 0:      # past
                    minute += offset
                else:                                           # to (before)
                    hour -= 1
                    minute = 60 - offset
            if hour < 0:            # "quarter to midnight" underflows -> 23:45
                hour += 24
        meridiem = match.slots.get("MERIDIEM")
        if meridiem is not None:
            off = self.spec.meridiems[meridiem.text]
            if off == 12 and hour < 12:
                hour += 12
            elif off == 0 and hour == 12:
                hour = 0
        return hour, minute, second
