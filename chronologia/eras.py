"""Named eras, epochs, and out-of-range dates.

``datetime.date`` only represents years 1..9999, so phrases like
"3000 BC", "10000 years before present" or "in the year 12000" cannot be
resolved into stdlib types.  This module provides the representation and the
arithmetic for those cases:

* :class:`AstroDate` — a frozen, date-like value using **astronomical year
  numbering** and an unbounded year.
* :func:`astro_year_range` — decade/century/millennium ranges for any year,
  the out-of-range counterpart of ``get_decade_range`` and friends.
* :class:`Era` / :data:`ERAS` / :func:`resolve_era` — a language-agnostic
  registry of calendar eras and epochs ("anno domini", "before present",
  "unix time", "julian day", ...) and the conversion of a count in an era
  into a concrete date.

Conventions
-----------
* **Astronomical year numbering** (ISO 8601 expanded / astronomical usage):
  there is a year 0, and ``X BC`` maps to year ``1 - X`` (1 BC = 0,
  4713 BC = -4712).  This keeps decade/century/millennium arithmetic pure
  floor division with no "no year zero" special case.
* **Proleptic Gregorian calendar** throughout, matching Python's ``datetime``.
  There is no Julian/Gregorian switch in 1582; historical Julian-calendar
  dates are out of scope.
* :class:`AstroDate` is tz-naive by construction (civil timezones are
  meaningless in 3000 BC).  It carries no imprecision tag — referential width
  is :class:`~chronologia.astrodate.DateSpan`'s job, not this type's.

Only results that ``datetime`` cannot represent become :class:`AstroDate`;
everything in range is returned as plain ``datetime.date`` / ``datetime``
so existing consumers never see the new type unless they parse era phrases.
"""
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Callable, Optional, Tuple, Union

from chronologia.astrodate import AstroDate, DateSpan, is_leap_year
from chronologia.calendars import (CALENDARS, Calendar, gregorian_to_jdn,
                                        jdn_to_gregorian)
from chronologia.resolution import DateTimeResolution

# The proleptic Gregorian calendar as a JDN-hub :class:`Calendar`, so an era
# may be *numbered on the Gregorian calendar itself* (the Byzantine Anno Mundi
# reckoning below) without touching the arithmetic-calendar registry.  Not
# added to ``CALENDARS`` (that module is math-only and owns its own set);
# era-year resolution looks eras up through ``_ERA_CALENDARS``.
_GREGORIAN_CALENDAR = Calendar(
    "gregorian", 12, gregorian_to_jdn, jdn_to_gregorian,
    gregorian_to_jdn(1, 1, 1))
_ERA_CALENDARS = {**CALENDARS, "gregorian": _GREGORIAN_CALENDAR}


def astro_year_range(year: int, resolution: DateTimeResolution
                     ) -> Tuple[AstroDate, AstroDate]:
    """Decade/century/millennium containing ``year``, for any year.

    Out-of-range counterpart of ``get_decade_range``/``get_century_range``/
    ``get_millennium_range``; matches their convention that a period is the
    floor-division bucket (the 1980s are 1980..1989).  Astronomical numbering
    makes this exact for BC years with no special case: the century containing
    2999 BC (year -2998) is -3000..-2901.
    """
    span = {DateTimeResolution.YEAR: 1,
            DateTimeResolution.DECADE: 10,
            DateTimeResolution.CENTURY: 100,
            DateTimeResolution.MILLENNIUM: 1000}.get(resolution)
    if span is None:
        raise ValueError(f"unsupported resolution for a year range: "
                         f"{resolution}")
    start = (year // span) * span
    return (AstroDate(start, 1, 1), AstroDate(start + span - 1, 1, 1))


# --------------------------------------------------------------------------
# Era registry
# --------------------------------------------------------------------------

class EraCounting:
    """How a numeric value counts within an era (plain constants, not Enum,
    so per-language tables can be trivially serialized later)."""
    YEARS_SINCE = "years_since"      # "year N of the era"; year 1 = epoch year
    YEARS_BEFORE = "years_before"    # "N years before the epoch" (e.g. BP)
    DAYS_SINCE = "days_since"        # day count from a fixed origin (Julian day)
    SECONDS_SINCE = "seconds_since"  # second count from a fixed origin (unix)


@dataclass(frozen=True)
class Era:
    """A year-numbering convention, optionally *attached to a calendar*.

    ``epoch.year`` is the astronomical year of **era year 1** for
    YEARS_SINCE eras, or the reference point for the other counting modes.

    ``calendar`` names an entry in :data:`~chronologia.calendars.CALENDARS`
    when the era numbers a non-Gregorian calendar's own years (Anno Mundi is
    the Hebrew calendar's numbering, the French Republican and Bahá'í eras
    number their own calendars).  ``year_transform`` maps the spoken era-year
    to that calendar's native year (identity for AM/FR/BE).  Calendar-backed
    eras resolve **exactly** through the calendar's JDN hub instead of the
    epoch+count approximation the counting modes use.
    """
    key: str
    epoch: AstroDate
    counting: str = EraCounting.YEARS_SINCE
    calendar: Optional[str] = None
    year_transform: Optional[Callable[[int], int]] = None
    #: ``(month, day)`` at which this era's year begins on its calendar, when
    #: it is not 1 January / day 1.  The Byzantine Anno Mundi year begins 1
    #: September (Gregorian), so its era-year span runs 1 Sep -> next 1 Sep.
    #: ``None`` falls back to :data:`_CALENDAR_YEAR_START` then ``(1, 1)``.
    year_start: Optional[Tuple[int, int]] = None
    #: number of calendar years one era "year" spans; 1 for ordinary eras,
    #: 4 for the Olympiad (a four-year cycle counted from the first Olympiad).
    year_length: int = 1


# The (month, day) at which a calendar's year begins in ITS OWN numbering,
# used to place a calendar-backed era year.  The Hebrew civil year begins on
# 1 Tishri (month 7 in the ecclesiastical numbering calendars.py transcribes);
# the arithmetic French Republican and Bahá'í years begin at month 1 day 1.
_CALENDAR_YEAR_START = {"hebrew": (7, 1)}


#: Language-agnostic era registry.  Keys are stable identifiers that
#: per-language vocabularies map surface forms onto ("avant J.-C." ->
#: "before_christ").  Epochs are cited to canonical sources saved under
#: ``~/AgentWorkspaces/papers/calendars/`` where noted.
ERAS = {
    # Common/Christian era.  Era year 1 == astronomical year 1 by definition
    # of astronomical numbering.
    "common_era": Era("common_era", AstroDate(1, 1, 1)),
    # BC/BCE counts years *backwards* ending at 1 BC (astronomical 0):
    # "X BC" = year 1 - X, which is YEARS_BEFORE reckoned from year 1.
    "before_christ": Era("before_christ", AstroDate(1, 1, 1),
                         EraCounting.YEARS_BEFORE),
    # Radiocarbon "Before Present": present fixed at AD 1950.
    # Stuiver & Polach 1977, "Discussion: Reporting of 14C Data",
    # Radiocarbon 19(3):355-363 (papers/calendars/
    # stuiver_polach_1977_reporting_c14_data.pdf).
    "before_present": Era("before_present", AstroDate(1950, 1, 1),
                          EraCounting.YEARS_BEFORE),
    # Unix time: seconds since 1970-01-01T00:00:00Z, "the Epoch" per
    # POSIX.1-2017 §4.16 (papers/calendars/opengroup_epoch_seconds.html).
    "unix": Era("unix", AstroDate(1970, 1, 1),
                EraCounting.SECONDS_SINCE),
    # Julian day number: JD 0 begins Greenwich noon, 1 January 4713 BC
    # proleptic *Julian* calendar = astronomical -4712 (USNO, "Converting
    # Between Julian Dates and Gregorian Calendar Dates",
    # papers/calendars/usno_julian_date.html).  Resolution to a Gregorian
    # date is done by integer algorithm, not epoch arithmetic — see
    # julian_day_to_date().
    "julian_day": Era("julian_day", AstroDate(-4712, 1, 1),
                      EraCounting.DAYS_SINCE),
    # Holocene/Human Era (Emiliani 1993, Nature 366:716): HE = CE + 10000,
    # hence HE year 1 = 10000 BC = astronomical -9999.  (Upstream
    # lingua-franca #96 had -10000 — an off-by-one.)
    "holocene": Era("holocene", AstroDate(-9999, 1, 1)),
    # Anno Mundi == the Hebrew calendar's own year numbering; AM N resolves
    # EXACTLY to 1 Tishri of Hebrew year N through calendars.py (AM 1 =
    # -3760-09-07, AM 5786 = 2025-09-23), not the epoch.year+N-1 approximation.
    "anno_mundi": Era("anno_mundi", AstroDate(-3760, 1, 1),
                      calendar="hebrew"),
    # French Republican era numbers its own calendar; An I began
    # 22 September 1792 (décret of the Convention nationale, 1793).
    "french_republican": Era("french_republican", AstroDate(1792, 9, 22),
                             calendar="french_republican"),
    # Bahá'í (Badí') era numbers its own calendar; BE 1 began 21 March 1844.
    "bahai": Era("bahai", AstroDate(1844, 3, 21), calendar="bahai"),
    # Thai (Rattanakosin-era solar) year count as fixed by the 1941 act:
    # BE = CE + 543; era year 1 = 543 BC = astronomical -542.
    "buddhist": Era("buddhist", AstroDate(-542, 1, 1)),
    # Byzantine (Creation) Anno Mundi: a year-numbering *on the Gregorian
    # calendar* whose civil year begins 1 September; AM n begins 1 September
    # of Gregorian year n - 5509, so AM 7535 spans 2026-09-01..2027-09-01
    # (byzantine_calendar_reference.html: epoch 1 Sep 5509 BC, current-year
    # worked example AD 2026 -> AM 7535 after 1 September).
    "byzantine_am": Era("byzantine_am", AstroDate(-5508, 9, 1),
                        calendar="gregorian",
                        year_transform=lambda n: n - 5509,
                        year_start=(9, 1)),
    # Olympiad era: a four-year cycle counted from the first Olympiad, 776 BC
    # (astronomical -775), each period beginning at midsummer (1 July).
    # Olympiad N begins in Gregorian year 4N - 779 (olympiad_era_reference.html).
    "olympiad": Era("olympiad", AstroDate(-775, 7, 1),
                    calendar="gregorian",
                    year_transform=lambda n: 4 * n - 779,
                    year_start=(7, 1), year_length=4),
}


def julian_day_to_date(jd: int) -> Union[date, AstroDate]:
    """Convert an integral Julian day number to a proleptic Gregorian date.

    Delegates the arithmetic to :func:`calendars.jdn_to_gregorian` (the single
    JDN hub, Fliegel & Van Flandern), returning a plain ``datetime.date`` when
    representable and an :class:`AstroDate` otherwise.  The day returned is the
    civil date on which that Julian day *begins* (Julian days start at noon).
    """
    year, month, day = jdn_to_gregorian(int(jd))
    if date.min.year <= year <= date.max.year:
        return date(year, month, day)
    return AstroDate(year, month, day)


def _era_native_year(era: Era, value: Union[int, float]) -> int:
    """The calendar-native year AM/BE/... value ``value`` names."""
    return era.year_transform(int(value)) if era.year_transform else int(value)


def _era_year_start(era: Era) -> Tuple[int, int]:
    """``(month, day)`` this era's year begins on its calendar."""
    if era.year_start is not None:
        return era.year_start
    return _CALENDAR_YEAR_START.get(era.calendar, (1, 1))


def resolve_era_year_span(era: Union[str, Era], value: Union[int, float]
                          ) -> Tuple[AstroDate, AstroDate]:
    """Half-open ``[start, next-start)`` span of a calendar-backed era year.

    The era's year begins at :attr:`Era.year_start` on its calendar and runs
    to the same day of the next era year, so era years tile with no gap even
    when the year does not start on 1 January (Byzantine Anno Mundi: 1
    September to the next 1 September).  Both endpoints go through the
    calendar's own JDN hub, so the span is exact.
    """
    if isinstance(era, str):
        era = ERAS[era]
    if era.calendar is None:
        raise ValueError(f"era {era.key!r} is not calendar-backed; "
                         f"resolve_era_year_span needs a calendar")
    cal = _ERA_CALENDARS[era.calendar]
    cyear = _era_native_year(era, value)
    sm, sd = _era_year_start(era)
    start = AstroDate(*jdn_to_gregorian(cal.to_jdn(cyear, sm, sd)))
    end = AstroDate(*jdn_to_gregorian(
        cal.to_jdn(cyear + era.year_length, sm, sd)))
    return start, end


# --------------------------------------------------------------------------
# Scaled Before-Present units (deep time)
# --------------------------------------------------------------------------

#: Years per scaled Before-Present unit.  ``a`` = annum (year), ``ka`` = kilo-
#: annum (10^3 yr), ``Ma`` = mega-annum (10^6 yr), ``Ga`` = giga-annum
#: (10^9 yr) — the SI-prefixed units of the geologic literature (IUGS/ICS).
_BP_UNITS = {"a": 1, "ka": 1_000, "Ma": 1_000_000, "Ga": 1_000_000_000}

#: The Before-Present epoch: AD 1950 (Stuiver & Polach 1977; see
#: ``ERAS["before_present"]``).  "0 BP" is 1950-01-01.
_BP_EPOCH_YEAR = 1950

# Mean Gregorian year in days, for the (rare) sub-year BP remainder only.
_MEAN_YEAR_DAYS = Decimal("365.2425")


def _astrodate_years_before_present(years_before: Decimal) -> AstroDate:
    """The :class:`AstroDate` ``years_before`` years before AD 1950.

    Whole years step the astronomical year field exactly (leap structure
    preserved); a fractional part — only reachable with sub-year precision —
    is applied as a mean-Gregorian-year number of days, the one documented
    approximation (a fraction of a year has no exact calendar length).
    """
    whole = int(years_before)                      # truncates toward zero
    frac = years_before - whole
    base = AstroDate(_BP_EPOCH_YEAR - whole, 1, 1)
    if frac == 0:
        return base
    # larger years_before == further into the past == earlier date
    return base - timedelta(days=float(frac * _MEAN_YEAR_DAYS))


def resolve_bp(value: Union[int, float, str, Decimal], unit: str = "a"
               ) -> DateSpan:
    """Resolve a scaled Before-Present expression into a :class:`DateSpan`.

    ``unit`` is one of ``a``/``ka``/``Ma``/``Ga`` (10^0/10^3/10^6/10^9 years).
    The returned span's **width is the precision of the expression**, read off
    the last significant digit: the span is one unit of that digit's place
    wide.  Pass ``value`` as a **string** (or ``Decimal``) when precision
    matters — ``"66"`` and ``"66.0"`` denote different precisions but the
    floats ``66``/``66.0`` are indistinguishable once parsed, so the string
    form is authoritative.

    Sig-fig rule (precise): let ``e`` be the decimal exponent of ``value`` as
    written (``Decimal(str(value)).as_tuple().exponent`` — ``0`` for ``"66"``,
    ``-3`` for ``"66.043"``, ``-1`` for ``"66.0"``).  The precision is
    ``10**e`` of the unit, so:

    * ``"66 Ma"``    (e=0)  -> 1 Ma wide;
    * ``"66.043 Ma"``(e=-3) -> 10^-3 Ma = 1 ka wide;
    * ``"66.0 Ma"``  (e=-1) -> 10^-1 Ma = 100 ka wide.

    Trailing zeros *before* the decimal point are treated as significant
    (``"660"`` -> place value = ones), the standard ambiguous case, resolved
    this way because ``Decimal`` reports their exponent as ``0``.

    Orientation: the stated value is the span's **start** (the older, more
    negative astronomical year) and the span runs one precision unit *toward
    the present* — half-open ``[value, value + precision)`` on the
    years-before-present axis — so consecutive precision bins tile exactly
    ("66 Ma" abuts "67 Ma" at their shared 66-Ma-ago edge).  ``basis`` is
    ``"reconstructed"``: a deep-time date is a modelled (e.g. radiometric)
    reconstruction, never an observed civil instant.

    Example: ``resolve_bp("66", "Ma")`` -> a 1-Ma span whose ``start`` is
    astronomical year ``1950 - 66_000_000 = -65_998_050`` (the K–Pg boundary
    epoch to Ma precision).
    """
    if unit not in _BP_UNITS:
        raise ValueError(f"unknown BP unit {unit!r}; expected one of "
                         f"{sorted(_BP_UNITS)}")
    dval = Decimal(str(value))
    mult = _BP_UNITS[unit]
    years_before = dval * mult
    precision_years = Decimal(1).scaleb(dval.as_tuple().exponent) * mult
    start = _astrodate_years_before_present(years_before)
    end = _astrodate_years_before_present(years_before - precision_years)
    return DateSpan(start, end, basis="reconstructed")


def resolve_era(era: Union[str, Era], value: Union[int, float]
                ) -> Union[date, datetime, AstroDate]:
    """Resolve "value in era" into a concrete date.

    Returns plain ``datetime.date`` (or, for second-counted eras, an aware
    UTC ``datetime``) whenever the result is representable; an
    :class:`AstroDate` otherwise.  Never raises ``OverflowError``.
    """
    if isinstance(era, str):
        era = ERAS[era]

    if era.calendar is not None:
        # calendar-backed era: resolve EXACTLY to the start of the named
        # calendar year through that calendar's JDN hub (no epoch+count drift)
        cal = _ERA_CALENDARS[era.calendar]
        cyear = _era_native_year(era, value)
        start_month, start_day = _era_year_start(era)
        return julian_day_to_date(cal.to_jdn(cyear, start_month, start_day))

    if era.counting == EraCounting.SECONDS_SINCE:
        # sub-year precision is meaningful here; epochs are in range
        epoch = datetime(era.epoch.year, era.epoch.month,
                         era.epoch.day, tzinfo=timezone.utc)
        return epoch + timedelta(seconds=value)

    if era.counting == EraCounting.DAYS_SINCE:
        # julian_day is the only day-counted era; its origin is baked into
        # the conversion algorithm rather than derived from the epoch field
        return julian_day_to_date(int(value))

    value = int(value)
    if era.counting == EraCounting.YEARS_BEFORE:
        year = era.epoch.year - value
    else:  # YEARS_SINCE: era year 1 is the epoch year
        year = era.epoch.year + value - 1

    result = AstroDate(year, 1, 1)
    return result.date() or result
