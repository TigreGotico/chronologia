"""The resolved-rule wrapper and the output holiday object.

:class:`HolidayRule` is a named date *kind* plus its civil metadata and the
resolution logic (validity ranges, decree-horizon bridging, observed-shift
application). :class:`CivilHoliday` is the resolved output object — a day- or
half-day-wide span with its metadata and the i18n display API.

The horizon-bridge in :meth:`HolidayRule.resolve` (and its ``predict``
validation) consults the well-known registry
(:data:`~chronologia.civil_holidays.well_known.WELL_KNOWN_BY_KEY`). Because that
registry in turn depends on this module's span helpers, the reference is a
runtime (function-local) import inside the two methods that use it — there is no
import-time dependency from this module on the well-known tier.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
from types import MappingProxyType
from typing import FrozenSet, Mapping, Optional, Tuple

from chronologia.astrodate import BASIS_PREDICTED, AstroDate, DateSpan

from .rules import CATEGORIES, RuleKind
from .shifts import ObservedShift, ShiftPolicy


# --------------------------------------------------------------------------
# The rule wrapper and the output object.
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class HolidayRule:
    """A named holiday rule: a date *kind* plus its civil metadata.

    The ``kind`` is one of the per-kind frozen classes above; ``categories`` is
    a subset of :data:`CATEGORIES`; ``subdiv`` scopes the rule to a subdivision
    (``None`` = jurisdiction-wide); ``shift`` optionally attaches a weekend
    policy — an :class:`ObservedShift` that relocates the computed date onto its
    observed day, or a :class:`SubstitutePolicy` that grants an in-lieu day
    (resolved calendar-wide, see :meth:`HolidayCalendar.holidays`); ``from_year``
    / ``until_year`` optionally bound the years the rule is in force (inclusive).
    """

    name: str
    kind: RuleKind
    categories: FrozenSet[str]
    subdiv: Optional[str] = None
    #: An optional weekend policy — either an :class:`ObservedShift` (relocates
    #: the nominal day, applied here in :meth:`resolve`) or a
    #: :class:`SubstitutePolicy` (adds an in-lieu day, applied calendar-wide in
    #: :meth:`HolidayCalendar.holidays`). One field for both; the applying site
    #: dispatches by type.
    shift: Optional[ShiftPolicy] = None
    from_year: Optional[int] = None
    until_year: Optional[int] = None
    span_shape: str = "day"
    #: Optional name of a :data:`WELL_KNOWN` holiday whose computable rule
    #: *predicts* this holiday's date in years beyond a :class:`DecreeTableRule`
    #: horizon. It bridges the silent time bomb: a decree table that tabulates
    #: 2024–2027 with ``predict="eid_al_fitr"`` resolves 2028 through the
    #: Umm al-Qura calendar with basis ``predicted`` instead of vanishing. Only
    #: honest where a genuine computable mapping exists — a decree row is
    #: annotated with a ``predict`` key only when the key's computed date
    #: matches the tabulated dates for *every* year the row tabulates (proven by
    #: construction, never guessed from the name). See :meth:`resolve`.
    predict: Optional[str] = None
    #: Official-language name alternates, ``lang -> name`` (see
    #: :func:`parse_name_cell`). ``name`` is the primary (first) official name;
    #: this maps *every* official-language rendering the source publishes, and is
    #: empty for a single-name rule. Excluded from equality/hash (it is derived
    #: metadata on the same rule identity, and keeps the rule hashable).
    names: Mapping[str, str] = field(default_factory=dict, compare=False)

    def __post_init__(self) -> None:
        from .well_known import WELL_KNOWN_BY_KEY
        object.__setattr__(self, "names", MappingProxyType(dict(self.names)))
        bad = set(self.categories) - CATEGORIES
        if bad:
            raise ValueError(
                f"unknown categories {sorted(bad)}; schema is {sorted(CATEGORIES)}")
        if self.span_shape not in _SPAN_SHAPES:
            raise ValueError(
                f"unknown span shape {self.span_shape!r}; expected {_SPAN_SHAPES}")
        if (self.from_year is not None and self.until_year is not None
                and self.from_year > self.until_year):
            raise ValueError(
                f"from_year {self.from_year} > until_year {self.until_year}")
        if self.predict is not None:
            if self.predict not in WELL_KNOWN_BY_KEY:
                raise ValueError(
                    f"predict names unknown well-known key {self.predict!r}")
            # The horizon bridge is only honest where the predicting rule
            # reproduces the table's OWN dates for every year the table
            # tabulates (docstring invariant "matches ... for every year ...,
            # proven by construction"). Enforce it at load: if the computable
            # rule disagrees with a tabulated year, extrapolating it past the
            # horizon would fabricate a date the table itself contradicts.
            wk = WELL_KNOWN_BY_KEY[self.predict]
            horizon = getattr(self.kind, "horizon", None)
            bounds = horizon() if callable(horizon) else None
            if bounds is not None:
                for y in range(bounds[0], bounds[1] + 1):
                    tabulated = {d for d, _ in self.kind.observances(y)}
                    if not tabulated:
                        continue
                    predicted = {d for d, _ in wk.kind.observances(y)}
                    if tabulated != predicted:
                        raise ValueError(
                            f"predict {self.predict!r} for {self.name!r} "
                            f"disagrees with the tabulated date(s) in {y}: "
                            f"tabulated {sorted(map(str, tabulated))}, predicted "
                            f"{sorted(map(str, predicted))}. Bridging past "
                            f"{bounds[1]} with this key would fabricate a date "
                            f"the table itself contradicts.")

    def in_force(self, year: int) -> bool:
        """True when ``year`` is within this rule's validity range (inclusive)."""
        if self.from_year is not None and year < self.from_year:
            return False
        if self.until_year is not None and year > self.until_year:
            return False
        return True

    def past_horizon(self, year: int) -> bool:
        """True when ``year`` is outside this rule's :class:`DecreeTableRule` horizon.

        Only a decree-table kind has a horizon; any other kind (computable every
        year) is never "past" one, so this is ``False`` for it.
        """
        horizon = getattr(self.kind, "horizon", None)
        if horizon is None:
            return False
        bounds = horizon()
        if bounds is None:
            return False
        return year < bounds[0] or year > bounds[1]

    def resolve(self, year: int, strict_horizon: bool = False
                ) -> Tuple[Tuple[AstroDate, str], ...]:
        """Resolve this rule for ``year`` into ``(AstroDate, basis)`` pairs.

        By default (``strict_horizon=False``) a decree-tabulated holiday queried
        beyond its :meth:`past_horizon` is *predicted* through its ``predict``
        well-known rule (basis ``predicted``) rather than vanishing. Pass
        ``strict_horizon=True`` to require authoritative-only results: past this
        rule's tabulated horizon it returns ``()`` instead of a predicted date.
        The horizon is per-rule, so only a decree-table rule that is genuinely
        past *its own* horizon is refused — a computable kind (fixed,
        nth-weekday, Easter-offset, …) has no horizon and is never refused.
        """
        from .well_known import WELL_KNOWN_BY_KEY
        if not self.in_force(year):
            return ()
        obs = self.kind.observances(year)
        # Bridge the horizon: a decree-tabulated holiday queried beyond the years
        # it tabulates resolves through its ``predict`` well-known rule (the same
        # computable calendar the feast really follows) with basis ``predicted``,
        # rather than silently vanishing. Strict callers opt out of the bridge
        # and take the honest silence instead of a predicted date.
        if (not strict_horizon and not obs and self.predict is not None
                and self.past_horizon(year)):
            wk = WELL_KNOWN_BY_KEY.get(self.predict)
            if wk is not None:
                obs = tuple((date, BASIS_PREDICTED)
                            for date, _ in wk.kind.observances(year))
        out = []
        for date, basis in obs:
            if isinstance(self.shift, ObservedShift):
                date = self.shift.apply(date)
            out.append((date, basis))
        return tuple(out)


@dataclass(frozen=True)
class CivilHoliday:
    """A resolved holiday: a day-wide span with its civil metadata (objects out).

    ``span`` is a day-wide :class:`~chronologia.astrodate.DateSpan`; ``basis``
    records how the date was established (``exact`` for computed dates,
    ``tabulated`` for calendar-table / decree dates).
    """

    name: str
    span: DateSpan
    jurisdiction: str
    subdiv: Optional[str]
    categories: FrozenSet[str]
    basis: str
    #: Official-language name alternates (``lang -> name``), copied from the
    #: rule. ``name`` is the primary (first) official name; empty for a
    #: single-name holiday. Excluded from equality/hash (derived display data).
    names: Mapping[str, str] = field(default_factory=dict, compare=False)
    #: Display *translations* (``lang -> text``) — renderings we authored, not
    #: official names (see ``holiday_data/translations.tab``). Distinct from
    #: :attr:`names` on purpose. Excluded from equality/hash.
    translations: Mapping[str, str] = field(default_factory=dict, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "names", MappingProxyType(dict(self.names)))
        object.__setattr__(
            self, "translations", MappingProxyType(dict(self.translations)))

    @property
    def date(self) -> AstroDate:
        """The holiday's day (the span's start)."""
        return self.span.start

    def display_name(self, lang: str) -> str:
        """The best name to *show* in ``lang``, along a documented fallback chain.

        The government's own word wins where it exists: an **official** name for
        ``lang`` (from :attr:`names`) is returned first; failing that a **display
        translation** (from :attr:`translations`); failing that the primary
        :attr:`name` itself. ``lang`` is matched exactly, then by its primary
        subtag (so ``"pt-BR"`` falls back to ``"pt"``).
        """
        for table in (self.names, self.translations):
            if lang in table:
                return table[lang]
        base = lang.split("-", 1)[0]
        if base != lang:
            for table in (self.names, self.translations):
                if base in table:
                    return table[base]
        return self.name

    def to_json(self) -> dict:
        """A ``json.dumps``-ready dict envelope (see :meth:`from_json`).

        ``categories`` serialize as a sorted list (deterministic output);
        :meth:`from_json` restores the :class:`frozenset`. ``names`` and
        ``translations`` serialize only when non-empty (backward-compatible with
        older single-name envelopes, which :meth:`from_json` reads too).
        """
        env = {"type": "CivilHoliday", "name": self.name,
               "span": self.span.to_json(), "jurisdiction": self.jurisdiction,
               "subdiv": self.subdiv, "categories": sorted(self.categories),
               "basis": self.basis}
        if self.names:
            env["names"] = dict(self.names)
        if self.translations:
            env["translations"] = dict(self.translations)
        return env

    @classmethod
    def from_json(cls, data: dict) -> "CivilHoliday":
        """Rebuild a :class:`CivilHoliday` from a :meth:`to_json` envelope."""
        if data.get("type") != "CivilHoliday":
            raise ValueError(
                f"not a CivilHoliday envelope: {data.get('type')!r}")
        return cls(data["name"], DateSpan.from_json(data["span"]),
                   data["jurisdiction"], data.get("subdiv"),
                   frozenset(data.get("categories", ())), data["basis"],
                   data.get("names", {}), data.get("translations", {}))


def _day_span(date: AstroDate, basis: str) -> DateSpan:
    start = AstroDate(date.year, date.month, date.day)
    return DateSpan(start, start + timedelta(days=1), basis)


#: Half-day span shapes. The engine's :class:`~chronologia.astrodate.DateSpan`
#: is span-native — its *width* IS the referent — so a half-day holiday is not a
#: flag bolted onto a day, it is a genuinely narrower span. ``half_pm`` (the
#: common "offices close at noon" pre-holiday afternoon) is the interval
#: ``[12:00, 24:00)`` of the day — the free afternoon; ``half_am`` is
#: ``[00:00, 12:00)``. ``day`` (the default) is the full ``[00:00, 24:00)``.
_SPAN_SHAPES = ("day", "half_pm", "half_am")


def _shape_span(date: AstroDate, basis: str, shape: str) -> DateSpan:
    """Build the resolved :class:`DateSpan` for ``shape``.

    A half-day is a real 12-hour-wide span, so ``span.width`` reports
    ``timedelta(hours=12)`` and ``span.contains`` is honest about which half of
    the civil day the holiday actually covers (a ``half_pm`` afternoon does not
    contain the morning). This is the first holiday whose width is not a whole
    day — the payoff of a span-native model over a date-plus-flag one.
    """
    day0 = AstroDate(date.year, date.month, date.day)
    if shape == "day":
        return DateSpan(day0, day0 + timedelta(days=1), basis)
    if shape == "half_pm":
        return DateSpan(day0.replace(hour=12), day0 + timedelta(days=1), basis)
    if shape == "half_am":
        return DateSpan(day0, day0.replace(hour=12), basis)
    raise ValueError(f"unknown span shape {shape!r}; expected {_SPAN_SHAPES}")
