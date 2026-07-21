"""Timelines: a jurisdiction's history of civil label-mappings.

The astronomical timeline (JDN / :class:`~chronologia.astrodate.AstroDate`)
never has discontinuities — it is a pure count of days.  Only *civil*
label-mappings jump: a pope, parliament, tsar or emperor decrees that
"tomorrow" shall be called something the calendar in force would never have
generated.  Calendars stay pure proleptic bijections; a **Timeline** records,
for one jurisdiction, which calendar was in force over each stretch of JDN and
what its one-time reforms did to the labels.

Model
-----
* :class:`TimelineSegment` — an ordered ``(start_jdn, calendar_key)`` stretch,
  optionally carrying a civil ``year_start`` (the ``(month, day)`` on which the
  civil year number turns over) and a constant ``year_offset``.
* :class:`Discontinuity` — a one-time event at a JDN, one of four
  :class:`DiscontinuityKind`:

  - **SKIP** — labels that never existed (Rome: 5–14 October 1582; Britain:
    3–13 September 1752).  The two calendars straddling the seam both place the
    queried label across it, so no JDN ever bore it.
  - **REPEAT** — one label, two JDNs (Alaska 1867): :meth:`Timeline.to_jdn`
    yields the two-candidate tuple (the existing two-JDN indeterminacy).
  - **INSERT** — a label no calendar in force generates (Sweden, 30 February
    1712), supplied as a timeline-level label override on a single JDN.
  - **RELABEL** — a year-start / numbering change (England, 25 March → 1
    January in 1752, with dual dating "1731/32"), expressed per segment through
    the ``year_start`` machinery that the era layer already uses.

Properties (design, issue #1 "Timelines & discontinuities"): duration math is
unaffected because it always happens in JDN space; a non-existent label returns
a typed :class:`NeverExisted` ("never existed + why", carrying the
discontinuity) rather than raising; conversions default to the **proleptic**
timeline (:func:`proleptic`, zero discontinuities = zero behaviour change).
The boundary rule: predictable from the calendar's own law → it belongs to the
calendar; it took a pope / parliament / tsar / emperor → it belongs to a
timeline.  Timezone shifts (Samoa 2011) are *not* discontinuities.

Sources (downloaded under ``~/AgentWorkspaces/papers/calendars/``):

* ``gregorian_adoption_reference.html`` — Wikipedia, "Adoption of the Gregorian
  calendar": "the day after Thursday, 4 October 1582 was dated as Friday, 15
  October 1582"; the Catholic states of the Holy Roman Empire, the Italian
  principalities, Poland–Lithuania, and Spain–Portugal were first to adopt.
* ``old_new_style_dates_reference.html`` — Wikipedia, "Old Style and New Style
  dates": England's civil year began on 25 March (Lady Day) until 1751; dual
  dating "1731/32" for dates between 1 January and 24 March under the two
  reckonings.
* ``calendar_new_style_act_1750_reference.html`` — Wikipedia, "Calendar (New
  Style) Act 1750": 1 January 1752 fixed as new-year's day (1751 ran 25 March
  – 31 December), and Wednesday 2 September 1752 followed by Thursday 14
  September 1752 (eleven days omitted).
* ``swedish_calendar_reference.html`` — Wikipedia, "Swedish calendar": in use 1
  March 1700 – 30 February 1712, "one day ahead of the Julian calendar and ten
  days behind the Gregorian"; Sweden reverted to the Julian calendar in 1712
  (via the double leap day 30 February 1712) and adopted the Gregorian in 1753.
* ``japanese_calendar_reference.html`` — Wikipedia, "Japanese calendar":
  Gregorian introduced in 1873; the Tenpō lunisolar calendar was the reference
  calendar 1844–1872, before the switch at Meiji 6 = 1 January 1873.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, Tuple, Union

from chronologia.calendars import (CALENDARS, Calendar, gregorian_to_jdn,
                                    jdn_to_gregorian, julian_to_jdn)

# Lower bound standing in for "the beginning of the timeline" — a plain int so
# it orders against real JDNs; never itself a valid civil day.
_MIN_JDN = -(10 ** 15)

# The proleptic Gregorian calendar as a JDN-hub Calendar, so a segment may name
# "gregorian" without touching the arithmetic-only registry in calendars.py
# (which owns its own set and deliberately omits Gregorian).
_GREGORIAN = Calendar("gregorian", 12, gregorian_to_jdn, jdn_to_gregorian,
                      gregorian_to_jdn(1, 1, 1))
_TL_CALENDARS: Dict[str, Calendar] = {**CALENDARS, "gregorian": _GREGORIAN}


class DiscontinuityKind(Enum):
    """The four ways a civil label-mapping can jump (see module docstring)."""
    SKIP = "skip"        # labels that never existed
    REPEAT = "repeat"    # one label, two JDNs
    INSERT = "insert"    # a label no calendar in force generates
    RELABEL = "relabel"  # year-start / numbering change


@dataclass(frozen=True)
class CivilLabel:
    """A civil date label ``(year, month, day)`` under the calendar in force.

    The ``year`` is the number a person of the jurisdiction would have written,
    honouring its year-start convention — not necessarily the astronomical year
    of the underlying calendar (England's "24 February 1731" is astronomical
    Julian 1732; the dual date "1731/32" carries both).
    """
    year: int
    month: int
    day: int

    def as_tuple(self) -> Tuple[int, int, int]:
        return (self.year, self.month, self.day)


def _label(x: Union[CivilLabel, Tuple[int, int, int]]) -> CivilLabel:
    """Coerce a ``(y, m, d)`` tuple or :class:`CivilLabel` to a CivilLabel."""
    if isinstance(x, CivilLabel):
        return x
    return CivilLabel(*x)


@dataclass(frozen=True)
class Discontinuity:
    """A one-time civil-label event at :attr:`jdn` (see :class:`DiscontinuityKind`).

    ``before_label`` is the last label the outgoing reckoning produced;
    ``after_label`` is the first label of the incoming one.  For **INSERT**,
    ``after_label`` is the overriding label the timeline stamps on :attr:`jdn`
    itself.  ``citation`` names the decree / source that caused the jump.
    """
    jdn: int
    kind: DiscontinuityKind
    before_label: CivilLabel
    after_label: CivilLabel
    citation: str

    def __post_init__(self):
        object.__setattr__(self, "before_label", _label(self.before_label))
        object.__setattr__(self, "after_label", _label(self.after_label))


@dataclass(frozen=True)
class NeverExisted:
    """Typed result: a label that no JDN ever bore, and why.

    Returned by :meth:`Timeline.to_jdn` for a label that falls inside a
    :attr:`DiscontinuityKind.SKIP` window — a real answer ("this label never
    existed"), never an error.  Carries the :class:`Discontinuity` responsible.
    """
    label: CivilLabel
    discontinuity: Discontinuity


class UnknownCalendar(KeyError):
    """The calendar in force at a JDN is not in the registry (e.g. Japan's
    pre-1873 lunisolar segment) — its labels cannot be generated."""


class OutOfTimeline(KeyError):
    """A queried label maps to no segment of this timeline and to no
    discontinuity (it is simply outside the modelled span)."""


@dataclass(frozen=True)
class TimelineSegment:
    """A stretch of a timeline: from :attr:`start_jdn` (inclusive) until the
    next segment's start, the calendar :attr:`calendar_key` was in force.

    ``year_start`` is the ``(month, day)`` on which the civil year number turns
    over (``(1, 1)`` for the modern convention; ``(3, 25)`` for pre-1752
    England); labels before it in the calendar year carry the previous year's
    number.  ``year_offset`` is a constant added to the civil year number.
    """
    start_jdn: int
    calendar_key: str
    year_start: Tuple[int, int] = (1, 1)
    year_offset: int = 0


@dataclass(frozen=True)
class Timeline:
    """A jurisdiction's ordered segments and one-time discontinuities.

    The sixth registry beside Calendar / Era / RegnalSequence / DayCycle /
    DaySubdivision.  Duration math is unaffected (always JDN space); only the
    civil ``from_jdn`` / ``to_jdn`` label-mappings feel the discontinuities.
    """
    key: str
    segments: Tuple[TimelineSegment, ...]
    discontinuities: Tuple[Discontinuity, ...] = ()
    _insert_jdns: frozenset = field(default=frozenset(), init=False, repr=False,
                                    compare=False)

    def __post_init__(self):
        segs = tuple(sorted(self.segments, key=lambda s: s.start_jdn))
        object.__setattr__(self, "segments", segs)
        object.__setattr__(self, "discontinuities", tuple(self.discontinuities))
        object.__setattr__(self, "_insert_jdns", frozenset(
            d.jdn for d in self.discontinuities
            if d.kind is DiscontinuityKind.INSERT))

    # -- segment lookup ----------------------------------------------------

    def _segment_at(self, jdn: int) -> TimelineSegment:
        """The segment in force at ``jdn`` (last one whose start <= jdn)."""
        found = None
        for seg in self.segments:
            if seg.start_jdn <= jdn:
                found = seg
            else:
                break
        if found is None:
            raise OutOfTimeline(f"{jdn} precedes timeline {self.key!r}")
        return found

    def _seg_end(self, seg: TimelineSegment) -> int:
        """Exclusive upper JDN bound of ``seg`` (next segment's start)."""
        after = [s.start_jdn for s in self.segments if s.start_jdn > seg.start_jdn]
        return min(after) if after else _MIN_JDN + 2 * 10 ** 15  # +inf-ish

    def calendar_at(self, jdn: int) -> str:
        """The ``calendar_key`` in force at ``jdn``."""
        return self._segment_at(jdn).calendar_key

    # -- label <-> jdn helpers --------------------------------------------

    @staticmethod
    def _civil_from_native(seg: TimelineSegment, y: int, m: int, d: int
                           ) -> CivilLabel:
        civil_year = y + seg.year_offset
        if (m, d) < seg.year_start:
            civil_year -= 1
        return CivilLabel(civil_year, m, d)

    @staticmethod
    def _native_year(seg: TimelineSegment, label: CivilLabel) -> int:
        native = label.year - seg.year_offset
        if (label.month, label.day) < seg.year_start:
            native += 1
        return native

    def _label_to_jdn_via(self, seg: TimelineSegment, label: CivilLabel) -> int:
        cal = _TL_CALENDARS[seg.calendar_key]
        return cal.to_jdn(self._native_year(seg, label),
                          label.month, label.day)

    # -- public conversions ------------------------------------------------

    def from_jdn(self, jdn: int) -> CivilLabel:
        """Civil label of ``jdn`` under the calendar in force.

        Honours INSERT overrides (the label no calendar generates) and the
        segment's RELABEL year-start rule.  Raises :class:`UnknownCalendar`
        when the segment's calendar is out of the registry.
        """
        for d in self.discontinuities:
            if d.kind is DiscontinuityKind.INSERT and d.jdn == jdn:
                return d.after_label
        seg = self._segment_at(jdn)
        if seg.calendar_key not in _TL_CALENDARS:
            raise UnknownCalendar(
                f"calendar {seg.calendar_key!r} (in force at {jdn} on "
                f"timeline {self.key!r}) is not in the registry")
        cal = _TL_CALENDARS[seg.calendar_key]
        y, m, d = cal.from_jdn(jdn)
        return self._civil_from_native(seg, y, m, d)

    def to_jdn(self, label: Union[CivilLabel, Tuple[int, int, int]]
               ) -> Union[int, Tuple[int, int], NeverExisted]:
        """JDN(s) a civil label maps to, or a typed :class:`NeverExisted`.

        Returns an ``int`` for the ordinary one-to-one case, a two-tuple for a
        REPEAT (one label, two JDNs), or :class:`NeverExisted` when the label
        falls inside a SKIP window.  Raises :class:`OutOfTimeline` when the
        label belongs to no segment and no discontinuity.
        """
        label = _label(label)

        for d in self.discontinuities:
            if d.kind is DiscontinuityKind.INSERT and d.after_label == label:
                return d.jdn

        answers = []
        for seg in self.segments:
            if seg.calendar_key not in _TL_CALENDARS:
                continue
            try:
                jdn = self._label_to_jdn_via(seg, label)
            except (ValueError, KeyError):
                continue
            if jdn in self._insert_jdns:
                continue  # that JDN is claimed by an INSERT override
            lo, hi = seg.start_jdn, self._seg_end(seg)
            if lo <= jdn < hi and jdn not in answers:
                answers.append(jdn)

        if len(answers) == 1:
            return answers[0]
        if len(answers) >= 2:
            return tuple(sorted(answers))

        # No segment bore this label — is it inside a SKIP window?
        for d in self.discontinuities:
            if d.kind is not DiscontinuityKind.SKIP:
                continue
            try:
                seg_b = self._segment_at(d.jdn - 1)
                seg_a = self._segment_at(d.jdn)
                jb = self._label_to_jdn_via(seg_b, label)
                ja = self._label_to_jdn_via(seg_a, label)
            except (ValueError, KeyError, OutOfTimeline):
                continue
            if jb >= d.jdn and ja < d.jdn:
                return NeverExisted(label, d)

        raise OutOfTimeline(
            f"label {label.as_tuple()} maps to no segment of "
            f"timeline {self.key!r}")


# --------------------------------------------------------------------------
# Data instances (citations above; gold values in test/test_timelines.py).
# --------------------------------------------------------------------------

def proleptic(calendar_key: str) -> Timeline:
    """A zero-discontinuity timeline over one calendar — the default behaviour.

    ``proleptic("julian").from_jdn(j)`` is exactly the raw calendar's label for
    ``j``; there are no reforms, so conversions match the bare calendar.
    """
    return Timeline(f"proleptic:{calendar_key}",
                    (TimelineSegment(_MIN_JDN, calendar_key),))


# -- rome_1582 and the initial Catholic-adopter group (es/pt/it/pl) --------
# gregorian_adoption_reference.html: "the day after Thursday, 4 October 1582
# was dated as Friday, 15 October 1582"; Spain–Portugal, the Italian
# principalities and Poland–Lithuania switched with the Papal States.
_ROME_SEAM = gregorian_to_jdn(1582, 10, 15)  # == julian_to_jdn(1582,10,4) + 1
rome_1582 = Timeline(
    "rome_1582",
    (TimelineSegment(_MIN_JDN, "julian"),
     TimelineSegment(_ROME_SEAM, "gregorian")),
    (Discontinuity(_ROME_SEAM, DiscontinuityKind.SKIP,
                   (1582, 10, 4), (1582, 10, 15),
                   "Inter gravissimas (1582); gregorian_adoption_reference.html"),))


# -- britain_1752: SKIP + RELABEL year-start (25 March -> 1 January) --------
# calendar_new_style_act_1750_reference.html: 1 January 1752 fixed as new
# year's day (1751 ran 25 March – 31 December); Wednesday 2 September 1752 was
# followed by Thursday 14 September 1752.
_BRIT_YEARSTART = julian_to_jdn(1752, 1, 1)   # civil year turns over here now
_BRIT_SEAM = gregorian_to_jdn(1752, 9, 14)    # == julian_to_jdn(1752,9,2) + 1
britain_1752 = Timeline(
    "britain_1752",
    (TimelineSegment(_MIN_JDN, "julian", year_start=(3, 25)),
     TimelineSegment(_BRIT_YEARSTART, "julian", year_start=(1, 1)),
     TimelineSegment(_BRIT_SEAM, "gregorian", year_start=(1, 1))),
    (Discontinuity(_BRIT_YEARSTART, DiscontinuityKind.RELABEL,
                   (1751, 12, 31), (1752, 1, 1),
                   "Calendar (New Style) Act 1750; "
                   "calendar_new_style_act_1750_reference.html"),
     Discontinuity(_BRIT_SEAM, DiscontinuityKind.SKIP,
                   (1752, 9, 2), (1752, 9, 14),
                   "Calendar (New Style) Act 1750; "
                   "calendar_new_style_act_1750_reference.html")))


# -- russia_1918: SKIP 1–13 February 1918 (Julian -> Gregorian) ------------
# Decree of the Council of People's Commissars, 24 Jan 1918 (Julian): the day
# after 31 January 1918 was to be 14 February 1918. gregorian_adoption_reference.html.
_RUSSIA_SEAM = gregorian_to_jdn(1918, 2, 14)  # == julian_to_jdn(1918,1,31) + 1
russia_1918 = Timeline(
    "russia_1918",
    (TimelineSegment(_MIN_JDN, "julian"),
     TimelineSegment(_RUSSIA_SEAM, "gregorian")),
    (Discontinuity(_RUSSIA_SEAM, DiscontinuityKind.SKIP,
                   (1918, 1, 31), (1918, 2, 14),
                   "Sovnarkom decree, 24 Jan 1918; "
                   "gregorian_adoption_reference.html"),))


# -- greece_1923: SKIP 16–28 February 1923 (Julian -> Gregorian) -----------
# gregorian_adoption_reference.html: Greece's civil switch, the day after 15
# February 1923 (Julian) was 1 March 1923 (Gregorian).
_GREECE_SEAM = gregorian_to_jdn(1923, 3, 1)  # == julian_to_jdn(1923,2,15) + 1
greece_1923 = Timeline(
    "greece_1923",
    (TimelineSegment(_MIN_JDN, "julian"),
     TimelineSegment(_GREECE_SEAM, "gregorian")),
    (Discontinuity(_GREECE_SEAM, DiscontinuityKind.SKIP,
                   (1923, 2, 15), (1923, 3, 1),
                   "Greek civil adoption, 1923; "
                   "gregorian_adoption_reference.html"),))


# -- sweden_1700_1712: the gradual mess, modelled to what the source pins ---
# swedish_calendar_reference.html: the Swedish calendar was in use 1 March 1700
# – 30 February 1712, "one day ahead of the Julian calendar and ten days behind
# the Gregorian"; Sweden reverted to the Julian calendar in 1712 via the double
# leap day 30 February 1712, and adopted the Gregorian in 1753.
#
# SIMPLIFICATION (documented): the branch registry has no Swedish calendar
# (Julian-minus-one-day, 1700–1712), so the 1700–1712 one-day divergence is NOT
# modelled as its own segment.  The timeline models the two label-affecting
# events the source pins exactly: the INSERT of 30 February 1712 (= the day the
# Julian calendar calls 29 February 1712 = Gregorian 11 March 1712, "ten days
# behind the Gregorian"), and the 1753 Gregorian adoption.  Consequences:
#   * the underlying calendar is Julian throughout 1700–1753 (what Sweden used
#     after the 1712 reversion; a close proxy before 1700);
#   * the actual day at the INSERT JDN carries only the "30 February 1712"
#     label — the Julian "29 February 1712" label it would otherwise bear is
#     shadowed by the override (Sweden really had both that year; the extra
#     day is what is preserved here as the notable civil label).
_SWED_INSERT = gregorian_to_jdn(1712, 3, 11)  # Julian 29 Feb 1712 -> "Feb 30"
# 1753: the day after 17 February 1753 (Julian) was 1 March 1753 (Gregorian).
_SWED_SEAM = gregorian_to_jdn(1753, 3, 1)     # == julian_to_jdn(1753,2,17) + 1
sweden_1700_1712 = Timeline(
    "sweden_1700_1712",
    (TimelineSegment(_MIN_JDN, "julian"),
     TimelineSegment(_SWED_SEAM, "gregorian")),
    (Discontinuity(_SWED_INSERT, DiscontinuityKind.INSERT,
                   (1712, 2, 28), (1712, 2, 30),
                   "double leap day 30 Feb 1712; "
                   "swedish_calendar_reference.html"),
     Discontinuity(_SWED_SEAM, DiscontinuityKind.SKIP,
                   (1753, 2, 17), (1753, 3, 1),
                   "Swedish Gregorian adoption 1753; "
                   "swedish_calendar_reference.html")))


# -- japan_1873: lunisolar -> Gregorian at Meiji 6 = 1 January 1873 ---------
# japanese_calendar_reference.html: the Gregorian calendar was introduced in
# 1873; the Tenpō lunisolar calendar (1844–1872) was the reference calendar
# before the switch.  Meiji 5, 12th month, day 2 (lunisolar) was the last day,
# directly followed by Meiji 6 = 1 January 1873 (Gregorian).
#
# The pre-1873 segment's calendar ("japanese_lunisolar") is NOT in the branch's
# CALENDARS registry, so its labels cannot be generated: from_jdn on a pre-1873
# JDN raises UnknownCalendar, and a pre-1873 label raises OutOfTimeline.  Only
# the switch discontinuity and the post-1873 Gregorian segment are fully
# functional.  (Wire the lunisolar segment once a Tenpō calendar lands.)
_JAPAN_SEAM = gregorian_to_jdn(1873, 1, 1)
japan_1873 = Timeline(
    "japan_1873",
    (TimelineSegment(_MIN_JDN, "japanese_lunisolar"),
     TimelineSegment(_JAPAN_SEAM, "gregorian")),
    (Discontinuity(_JAPAN_SEAM, DiscontinuityKind.RELABEL,
                   (1872, 12, 2), (1873, 1, 1),
                   "Meiji Council of State decree 337 (1872); "
                   "japanese_calendar_reference.html"),))


#: The timeline registry.  The initial Catholic-adopter group (Spain, Portugal,
#: the Italian principalities, Poland–Lithuania) switched on the same 1582 seam
#: as Rome, so they alias the ``rome_1582`` timeline.
TIMELINES: Dict[str, Timeline] = {
    "rome_1582": rome_1582,
    "spain_1582": rome_1582,
    "portugal_1582": rome_1582,
    "italy_1582": rome_1582,
    "poland_1582": rome_1582,
    "britain_1752": britain_1752,
    "russia_1918": russia_1918,
    "greece_1923": greece_1923,
    "sweden_1700_1712": sweden_1700_1712,
    "japan_1873": japan_1873,
}
