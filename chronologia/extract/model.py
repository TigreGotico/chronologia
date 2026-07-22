"""Frozen value types shared by every stage of the declarative engine.

These mirror the object model in
``docs/design/declarative-datetime-engine.md``.  Every value type is a
frozen dataclass so each pipeline stage consumes and produces immutable,
hashable, comparable values and can be unit-tested in isolation.

Deviations from the design doc (recorded here as the doc requires):

* ``LangSpec.vocab: Mapping[str, frozenset[str]]`` in the doc is split
  into several **typed, value-bearing** maps (``months`` surface->int,
  ``units`` surface->kind, ``named_days`` surface->offset, ``directions``
  surface->sign, ...).  A bare ``frozenset`` of surface forms cannot carry
  the month number, day offset or direction sign a slot needs; those
  values are facts encoded via the loader's filename convention
  (``month_6.voc``, ``named_day_+1.voc``, ``marker_past.voc``), so no
  behaviour leaks into the JSON.  See ``loader.py``.
* ``Resolution.value`` is a :class:`~chronologia.astrodate.DateSpan`
  (endpoints are always ``AstroDate``); the ``DateTimeResolution`` is derived
  from the span's width, not stored, per the doc's reckoning model.
* ``SlotOrder`` is expanded into a tuple of parsed ``SlotElement`` (the
  doc names it as an opaque type); optionality (``DAY?``) and the
  slot/connector distinction are pre-parsed so the matcher stays a plain
  walk.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, FrozenSet, Mapping, Optional, Tuple

from chronologia.astrodate import DateSpan


class Direction(Enum):
    """Declared direction of an offset marker.

    The *sign* of a ``relative_offset`` comes from the marker's declared
    direction, engine-side -- never re-derived per language.  This is what
    makes the "N units ago" sign-flip bug class unwritable.
    """
    PAST = -1
    FUTURE = 1


@dataclass(frozen=True)
class Token:
    """A single lexical unit.

    ``text`` is the normalised form the matcher sees; ``raw`` is the
    original surface form kept for remainder reconstruction.
    """
    text: str
    raw: str
    index: int
    is_number: bool = False
    value: Optional[float] = None


@dataclass(frozen=True)
class TokenizerModes:
    """Per-language tokenizer switches (facts from ``lang.json``)."""
    split_contractions: bool = False
    ordinal_dot: bool = False


@dataclass(frozen=True)
class Conventions:
    """Non-translatable calendar conventions for a language."""
    week_start: str = "monday"
    dmy: bool = True
    hemisphere: Optional[str] = None
    prefer_future: bool = True
    # First day of the two-day weekend, as a Python weekday() index
    # (Monday=0).  The default 5 (Saturday) gives the Sat-Sun weekend of most
    # Western locales; Israel and much of the Arab world rest Friday-Saturday,
    # so their locales set 4 (Friday).  A fact, not logic -- the resolver
    # reads it when building a weekend span.
    weekend_start: int = 5
    # Continental-Germanic clock convention: a bare half-fraction names the
    # half *before* the stated hour ("halb neun" == 08:30, "half negen",
    # "halv nio"), the opposite of English "half nine" == 09:30.  A fact,
    # not logic -- the resolver reads it when a FRACTION binds with no
    # explicit CLOCKDIR.
    bare_half_to: bool = False


@dataclass(frozen=True)
class SlotElement:
    """One element of a construction order.

    ``is_slot`` distinguishes an uppercase placeholder (``MONTH``, ``NUM``)
    from a lowercase literal connector (``of``) matched against a vocab
    set.  ``optional`` is the trailing ``?`` in the order string.
    """
    name: str
    optional: bool
    is_slot: bool


@dataclass(frozen=True)
class SlotOrder:
    """A parsed construction order, e.g. ``"MONTH DAY? YEAR?"``."""
    construction: str
    elements: Tuple[SlotElement, ...]
    raw: str


@dataclass(frozen=True)
class LangSpec:
    """Parsed ``lang.json`` plus every loaded vocabulary for a language."""
    lang: str
    months: Mapping[str, int]
    weekdays: Mapping[str, int]
    units: Mapping[str, str]            # surface -> unit kind
    named_days: Mapping[str, int]       # surface -> offset in days
    directions: Mapping[str, int]       # surface -> +1 / -1
    rel_markers: Mapping[str, int]      # surface -> week offset (next=1,...)
    connectors: Mapping[str, frozenset]  # connector name -> surface forms
    # calendar key -> (surface -> month number) for non-Gregorian calendars;
    # fed by the ``month_<calendar>_<n>.voc`` filename convention.  A surface
    # is unique across calendars within a language (loader enforces).
    calendar_months: Mapping[str, Mapping[str, int]]
    lemmas: Mapping[str, str]
    suffix_strip: Tuple[Tuple[str, str], ...]
    orders: Mapping[str, Tuple[SlotOrder, ...]]
    construction_flags: Mapping[str, Mapping]
    conventions: Conventions
    tokenizer: TokenizerModes
    guards: Mapping[str, int]
    hook: Optional[Callable] = None
    # clock_time slot vocab (surface -> value), all facts from filename convention
    clock_fractions: Mapping[str, int] = field(default_factory=dict)  # -> minutes
    meridiems: Mapping[str, int] = field(default_factory=dict)        # -> hour offset
    clock_dirs: Mapping[str, int] = field(default_factory=dict)       # past +1 / to -1
    # season_ref slot vocab (surface -> canonical season name)
    seasons: Mapping[str, str] = field(default_factory=dict)
    # scoped_ordinal unit vocab beyond the day/week/month units map
    # (decade/century/millennium surface -> kind); reuses ``units`` for the rest
    scope_units: Mapping[str, str] = field(default_factory=dict)
    ordinal_suffixes: Tuple[str, ...] = ()
    # weekday cycle binding: cycle name a weekday_ref order resolves against
    # (default None == the calendar's canonical 7-day week)
    day_cycles: Mapping[str, str] = field(default_factory=dict)  # surface -> cycle key
    cycle_positions: Mapping[str, int] = field(default_factory=dict)  # surface -> index
    # per-calendar day-subdivision name (a lang.json fact); its unit->fraction
    # table lives in cycles.DAY_SUBDIVISIONS (French decimal time: 10h/100m/100s)
    day_subdivision: Optional[str] = None
    # regnal era surface -> (sequence key, segment name), from the
    # regnal_<seqkey>_<segname>.voc filename convention (Japanese nengō)
    regnal_names: Mapping[str, Tuple[str, str]] = field(default_factory=dict)
    # Roman calendar-anchor surface -> anchor name (kalends/nones/ides)
    roman_anchors: Mapping[str, str] = field(default_factory=dict)
    # deep-time / era vocab (facts from the filename convention)
    # named-period surface -> chronologia PERIODS key (geological/archaeological)
    periods: Mapping[str, str] = field(default_factory=dict)
    # scale-word surface -> multiplier ("million" -> 1_000_000)
    scales: Mapping[str, int] = field(default_factory=dict)
    # subdivision-word surface -> chronologia subdivide part (early/mid/late)
    period_parts: Mapping[str, str] = field(default_factory=dict)
    # spoken-decade surface -> tens digit ("nineties" -> 90)
    decade_words: Mapping[str, int] = field(default_factory=dict)
    # clock-landmark surface -> minutes since midnight ("noon" -> 720)
    clock_landmarks: Mapping[str, int] = field(default_factory=dict)
    # quantifier surface -> count ("a" -> 1, "couple" -> 2, "half" -> 0.5)
    quantifiers: Mapping[str, float] = field(default_factory=dict)
    # weekend surface forms ("weekend", "fim de semana", "Wochenende", ...)
    weekend_words: FrozenSet[str] = field(default_factory=frozenset)
    # full weekday names only, excluding abbreviations: the bare-weekday order
    # binds against these so short abbreviation surfaces that collide with
    # common words (de "so", nl "zo", es "mar") never resolve without a marker,
    # while marker-ed orders still accept both via ``weekdays``
    weekday_full: Mapping[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class Match:
    """One construction claiming a span of tokens."""
    construction: str
    span: Tuple[int, int]               # (start, end) exclusive
    slots: Mapping[str, Token]
    # which registered calendar a CAL_MONTH slot resolved to, if any
    calendar: Optional[str] = None

    @property
    def length(self) -> int:
        return self.span[1] - self.span[0]


@dataclass(frozen=True)
class Resolution:
    """The semantic value of a match, before any formatting.

    ``value`` is a :class:`DateSpan`: referential width is primitive, and the
    ``DateTimeResolution`` is *derived* from the span's width rather than
    carried as a separate, potentially-inconsistent tag.
    """
    value: DateSpan
    consumed: Tuple[int, ...]
