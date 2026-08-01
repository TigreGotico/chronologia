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
import logging
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from typing import Callable, Optional, Tuple, Union

_log = logging.getLogger(__name__)

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

    def __repr__(self) -> str:
        return "EraCounting()"       # a constants namespace; carries no state


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
    #: JDN one *below* day 1 of a DAYS_SINCE era, so day ``n`` resolves to
    #: ``julian_day_to_date(day_epoch_jdn + n)``.  ``None`` (the Julian-day era)
    #: means the counted value *is itself* the JDN (no shift).  Rata Die counts
    #: from R.D. 1 = 0001-01-01 (proleptic Gregorian), the Lilian date from
    #: L.D. 1 = 1582-10-15 (the Gregorian reform day).
    day_epoch_jdn: Optional[int] = None
    #: the new-year (month, day) shifts one day EARLIER in a Gregorian leap
    #: year.  The reformed Saka (Indian national) calendar's Chaitra 1 is
    #: 22 March in a common year and 21 March in a Gregorian leap year.
    leap_shifts_new_year: bool = False


# The (month, day) at which a calendar's year begins in ITS OWN numbering,
# used to place a calendar-backed era year.  The Hebrew civil year begins on
# 1 Tishri (month 7 in the ecclesiastical numbering calendars.py transcribes);
# the arithmetic French Republican and Bahá'í years begin at month 1 day 1.
_CALENDAR_YEAR_START = {"hebrew": (7, 1)}


#: Language-agnostic era registry.  Keys are stable identifiers that
#: per-language vocabularies map surface forms onto ("avant J.-C." ->
#: "before_christ").  Epochs are cited to canonical sources where noted.
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
    # Radiocarbon 19(3):355-363.
    "before_present": Era("before_present", AstroDate(1950, 1, 1),
                          EraCounting.YEARS_BEFORE),
    # Unix time: seconds since 1970-01-01T00:00:00Z, "the Epoch" per
    # POSIX.1-2017 §4.16.
    "unix": Era("unix", AstroDate(1970, 1, 1),
                EraCounting.SECONDS_SINCE),
    # Julian day number: JD 0 begins Greenwich noon, 1 January 4713 BC
    # proleptic *Julian* calendar = astronomical -4712 (USNO, "Converting
    # Between Julian Dates and Gregorian Calendar Dates").  Resolution to a Gregorian
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
    # (Wikipedia, "Byzantine calendar": epoch 1 Sep 5509 BC, current-year
    # worked example AD 2026 -> AM 7535 after 1 September).
    "byzantine_am": Era("byzantine_am", AstroDate(-5508, 9, 1),
                        calendar="gregorian",
                        year_transform=lambda n: n - 5509,
                        year_start=(9, 1)),
    # Ab urbe condita ("from the founding of the City"): the Varronian epoch
    # dates Rome's foundation to 753 BC (astronomical -752), so AUC year 1 ==
    # 753 BC and AUC 753 == 1 BC (astronomical 0).  A proleptic year count, not
    # attached to a calendar; YEARS_SINCE reckons AUC N as astronomical year
    # -752 + N - 1.  (Varro's date is the conventional one; Cato's 751 BC and
    # Fabius Pictor's 748 BC are the historical alternatives, not used here.)
    # Source: Wikipedia, "Ab urbe condita".
    "ab_urbe_condita": Era("ab_urbe_condita", AstroDate(-752, 1, 1)),
    # Olympiad era: a four-year cycle counted from the first Olympiad, 776 BC
    # (astronomical -775), each period beginning at midsummer (1 July).
    # Olympiad N begins in Gregorian year 4N - 779 (Wikipedia, "Olympiad").
    "olympiad": Era("olympiad", AstroDate(-775, 7, 1),
                    calendar="gregorian",
                    year_transform=lambda n: 4 * n - 779,
                    year_start=(7, 1), year_length=4),

    # ------------------------------------------------------------------
    # Calendar-backed eras — resolved EXACTLY through calendars.py, never a
    # Gregorian approximation.  Each numbers its own calendar's year 1.
    # ------------------------------------------------------------------
    # Armenian era: year 1 begins 11 July 552 (Julian) = 13 July 552
    # (proleptic Gregorian), the epoch of the Armenian calendar's 365-day
    # wandering year.  (Wikipedia, "Armenian calendar": era of 552 AD.)
    "armenian": Era("armenian", AstroDate(552, 7, 13), calendar="armenian"),
    # Coptic Era of the Martyrs / Diocletian (Anno Martyrum): year 1 = 1 Thout
    # AM 1 = 29 August 284 (Julian epoch of Diocletian's accession), the Coptic
    # calendar's own numbering.  (Wikipedia, "Era of the Martyrs".)
    "diocletian": Era("diocletian", AstroDate(284, 8, 29), calendar="coptic"),
    # Ethiopian Incarnation Era (Amete Mihret, "Year of Grace"): the civil
    # Ethiopian calendar's own numbering, year 1 = 29 August 8 (Julian) =
    # 8-08-27 proleptic Gregorian.  (Wikipedia, "Ethiopian calendar".)
    "amete_mihret": Era("amete_mihret", AstroDate(8, 8, 27),
                        calendar="ethiopian"),
    # Islamic Hijri era (Anno Hegirae): year 1 = 1 Muharram AH 1 = 16 July 622
    # (Julian) = 622-07-19 proleptic Gregorian, the tabular civil-Hijri epoch.
    # (Wikipedia, "Islamic calendar".)
    "hijri": Era("hijri", AstroDate(622, 7, 19), calendar="islamic_civil"),
    # Solar Hijri / Jalali era: year 1 begins at the vernal-equinox Nowruz of
    # 622, 622-03-21 proleptic Gregorian, the Iranian solar calendar's epoch
    # (same Hijra year as the lunar count).  (Wikipedia, "Solar Hijri calendar".)
    "solar_hijri": Era("solar_hijri", AstroDate(622, 3, 21),
                       calendar="solar_hijri_arithmetic"),
    # Era of Nabonassar: the Egyptian 365-day civil calendar counted from the
    # accession of Nabonassar, 26 February 747 BC (Julian) = -746-02-18
    # proleptic Gregorian — the epoch Ptolemy reckons from in the Almagest.
    # (Wikipedia, "Era of Nabonassar".)
    "nabonassar": Era("nabonassar", AstroDate(-746, 2, 18),
                      calendar="egyptian"),

    # ------------------------------------------------------------------
    # Day-count eras (DAYS_SINCE): a running day number, not a year count.
    # ------------------------------------------------------------------
    # Rata Die: fixed-day count with R.D. 1 = 0001-01-01 proleptic Gregorian
    # (Reingold & Dershowitz, "Calendrical Calculations"); day n resolves to
    # JDN 1721425 + n.  Epoch AstroDate is the R.D.-1 date for the record.
    "rata_die": Era("rata_die", AstroDate(1, 1, 1), EraCounting.DAYS_SINCE,
                    day_epoch_jdn=1721425),
    # Lilian date: day count with L.D. 1 = 15 October 1582, the first day of the
    # Gregorian calendar (Bruce G. Ohms, IBM Systems Journal 25(1), 1986); day n
    # resolves to JDN 2299160 + n.
    "lilian": Era("lilian", AstroDate(1582, 10, 15), EraCounting.DAYS_SINCE,
                  day_epoch_jdn=2299160),

    # ------------------------------------------------------------------
    # Year-count offsets (YEARS_SINCE): a constant integer offset from the
    # Common Era.  ONLY eras whose year is Gregorian/tropical-year-aligned are
    # registered here — the offset is then EXACT and the epoch is the era's
    # TRUE civil new-year (month, day), which resolve_era honours.  Lunisolar
    # eras, whose year drifts against the Gregorian year, are deliberately NOT
    # offset eras (a fixed-date offset would be false precision); they are
    # listed in the discard note below and await their own calendars.py backing.
    # ------------------------------------------------------------------
    # Julian Period (Scaliger): a Julian-calendar year count, 1 January new
    # year; year 1 = 4713 BC = astronomical -4712, the year-count companion of
    # the ``julian_day`` day-count above.  (Wikipedia, "Julian day".)
    "julian_period": Era("julian_period", AstroDate(-4712, 1, 1)),
    # Assyrian calendar: modern Assyrian year = CE + 4750, a Gregorian-aligned
    # reckoning whose new year is Kha b-Nisan, fixed at 1 April; year 1 =
    # 1 April 4750 BC = astronomical -4749-04-01.  (Wikipedia, "Assyrian
    # calendar": Kha b-Nisan, 1 April.)
    "assyrian": Era("assyrian", AstroDate(-4749, 4, 1)),
    # Anno Lucis ("Year of Light", Freemasonry): A.L. = CE + 4000, a plain
    # Gregorian-year offset (1 January), year 1 = 4000 BC = astronomical -3999.
    # (Wikipedia, "Anno Lucis".)
    "anno_lucis": Era("anno_lucis", AstroDate(-3999, 1, 1)),
    # Spanish era / Era of Caesar: a Julian-calendar year count (1 January new
    # year) long used in Iberia, Era = CE + 38; year 1 = 38 BC = astronomical
    # -37.  (Wikipedia, "Spanish era".)
    "spanish_era": Era("spanish_era", AstroDate(-37, 1, 1)),
    # Saka era (Indian national calendar): the reformed calendar is a tropical
    # SOLAR calendar, Gregorian-year-aligned, whose new year Chaitra 1 is
    # 22 March (21 March in Gregorian leap years).  Gregorian = Saka + 78 (Saka
    # 1879 = 22 March 1957, the adoption epoch; the current Saka 1946 began 2024),
    # so era year 1 = 79-03-22 in the year-1-based YEARS_SINCE counting.
    # (Wikipedia, "Indian national calendar".)
    "saka": Era("saka", AstroDate(79, 3, 22), leap_shifts_new_year=True),
    # Discordian era: YOLD = CE + 1166, and the Discordian year is aligned to
    # the Gregorian one (five 73-day seasons begin 1 January, St. Tib's Day as
    # the leap day), so year 1 = 1166 BC = astronomical -1165 on 1 January is
    # exact.  (Principia Discordia.)
    "discordian": Era("discordian", AstroDate(-1165, 1, 1)),
    # Positivist era (Auguste Comte): a Gregorian-aligned 13-month calendar
    # beginning 1 January; year 1 = 1789 CE, "the Great Crisis".  (Wikipedia,
    # "Positivist calendar".)
    "positivist": Era("positivist", AstroDate(1789, 1, 1)),
    # Rattanakosin Sok (R.S.): the Thai SOLAR (suriyakati) era counted from the
    # founding of Bangkok, 6 April 1782; the tropical-solar year tracks the
    # Gregorian year, so year 1 = 1782-04-06.  (Wikipedia, "Rattanakosin
    # Kingdom": founding 6 April 1782.)
    "rattanakosin": Era("rattanakosin", AstroDate(1782, 4, 6)),
    # Era Fascista: Gregorian-aligned, its year beginning with the March on
    # Rome, 28 October 1922; year 1 (Anno I) = 1922-10-28.  (Wikipedia, "Era
    # Fascista".)
    "era_fascista": Era("era_fascista", AstroDate(1922, 10, 28)),
    # Republic of China / Minguo era: the Gregorian calendar with a re-based
    # year number (1 January new year), year 1 = 1912 CE (founding of the ROC);
    # the "Chinese Republican" reckoning.  (Wikipedia, "Republic of China
    # calendar".)
    "minguo": Era("minguo", AstroDate(1912, 1, 1)),
    # Juche era (DPRK): the Gregorian calendar re-numbered from Kim Il-sung's
    # birth year, 1 January new year; year 1 = 1912 CE.  (Wikipedia, "Juche
    # calendar".)
    "juche": Era("juche", AstroDate(1912, 1, 1)),
    # After Dianetics (A.D., Scientology): a Gregorian-year offset from the 1950
    # publication of "Dianetics"; year 1 = 1950 CE.  (Wikipedia, "Timeline of
    # Scientology".)
    "after_dianetics": Era("after_dianetics", AstroDate(1950, 1, 1)),
}


#: **Deliberately NOT registered — lunisolar / sidereal eras whose year drifts
#: against the Gregorian year.**  Each would need its own calendar in
#: :mod:`chronologia.calendars` to resolve exactly; a fixed-date integer offset
#: would be false precision (the same defect that keeps the Yazdegerd wandering
#: era out).  Recorded here so the omission is explicit, not forgotten:
#:
#: * ``vikrama`` (Vikram Samvat) — Hindu lunisolar; the year drifts.
#: * ``kali_yuga`` — Hindu lunisolar / traditional; the year drifts.
#: * ``seleucid`` (Anno Graecorum) — classically Babylonian/Hebrew lunisolar;
#:   its epoch (spring 311 BC vs autumn 312 BC) and calendar are ambiguous.
#: * ``bengali_san`` — traditional Bengali lunisolar-derived; drifts.
#: * ``burmese`` — Burmese lunisolar (Thingyan new year drifts).
#: * ``kollam`` (Malayalam) — sidereal-solar; precession drags its new year
#:   against the tropical/Gregorian year (~1 day per ~70 yr).
#: * ``nepal_sambat`` — lunisolar; drifts.
#: * ``yazdegerd`` — Zoroastrian 365-day wandering year (no leap); drifts a full
#:   day every four years.
_DRIFTING_ERAS_NEEDING_CALENDARS = (
    "vikrama", "kali_yuga", "seleucid", "bengali_san", "burmese", "kollam",
    "nepal_sambat", "yazdegerd")


#: Surface-name aliases that resolve to an existing epoch instead of a new
#: registry entry.  "Anno Domini", "after Christ", the "Christian"/"Calendar"
#: era, plain "AD"/"CE", and Thelemic/Masonic "Era Vulgaris" all denote the
#: Common Era — the same year-1 epoch as :data:`ERAS`\ ``["common_era"]``, so
#: they alias it rather than duplicate the entry.
ERA_ALIASES = {
    "anno_domini": "common_era",
    "after_christ": "common_era",
    "christian_era": "common_era",
    "calendar_era": "common_era",
    "ad": "common_era",
    "ce": "common_era",
    "era_vulgaris": "common_era",
}


# --------------------------------------------------------------------------
# The heat death of the universe: the physics-imposed upper bound on a date
# --------------------------------------------------------------------------
#: Astronomical year of the heat death of the universe: ~10^100 years after the
#: Big Bang, set by the evaporation of the most massive supermassive black holes
#: in the Dark Era (Adams & Laughlin 1997, "A dying universe: the long-term fate
#: and evolution of astrophysical objects", Rev. Mod. Phys. 69, 337).  The Big
#: Bang's ~1.4x10^10-year offset from year 0 is utterly negligible at this
#: scale, so the bound is taken as astronomical year 10^100.  AstroDate years
#: are unbounded Python ints, so dates *past* this remain representable — but
#: resolving one trips an :func:`logging.warning` easter egg (see
#: ``_warn_if_past_heat_death``): there are no clocks left to read them.
HEAT_DEATH_YEAR = 10 ** 100

#: Fires the heat-death warning at most once per process (tasteful, not spammy).
_heat_death_warned = False


def _warn_if_past_heat_death(result: Union[date, datetime, "AstroDate"]
                             ) -> Union[date, datetime, "AstroDate"]:
    """Emit the heat-death easter-egg warning when ``result`` is past the bound.

    Only :class:`AstroDate` can carry a year beyond :data:`HEAT_DEATH_YEAR`
    (``datetime`` caps at 9999), so plain dates never trip it.  Passes
    ``result`` straight through — the library still supports these dates.
    """
    global _heat_death_warned
    year = getattr(result, "year", 0)
    if year > HEAT_DEATH_YEAR and not _heat_death_warned:
        _heat_death_warned = True
        _log.warning(
            "resolved a date in astronomical year %s — past the heat death of "
            "the universe (~10^100 yr, Adams & Laughlin 1997, Rev. Mod. Phys. "
            "69, 337). Entropy is maximal, the last black holes have evaporated "
            "into the Dark Era, and no clocks remain to read this date.", year)
    return result


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
    return _CALENDAR_YEAR_START.get(era.calendar or "", (1, 1))


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
        if era not in ERAS:
            raise ValueError(f"unknown era {era!r}; known: {sorted(ERAS)}")
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
    # value is documented as acceptable as a str, so a malformed literal
    # ("abc") or a non-finite float (nan/inf) must be a clean ValueError, not
    # the raw decimal.InvalidOperation (an ArithmeticError) / int() leak.
    try:
        dval = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(f"invalid BP value {value!r}: not a number") from exc
    if not dval.is_finite():
        raise ValueError(f"invalid BP value {value!r}: must be finite")
    mult = _BP_UNITS[unit]
    years_before = dval * mult
    precision_years = Decimal(1).scaleb(int(dval.as_tuple().exponent)) * mult
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
        key = ERA_ALIASES.get(era, era)
        if key not in ERAS:
            raise ValueError(
                f"unknown era {era!r}; known: {sorted(ERAS)}")
        era = ERAS[key]

    if era.calendar is not None:
        # calendar-backed era: resolve EXACTLY to the start of the named
        # calendar year through that calendar's JDN hub (no epoch+count drift)
        cal = _ERA_CALENDARS[era.calendar]
        cyear = _era_native_year(era, value)
        start_month, start_day = _era_year_start(era)
        return _warn_if_past_heat_death(
            julian_day_to_date(cal.to_jdn(cyear, start_month, start_day)))

    if era.counting == EraCounting.SECONDS_SINCE:
        # sub-year precision is meaningful here; epochs are in range
        epoch = datetime(era.epoch.year, era.epoch.month,
                         era.epoch.day, tzinfo=timezone.utc)
        return epoch + timedelta(seconds=value)

    if era.counting == EraCounting.DAYS_SINCE:
        # day-counted eras: ``julian_day`` counts the JDN itself (no shift);
        # Rata Die / Lilian shift by a fixed ``day_epoch_jdn`` so their day 1
        # lands on the cited calendar day.
        jdn = int(value) if era.day_epoch_jdn is None \
            else era.day_epoch_jdn + int(value)
        return _warn_if_past_heat_death(julian_day_to_date(jdn))

    value = int(value)
    if era.counting == EraCounting.YEARS_BEFORE:
        year = era.epoch.year - value
    else:  # YEARS_SINCE: era year 1 is the epoch year
        year = era.epoch.year + value - 1

    # A Gregorian-aligned offset era begins each year at its epoch's civil
    # (month, day) — the true new-year date, not a lazy 1 January.  These eras
    # track the Gregorian/tropical year with a constant integer offset, so the
    # (month, day) is fixed and the result is exact; only genuinely
    # solar/Gregorian-aligned eras are registered as offsets (lunisolar eras,
    # whose year drifts against the Gregorian year, are NOT — they would need
    # their own calendar in calendars.py).
    day = era.epoch.day
    if era.leap_shifts_new_year and is_leap_year(year):
        day -= 1
    result = AstroDate(year, era.epoch.month, day)
    return _warn_if_past_heat_death(result.date() or result)
