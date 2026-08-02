"""Weekend / in-lieu shift policies layered on top of any rule kind.

An :class:`ObservedShift` modifier is layered on top of any kind: a weekend
falling on a listed weekday shifts by a signed delta (the U.S. federal rule is
Saturday → preceding Friday, Sunday → following Monday) — it *relocates* the day.

A :class:`SubstitutePolicy` is the complementary mechanism: instead of moving the
nominal day it *adds* a separate substitute holiday when the nominal falls on a
listed weekday, keeping the nominal day too. This is the UK "in-lieu" convention
(gov.uk: a bank holiday on a weekend grants a substitute weekday — normally the
following Monday — and the Christmas/Boxing pair can cascade two substitutes when
25/26 December fall on a weekend) and Japan's 振替休日 furikae (a holiday on a
Sunday makes the following non-holiday weekday a holiday). Because the substitute
must land on the next day that is not *already* a holiday, the policy is resolved
at the
:class:`~chronologia.civil_holidays.loader.HolidayCalendar` level (it needs the
year's whole holiday set), not inside a single rule.

A :class:`RelocateShift` is the third variant: it *relocates* the nominal day
onto its observed weekday like :class:`ObservedShift`, but — like
:class:`SubstitutePolicy` — it cascades calendar-wide so two holidays relocating
into the same slot do not collide. A stock exchange does not trade on weekends,
so it lists only the observed weekday closure (never the weekend nominal); when
both Christmas Day and Boxing Day fall on a weekend the second one skips the day
the first already claimed (TSX 2021: Sat 25 / Sun 26 Dec → Mon 27 + Tue 28, not
both on Mon 27). It therefore relocates (no nominal kept, unlike the additive
substitute) *and* needs the year's whole holiday set (unlike the per-rule
:class:`ObservedShift`), so it too is resolved at the
:class:`~chronologia.civil_holidays.loader.HolidayCalendar` level.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Dict, FrozenSet, Optional, Tuple, Union

from chronologia.astrodate import AstroDate


# --------------------------------------------------------------------------
# Observed-shift modifier (weekend / in-lieu policies).
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class ObservedShift:
    """A parameterized weekend-shift policy.

    ``shifts`` is a tuple of ``(weekday, delta_days)``: a holiday landing on
    ``weekday`` (Monday==0 .. Sunday==6) is *observed* ``delta_days`` away. The
    first matching entry wins. The U.S. federal rule is Saturday → −1 (Friday),
    Sunday → +1 (Monday); many "next Monday" jurisdictions use just Sunday → +1.
    """

    shifts: Tuple[Tuple[int, int], ...]

    def apply(self, date: AstroDate) -> AstroDate:
        wd = date.weekday()
        for weekday, delta in self.shifts:
            if wd == weekday:
                return date + timedelta(days=delta)
        return date


#: U.S. federal rule (5 U.S.C. 6103): Saturday observed the preceding Friday,
#: Sunday observed the following Monday.
US_OBSERVED_SHIFT = ObservedShift(((5, -1), (6, 1)))
#: "If it falls on a Sunday, observe the next Monday."
SUNDAY_TO_MONDAY = ObservedShift(((6, 1),))
#: Australian "weekend → next Monday" rule (Australia Day and, in most
#: states, Christmas/Boxing/ANZAC): Saturday → +2, Sunday → +1.
SATURDAY_SUNDAY_TO_MONDAY = ObservedShift(((5, 2), (6, 1)))
#: Israel's Yom Ha'atzmaut (Independence Day) postponement, keyed to the
#: weekday of the nominal Iyar 5. Under the 2004 amendment 5 Iyar can only be
#: Monday, Wednesday, Friday or Saturday: Monday → +1 (Tuesday, to keep the
#: preceding Yom HaZikaron off Sunday), Friday → −1 and Saturday → −2 (both to
#: Thursday, away from Shabbat); Wednesday is unshifted.
IL_INDEPENDENCE_SHIFT = ObservedShift(((0, 1), (4, -1), (5, -2)))
#: Netherlands Koningsdag (King's Day): celebrated 27 April, but when the 27th
#: is a Sunday it is brought forward to Saturday 26 April (never postponed).
NL_KINGSDAY_SHIFT = ObservedShift(((6, -1),))


# --------------------------------------------------------------------------
# Shared calendar-wide cascade: roll forward past taken days (and, optionally,
# weekends) to the next free day. Used by both the additive substitute and the
# relocating shift — the same "next available business day" walk, differing only
# in whether the nominal day is kept (substitute) or moved (relocate).
# --------------------------------------------------------------------------
def _cascade_forward(nominal: AstroDate, taken: FrozenSet[AstroDate],
                     skip_weekends: bool) -> AstroDate:
    """The first day after ``nominal`` not in ``taken`` (and not a weekend when
    ``skip_weekends``). Rolls one day at a time so a colliding pair cascades to
    distinct days."""
    cand = nominal + timedelta(days=1)
    while cand in taken or (skip_weekends and cand.weekday() >= 5):
        cand = cand + timedelta(days=1)
    return cand


# --------------------------------------------------------------------------
# Substitute-day (in-lieu) policy — ADDS a day, resolved calendar-wide.
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class SubstitutePolicy:
    """An in-lieu substitute-day policy: *adds* a holiday, never relocates.

    When a holiday's nominal date lands on one of ``trigger_weekdays`` (Monday==0
    .. Sunday==6), a separate substitute holiday is granted on the next day that
    is not *already* a holiday — and, when ``skip_weekends`` is set, not a
    Saturday or Sunday either. The nominal day stays a holiday in its own right;
    the substitute is emitted alongside it with ``label`` appended to the name.

    Unlike :class:`ObservedShift`, which each rule can apply on its own, a
    substitute must know the year's *whole* holiday set to skip days already
    taken (so the UK Christmas/Boxing pair cascades to two distinct Mondays/
    Tuesdays rather than colliding). It is therefore applied by
    :meth:`~chronologia.civil_holidays.loader.HolidayCalendar.holidays`, not by
    the rule in isolation.

    * UK bank holidays (:data:`GB_SUBSTITUTE`): a weekend bank holiday
      (Saturday or Sunday) → the next free weekday, gov.uk's "substitute day".
    * Japan 振替休日 (:data:`JP_FURIKAE`): a Sunday holiday → the following
      non-holiday day (Saturdays are eligible substitutes, so weekends are not
      skipped).
    """

    trigger_weekdays: Tuple[int, ...]
    skip_weekends: bool = True
    label: str = " (substitute)"

    def __post_init__(self) -> None:
        for wd in self.trigger_weekdays:
            if not 0 <= wd <= 6:
                raise ValueError(f"weekday out of range: {wd}")

    def substitute_for(self, nominal: AstroDate,
                       taken: FrozenSet[AstroDate]) -> Optional[AstroDate]:
        """The substitute day for ``nominal`` given already-``taken`` holidays.

        Returns ``None`` when ``nominal``'s weekday is not a trigger. Otherwise
        rolls forward one day at a time past any day already in ``taken`` (and,
        if ``skip_weekends``, past Saturdays and Sundays) and returns the first
        free day.
        """
        if nominal.weekday() not in self.trigger_weekdays:
            return None
        return _cascade_forward(nominal, taken, self.skip_weekends)


#: UK gov.uk substitute-day rule: a bank holiday on Saturday or Sunday grants a
#: substitute on the next weekday that is not already a bank holiday.
GB_SUBSTITUTE = SubstitutePolicy((5, 6), skip_weekends=True,
                                 label=" (substitute day)")
#: Japan 振替休日: a national holiday on a Sunday makes the following non-holiday
#: day a holiday (weekends are not skipped — a Saturday can be the substitute).
JP_FURIKAE = SubstitutePolicy((6,), skip_weekends=False, label=" (振替休日)")
#: Australian in-lieu rule: New Year, Christmas and Boxing Day landing on a
#: Saturday or Sunday keep their nominal date and grant an *additional* holiday
#: on the next free weekday — the reference lib labels it " (observed)". Like the
#: UK rule the Christmas/Boxing pair cascades (25/26 Dec on a weekend give two
#: distinct substitutes), which is why it must ADD rather than relocate: the old
#: relocating ``sat_sun_mon`` shift collided the pair onto one Monday and dropped
#: both nominal dates.
AU_SUBSTITUTE = SubstitutePolicy((5, 6), skip_weekends=True, label=" (observed)")


# --------------------------------------------------------------------------
# Relocating cascade policy — MOVES the day, resolved calendar-wide.
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class RelocateShift:
    """A relocating weekend policy that cascades calendar-wide.

    Like :class:`ObservedShift` it *moves* a holiday off a non-business day onto
    the next business day, and the nominal day is *not* kept (unlike
    :class:`SubstitutePolicy`, which adds a day). Like :class:`SubstitutePolicy`
    it needs the year's whole holiday set: each holiday lands on the next day that
    is neither a weekend (when ``skip_weekends``) nor already ``taken`` by another
    holiday's observed day — the "next available business day" walk.

    This is the stock-exchange convention: the exchange does not trade on
    weekends, so it publishes only the observed weekday closure — never the
    weekend nominal. Crucially the cascade fires not only when a holiday's *own*
    nominal is a weekend, but also when its nominal weekday has been claimed by an
    earlier holiday that relocated onto it. When Christmas Day *and* Boxing Day
    both fall on a weekend the second cascades one further business day (TSX 2021:
    Sat 25 / Sun 26 Dec → Mon 27 + Tue 28); and when Christmas relocates onto
    Boxing's own weekday, Boxing bumps forward too (TSX 2022: Sun 25 Dec Christmas
    → Mon 26, so Mon 26 Boxing → Tue 27). Because the walk must know the whole
    year's holiday set, it is resolved by
    :meth:`~chronologia.civil_holidays.loader.HolidayCalendar.holidays`, not by
    the rule in isolation.
    """

    skip_weekends: bool = True

    def observed_for(self, nominal: AstroDate,
                     taken: FrozenSet[AstroDate]) -> AstroDate:
        """The observed day ``nominal`` occupies given already-``taken`` days.

        Rolls forward from ``nominal`` past any weekend (when ``skip_weekends``)
        and past any day already ``taken`` by another holiday, returning the
        first free business day. A lone weekday holiday whose slot is free is
        returned unchanged; a weekend nominal, or a weekday slot an earlier
        relocation already claimed, cascades forward.
        """
        day = nominal
        while day in taken or (self.skip_weekends and day.weekday() >= 5):
            day = day + timedelta(days=1)
        return day


#: Stock-exchange "next free business day" relocating cascade (Saturday/Sunday
#: relocate to the following Monday, and any holiday bumps past a day another
#: holiday already claimed). Used by the TSX (:file:`xtse.tab`) Christmas/Boxing
#: pair.
SATURDAY_SUNDAY_TO_MONDAY_CASCADE = RelocateShift(skip_weekends=True)


# --------------------------------------------------------------------------
# One shift registry for the ``.tab`` ``observed`` column.
# --------------------------------------------------------------------------
#: A weekend-triggered date policy attached to a rule. There are two, kept as
#: distinct classes on purpose because they act at *different points* with
#: *different semantics* (the per-kind-class doctrine applied to shifts too):
#:
#: * :class:`ObservedShift` *relocates* the nominal day — applied per rule in
#:   :meth:`~chronologia.civil_holidays.model.HolidayRule.resolve`, since it
#:   needs nothing but the date itself.
#: * :class:`SubstitutePolicy` *adds* a separate in-lieu day — applied
#:   calendar-wide in
#:   :meth:`~chronologia.civil_holidays.loader.HolidayCalendar.holidays`, since
#:   the substitute must skip days the rest of the year already took (the UK
#:   cascade).
#:
#: They are unified only where they were needlessly parallel: a single named
#: registry and a single :attr:`HolidayRule.shift` field carry either, dispatched
#: by type at the one point each applies — no twin dicts, no twin rule fields.
ShiftPolicy = Union[ObservedShift, SubstitutePolicy, RelocateShift]

#: ``observed``-column name -> shift policy (relocating, in-lieu, or relocating
#: cascade).
_SHIFT_POLICIES: Dict[str, ShiftPolicy] = {
    "us": US_OBSERVED_SHIFT,
    "sun_mon": SUNDAY_TO_MONDAY,
    "sat_sun_mon": SATURDAY_SUNDAY_TO_MONDAY,
    "sat_sun_mon_cascade": SATURDAY_SUNDAY_TO_MONDAY_CASCADE,
    "il_independence": IL_INDEPENDENCE_SHIFT,
    "nl_kingsday": NL_KINGSDAY_SHIFT,
    "gb_substitute": GB_SUBSTITUTE,
    "jp_furikae": JP_FURIKAE,
    "au_substitute": AU_SUBSTITUTE,
}
