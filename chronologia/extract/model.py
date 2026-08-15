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
    # half-open character extent ``[char_start, char_end)`` into the ORIGINAL
    # utterance the tokenizer read, recorded from the regex match offsets.
    # ``None`` on tokens the engine synthesised (a folded spelled number keeps
    # the extent of the surface run it replaced).  Never recovered by string
    # search -- it rides along from the one place that knows it, the tokenizer.
    char_start: Optional[int] = None
    char_end: Optional[int] = None
    # Whether the token's FIRST character was upper-case in the original
    # utterance (``text``/``raw`` are lower-cased for matching, so the case is
    # recorded here at tokenise time).  Read for the proper-noun positional
    # guard on the bare-daypart reading; ``False`` on synthesised tokens.
    cap: bool = False
    # Whether the token IMMEDIATELY PRECEDING this one (in the original
    # utterance, before number folding) opened with a capital.  Recorded at
    # tokenise time so it survives the fold that would otherwise turn a spelled
    # capitalised predecessor into a bare digit ("Twelfth" -> "12"), letting the
    # proper-noun guard fire on "Twelfth Night" as well as "Bonfire Night".
    prev_cap: bool = False
    # Whether a number token was IMMEDIATELY preceded by an apostrophe in the
    # original utterance ("'42", "the '90s").  The tokenizer drops the leading
    # apostrophe from ``raw`` (it is a separator, not part of the digit run),
    # so this flag is the only surviving record that the digits carried the
    # apostrophe cue -- the strong signal that licenses a bare two-digit year
    # even when its value is below the year matcher's usual >=32 threshold.
    apostrophe: bool = False
    # Whether this number token was composed from an INDEFINITE ARTICLE deep-time
    # magnitude ("a million years ago", "a hundred thousand years ago") rather
    # than a spoken numeral.  The article form is a colloquial count-from-now
    # offset -- a single-year point at ``anchor - count*scale`` -- while the
    # numeral form ("66 million", "two thousand") is the geological
    # Before-Present measurement with its sig-fig span.  Set by
    # ``_fold_article_magnitude`` and read by the deep-time resolver, which is
    # the only place that tells the two readings apart once the count is a digit.
    article: bool = False


@dataclass(frozen=True)
class TokenizerModes:
    """Per-language tokenizer switches (facts from ``lang.json``)."""
    split_contractions: bool = False
    ordinal_dot: bool = False
    # the widest digit run ``ordinal_dot`` folds the trailing dot onto.
    # ``None`` (default) is unbounded -- a locale like Hungarian legitimately
    # writes a dotted YEAR that opens a year-first dotted date ("2026.
    # június 20.": the dot after the 4-digit year is a real part of that
    # construction, not a stray sentence period).  German ordinals never run
    # past 2 digits (a day-of-month, a two-digit count), so capping there
    # keeps a bare 4-digit year's trailing SENTENCE period ("Jahr 2027. Es
    # ...") from being folded into the year token as if it were an ordinal
    # dot.  A per-locale fact, not shared logic: the two languages disagree
    # on how wide a genuine ordinal-dot number gets.
    ordinal_dot_max_digits: Optional[int] = None
    # the language writes its everyday numeric date with dots
    # ("15.06.2020"), so that surface is read as one date literal instead of
    # as loose numbers.  Off by default: a language with no dotted
    # convention -- English above all -- must keep reading those digits as
    # the numbers they are.
    dotted_date: bool = False
    # the language groups thousands with a dot and marks the decimal with a
    # comma ("1.234,5" == 1234.5), the Continental-European convention shared
    # by de/es/it/fr/pt/nl/pl/ru/... .  Off by default -- the dot-decimal
    # convention of English (and Hebrew, Malay), where the comma groups
    # thousands ("1,234.5" == 1234.5).  A fact, not logic: the tokenizer reads
    # it to decide which of ',' / '.' inside a digit run is the decimal point
    # and which merely groups thousands, so the SAME two characters are read
    # oppositely per locale instead of silently splitting the number.
    decimal_comma: bool = False


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
    # Finno-Ugric "counting-toward-the-hour" clock convention: a bare
    # fraction names that fraction *of the way toward* the stated (coming)
    # hour, so the quarter forms are unambiguous -- Hungarian "negyed
    # kilenc" == 08:15, "haromnegyed kilenc" == 08:45; Estonian "veerand
    # uheksa" == 08:15, "kolmveerand uheksa" == 08:45 -- alongside the half
    # ("fel kilenc"/"pool uheksa" == 08:30).  Distinct from bare_half_to:
    # the Continental-Germanic family shares the half but a bare quarter
    # ("viertel neun") is regionally ambiguous there, so only these
    # full-system locales opt in.  A fact, not logic -- the resolver reads
    # it when a FRACTION binds with no explicit CLOCKDIR.
    bare_quarter_to: bool = False
    # Twelve-hour reckoning for the toward-hour clock: when a bare toward-hour
    # fraction counts toward the *first* hour ("pol enih" == half toward one),
    # the previous hour is spoken as twelve, not zero -- so the reading is
    # 12:30, not 00:30.  Slovenian, Russian, Polish and Czech colloquial speech
    # all render it this way ("pol enih"/"половина первого"/"wpol do pierwszej"/
    # "pul prvni" == 12:30).  The 24h-reckoning Germanic locales (Danish "halv
    # et" == 00:30, Frisian "healwei ienen") leave it off.  A fact, not logic --
    # the resolver reads it only when the toward-hour subtraction hits zero.
    toward_hour_12h: bool = False
    # British-colloquial additive bare half: a bare half-fraction names the half
    # *past* the stated hour ("half nine" == 09:30), the OPPOSITE direction of
    # the Continental-Germanic bare_half_to ("halb neun" == 08:30).  Only the
    # half takes this colloquial form -- "quarter nine" is not English, so a
    # bare quarter is rejected.  Distinct from bare_half_to (toward the hour)
    # and from the explicit "half past nine" (which the CLOCKDIR path already
    # handles).  A fact, not logic -- the resolver reads it when a bare FRACTION
    # binds with no CLOCKDIR.  Source: Cambridge Dictionary, "half past";
    # British native-speaker consensus that "half nine" == "half past nine".
    bare_half_past: bool = False
    # Positional licensing for the bare-daypart reading: refuse to read a bare
    # DAYPART word ("Night") as a time-of-day band when it is the CAPITALISED
    # tail of a capitalised multi-word phrase -- a proper-noun holiday name such
    # as "Guy Fawkes Night", "Bonfire Night", "Twelfth Night".  Without this the
    # daypart hijacks the noun, stranding the rest of the name and returning
    # tonight's band for a phrase that names no daypart at all.  Set only for
    # languages that capitalise proper nouns but NOT common nouns (English);
    # noun-capitalising languages (German) leave it off, since there a leading
    # capital does not distinguish a proper noun.  A fact, not logic -- the
    # matcher reads it, mirroring the es/gl/pt bare-daypart drop for "mañana".
    daypart_proper_noun_guard: bool = False
    # "since A until B" is a DIRECTIONAL range: "since" past-anchors the start
    # (its most recent past occurrence) while "until" places the end at-or-after
    # that start, so "since monday until friday" reads [last monday, next
    # friday] rather than the both-forward [next monday, next friday] of a plain
    # "from A to B".  Set ONLY for languages whose "since" marker is genuinely
    # past-anchored AND distinct from the forward "from" (English "since").
    # Left off by default because many languages spell "from" and "since" with
    # ONE word that opens a FORWARD closed range (Persian «از», Mirandese "zde",
    # the Romance "desde"/"de") -- there "since A until B" is an ordinary forward
    # interval and must NOT be past-anchored.  A linguistic fact, not logic.
    since_directional: bool = False
    # "at" surfaces that carry NO fused/agreeing article -- the bare
    # preposition, as opposed to a form that already bakes the article in
    # ("la"/"las"/"al" for Spanish, "à"/"às"/"ao" for Portuguese). A bare-hour
    # clock reading (no CLOCKDIR/FRACTION/MINUTE/MERIDIEM evidence) immediately
    # after one of these is not a licensed clock time: Spanish and Portuguese
    # always name the hour with its agreeing article ("a la una", "às três"),
    # never the bare preposition plus a spelled/digit hour ("a un", "a um" --
    # indistinguishable at the token from the everyday indefinite article/
    # count, so it fabricates a time out of "a un rato" / "a um acordo").
    # A fact, not logic -- the matcher reads it to veto that one reading;
    # languages that mark clock hours without articles at all leave it empty.
    bare_at_markers: FrozenSet[str] = frozenset()


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
    # a spelled genitive-cardinal minute count that only ever names the
    # subtractive CLOCKDIR direction ("без пяти" == without five) -- unlike
    # clock_fractions it carries no bare toward-hour idiom of its own, so it
    # cannot ride the FRACTION slot's bare "FRACTION HOUR" order.
    clock_dir_minutes: Mapping[str, int] = field(default_factory=dict)  # -> minutes
    meridiems: Mapping[str, int] = field(default_factory=dict)        # -> hour offset
    # NIGHT meridiem surfaces (ar ليل, az gecə): the night daypart is a BAND
    # that crosses midnight, not a uniform +12 PM shift.  Small hours stay AM,
    # evening hours go PM, twelve is midnight -- the band-split lives in the
    # resolver (_clock_hms).  A surface here is also present in ``meridiems`` so
    # the MERIDIEM slot binds it; its numeric offset there is unused.
    night_meridiems: FrozenSet[str] = field(default_factory=frozenset)
    clock_dirs: Mapping[str, int] = field(default_factory=dict)       # past +1 / to -1
    # season_ref slot vocab (surface -> canonical season name)
    seasons: Mapping[str, str] = field(default_factory=dict)
    # solar_event slot vocab: EVENT surface -> kind ("solstice"/"equinox");
    # SOLARQUAL surface -> canonical season name for the formal equinox names
    # (vernal -> spring, autumnal -> autumn) that are NOT plain season words
    solar_events: Mapping[str, str] = field(default_factory=dict)
    solar_quals: Mapping[str, str] = field(default_factory=dict)
    # scoped_ordinal unit vocab beyond the day/week/month units map
    # (decade/century/millennium surface -> kind); reuses ``units`` for the rest
    scope_units: Mapping[str, str] = field(default_factory=dict)
    # dual-noun unit vocab (surface -> unit kind): Semitic languages fuse the
    # count "two" with the unit into a single dual noun -- Arabic ساعتان /
    # ساعتين ("two hours"), يومين ("two days"), Hebrew שעתיים, יומיים -- with no
    # separate "two" word anywhere in the number vocabulary.  A surface here is
    # read by the duration engine as exactly (2 x unit); it is deliberately NOT
    # folded into ``units`` so no other grammar order (offset/timespan) sees it.
    dual_units: Mapping[str, str] = field(default_factory=dict)
    # bare-unit implied-one vocab (surface -> unit kind): the case form a
    # relative offset with no count takes when the count is an implied one
    # ("через неделю" = in a/one week).  Languages without an article encode
    # only the grammatical singular here so an inflected plural/genitive
    # near-miss ("через недели") stays unmatched; empty for most languages.
    singular_units: Mapping[str, str] = field(default_factory=dict)
    # unit/scope-unit surfaces that are a grammatical PLURAL of a singular
    # surface of the SAME kind (day/days, hour/hours, fortnight/fortnights).
    # Derived at load time from the vocab (a surface that is another same-kind
    # surface plus an ``-s``/``-es`` ending), never hand-listed, so it is
    # populated only for the ``-s``-plural languages and stays empty elsewhere.
    # A scoped-ordinal selection ("the Nth <unit> of ...") is grammatically
    # singular in every language, so a plural unit in that frame is a COUNT,
    # not an ordinal day-of-month -- the matcher vetoes the scoped_ordinal
    # reading when the bound unit is one of these ("the two days of June" is
    # not June 2).  Empty for a non-``-s`` language leaves that reading
    # untouched, so the derivation can never wrongly veto there.
    plural_units: frozenset = frozenset()
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
    # Athenian eponymous-archon surface -> archon key (chronologia.archons.ARCHONS),
    # from the archon_<key>.voc filename convention
    archon_names: Mapping[str, str] = field(default_factory=dict)
    # deep-time / era vocab (facts from the filename convention)
    # named-period surface -> chronologia PERIODS key (geological/archaeological)
    periods: Mapping[str, str] = field(default_factory=dict)
    # scale-word surface -> multiplier ("million" -> 1_000_000).  Holds every
    # scale surface (the union across dialect scales) so the SCALE slot binds
    # regardless of the active short/long dialect; a surface whose value is
    # dialect-dependent (the "billion"-cognate) additionally appears in
    # ``scales_by_mode`` and the resolver reads that first.
    scales: Mapping[str, int] = field(default_factory=dict)
    # dialect short/long scale overrides: mode ("short"/"long") -> surface ->
    # multiplier.  The AMBIGUOUS billion-cognate ("billion", "billón",
    # "bilione", "bilião"/"bilhão", "bilió", ...) resolves to 10^9 under the
    # short scale and 10^12 under the long scale; the active mode picks.
    scales_by_mode: Mapping[str, Mapping[str, int]] = field(default_factory=dict)
    # subdivision-word surface -> chronologia subdivide part (early/mid/late)
    period_parts: Mapping[str, str] = field(default_factory=dict)
    # spoken-decade surface -> tens digit ("nineties" -> 90)
    decade_words: Mapping[str, int] = field(default_factory=dict)
    # clock-landmark surface -> minutes since midnight ("noon" -> 720)
    clock_landmarks: Mapping[str, int] = field(default_factory=dict)
    # daypart surface -> canonical day-part name ("morning", "night"); the band
    # itself lives in chronologia.dayparts (CLDR-cited), keyed by that name.
    # Facts from the ``daypart_<name>.voc`` filename convention.
    dayparts: Mapping[str, str] = field(default_factory=dict)
    # deictic daypart selector surface -> "past"/"future": a marker that picks
    # the nearest past/future occurrence of a time-of-day band rather than a
    # fixed day offset (Indonesian "tadi"/"nanti").  Facts from the
    # ``marker_daypart_past.voc``/``marker_daypart_future.voc`` filenames.
    daypart_deictics: Mapping[str, str] = field(default_factory=dict)
    # bare daypart surfaces that are lexically fused with TODAY ("tonight",
    # "vanavond") -- unlike a plain band word ("night", "avond"), the future-
    # roll decision on a composed clock reading must not run for these; the
    # civil day is always the anchor's own day.  Facts from the
    # ``marker_dayparttoday.voc`` filename.
    daypart_today_words: FrozenSet[str] = field(default_factory=frozenset)
    # quantifier surface -> count ("a" -> 1, "couple" -> 2, "half" -> 0.5)
    quantifiers: Mapping[str, float] = field(default_factory=dict)
    # weekend surface forms ("weekend", "fim de semana", "Wochenende", ...)
    weekend_words: FrozenSet[str] = field(default_factory=frozenset)
    #: negation/exception particles that, when they govern a bare reference to
    #: their right ("not tomorrow", "excepto el lunes"), veto it as a *positive*
    #: date -- the residue-veto safety guard against handing back an excluded
    #: day. Empty for a locale that has not declared them (the guard is then a
    #: no-op there). ``exclusion_bound_guards`` are prepositions whose presence
    #: means the phrase is a *bound* ("before friday"), not an exclusion.
    exclusion_triggers: FrozenSet[str] = field(default_factory=frozenset)
    exclusion_bound_guards: FrozenSet[str] = field(default_factory=frozenset)
    #: coordinating triggers (English "but") that read as an exclusion ONLY when
    #: a scope word governs them ("every day but Tuesday" -> exclude Tuesday);
    #: standing alone they are a clause conjunction or discourse opener ("... but
    #: Tuesday is free", "But Tuesday works") and veto nothing. A subset of
    #: ``exclusion_triggers``.
    exclusion_coord: FrozenSet[str] = field(default_factory=frozenset)
    #: scope/quantifier words ("every", "any", "all", "day", "week", ...) that
    #: license a coordinating trigger to read as "except".
    exclusion_scope: FrozenSet[str] = field(default_factory=frozenset)
    #: closed-class filler (copulas/pronouns) the exclusion idiom skips over when
    #: deciding whether a trigger is adjacent ("unless it is Tuesday").
    exclusion_filler: FrozenSet[str] = field(default_factory=frozenset)
    # holiday_ref surface -> well-known holiday key ("christmas", "easter");
    # derived at load time from the holidays engine's i18n tables (native
    # names + translations + curated spoken aliases), never hand-listed here
    holidays: Mapping[str, str] = field(default_factory=dict)
    # well-known holiday key -> provenance label ("PT:Natal"), for explain()
    holiday_sources: Mapping[str, str] = field(default_factory=dict)
    # clock timezone surface -> base UTC offset in minutes ("utc"/"gmt" -> 0);
    # a trailing signed offset on the surface token ("utc+2") is added at
    # resolve time.  Facts from the ``clock_zone_<minutes>.voc`` convention.
    clock_zones: Mapping[str, int] = field(default_factory=dict)
    # country/region-name surface -> jurisdiction code ("portugal" -> "PT"),
    # from the ``jurisdiction_<code>.voc`` convention. Per-locale opt-in vocab
    # covering only the jurisdictions that locale names; empty for a locale
    # that has not declared any, in which case "every holiday in <X>" simply
    # never matches (never a shared cross-locale list).
    jurisdictions: Mapping[str, str] = field(default_factory=dict)
    # full weekday names only, excluding abbreviations: the bare-weekday order
    # binds against these so short abbreviation surfaces that collide with
    # common words (de "so", nl "zo", es "mar") never resolve without a marker,
    # while marker-ed orders still accept both via ``weekdays``
    weekday_full: Mapping[str, int] = field(default_factory=dict)
    # marker POSITIONALITY: role name (open-range / recurrence-bound marker,
    # e.g. "until", "since", "for") -> where that marker sits relative to the
    # date it frames -- "pre" (leads, the default), "post" (a postposed bound
    # word trailing its date: Finnish "asti", Turkish "kadar", Basque "arte"),
    # or "affix" (a bound suffix fused onto the date's final surface token:
    # Hungarian "-ig", "péntekig" = "péntek" + "ig").  A role absent from this
    # map is "pre".  The engine consults this fact so agglutinative /
    # postpositional languages express these constructions natively instead of
    # being documented exceptions.  Loaded from ``lang.json`` ``positions``.
    positions: Mapping[str, str] = field(default_factory=dict)


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
    #: set by the "week of X" post-pass when it widens an inner date to its
    #: seven-day calendar week.  A widened week is a span, not a day: a lone
    #: clock/daypart must NOT compose a pinpoint time onto it ("the week of
    #: June 15 at 3pm" is not a one-minute reading), so the composer reads this
    #: flag to keep the week and strand the clock in the remainder instead.
    week_widened: bool = False
