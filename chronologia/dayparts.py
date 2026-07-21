"""Day-part registry: named stretches *within* a civil day, resolved to spans.

A :class:`DayPart` binds a human name for a portion of the day ("morning",
"tarde") to a start and end **time-of-day** (a day fraction: 06:00 is a quarter
of the way through the day), tagged with an optional *region* (``None`` == the
global default convention) and a versioned *source*.  Applied to a concrete
civil date by :func:`daypart_span`, it becomes a :class:`DateSpan` — the same
half-open interval type every other reckoning layer produces.

The golden rule this module teaches: **a day-part is a convention, and
conventions differ.**  "Morning" is not a fact about the sun; it is a boundary
a culture draws, and different cultures draw it differently.  English splits the
post-noon day into *afternoon* and *evening*; Spanish runs one *tarde* straight
across both.  So the boundaries are *data*, region-tagged exactly like the named
periods in :mod:`chronologia.periods`, never hard-coded engine logic.

Canonical source
----------------
The boundaries are the **Unicode CLDR Day Period Rules** (TR35 / CLDR 47),
the machine-readable authority for locale-specific day periods — precisely
because it encodes that these boundaries vary by locale.  A copy of the chart
lives in the papers library
(``standards/cldr47_day_period_rules.html``).  Deviation from the design
sketch, recorded as the schema-review rule requires: the sketch put the
afternoon/evening boundary at 17:00; CLDR (and this module, following it) puts
it at 18:00, so the default set is cited exactly rather than rounded.

Default convention (region ``None``), from CLDR locale ``en``:

============ =============== ==================
day-part     interval        note
============ =============== ==================
``morning``  ``[06:00, 12:00)``
``afternoon`` ``[12:00, 18:00)``
``evening``  ``[18:00, 21:00)``
``night``    ``[21:00, 06:00)`` crosses midnight
``noon``     ``[12:00, 12:01)`` minimal-width anchor
``midnight`` ``[00:00, 00:01)`` minimal-width anchor
============ =============== ==================

Region variant (region ``"es"``), from CLDR locale ``es``: ``tarde``
``[12:00, 20:00)`` — one span covering what English calls afternoon *and* early
evening, the demonstration that the mechanism is real.  ``madrugada``
``[00:00, 06:00)`` ships alongside it as the Spanish small-hours name English
has no single word for.

Lookup falls back from a region to the global default: asking for ``morning``
in region ``"es"`` yields the default morning (Spanish overrides ``tarde``, not
``morning``); asking for ``tarde`` with no region raises, since ``tarde`` is
not a global name.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Dict, List, Optional, Tuple, Union

from chronologia.astrodate import AstroDate, DateSpan, civil_add

#: One-minute minimal width for instant anchors (noon, midnight), matching the
#: point convention used elsewhere ("3 pm" == ``[15:00, 15:01)``).
_ANCHOR_WIDTH = timedelta(minutes=1)

#: CLDR release the default and region boundaries are transcribed from.
CLDR_VERSION = "47"

_CLDR_EN = f"Unicode CLDR {CLDR_VERSION} Day Period Rules (locale en)"
_CLDR_ES = f"Unicode CLDR {CLDR_VERSION} Day Period Rules (locale es)"


class UnknownDayPartError(KeyError):
    """No day-part matches the requested ``(name, region)``.

    Raised by :func:`lookup` (and therefore :func:`daypart_span`) when neither
    a region-specific entry nor a global default carries the name.
    """


@dataclass(frozen=True, slots=True)
class DayPart:
    """A named portion of the civil day, bound to a start/end time-of-day.

    :param name: the human-facing name ("morning", "tarde").
    :param start: the day-fraction time the part opens at (inclusive).
    :param end: the day-fraction time the part closes at (exclusive, half-open).
    :param region: region tag (``"es"``) or ``None`` for the global default.
    :param source: the versioned authority the boundaries came from.
    :param crosses_midnight: ``True`` when the part wraps past 24:00 into the
        next civil day (``end <= start``), e.g. ``night`` ``[21:00, 06:00)``.

    ``start``/``end`` are *times of day*, not instants: a :class:`DayPart` is a
    convention with no date until :func:`daypart_span` anchors it to one.  The
    ``crosses_midnight`` flag is validated against the endpoints so it can never
    silently disagree with them.
    """
    name: str
    start: time
    end: time
    region: Optional[str]
    source: str
    crosses_midnight: bool

    def __post_init__(self):
        if not isinstance(self.start, time) or not isinstance(self.end, time):
            raise TypeError("DayPart start/end must be datetime.time")
        wraps = self.end <= self.start
        if wraps != self.crosses_midnight:
            raise ValueError(
                f"crosses_midnight={self.crosses_midnight} disagrees with "
                f"endpoints {self.start}..{self.end}; a part wraps iff "
                f"end <= start")

    @property
    def key(self) -> str:
        """Registry key: the bare name (global) or ``name_region``."""
        return self.name if self.region is None \
            else f"{self.name}_{self.region.lower()}"


def _p(name: str, start: Tuple[int, int], end: Tuple[int, int],
       region: Optional[str], source: str) -> DayPart:
    s = time(*start)
    e = time(*end)
    return DayPart(name, s, e, region, source, crosses_midnight=e <= s)


def _anchor(name: str, hm: Tuple[int, int], region: Optional[str],
            source: str) -> DayPart:
    s = time(*hm)
    e = (datetime(2000, 1, 1, *hm) + _ANCHOR_WIDTH).time()
    return DayPart(name, s, e, region, source, crosses_midnight=False)


_DEFAULTS: List[DayPart] = [
    _p("morning", (6, 0), (12, 0), None, _CLDR_EN),
    _p("afternoon", (12, 0), (18, 0), None, _CLDR_EN),
    _p("evening", (18, 0), (21, 0), None, _CLDR_EN),
    _p("night", (21, 0), (6, 0), None, _CLDR_EN),          # crosses midnight
    _anchor("noon", (12, 0), None, _CLDR_EN),
    _anchor("midnight", (0, 0), None, _CLDR_EN),
]

_REGIONAL: List[DayPart] = [
    # es: one "tarde" covers English afternoon + early evening — the proof the
    # boundaries are conventional and region-specific, not universal.
    _p("tarde", (12, 0), (20, 0), "es", _CLDR_ES),
    _p("madrugada", (0, 0), (6, 0), "es", _CLDR_ES),        # crosses midnight
]

#: The day-part registry, keyed by :attr:`DayPart.key`.
DAY_PARTS: Dict[str, DayPart] = {p.key: p for p in _DEFAULTS + _REGIONAL}


def lookup(name: str, region: Optional[str] = None) -> DayPart:
    """Resolve a day-part by ``name``, preferring a ``region`` override.

    A region-specific entry (``tarde`` in ``es``) wins; otherwise the global
    default carries the name (``morning`` has no ``es`` override, so ``es``
    falls back to it).  Raises :class:`UnknownDayPartError` when neither exists.
    """
    if region is not None:
        regional = DAY_PARTS.get(f"{name}_{region.lower()}")
        if regional is not None:
            return regional
    default = DAY_PARTS.get(name)
    if default is not None:
        return default
    raise UnknownDayPartError(
        f"no day-part {name!r} for region {region!r}; known: "
        f"{sorted(DAY_PARTS)}")


def _civil_ymd(date_or_span: Union[AstroDate, date, datetime, DateSpan]
               ) -> Tuple[int, int, int]:
    if isinstance(date_or_span, DateSpan):
        anchor = date_or_span.start
    else:
        anchor = date_or_span
    return anchor.year, anchor.month, anchor.day


def _span_on_date(part: DayPart, y: int, m: int, d: int) -> DateSpan:
    start = AstroDate(y, m, d, part.start.hour, part.start.minute,
                      part.start.second, part.start.microsecond)
    if part.crosses_midnight:
        nxt = civil_add(AstroDate(y, m, d), days=1)
        y2, m2, d2 = nxt.year, nxt.month, nxt.day
    else:
        y2, m2, d2 = y, m, d
    end = AstroDate(y2, m2, d2, part.end.hour, part.end.minute,
                    part.end.second, part.end.microsecond)
    return DateSpan(start, end)


def daypart_span(date_or_span: Union[AstroDate, date, datetime, DateSpan],
                 name: str, region: Optional[str] = None) -> DateSpan:
    """The span a day-part occupies on a concrete date.

    ``date_or_span`` supplies the civil date to anchor to — an
    :class:`AstroDate`/``date``/``datetime`` names the day directly; a
    :class:`DateSpan` contributes the civil date of its ``start``.

    A midnight-crosser anchors to the *named* date and reaches into the next
    civil day: ``daypart_span(tuesday, "night")`` is Tue 21:00 → **Wed** 06:00
    (the documented convention — "tuesday night" belongs to Tuesday even though
    it ends on Wednesday).

    When ``date_or_span`` is itself a :class:`DateSpan`, the result is
    *composed* with it via :meth:`DateSpan.intersect` — ``daypart_span(some_day,
    "morning")`` returns morning clipped to that day-span, so applying a
    day-part to "tuesday" and to a truncated slice of Tuesday differ exactly by
    the overlap.  A day-part disjoint from the given span raises
    :class:`ValueError`, since there is no interval to return.
    """
    part = lookup(name, region)
    y, m, d = _civil_ymd(date_or_span)
    span = _span_on_date(part, y, m, d)
    if isinstance(date_or_span, DateSpan):
        composed = span.intersect(date_or_span)
        if composed is None:
            raise ValueError(
                f"day-part {name!r} on {y:04d}-{m:02d}-{d:02d} does not "
                f"intersect the given span {date_or_span}")
        return composed
    return span
