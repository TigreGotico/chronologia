"""Single-span date extraction: the ``extract_timespan`` implementation.

The declarative construction engine that turns a date written the way a human
writes it into the *referential width* of the phrase -- a half-open
:class:`~chronologia.astrodate.DateSpan`.  This module holds the single-span
public edges (:func:`extract_timespan`, :func:`extract_candidates`), the range
and open-range composition family, the per-dialect short/long scale policy, the
exclusion / impossible-date vetoes, the :class:`DateSpanResult` return type, and
the :class:`DateTimeEngine` facade with its lazy per-language engine cache.

The package ``chronologia.extract`` re-exports these names, so the public import
site is unchanged.  Keeping the implementation in this leaf module (which imports
only the engine-core modules, never the package ``__init__``) is what lets the
package ``__init__`` be a thin facade and lets :mod:`chronologia.extract.nseries`
import the shared helpers at module scope with no import cycle.
"""
from __future__ import annotations

import os
import re
import threading
from datetime import datetime, timedelta
from dataclasses import dataclass, replace
from typing import Dict, List, NamedTuple, Optional, Tuple

from chronologia.astrodate import AstroDate, DateSpan, WideDuration
from chronologia.extract.anchored import (apply_anchored_offset,
                                              apply_ordinal_count)
from chronologia.extract.business import apply_business_days
from chronologia.extract.compiler import ConstructionCompiler
from chronologia.extract.confidence import score_candidates as _score_candidates
from chronologia.extract.explain import ExplainTrace, explain
from chronologia.extract.loader import LOCALE_DIR, load_lang_spec
from chronologia.extract.matcher import ConstructionMatcher
from chronologia.extract.model import (LangSpec, Resolution, Token)
from chronologia.extract.normaliser import TemporalNormaliser
from chronologia.extract.pipeline import (fold_tokens, prematch_tokens,
                                              pretokens, render_remainder,
                                              require_text)
from chronologia.extract.resolver import (DATE_CONSTRUCTIONS, Resolver,
                                              compose_date_clock,
                                              compose_date_daypart, _WEEK_START)
from chronologia.extract.tokenizer import Tokenizer


class DateSpanResult(NamedTuple):
    """Return of :func:`extract_timespan`: a span and the leftover text.

    A plain 2-tuple ``(span, remainder)`` for unpacking, plus the named fields
    ``.span`` (a :class:`~chronologia.astrodate.DateSpan`) and ``.remainder``.
    Named ``DateSpanResult`` because it wraps a :class:`DateSpan`; sibling of
    :class:`DurationResult` / :class:`RecurrenceResult`.
    """
    span: DateSpan
    remainder: str


#: Deprecated former name of :class:`DateSpanResult`, kept as an alias through
#: the 1.x line. The wrapped payload is a ``DateSpan``, so the "DateSpan" name
#: is the coherent one; ``TimeSpanResult`` still imports and ``isinstance``-checks
#: identically (same type). Prefer :class:`DateSpanResult`.
TimeSpanResult = DateSpanResult


class DateTimeEngine:
    """Convenience facade wiring the stages for one language.

    Not a public API surface -- a test/introspection helper that runs the
    full pipeline (tokenize -> normalise -> match -> resolve) and returns
    every resolved construction in text order.
    """

    def __init__(self, spec: LangSpec,
                 compiler: Optional[ConstructionCompiler] = None):
        self.spec = spec
        self.compiler = compiler or ConstructionCompiler()
        self.compiled = self.compiler.compile(spec)
        self.tokenizer = Tokenizer(spec.tokenizer)
        self.normaliser = TemporalNormaliser(spec)
        self.matcher = ConstructionMatcher(self.compiled)
        self.resolver = Resolver(spec)

    def tokenize(self, text: str) -> Tuple[Token, ...]:
        # the single shared pre-match pipeline, identical to the one
        # explain() replays, so a trace never misrepresents a real parse
        return prematch_tokens(text, self.spec)

    def resolve(self, text: str, anchor: datetime) -> List[Resolution]:
        matches = self.matcher.match(self.tokenize(text))
        pairs = [(m, self.resolver.resolve(m, anchor)) for m in matches]
        pairs = [(m, r) for m, r in pairs if r is not None]
        return self._compose(pairs)

    def _compose(self, pairs) -> List[Resolution]:
        """Fold a lone clock_time (or a lone daypart) onto a lone date
        construction -- date span intersect clock -> minute span, or date narrowed
        to a daypart band -- otherwise return every resolution in text order."""
        clocks = [(m, r) for m, r in pairs if m.construction == "clock_time"]
        dayparts = [(m, r) for m, r in pairs
                    if m.construction == "daypart_ref"]
        dates = [(m, r) for m, r in pairs
                 if m.construction in DATE_CONSTRUCTIONS]
        merged = second = None
        if len(clocks) == 1 and len(dates) == 1:
            merged, second = compose_date_clock(dates[0][1], clocks[0][1]), \
                clocks[0][0]
        elif len(dayparts) == 1 and len(dates) == 1 and not clocks:
            name = self.spec.dayparts[dayparts[0][0].slots["DAYPART"].text]
            merged, second = compose_date_daypart(
                dates[0][1], dayparts[0][1], name), dayparts[0][0]
        if merged is not None:
            drop = {id(second), id(dates[0][0])}
            kept = [(m, r) for m, r in pairs if id(m) not in drop]
            start = min(dates[0][0].span[0], second.span[0])
            out = [(start, merged)] + [(m.span[0], r) for m, r in kept]
            return [r for _, r in sorted(out, key=lambda e: e[0])]
        return [r for _, r in pairs]

    def explain(self, text: str, anchor: datetime) -> ExplainTrace:
        return explain(text, self.spec, anchor)


_TIMESPAN_ENGINES: Dict[str, "DateTimeEngine"] = {}
#: guards the lazy, per-language engine cache.  The first ``extract_*`` call
#: for a language loads *only* that locale (nothing at import), compiles its
#: engine, and memoises it; the lock makes concurrent first-calls for
#: different languages from separate threads safe (each locale is loaded once,
#: and every later call for a language returns the identical cached engine).
_ENGINE_LOCK = threading.Lock()


def _timespan_engine(lang: str) -> "DateTimeEngine":
    """Return the memoised :class:`DateTimeEngine` for ``lang``.

    Lazy and cached: the locale is loaded and compiled on first use and never
    again.  Raises :class:`NotImplementedError` for languages that have no
    engine locale data (``chronologia/locale/<code>/lang.json``).
    """
    region = lang.lower()
    code = region.split("-")[0]
    # English is the one base language whose NUMERIC day/month order splits by
    # region -- the US reads mdy ("03/04" = March 4), the rest of the anglosphere
    # dmy ("03/04" = 3 April).  The bare ``en`` locale ships the US default
    # (dmy=False); a Commonwealth region subtag flips it.  A region with an
    # override gets its own cached engine keyed on the full tag (mirroring the
    # region-keyed ``_REGION_SCALE`` default for the orthogonal scale feature).
    dmy_override = _REGION_DMY.get(region)
    cache_key = region if dmy_override is not None else code
    engine = _TIMESPAN_ENGINES.get(cache_key)
    if engine is not None:
        return engine
    with _ENGINE_LOCK:
        # re-check under the lock: another thread may have built it while we
        # waited, so a language is only ever compiled once
        engine = _TIMESPAN_ENGINES.get(cache_key)
        if engine is None:
            if not os.path.exists(os.path.join(LOCALE_DIR, code, "lang.json")):
                raise NotImplementedError(
                    f"extract_timespan has no locale data for {lang!r}; only "
                    f"languages with locale/<code>/lang.json are supported so far")
            spec = load_lang_spec(code)
            if dmy_override is not None and spec.conventions.dmy != dmy_override:
                spec = replace(spec, conventions=replace(
                    spec.conventions, dmy=dmy_override))
            engine = DateTimeEngine(spec)
            _TIMESPAN_ENGINES[cache_key] = engine
        return engine


#: Region subtags that override the bare code's numeric day/month order.  Only
#: English needs this: the bare ``en`` locale is US-mdy, so every dmy-convention
#: anglophone region must flip ``conventions.dmy`` back on.  Sources: each
#: country's national date-format norm (all dmy except the US).
_REGION_DMY = {
    "en-gb": True, "en-au": True, "en-nz": True, "en-ie": True,
    "en-in": True, "en-za": True,
}


# ---------------------------------------------------------------------------
# per-dialect short/long scale default (deep time: "a billion years ago")
# ---------------------------------------------------------------------------
#
# The short vs long scale ("billion" = 10^9 short, 10^12 long) is orthogonal to
# the locale's number/date grammar -- the SAME base locale data serves every
# region -- but the dialect default differs by naming country.  A full BCP-47
# code selects the dialect (``pt-BR`` short, ``pt-PT`` long) while loading the
# same base voc; a bare code is the naming country's own norm.  An explicit
# ``scale=`` kwarg hard-overrides both.  Precedence: explicit kwarg > region
# subtag > bare-code naming-country default.  Sources: Wikipedia, "Long and
# short scales" (per-language sections).
#
#: bare language codes whose naming country uses the LONG scale.  Continental
#: European Romance/Germanic (billion = 10^12; 10^9 is milliard/mil-millions):
#: pt(=pt-PT), es (RAE), fr (France), it, ca, gl, ro; de, nl, da, sv, nb, nn.
_LONG_SCALE_LANGS = frozenset({
    "pt", "es", "fr", "it", "ca", "gl", "ro",
    "de", "nl", "da", "sv", "nb", "nn",
})
#: explicit region dialects that override (or pin) the bare-code default.
#: pt-BR and en are short; en-GB has been short since the 1974 UK Treasury
#: switch (Hansard, HC Deb 20 Dec 1974); the continental *-<region> variants
#: pin their long default so a caller can be explicit.
_REGION_SCALE = {
    "pt-pt": "long", "pt-br": "short",
    "es-es": "long", "fr-fr": "long", "de-de": "long",
    "it-it": "long", "nl-nl": "long",
    "en-gb": "short", "en-us": "short",
}
#: every language not otherwise classified defaults to the SHORT scale -- the
#: modern SI-aligned trend and the reading English (the fallback base) already
#: uses.  A locale with no dialect-tagged scale voc resolves identically under
#: either mode, so this default is byte-neutral for them; it only bites the
#: languages that actually ship ``scale_*.short.voc`` / ``.long.voc`` data.


def _resolve_scale_mode(lang: str, scale):
    """The active short/long scale for ``lang`` given an optional ``scale``.

    ``scale`` (``"short"``/``"long"``/``None``) hard-overrides when set;
    otherwise a full BCP-47 region subtag picks the dialect and a bare code
    falls back to its naming country's norm.  Returns ``"short"`` or ``"long"``.
    """
    if scale is not None:
        if scale not in ("short", "long"):
            raise ValueError(
                f"scale must be 'short', 'long' or None, not {scale!r}")
        return scale
    key = lang.strip().lower().replace("_", "-")
    if key in _REGION_SCALE:
        return _REGION_SCALE[key]
    base = key.split("-")[0]
    return "long" if base in _LONG_SCALE_LANGS else "short"


#: default (English) range framing words, always available so English
#: behaviour is unchanged.  A language adds its own surfaces via the
#: ``from``/``to``/``between``/``and`` connectors (``marker_from.voc`` ...),
#: which are unioned in per language -- ranges are not English-only.  ``"-"``
#: is deliberately *not* a ``to`` word here: a hyphen is punctuation the
#: tokenizer drops, so a dash range separator is detected on the character gap
#: between two tokens instead (see :func:`_dash_between`).
_RANGE_FROM = ("from",)
_RANGE_TO = ("to", "until", "till", "through", "thru")
_RANGE_BETWEEN = ("between",)
_RANGE_AND = ("and",)
#: leading markers of an open-ended range -- "until friday" (open start,
#: bounded below by "now") and "since 2019" (open end, bounded above by
#: "now").  Languages add their own surfaces via the ``until``/``since``
#: connectors; the English defaults keep English working with no locale data.
_RANGE_UNTIL = ("until", "till", "through", "thru")
_RANGE_SINCE = ("since",)

#: a bare "A to B" is capped at two endpoints; a chain of range connectors
#: ("monday to monday to monday ...") is *scanned* for the first split, never
#: recursed once per connector, so a pathological connector run cannot exhaust
#: the stack -- everything past the first endpoint pair falls to the remainder.
_DASH_GAP = re.compile(r"\s+-+\s+")

#: an unspaced dash gap, as a written year range is set ("1914-1918"); the en
#: and em dashes are included because typeset prose uses them for exactly this.
_TIGHT_DASH = re.compile(r"[-–—]")

#: a slash gap, the ISO-8601 §4.4.1 time-interval separator ("2020/2021",
#: "2020-04/2020-06").  Unlike the dash, the slash also glues the components of
#: an English numeric date ("06/15/2020"), so it is trusted as an interval
#: separator ONLY between two year-first ISO endpoints (see ``_dash_between``).
_SLASH_GAP = re.compile(r"/")

#: a year-first ISO date endpoint -- a bare four-digit year ("2020") or an ISO
#: calendar/year-month literal the tokenizer kept whole ("2020-04",
#: "2020-06-15").  This is the ONLY shape a "/" is trusted to join into an
#: interval, so a numeric date whose first component is not a four-digit year
#: ("04/2020", "2020/04", "2024/03") is never mistaken for one.
_ISO_YEAR_FIRST = re.compile(r"\d{4}(?:-\d{1,2}){0,2}")

#: the constructions a lone ``clock_time`` composes onto (its minute-wide time
#: placed on the day the date names).  A single composable-date set so the
#: synthesised day-wide results of the post-passes -- a business-day count
#: ("in 5 business days at 3pm"), an anchor-relative weekday count ("3 fridays
#: from now at noon"), the weekend-after-next -- fold with a trailing clock
#: exactly as a matcher-native date does, rather than being second-class to the
#: ``DATE_CONSTRUCTIONS`` the matcher itself emits.
_COMPOSABLE_DATES = DATE_CONSTRUCTIONS | {
    "business_days", "weekday_count", "weekend_after_next",
    "weekend_before_last", "weekend_ago"}

#: A weekday next to one of these LITERAL calendar dates is read as a restated
#: label of it ("Monday, March 2" -> March 2, weekday consumed).  A DERIVED date
#: (a business-day / anchored-offset / ordinal-count / holiday result) is NOT
#: labelable: a weekday beside it is a separate mention, not a restatement, and
#: swallowing it would silently drop a token that may even name a different day
#: than the computed date lands on.
_WEEKDAY_LABELABLE_DATES = frozenset({
    "calendar_date", "month_day_ref", "iso_date", "numeric_date",
    "reckoned_date", "nongregorian_date"})


def _conn_surfaces(spec, name, defaults):
    """The connector ``name`` as word lists (longest first) for token matching.

    The English defaults unioned with the language's own connector surfaces --
    the same set the old regex alternated over, but kept as tokens so a
    connector is recognised on the *stream*, never by scanning the raw string.
    """
    forms = set(defaults) | set(spec.connectors.get(name, ()))
    return sorted((f.lower().split() for f in forms if f),
                  key=len, reverse=True)


def _match_conn_at(tokens, i, surfaces):
    """Token length of the (possibly multi-word) connector at ``i``; 0 if none."""
    for words in surfaces:
        n = len(words)
        if i + n <= len(tokens) \
                and [t.text for t in tokens[i:i + n]] == words:
            return n
    return 0


def _is_written_year(token):
    """True for a bare four-digit number -- the shape a written year range uses."""
    return (token.is_number and token.raw is not None
            and len(token.raw) == 4 and token.raw.isdigit())


def _is_iso_year_first_token(token):
    """True when ``token`` is a year-first ISO endpoint ("2020", "2020-04").

    A "/" is the ISO-8601 interval separator, but it is also the English
    numeric-date separator, so it is only trusted as a separator between two of
    these -- both sides being year-first is what tells the interval apart from
    a numeric date (see :func:`_dash_between`)."""
    return (token.raw is not None
            and _ISO_YEAR_FIRST.fullmatch(token.raw) is not None)


def _dash_between(tokens, p, text):
    """True when a hyphen in the gap before token ``p`` separates two range
    endpoints.

    A dash range separator ("junho - agosto", "5 de junho - 12 de junho") is
    punctuation the tokenizer never emits, so it is read straight from the
    character gap between the adjacent tokens' recorded extents -- linear and
    anchored, no raw-string regex over the whole input.

    Spaced, the dash is unambiguous.  Tight ("1914-1918") it is only trusted
    between two four-digit numbers, which is what makes the rule safe: every
    other hyphenated numeric shape a date can wear is lexed as one token before
    this code ever sees it (an ISO date "2026-07-24", an ISO year-month
    "2026-07", a numeric date "5-6-24", an ISO week "2026-W01" -- all leave no
    gap at all), and no calendar component other than a year is written with
    four digits.  So "12-15" is not a range, "2026-07" is still a month, and
    "1914-1918" reads as the range it is instead of being refused."""
    a, b = tokens[p - 1].char_end, tokens[p].char_start
    if a is None or b is None:
        return False
    gap = text[a:b]
    if _DASH_GAP.fullmatch(gap) is not None:
        return True
    # the ISO-8601 time-interval separator "/": trusted only between two
    # year-first ISO endpoints ("2020/2021", "2020-04/2020-06"), so the English
    # numeric date ("06/15/2020") and a lone slashed pair ("04/2020",
    # "2020/04") -- neither of which is two year-first ISO dates -- are left to
    # the numeric-date reading untouched.
    if _SLASH_GAP.fullmatch(gap) is not None:
        return (_is_iso_year_first_token(tokens[p - 1])
                and _is_iso_year_first_token(tokens[p]))
    if _TIGHT_DASH.fullmatch(gap) is None:
        return False
    # A tight dash between two written years is the set year range ("1914-1918").
    if _is_written_year(tokens[p - 1]) and _is_written_year(tokens[p]):
        return True
    # A tight dash between two plain numerals is the day-range shorthand of the
    # languages that write it that way ("3-10 Temmuz", "3.-10. heinaekuuta").
    # It is safe to trust here because the *composition* still has to succeed:
    # a bare "12-15" leaves both endpoints unresolvable with no month to share,
    # so it never becomes a range -- only a pair where one side lends the other
    # a month (see :func:`_shared_context`) composes.
    return tokens[p - 1].is_number and tokens[p].is_number


def _first_to_split(tokens, left_start, to_surf, text):
    """First "to"-connector at a boundary after ``left_start``.

    Returns ``(p, k)`` -- the connector begins at token ``p`` and spans ``k``
    tokens (``k == 0`` for a dash gap, which consumes no token) -- with a
    non-empty left (``tokens[left_start:p]``) and right side, or ``None``.
    Scanning left to right and returning the first hit mirrors the old
    non-greedy ``(.+?)`` that split on the *first* connector."""
    n = len(tokens)
    for p in range(left_start + 1, n):
        k = _match_conn_at(tokens, p, to_surf)
        if k and p + k < n:                       # word connector, right non-empty
            return p, k
        if _dash_between(tokens, p, text):        # dash gap, right is tokens[p:]
            return p, 0
    return None


def _find_conn(tokens, surfaces):
    """``(pos, k)`` of the first connector from ``surfaces``, or ``None``.

    The range lead ("from", "between") is not always utterance-initial -- it
    is routinely preceded by a subject ("the shop is open from 9 to 5") or by
    a scoping qualifier ("next week from monday to friday").  Anchoring the
    lead scan at token 0 left that pre-text *inside* the left endpoint slice,
    where it could be swallowed by an unrelated construction ("week from
    monday" read as a week reference, re-anchoring the whole range a week
    late).  Scanning for the lead wherever it sits keeps the endpoint slices
    to the endpoints, and the pre-lead text goes to the remainder where it
    belongs.
    """
    for i in range(len(tokens)):
        k = _match_conn_at(tokens, i, surfaces)
        if k:
            return i, k
    return None


def _lead_at(tokens, surfaces, spec):
    """Where the range lead sits: ``(pos, k)`` or ``None``.

    Utterance-initial for any surface, anywhere for a surface that cannot be
    mistaken for a date particle (see :func:`_unambiguous_lead`).
    """
    k = _match_conn_at(tokens, 0, surfaces)
    if k:
        return 0, k
    return _find_conn(tokens, _unambiguous_lead(spec, surfaces))


def _unambiguous_lead(spec, surfaces):
    """``surfaces`` minus those that double as a date particle.

    A lead is only worth hunting for mid-utterance when its surface says
    "range" wherever it appears.  The Romance ``de`` is both the range lead
    ("de juny a agost") and the genitive that glues a date together ("5 de
    juny"), so scanning for it would split "5 de juny - 12 de juny" at the
    genitive and throw the day away.  Such a surface stays trusted only
    utterance-initially, where nothing precedes it to be a date.  English
    ``from`` is no one's particle, so it is scanned for freely.
    """
    particles = set(spec.connectors.get("of", ())) \
        | set(spec.connectors.get("at", ()))
    return [w for w in surfaces if " ".join(w) not in particles]


def _with_prefix(got, prefix):
    """Prepend the pre-lead text to a composed range's remainder."""
    if got is None or not prefix:
        return got
    span, rem = got
    return span, (prefix + " " + rem).strip() if rem else prefix


def _crosses_midnight(span):
    """True when ``span``'s wall clock ends on a later calendar day than it
    starts -- it only became a band by rolling across midnight."""
    sd, ed = span.start_datetime, span.end_datetime
    return sd is not None and ed is not None and ed.date() > sd.date()


def _subtractive_clock_complete(text, sub, engine, anchor):
    """True when ``sub`` resolves whole as one sub-day clock time.

    The subtractive clock ("ten to eight pm" == ten minutes to eight) reads the
    entire slice as a single time of day.  When the SINGLE core consumes every
    token of the slice that carries text into a span narrower than a day, that
    reading is both available and complete -- proof the slice is one clock, not
    two range endpoints.  Used only to veto a clock-*range* that descended into
    a cross-midnight band (see :func:`_extract_range`)."""
    folded = fold_tokens(tuple(sub), engine.spec, text)
    core = _resolve_core(folded, engine, anchor)
    if core is None:
        return False
    span, consumed = core
    if span.end - span.start >= timedelta(days=1):
        return False
    return all(t.index in consumed
               for t in folded if t.char_start is not None)


def _extract_range(text, tokens, engine, anchor, scale_mode="short"):
    """A "from A to B" / "between A and B" span, endpoints from two sub-parses.

    Token-native: the connector is found on the *pre-fold* token stream (so the
    number fold cannot swallow the ``and``/``to`` a range hinges on) and the two
    endpoints are resolved from slices of that stream, each folded on its own --
    never re-tokenized, never recursed back into range detection.  So a long
    connector chain is scanned once for the first split rather than recursed once
    per connector.

    Only fires when *both* sides parse on their own and the left edge is not
    after the right; otherwise returns ``None`` so the normal single-span path
    runs (this keeps "quarter to five" -- a clock, not a range -- from being
    read as a range)."""
    spec = engine.spec
    n = len(tokens)
    if n < 2:
        return None
    # a language's ``until`` word *is* its closed-range terminator: English
    # says so in the defaults above, where "until"/"till"/"through" are ``to``
    # words as much as "to" is.  Many locales declare their terminator only in
    # ``marker_until`` -- Persian "تا", Indonesian "sampai", Malay "hingga" --
    # and a closed range said with one of those used to fall through to the
    # OPEN reading, returning "from the left endpoint to now": a strictly
    # wider span than was uttered, with the stated terminator left in the
    # remainder.  Unioning the two connectors makes the word bind on both
    # readings in every language at once.  The open reading is untouched: a
    # leading marker sits at token 0, where :func:`_first_to_split` cannot
    # split because that would leave the left endpoint empty.
    # a "to" surface that is licensed ONLY after an explicit from/between lead
    # -- a directional/dative preposition too common to trust unconditionally
    # (Hebrew proclitic ל־ "to/for": "מ־ינואר ל־אפריל" is a range, a bare
    # "ל־3 שעות" is not).  A locale declares these via ``marker_to_after_from``;
    # they join the range terminators so the split can find them, and join the
    # lead-required guard below so a bare "A ל B" never fabricates a range.
    lead_only_to = tuple(spec.connectors.get("to_after_from", ()))
    to_surf = _conn_surfaces(
        spec, "to",
        _RANGE_TO + tuple(spec.connectors.get("until", ())) + lead_only_to)
    from_surf = _conn_surfaces(spec, "from", _RANGE_FROM)
    between_surf = _conn_surfaces(spec, "between", _RANGE_BETWEEN)
    and_surf = _conn_surfaces(spec, "and", _RANGE_AND)
    # lone clock-fraction words that a bare "A to B" must never treat as a
    # range endpoint (would hijack "quarter to five" / "čtvrt na päť")
    fraction_words = set(spec.clock_fractions) | {"quarter", "half", "a quarter"}
    # a "to" surface that is *also* the language's ``at`` marker is a hyper-common
    # preposition (Spanish/Portuguese "a" -- "a las 3", "vamos a Madrid") and so
    # is only trusted as a range boundary when an explicit ``from`` lead ("de",
    # "desde") disambiguates it: a bare "A a B" must not fabricate a range out of
    # "junio a las tres".  English "to"/"until" are not ``at`` markers, so this
    # set is empty for English and every other language leaves bare ranges intact.
    at_words = set(spec.connectors.get("at", ()))
    lead_required = {s.lower()
                     for s in set(spec.connectors.get("to", ()))
                     | set(spec.connectors.get("until", ()))
                     if s in at_words}
    lead_required |= {s.lower() for s in lead_only_to}
    # the marker word set that reads specifically as "until"/"till"/"through"
    # (never plain "to") -- used below to scope the month-fraction veto so it
    # never touches a bare "X to Y" range.
    until_words = {" ".join(w) for w in _conn_surfaces(spec, "until", _RANGE_UNTIL)}
    # the bare "to" surface itself (never "until"/"till"/"through") -- the
    # #660 double-bind veto below was originally scoped to ``until_words``
    # only, leaving "first half of august to 2030" to reproduce the same
    # self-contradictory span (2030-08-01..2031-01-01) that #660 fixed for
    # the until-words.  Its own comment flagged "to" as untouched; no test
    # pinned it.  Unioning the plain "to" surface here closes that gap while
    # leaving every other bare-"to" reading (clock ranges, date ranges,
    # duration connectors) untouched, since the veto still only fires when
    # the left side carries a fraction marker and the right side is a lone
    # bare year.
    bare_to_words = {" ".join(w) for w in _conn_surfaces(spec, "to", _RANGE_TO)} \
        - until_words
    # the period-fraction markers ("half"/"quarter") that name a HALF/QUARTER
    # OF A MONTH construction (``half_period``'s MONTH order, ``quarter_of_
    # month``) -- see the veto below.
    fraction_marker_words = (set(spec.connectors.get("half", ()))
                             | set(spec.connectors.get("quarter_word", ())))

    def endpoint(sub):
        return _range_endpoint(text, sub, engine, anchor, scale_mode=scale_mode)

    def bare_of(sub):
        return _bare_numeral(text, sub, engine, anchor)

    def borrowed(sub):
        # a slice carrying tokens lent by the other endpoint; resolved through
        # the synthetic-token path so the lent words, which have no extent of
        # their own here, cannot surface in this endpoint's remainder
        return _range_endpoint(text, sub, engine, anchor,
                               resolve=_variant_endpoint, scale_mode=scale_mode)

    # -- from A to B -------------------------------------------------------
    at_from = _lead_at(tokens, from_surf, spec)
    at_between = _lead_at(tokens, between_surf, spec)
    lead_at, lead = at_from if at_from is not None else (0, 0)
    split = _first_to_split(tokens, lead_at + lead, to_surf, text)
    if split is not None:
        p, k = split
        left_tok, right_tok = tokens[lead_at + lead:p], tokens[p + k:]
        # a bare "A to B" (no from/between) is only trusted when the left side is
        # not a lone clock fraction word (avoids hijacking "quarter to five") AND
        # the connector is not an ``at``-ambiguous preposition (avoids fabricating
        # "junio a las tres" into a range); either trap is disarmed by a lead.
        led = bool(lead) or at_between is not None
        left_words = " ".join(t.text for t in left_tok)
        conn_words = " ".join(t.text for t in tokens[p:p + k]).lower()
        if led or (left_words not in fraction_words
                   and conn_words not in lead_required):
            prefix = render_remainder(text, list(tokens[:lead_at])) \
                if lead else ""
            # an explicit lead licenses the bare-hour reading of a numeric
            # endpoint ("from 9 to 5"), which must be tried *before* the
            # generic composition so a borrowed meridiem cannot roll a day.
            got = None
            # an explicit lead ("from 9 to 5") OR a trailing meridiem that
            # already frames the pair as clock times ("9 to 5 pm") licenses the
            # bare-hour reading with its am/pm fallback, which must be tried
            # *before* the generic composition so a borrowed meridiem cannot
            # roll a bogus ~20h day-crossing span (9->21:00, then 5pm rolled to
            # tomorrow).  A bare "9 to 5" with no meridiem stays the subtractive
            # clock ("nine minutes to five"), untouched.
            if led or _trailing_meridiem(right_tok, spec) is not None \
                    or _trailing_meridiem(left_tok, spec) is not None:
                got = _compose_clock_range(text, left_tok, right_tok,
                                           engine, anchor)
            if got is None:
                got = _compose_range(left_tok, right_tok, endpoint,
                                     borrowed, spec, bare_of)
            # A month-fraction left endpoint ("first half of august", "third
            # quarter of february") whose right side is a BARE lone year
            # joined by "until"/"till"/"through" double-binds that year: the
            # same token both fills the fraction construction's own optional
            # YEAR slot (via _lend_year, so the left resolves the correct
            # in-year fraction span) AND is read again as its own full
            # calendar-year endpoint, whose ``.end`` then closes the range --
            # "first half of august, until 2030" would otherwise yield
            # 2030-08-01..2031-01-01, a self-contradictory span (a half-month
            # start paired with a whole-year end).  Refuse rather than surface
            # it; a bare "to" ("first half of august to 2030") and any left
            # side that is not a month-fraction (bare "june until 2030") are
            # untouched -- both compose exactly as before.
            if got is not None \
                    and any(t.text in fraction_marker_words for t in left_tok) \
                    and (conn_words in until_words or conn_words in bare_to_words) \
                    and bare_of(right_tok) is not None:
                got = None
            # A bare (unled) "MINUTE to HOUR pm" is the subtractive clock
            # ("ten to eight pm" == ten minutes to eight pm == 19:50), not a
            # range.  Read as two endpoints the same-meridiem pair descends
            # (10pm > 8pm), so the composed span only exists by rolling the
            # right end across midnight -- an absurd ~22h cross-midnight band
            # that would still preempt the correct minute-wide clock.  When the
            # whole slice resolves cleanly as one sub-day clock (the subtractive
            # reading is available AND complete) and the composed range only
            # spans by crossing midnight, the range is that misreading: bail so
            # the single-span path returns the subtractive clock.  An explicit
            # lead ("from 10 pm to 8 am") is a deliberate range and is untouched,
            # as is any ascending same-day pair ("5 to 9 am", "8 to 11 pm"),
            # which never crosses midnight.
            if got is not None and not led \
                    and _crosses_midnight(got[0]) \
                    and _subtractive_clock_complete(
                        text, tokens[lead_at + lead:], engine, anchor):
                return None
            if got is not None:
                return _with_prefix(got, prefix)

    # -- between A and B ---------------------------------------------------
    if at_between is not None:
        lead_at, lead = at_between
        split = _first_to_split(tokens, lead_at + lead, and_surf, text)
        if split is not None:
            p, k = split
            left_tok, right_tok = tokens[lead_at + lead:p], tokens[p + k:]
            prefix = render_remainder(text, list(tokens[:lead_at]))
            got = _compose_clock_range(text, left_tok, right_tok,
                                       engine, anchor)
            if got is None:
                got = _compose_range(left_tok, right_tok, endpoint,
                                     borrowed, spec, bare_of)
            if got is not None:
                return _with_prefix(got, prefix)
    return None


#: the surfaces "now" resolves from -- the anchor instant.  Kept as a connector
#: (``marker_now.voc`` -> ``spec.connectors["now"]``) so a locale supplies its
#: own; the English defaults carry the bare word and its "right now" intensifier.
_NOW_WORDS = ("now", "right now")


def _now_surfaces(spec):
    return _conn_surfaces(spec, "now", _NOW_WORDS)


def _is_now_slice(sub, spec):
    """True when ``sub`` is *exactly* a "now" surface ("now" / "right now").

    Matched whole-slice only, so it never fires inside a longer phrase ("now and
    then", "for now"): those carry extra tokens and so are not a bare "now".
    """
    if not sub:
        return False
    words = [t.text.lower() for t in sub]
    return any(words == w for w in _now_surfaces(spec))


def _now_span(anchor):
    """The anchor instant as a zero-width span ("now" is a point, not a band)."""
    now = AstroDate.from_datetime(anchor)
    return DateSpan(now, now)


#: the bare English surfaces for New Year's Day that carry NO "day"/"eve" tail.
#: Held in code, NOT as a well-known spoken alias, on purpose: a "new year"
#: holiday surface would be folded into a single multiword token and so would
#: shadow the ``hebrew_new_year`` construction ("the hebrew new year 5786"),
#: whose grammar needs "new" and "year" as separate slots.  Matching the bare
#: surface here -- only as a whole endpoint slice or a whole standalone
#: utterance -- resolves "from Christmas to New Year" and a lone "New Year"
#: without touching the token fold.  "new year's day"/"new years day" keep
#: resolving through the ordinary holiday path.
_NEW_YEAR_WORDS = (("new", "year"), ("new", "years"))


def _is_new_year_slice(sub, spec):
    """True when ``sub`` is exactly the bare "new year"/"new years" surface."""
    if not sub:
        return False
    words = tuple(t.text.lower() for t in sub)
    return words in _NEW_YEAR_WORDS


def _new_year_span(anchor):
    """New Year's Day (Jan 1) as a whole-day span, the occurrence on or after
    the anchor date -- the same choice a bare holiday reference makes."""
    from chronologia.civil_holidays import WELL_KNOWN_BY_KEY
    wk = WELL_KNOWN_BY_KEY.get("new_year")
    year = anchor.year
    got = wk.date_for(year)
    if got is not None and got[0] < anchor.date():
        year += 1
    span, _basis = wk.span_for(year)
    return DateSpan(span.start, span.end)


def _range_endpoint(text, sub, engine, anchor, resolve=None, scale_mode="short"):
    """A range endpoint carrying its *granularity kind* and whether its year was
    pinned, so :func:`_compose_range` can roll it without fabricating.

    Returns ``(span, remainder, kind, pinned)`` or ``None``.  ``kind`` is:

    * ``"clock"`` -- a sub-day span (a time of day); its cycle is one day, so a
      right endpoint that lands before the start ("10 pm to 2 am") rolls a day;
    * ``"weekday"`` -- a bare weekday, a day-wide span whose cycle is one week
      ("monday to friday"); it rolls a week;
    * ``"dated"`` -- a calendar date / month / year / era, whose year was
      already placed by the endpoint's own resolution (prefer_future).  A dated
      endpoint is **never** day/week-rolled: rolling a fixed calendar date by
      single days is exactly the fabrication that turned "june 12 2020 to june 5
      2020" into a bogus one-day span.

    ``pinned`` is True when the slice carries an explicit year (a year-magnitude
    number).  A pinned endpoint's cycle is fixed, so the straddle pull-back that
    repairs a bare, prefer_future-flung endpoint must not touch it.

    ``resolve`` names which reader the slice goes through; it defaults to the
    plain one and is swapped for :func:`_variant_endpoint` when the slice
    carries tokens lent by the other endpoint, whose text belongs to that
    endpoint and so must not reach this one's remainder.
    """
    # "now" as an endpoint is the anchor instant: a fixed point, never rolled or
    # year-pulled (kind "dated", pinned).  Wiring it here is what lets "from now
    # to X" / "between now and X" compose as [anchor, X] instead of collapsing to
    # X's point when the "now" endpoint failed to resolve.
    if _is_now_slice(sub, engine.spec):
        return _now_span(anchor), "", "dated", True
    # a bare "new year" endpoint is New Year's Day -- a fixed calendar date, so
    # dated and pinned (never rolled).  This is what binds the trailing holiday
    # of "from Christmas to New Year" instead of dropping it and collapsing the
    # range onto Christmas.
    if _is_new_year_slice(sub, engine.spec):
        return _new_year_span(anchor), "", "dated", True
    resolve = resolve or _resolve_endpoint
    pinned = any(t.is_number and t.value is not None and t.value >= 100
                 for t in sub)
    weekday = any(t.text in engine.spec.weekdays for t in sub)
    got = resolve(text, sub, engine, anchor, scale_mode=scale_mode)
    if got is not None:
        span, rem = got
        deep_time = False
        width = span.end - span.start
        if isinstance(width, WideDuration):
            # a deep-time endpoint (a geological epoch spanning millions of
            # years) is wider than any timedelta, so subtracting its endpoints
            # yields a WideDuration.  It is a wider-than-a-day span (so never
            # clock/weekday), and its own "deep_time" kind lets _compose_range
            # treat a reversed range spanning it as an acyclic interval to swap
            # rather than a civil ordering error to refuse.
            sub_day = day_wide = False
            deep_time = True
        else:
            sub_day = width < timedelta(days=1)
            day_wide = width <= timedelta(days=1)
        if sub_day:
            kind = "clock"
        elif day_wide and weekday:
            kind = "weekday"
        elif deep_time:
            kind = "deep_time"
        else:
            kind = "dated"
        return span, rem, kind, pinned
    bw = _bare_weekday_endpoint(sub, engine, anchor)
    if bw is not None:
        return bw[0], bw[1], "weekday", pinned
    return None


#: the hours a bare numeral may name on a 12-hour clock
_BARE_HOUR = (1, 12)


def _align_awareness(left_span, right_span):
    """The two endpoint spans read on a common UTC offset.

    A zone literal binds to the endpoint that carries it ("from noon to 3:30
    utc+2"), leaving the other endpoint naive -- and comparing a naive to an
    aware value raises :class:`TypeError`, which the public extractors
    (documented as "returns ``None``, never raises") must never surface.

    A range is one interval, so its two ends are read on **one** clock: the
    naive endpoint is taken to be a *wall clock in the zone the other endpoint
    names*.  "from noon to 3:30 utc+2" is noon UTC+2 to 3:30 UTC+2 -- the
    reading a speaker intends when they name the zone once for the pair.  The
    wall-clock reading is preserved (the offset is *attached*, never
    converted), so no stated time is silently shifted.  When neither or both
    endpoints are aware the pair is already common and is returned untouched.
    """
    lz = left_span.start.tzinfo
    rz = right_span.start.tzinfo
    if (lz is None) == (rz is None):
        return left_span, right_span
    zone = rz if lz is None else lz

    def attach(span):
        if span.start.tzinfo is not None:
            return span
        return DateSpan(span.start.replace(tzinfo=zone),
                        span.end.replace(tzinfo=zone))

    return attach(left_span), attach(right_span)


def _roll_after(span, start, step):
    """``span`` advanced by whole ``step``s until it ends after ``start``.

    The cycle count is computed arithmetically rather than stepped.  Stepping
    cost the *day distance* between the endpoints, which the utterance chooses
    freely via its year -- "from june 12 9999 to 3:30" spun ~2.9 million
    iterations (~45 s) inside a synchronous intent parse.  The answer is a
    division, so it is O(1) whatever the distance.
    """
    delta = start - span.end
    if delta < timedelta(0):
        return span
    n = delta // step + 1
    return DateSpan(span.start + n * step, span.end + n * step)


def _dateless_clock(sub, spec):
    """True when the slice names *only* an hour (plus its meridiem).

    Such an endpoint carries no day of its own, so it is the one that gets
    placed on the other endpoint's day.
    """
    return not [t for t in sub
                if not (t.is_number and t.value is not None)
                and t.text not in spec.meridiems]


def _bare_hour_pos(sub, spec):
    """Index in ``sub`` of a lone hour written *without* a meridiem, else None.

    The slice must carry exactly one integer 1..12 and no am/pm word of its
    own -- "9" in "from 9 to 5", "5" in "5 on tuesday".  A clock literal
    ("09:00") is a single lexical token and is not a bare number, so an
    explicit time is never second-guessed.
    """
    nums = [i for i, t in enumerate(sub) if t.is_number and t.value is not None]
    if len(nums) != 1 or any(t.text in spec.meridiems for t in sub):
        return None
    v = sub[nums[0]].value
    if v != int(v) or not _BARE_HOUR[0] <= int(v) <= _BARE_HOUR[1]:
        return None
    return nums[0]


def _meridiem_surfaces(spec):
    """The shortest ``(am, pm)`` surface the language spells a half-day with."""
    def pick(offset):
        forms = sorted((s for s, off in spec.meridiems.items() if off == offset),
                       key=len)
        return forms[0] if forms else None
    return pick(0), pick(12)


def _with_meridiem(sub, pos, surface):
    """``sub`` with ``surface`` spliced in right after the hour at ``pos``.

    The spliced tokens are synthetic: they carry no character extent, which is
    exactly how :func:`_variant_endpoint` keeps them out of the remainder.
    """
    extra = tuple(Token(text=w, raw=w, index=-1 - i)
                  for i, w in enumerate(surface.split()))
    return tuple(sub[:pos + 1]) + extra + tuple(sub[pos + 1:])


def _variant_endpoint(text, sub, engine, anchor, scale_mode="short"):
    """:func:`_resolve_endpoint` over a slice carrying synthesised tokens.

    Identical to the real path except that the remainder is rendered from the
    *original* tokens only -- a synthesised meridiem has no extent in the
    utterance and must never surface as leftover text.
    """
    folded = fold_tokens(tuple(sub), engine.spec, text)
    core = _resolve_core(folded, engine, anchor, scale_mode=scale_mode)
    if core is None:
        return None
    span, consumed = core
    left = [t for t in folded
            if t.index not in consumed and t.char_start is not None]
    return span, render_remainder(text, left)


def _numeral_is_free(text, sub, engine, anchor, pos):
    """Whether the numeral at ``pos`` is unclaimed by the slice's own reading.

    A numeral that the endpoint already spends on a date field is not
    available to be re-read as an hour.  Catalan "de 5 de juny a 12 de juny"
    is the case that matters: each endpoint holds exactly one numeral and no
    meridiem, so it *looks* like a bare hour, but the 5 is the day of June --
    re-reading it produced "1 June at 05:00", a silent-wrong that threw the
    day away.  In "from 9 to 5" (and in "5 on tuesday", where the reading is
    the weekday and the 5 is left over) the numeral is genuinely spare, so
    the hour reading stands.
    """
    folded = fold_tokens(tuple(sub), engine.spec, text)
    core = _resolve_core(folded, engine, anchor)
    if core is None:                # nothing read it at all -- it is free
        return True
    _, consumed = core
    numerals = [t for t in folded if t.is_number and t.value is not None]
    return not numerals or numerals[0].index not in consumed


def _clock_candidates(text, sub, engine, anchor, borrow=None):
    """Ordered clock readings of one endpoint slice.

    The literal reading first, then -- only for a slice whose hour is written
    bare -- the borrowed meridiem (the one the *other* endpoint spells out),
    then am, then pm.  Preference order is the whole point: the borrowed
    meridiem stays first, so "between 3 and 5 pm" keeps reading 15:00, and the
    am/pm fallbacks exist only for the pairings the borrow cannot satisfy.
    Readings a day or wider are not clocks and are dropped.
    """
    spec = engine.spec
    out = []
    got = _resolve_endpoint(text, sub, engine, anchor)
    if got is not None:
        out.append(got)
    pos = _bare_hour_pos(sub, spec)
    if pos is not None and _numeral_is_free(text, sub, engine, anchor, pos):
        am, pm = _meridiem_surfaces(spec)
        order = [s for s in (borrow, am, pm) if s is not None]
        seen = set()
        for surf in order:
            if surf in seen:
                continue
            seen.add(surf)
            v = _variant_endpoint(text, _with_meridiem(sub, pos, surf),
                                  engine, anchor)
            if v is not None:
                out.append(v)
    return [c for c in out if c[0].end - c[0].start < timedelta(days=1)]


def _rebase(span, day):
    """``span`` moved to the calendar day of ``day``, keeping its wall clock."""
    start = span.start.replace(year=day.year, month=day.month, day=day.day)
    return DateSpan(start, start + (span.end - span.start))


def _compose_clock_range(text, left_tok, right_tok, engine, anchor):
    """A clock range one of whose endpoints writes its hour bare, or ``None``.

    An explicit ``from``/``between`` lead says "these two are the ends of one
    interval", which licenses two readings a bare numeral never gets on its
    own: it is an **hour** ("from 9 to 5" is a working day, not "nine minutes
    to five"), and its meridiem is whichever one makes the pair a single
    coherent interval.

    The precedence rule: try the endpoint readings in preference order --
    literal first, then the meridiem borrowed from the other endpoint, then
    am, then pm -- and take the **first pairing that fits inside one day**.
    The dateless endpoint is placed on the other's day, so no reading is
    accepted at the price of a day roll.  "from 9 to 5 pm" therefore reads
    09:00-17:00 rather than borrowing the ``pm`` into a 20-hour span, while
    "between 3 and 5 pm" still borrows it, because there the borrow fits.

    Returns ``None`` -- deliberately, so the generic composition and then the
    plain single-span path (including the subtractive clock, which is correct
    English wherever no lead frames a range) get their turn -- whenever no
    pairing fits.  Fires only when an endpoint's hour is actually bare, so an
    explicit range ("from 9am to 5pm", "from 09:00 to 17:00") is untouched.
    """
    spec = engine.spec
    # a bare number governed by a trailing DURATION unit is a duration, not a
    # clock -- "6 to 8 hours" / "5 to 10 minutes" name an interval length, not
    # two times of day.  Reading them as hours fabricated a bogus clock span
    # ("cook for 6 to 8 hours" -> 07:54) and stranded the unit in the
    # remainder.  A unit anywhere in either endpoint slice vetoes the clock
    # reading, so the phrase falls through to ``None`` and defers to
    # :func:`extract_duration`.  A genuine clock range never carries a duration
    # unit ("6 to 8 pm", "from 9 to 5"), so this leaves every real range intact.
    units = set(spec.units) | set(spec.singular_units)
    if any(t.text in units for t in left_tok) \
            or any(t.text in units for t in right_tok):
        return None
    if _bare_hour_pos(left_tok, spec) is None \
            and _bare_hour_pos(right_tok, spec) is None:
        return None
    borrow = _trailing_meridiem(right_tok, spec)
    lefts = _clock_candidates(text, left_tok, engine, anchor,
                              borrow.text if borrow is not None else None)
    rights = _clock_candidates(text, right_tok, engine, anchor)
    if not lefts or not rights:
        return None
    # the endpoint with no day of its own is the one that moves; when both are
    # dateless the right joins the left, matching the generic composition's
    # left-anchored reading ("from 9am to 5pm" and "from 9 to 5" agree).
    move_left = _dateless_clock(left_tok, spec) \
        and not _dateless_clock(right_tok, spec)
    day = timedelta(days=1)
    for lspan, lrem in lefts:
        for rspan, rrem in rights:
            ls, rs = _align_awareness(lspan, rspan)
            ls, rs = (_rebase(ls, rs.start), rs) if move_left \
                else (ls, _rebase(rs, ls.start))
            if ls.start < rs.end <= ls.start + day:
                rem = " ".join(p for p in (lrem, rrem) if p).strip()
                return DateSpan(ls.start, rs.end), rem
    return None


def _lone_numeral(sub):
    """The single token of a slice that is nothing but one numeral, else None.

    Such an endpoint says a number and nothing else, so on its own it names no
    calendar field at all; it is the shape that has to look to its partner.
    """
    return sub[0] if len(sub) == 1 and sub[0].is_number \
        and sub[0].value is not None else None


def _bare_numeral(text, sub, engine, anchor):
    """The single numeral of a slice that names no date of its own, else None.

    The lone-numeral shape ("del 5 al 12 de junio", where "5" is nothing but a
    digit) is the clean case, but a bare range day is routinely written with a
    determiner in front -- Spanish "entre el 3 y el 10 de julio", English
    "between the 3rd and the 10th of july".  That slice holds exactly one
    numeral and still names no calendar field on its own (``el 3`` does not
    resolve), so it too must borrow its partner's month.  The article is not
    lent -- only the numeral goes into :func:`_shared_context` -- so it never
    reaches the remainder, and a slice that *does* resolve by itself (a real
    date, a bare weekday) is left to its own reading.
    """
    nums = [t for t in sub if t.is_number and t.value is not None]
    if len(nums) != 1:
        return None
    if len(sub) == 1:
        return nums[0]
    # a slice carrying a unit is a duration, not a bare day -- "za 3 dnya do 5
    # aprelya" ("3 days before April 5") is an anchored offset whose "za 3 dnya"
    # names three days, not the 3rd.  Such a slice must keep its own reading, so
    # it is never lent its partner's month.
    units = set(engine.spec.units) | set(engine.spec.singular_units)
    if any(t.text in units for t in sub):
        return None
    if _resolve_endpoint(text, sub, engine, anchor) is None:
        return nums[0]
    return None


def _shared_context(bare, donor):
    """``donor``'s slice with its numeral swapped for the ``bare`` endpoint's.

    Naming the month once for a pair of days is the *default* written form of
    a date range in the Romance languages -- "del 5 al 12 de junio" (RAE,
    Ortografia de la lengua espanola 5.2.5.1), "du 5 au 12 juin", "dal 5 al 12
    giugno" -- and English writes it too ("June 5 to 12").  The endpoint left
    holding only a bare day cannot be read on its own, so the pair used to
    lose it: the range collapsed onto the dated endpoint and returned a
    one-day span, or ran from the dated endpoint to the anchor instant.

    The repair is to read the bare endpoint through its partner's own words.
    The donor slice is rebuilt with its numeral replaced by the bare one, so
    "12 de junio" lends "5" everything except the day and "June 5" lends "12"
    the month that precedes it.  Word order and the language's own glue ("de",
    "di") come along unexamined, which is why this one rule serves every
    locale instead of forty spellings of the same special case.

    It fires only when the donor holds exactly one *day* numeral beside at
    least one other word.  One day numeral means there is no question which
    field the bare endpoint stands in for, and the other word is the context
    there would otherwise be nothing to borrow -- so two bare numerals ("from
    9 to 5") lend each other nothing and keep their existing clock reading.  A
    trailing year the donor carries ("12 June 2020") is *not* the field being
    swapped: it too belongs to both days, so it stays in place and is borrowed
    along with the month, lending the month AND year to the bare endpoint in
    one step (the day-range analogue of #323's month-range year-lending).  The
    lent tokens are synthesised without a character extent, because they belong
    to the *other* endpoint's stretch of the utterance and must never be billed
    to this one's remainder.
    """
    days = [i for i, t in enumerate(donor)
            if t.is_number and t.value is not None and t.value < 100]
    if len(days) != 1 or len(donor) < 2:
        return None
    # a word donor token (the month, its "de"/"of" glue) is re-synthesised from
    # its text so it re-folds cleanly; a *number* donor token -- the trailing
    # year kept in place -- is carried by :func:`replace` so its folded numeric
    # value survives (a fresh text-only Token would strip the year to nothing
    # and leave the borrower yearless).  Both lose their character extent: they
    # belong to the other endpoint and must never reach this one's remainder.
    return tuple(bare if i == days[0]
                 else replace(t, index=-1 - i, char_start=None, char_end=None)
                 if t.is_number
                 else Token(text=t.text, raw=t.raw, index=-1 - i)
                 for i, t in enumerate(donor))


def _endpoint_year(sub):
    """The slice's single year-magnitude numeral, else None.

    A number of at least three digits is the year token an endpoint carries
    (the same test :func:`_range_endpoint` uses for ``pinned``); a slice with
    exactly one names its own year and a slice with none looks to its partner
    for one.  Two such numbers (a numeric range "from 100 to 500") name no
    single year, so nothing is lent.
    """
    yrs = [t for t in sub
           if t.is_number and t.value is not None and t.value >= 100]
    return yrs[0] if len(yrs) == 1 else None


def _lend_year(bare, donor):
    """``bare``'s slice with the ``donor``'s trailing year appended.

    A range that names the year once for a pair of months -- "from January to
    March 2020", "de enero a marzo de 2020" -- is the ordinary written form,
    exactly as #236's shared month is ("del 5 al 12 de junio").  The endpoint
    left without a year would otherwise resolve in the anchor (or prefer-future)
    year, stranding the pair in two different years; the repair lends the
    donor's single year to the yearless endpoint so both read in it.  The lent
    token is synthesised without a character extent -- it belongs to the *other*
    endpoint's stretch of the utterance and must never reach this one's
    remainder -- and is appended after the yearless slice so the language's own
    "MONTH YEAR" order (and its "de"/"of" glue in the donor) reads it.  It fires
    only when the donor holds exactly one year and the borrower none, so a range
    whose endpoints each carry their own year ("from December 2019 to March
    2020") is left per-endpoint.
    """
    year = _endpoint_year(donor)
    if year is None:
        return None
    # keep the year's numeric value (so the "MONTH YEAR" order reads it) but
    # strip its character extent -- the token belongs to the other endpoint.
    lent = replace(year, index=-1 - len(bare), char_start=None, char_end=None)
    return tuple(bare) + (lent,)


def _compose_range(left_tok, right_tok, endpoint, borrowed, spec,
                   bare_of=_lone_numeral):
    """Resolve two endpoint sub-slices into one ``(span, remainder)``, or ``None``.

    A leading ``from``/``between`` and the connector are outside both slices, so
    they are dropped; each endpoint contributes its own leftover text.
    ``endpoint(sub)`` returns ``(span, remainder, kind, pinned)`` or ``None``.

    The span runs from the left endpoint's start to the right endpoint's end.
    When the right end lands at or before the start the endpoints sit in
    different cycles; this is reconciled by rolling **only** cyclic endpoints
    (a clock by its day, a bare weekday by its week) and, for a bare (unpinned)
    date whose prefer_future flung it a year ahead of a straddled anchor, by
    pulling the left endpoint back one year.  A pinned or dated endpoint is
    never rolled -- so a genuinely reversed range ("june 12 2020 to june 5
    2020") yields ``None`` rather than a fabricated span."""
    left = endpoint(left_tok)
    right = endpoint(right_tok)
    # one endpoint written as a bare number against a partner that names a
    # month is that month's day, and nothing else -- there is no second
    # reading of "del 5 al 12 de junio" in which the 5 is not the fifth of
    # June.  So the borrowed reading is preferred over whatever the lone
    # numeral resolved to by itself (a day of the *current* month, an hour),
    # which is where the endpoint was previously being thrown away.  See
    # :func:`_shared_context` for the conditions that keep it narrow.
    bare_left, bare_right = bare_of(left_tok), bare_of(right_tok)
    shared_left = shared_right = False
    if bare_left is not None and bare_right is None:
        shared = _shared_context(bare_left, right_tok)
        if shared is not None:
            left = borrowed(shared) or left
            shared_left = True
    elif bare_right is not None and bare_left is None:
        shared = _shared_context(bare_right, left_tok)
        if shared is not None:
            right = borrowed(shared) or right
            shared_right = True
    # a single trailing year is lent to the endpoint that lacks one, so "from
    # January to March 2020" reads both months in 2020 (see :func:`_lend_year`);
    # a range whose endpoints each name their own year is left per-endpoint.  It
    # is lent only to an endpoint that *already* names a dated span of its own
    # (a month/date placed in the anchor year), never to one that fails to
    # resolve -- lending a year to a non-date word ("... to Cairo") would let
    # the lone year resolve as a whole-year reference and fabricate a range.
    # a bare endpoint that borrowed its partner's month through
    # :func:`_shared_context` already carried that partner's trailing year
    # along with the month (the shared "12 June 2020" lends both to the "5"),
    # so it must not be year-lent a second time from its own bare numeral --
    # that would rebuild "5 2020" and clobber the shared reading.
    left_year, right_year = _endpoint_year(left_tok), _endpoint_year(right_tok)
    left_lent = right_lent = False
    if right_year is not None and left_year is None \
            and left is not None and left[2] == "dated" and not shared_left:
        lent = _lend_year(left_tok, right_tok)
        if lent is not None:
            new_left = borrowed(lent)
            if new_left is not None:
                left, left_lent = new_left, True
    elif left_year is not None and right_year is None \
            and right is not None and right[2] == "dated" and not shared_right:
        lent = _lend_year(right_tok, left_tok)
        if lent is not None:
            new_right = borrowed(lent)
            if new_right is not None:
                right, right_lent = new_right, True
    # a bare left endpoint ("3" in "between 3 and 5 pm") borrows the right
    # endpoint's trailing meridiem so both read on the same clock
    if left is None and right is not None and left_tok:
        merid = _trailing_meridiem(right_tok, spec)
        if merid is not None:
            left = endpoint(tuple(left_tok) + (merid,))
    if left is None or right is None:
        return None
    # one interval is read on one clock: a zone named on a single endpoint
    # governs both, so the two ends stay comparable (see _align_awareness).
    left_span, right_span = _align_awareness(left[0], right[0])
    # A date on the RIGHT endpoint ("9am to 5pm ON MONDAY") scopes the whole
    # pair -- the mirror of "MONDAY 9am to 5pm" (date on the left, already
    # handled by the roll-into-the-left's-cycle below).  A "5pm on monday"
    # endpoint resolves to a sub-day span, so it is classified "clock" and its
    # Monday would otherwise be ignored while the bare LEFT clock ("9am") landed
    # on the anchor's own day, fabricating a multi-day span.  When the right
    # carries a weekday/month and the left is a bare dateless clock, place the
    # left clock on the right's day.
    right_dated = any(t.text in spec.weekdays for t in right_tok) \
        or any(t.text in spec.months for t in right_tok)
    left_bare_clock = left[2] == "clock" \
        and not any(t.text in spec.weekdays for t in left_tok) \
        and not any(t.text in spec.months for t in left_tok)
    if right_dated and left_bare_clock:
        rs, ls = right_span.start, left_span.start
        start = AstroDate(rs.year, rs.month, rs.day, ls.hour, ls.minute,
                          ls.second, ls.microsecond)
    else:
        start = left_span.start
    # roll a cyclic right endpoint forward into the same cycle as the start; a
    # dated endpoint already carries its year, so it is left untouched.  The
    # roll is arithmetic (see _roll_after): the cycle count is chosen by the
    # utterance's year, so stepping it made a far-future range a hang.
    end = right_span.end
    if right[2] == "clock":
        end = _roll_after(right_span, start, timedelta(days=1)).end
    elif right[2] == "weekday":
        end = _roll_after(right_span, start, timedelta(days=7)).end
    # prefer-future asymmetry: a straddling range resolves its left endpoint a
    # whole year ahead (prefer_future) while the right stays put, inverting the
    # span.  Pull an unpinned left back one year so both read in the nearest
    # cycle ("july 20 to july 25" on july 22 stays this year).  A pinned left
    # (explicit year) is fixed and must not be pulled.
    if end <= start and not left[3] \
            and start.year != right_span.start.year:
        # The straddle repair only applies when the two endpoints landed in
        # DIFFERENT cycles: prefer_future flung the left a year ahead of a right
        # that stayed near the anchor ("july 20 to july 25" on july 22 -> left
        # 2018, right 2017), so pulling the left back unifies them in the near
        # cycle.  When BOTH endpoints were flung to the SAME future year and the
        # range is still reversed there ("june 12 to june 5" -- both 2018, 12 >
        # 5), it is a genuine reversal, not a straddle; pulling only the left
        # back a year would fabricate a bogus ~year-wide span, so leave it to
        # fail below (None -> the single-span fallback reads the left date).
        pulled = _minus_one_year(start)
        if pulled is not None and pulled < right_span.end:
            start, end = pulled, right_span.end
    # a year lent across the range (one endpoint named the pair's single year)
    # reads the borrowed month in the donor's own year, which reverses the span
    # when the two months sit on opposite sides of the calendar -- "from
    # december 2020 to march" reads march in 2020, before december.  Roll the
    # LENT endpoint into the adjacent year so the pair reads forward: the right
    # borrower one year on ("to march 2021"), the left borrower one year back
    # ("from december 2020 ...").  The donor keeps its explicit year, and a
    # non-reversing lend (january 2020 to march) never reaches here.
    if end <= start and right_lent:
        rolled = _plus_one_year(end)
        if rolled is not None and rolled > start:
            end = rolled
    elif end <= start and left_lent:
        pulled = _minus_one_year(start)
        if pulled is not None and pulled < end:
            start = pulled
    if end <= start and "deep_time" in (left[2], right[2]):
        # a reversed range that involves a DEEP-TIME endpoint ("from the
        # neolithic to the oligocene") is not a civil ordering error -- deep
        # time is acyclic, with no year-wraparound -- so it names the interval
        # spanning both endpoints, exactly as the forward "from the oligocene to
        # the neolithic" already does.  Swap to [older start, younger end].  A
        # civil reversed range ("june 12 to june 5") has no deep-time endpoint
        # and is left to fail below.
        start, end = right_span.start, left_span.end
    if end <= start:
        return None
    remainder = " ".join(p for p in (left[1], right[1]) if p).strip()
    return DateSpan(start, end), remainder


def _minus_one_year(astro):
    """The same day one calendar year earlier, or ``None`` when that day does
    not exist (Feb 29) or falls out of the representable range."""
    try:
        return astro.replace(year=astro.year - 1)
    except (ValueError, OverflowError):
        return None


def _plus_one_year(astro):
    """The same day one calendar year later, or ``None`` when that day does not
    exist (Feb 29) or falls out of the representable range."""
    try:
        return astro.replace(year=astro.year + 1)
    except (ValueError, OverflowError):
        return None


def _resolve_endpoint(text, sub, engine, anchor, scale_mode="short"):
    """Resolve a range endpoint from a slice of the *pre-fold* token stream.

    The slice is folded on its own (its numbers fold in isolation, so a range's
    two numeric endpoints never merge) and matched exactly as a whole utterance
    is -- no substring is ever re-tokenized.  Returns ``(span, remainder)`` where
    ``remainder`` is this endpoint's own leftover text (sliced from ``text`` by
    the unconsumed tokens' recorded extents), or ``None``.
    """
    if not sub:
        return None
    folded = fold_tokens(tuple(sub), engine.spec, text)
    core = _resolve_core(folded, engine, anchor, scale_mode=scale_mode)
    if core is None:
        return None
    span, consumed = core
    remainder = render_remainder(text, [t for t in folded
                                        if t.index not in consumed])
    return span, remainder


def _since_start(ep, sub, engine, anchor, now):
    """The start instant of a "since <endpoint>" span, or ``None``.

    "since X" is PAST-anchored: it names the most recent occurrence of X
    at-or-before now.  A bare weekday recurs WEEKLY, so resolve it backward
    directly (0..6 days back).  A DEFINITE endpoint -- a qualified weekday
    ("this/next friday"), a now-relative day word ("tomorrow", "today"), or an
    explicit year ("2019") -- names one fixed point: in the past it opens the
    span directly, in the FUTURE it is contradictory and returns ``None``
    (never pulled back into a point the user never named).  Only an
    underspecified endpoint whose prefer_future guessed the wrong cycle forward
    (bare "july 6", "christmas", "q3", a bare clock time) is rolled back by its
    OWN cycle -- a year for a date/quarter, a DAY for a time-of-day -- until it
    lands at-or-before now.
    """
    spec = engine.spec
    wk = _bare_weekday_endpoint(sub, engine, anchor, backward=True)
    if wk is not None:
        return wk[0].start
    if ep is None:
        return None
    start = ep[0].start
    if (any(t.text in spec.named_days for t in sub)
            or any(t.text in spec.rel_markers for t in sub)
            or any(t.text in spec.directions for t in sub)
            or any(t.is_number and t.value is not None and t.value >= 100
                   for t in sub)):
        # A DEFINITE endpoint: a now-relative day ("tomorrow"), a
        # direction/rel-qualified reference ("next month", "this friday") or an
        # explicit year ("2019").  A QUALIFIED weekday lands here too, via its
        # own direction/rel token.  None of these is an underspecified reference
        # prefer_future flung forward, so never roll it: in the past it opens
        # the span, in the future "since" it is contradictory and is refused.
        return start if start <= now else None
    if any(t.text in spec.weekdays for t in sub):
        # An UNqualified weekday (the bare-weekday-alone case is handled by
        # _bare_weekday_endpoint above; this is a weekday carrying a clock, e.g.
        # "monday 3pm").  It recurs WEEKLY, so roll the whole endpoint --
        # weekday and time-of-day together -- back one week at a time until it
        # lands at-or-before now.  Rolling by a DAY (the clock branch below)
        # would strand it on the wrong weekday.
        while start > now:
            start = start + timedelta(days=-7)
        return start
    # An underspecified recurring reference.  Roll back by its OWN cycle: a bare
    # time-of-day (a sub-day-wide span with no calendar-date word) recurs DAILY,
    # so "since noon" at 9am is yesterday noon -- NOT a year ago; everything else
    # (a bare month/day, a holiday, a quarter) is a yearly anniversary.
    is_clock = (ep[0].end - ep[0].start < timedelta(days=1)
                and not any(t.text in spec.months for t in sub))
    while start > now:
        pulled = (start + timedelta(days=-1) if is_clock
                  else _minus_one_year(start))
        if pulled is None:
            break
        start = pulled
    return start


def _extract_directional_range(text, tokens, engine, anchor, scale_mode="short"):
    """A range whose start marker is "since" and whose end marker is "until":
    "since monday until friday".

    Distinct from a plain closed "from A to B", where both endpoints roll
    FORWARD: here "since" past-anchors the START (its most recent past
    occurrence) while "until" future-anchors the END, so "since monday until
    friday" reads ``[last monday, next friday]`` rather than ``[next monday,
    next friday]``.  Fires only on a LEADING "since" marker with a following
    terminator, so bare "since X" (no terminator -> open since) and "from A to
    B" (no leading since) are both untouched.
    """
    spec = engine.spec
    # opt-in per locale: only languages whose "since" is genuinely past-anchored
    # AND distinct from a forward "from" read "since A until B" directionally.
    # Languages that spell from/since with one forward word (Persian «از»,
    # Mirandese "zde", Romance "desde"/"de") keep the plain closed-range reading.
    if not spec.conventions.since_directional:
        return None
    n = len(tokens)
    if n < 3:
        return None
    now = AstroDate.from_datetime(anchor)
    since_surf = _conn_surfaces(spec, "since", _RANGE_SINCE)
    k = _match_conn_at(tokens, 0, since_surf)
    if not k:
        return None
    to_surf = _conn_surfaces(
        spec, "to", _RANGE_TO + tuple(spec.connectors.get("until", ())))
    split = _first_to_split(tokens, k, to_surf, text)
    if split is None:
        return None
    p, m = split
    left_tok, right_tok = tokens[k:p], tokens[p + m:]
    if not left_tok or not right_tok:
        return None

    def endpoint(sub, at):
        # the "now" and "new year" special surfaces resolve only in
        # _range_endpoint (the closed/open-range paths); wire them here too so a
        # directional "since christmas until new year" / "... until now" keeps
        # its backward "since" reading and binds the trailing endpoint, instead
        # of failing to resolve the right side and silently downgrading to a
        # plain forward range with "since" dropped.  "now" is always the anchor
        # instant; "new year" is the first Jan 1 at or after `at`.
        if _is_now_slice(sub, engine.spec):
            return _now_span(anchor), ""
        if _is_new_year_slice(sub, engine.spec):
            return _new_year_span(at), ""
        return (_resolve_endpoint(text, sub, engine, at, scale_mode=scale_mode)
                or _bare_weekday_endpoint(sub, engine, at))

    left_ep = endpoint(left_tok, anchor)
    start = _since_start(left_ep, left_tok, engine, anchor, now)
    if start is None:
        return None
    start_dt = start.datetime()
    if start_dt is None:
        return None
    # Resolve the "until" end relative to the past-anchored START, not to now:
    # the first occurrence of the right endpoint at-or-after start.  This is
    # what keeps "since june 5 until june 12" a recent-past week rather than
    # letting "until june 12" roll a year forward on its own, and it is correct
    # for every endpoint kind (a weekday lands within the week, a dated
    # anniversary within the year).
    right_ep = endpoint(right_tok, start_dt)
    if right_ep is None:
        return None
    end = right_ep[0].end
    if start >= end:
        return None
    remainder = " ".join(r for r in ((left_ep[1] if left_ep else ""),
                                     right_ep[1]) if r).strip()
    return DateSpan(start, end), remainder


def _extract_open_range(text, tokens, engine, anchor, scale_mode="short"):
    """An open-ended range: "until friday" (open start) / "since 2019" (open
    end).  Only fires on an ``until``/``since`` marker whose remaining tokens
    parse as a date endpoint.

    The known endpoint keeps the closed-range endpoint convention -- an
    ``until`` endpoint contributes its ``.end`` (it is included in full, as the
    right endpoint of "from A to B" is), a ``since`` endpoint its ``.start`` --
    and the open side is pinned to the anchor instant ("now").  So "until
    friday" is ``[now, friday_end)`` and "since 2019" is ``[2019-01-01, now)``.
    The marker is found on the token stream, leading or postposed.
    """
    spec = engine.spec
    n = len(tokens)
    if n < 1:
        return None
    now = AstroDate.from_datetime(anchor)
    until_surf = _conn_surfaces(spec, "until", _RANGE_UNTIL)
    since_surf = _conn_surfaces(spec, "since", _RANGE_SINCE)

    def endpoint(sub):
        return (_resolve_endpoint(text, sub, engine, anchor, scale_mode=scale_mode)
                or _bare_weekday_endpoint(sub, engine, anchor))

    def until_span(ep, sub):
        return DateSpan(now, ep[0].end) if ep is not None and ep[0].end > now \
            else None

    def since_span(ep, sub):
        start = _since_start(ep, sub, engine, anchor, now)
        return DateSpan(start, now) if start is not None and start < now \
            else None

    def lead(surf, build):
        # the marker leads; its tokens are dropped, the endpoint keeps its own
        # leftover (the framing word is never part of the remainder)
        k = _match_conn_at(tokens, 0, surf)
        if not k:
            return None
        ep = endpoint(tokens[k:])
        span = build(ep, tokens[k:]) if ep is not None else None
        return (span, ep[1]) if span is not None else None

    def trail(surf, build):
        # a **postposed** marker -- the bound word trailing its date, the
        # native order for Finnish ("perjantaihin asti"), Turkish
        # ("cumaya kadar"), Basque ("ostirala arte"), Azerbaijani
        # ("cüməyə qədər").
        for words in surf:
            m = len(words)
            if m and m < n and [t.text for t in tokens[n - m:]] == words:
                ep = endpoint(tokens[:n - m])
                span = build(ep, tokens[:n - m]) if ep is not None else None
                if span is not None:
                    return span, ep[1]
        return None

    def affix(surf, build):
        # an **affix** marker -- a bound suffix fused onto the date's final
        # surface token (Hungarian "-ig": "péntekig" = "péntek" + "ig",
        # "2026-ig").  Split a known affix off the last token and re-resolve the
        # stripped host as the endpoint; accept ONLY when the host without the
        # affix parses as a date, so a random word ending in the same letters
        # ("nadrágig" = "trousers-until") never misfires.  Single-word affix
        # surfaces only (a suffix is one morpheme).
        last = tokens[-1]
        host_text = last.text
        for words in surf:
            if len(words) != 1:
                continue
            a = words[0]
            if len(a) < len(host_text) and host_text.endswith(a):
                stripped = last.__class__(
                    text=host_text[:-len(a)], raw=host_text[:-len(a)],
                    index=last.index, is_number=last.is_number,
                    value=last.value,
                    char_start=last.char_start,
                    char_end=(last.char_end - len(a)
                              if last.char_end is not None else None))
                sub_a = tuple(tokens[:-1]) + (stripped,)
                ep = endpoint(sub_a)
                span = build(ep, sub_a) if ep is not None else None
                if span is not None:
                    return span, ep[1]
        return None

    positions = spec.positions

    def scan(role, surf, build):
        # positionality drives which readings are attempted: a ``pre`` (default)
        # marker leads; ``post`` trails; ``affix`` is a fused suffix.  ``pre``
        # and ``post`` both keep the historical lead+trail fallback (behaviour-
        # identical for every already-supported locale); ``affix`` adds the
        # newly-unlocked fused-suffix reading on top.
        pos = positions.get(role, "pre")
        return (lead(surf, build) or trail(surf, build)
                or (affix(surf, build) if pos == "affix" else None))

    return (scan("until", until_surf, until_span)
            or scan("since", since_surf, since_span))


def _bare_weekday_endpoint(sub, engine, anchor, backward=False):
    """A lone weekday ("monday") as a range endpoint only: a day-wide span for
    the next occurrence on or after the anchor day, or -- with ``backward`` --
    the most recent occurrence at or before it.  A bare weekday never parses on
    its own (too ambiguous); it is only trusted inside a range, where the framing
    supplies the intent.  Reads a *token slice*.

    ``backward`` matters for "since <weekday>": a weekday recurs WEEKLY, so the
    most recent past occurrence is 0..6 days back -- resolving it directly avoids
    the yearly pull-back flinging it ~a year into the past."""
    if len(sub) != 1 or sub[0].text not in engine.spec.weekdays:
        return None
    target = engine.spec.weekdays[sub[0].text]
    if backward:
        delta = -((anchor.weekday() - target) % 7)   # most recent, on-or-before
    else:
        delta = (target - anchor.weekday()) % 7       # next, on-or-after
    day = (anchor.replace(hour=0, minute=0, second=0, microsecond=0)
           + timedelta(days=delta))
    start = AstroDate.from_datetime(day)
    return DateSpan(start, start + timedelta(days=1)), ""


def _trailing_meridiem(sub, spec):
    """The am/pm token ending a slice, or None -- for propagating a shared
    meridiem onto a bare range endpoint."""
    if sub and sub[-1].text in spec.meridiems:
        return sub[-1]
    return None


def _week_span(start_astro, week_start_name: str) -> DateSpan:
    """The locale-aligned seven-day week containing ``start_astro``.

    ``week_start_name`` is the locale ``week_start`` convention (Monday for the
    languages carrying the "week of" marker); the span begins on that weekday
    on-or-before the given date and is a fixed seven days wide, so its width
    reads WEEK.
    """
    idx = _WEEK_START.get(week_start_name, 0)
    d = datetime(start_astro.year, start_astro.month, start_astro.day)
    back = (d.weekday() - idx) % 7
    week_start = d - timedelta(days=back)
    s = AstroDate.from_datetime(week_start)
    return DateSpan(s, s + timedelta(days=7))


def _apply_week_of(tokens, resolved, spec):
    """Widen a date immediately preceded by the "week of" marker to its week.

    "the week of july 20" is resolved by the normal matcher as the inner date
    (july 20); this pass then finds the locale's ``weekof`` marker stranded
    right before that date -- claimed by no stronger construction -- and
    replaces the day span with the calendar week (locale ``week_start``) that
    contains it.  The marker is a per-locale fact (``marker_weekof.voc``); the
    widening is generic (it wraps *any* date the engine already resolves).

    It fires only when the marker tokens are consumed by no other match (so
    "the first week of june", a scoped ordinal, is left untouched) and are not
    preceded by a number (a defensive guard against a stranded ordinal such as
    "the 2nd week of ...").
    """
    surfaces = spec.connectors.get("weekof")
    if not surfaces:
        return resolved
    covered = set()
    for m, _ in resolved:
        covered.update(range(*m.span))
    phrases = sorted((s.split() for s in surfaces), key=len, reverse=True)
    out = []
    for m, res in resolved:
        widened = None
        if m.construction in DATE_CONSTRUCTIONS:
            begin = m.span[0]
            for words in phrases:
                j = begin - len(words)
                if j < 0 or (j - 1 >= 0 and tokens[j - 1].is_number):
                    continue
                if any(k in covered for k in range(j, begin)):
                    continue
                if [t.text for t in tokens[j:begin]] == words:
                    week = _week_span(res.value.start,
                                      spec.conventions.week_start)
                    consumed = tuple(sorted(set(res.consumed)
                                            | set(range(j, begin))))
                    widened = (m, Resolution(week, consumed,
                                             week_widened=True))
                    covered.update(range(j, begin))
                    break
        out.append(widened or (m, res))
    return out


def extract_timespan(
        text: str,
        lang: str = "en-us",
        anchor: Optional[datetime] = None,
        jurisdiction: Optional[str] = None,
        enable: Tuple[str, ...] = (),
        scale: Optional[str] = None,
) -> Optional[DateSpanResult]:
    """Extract a :class:`~chronologia.DateSpan` from natural-language ``text``.

    Returns the referential *width* of a date phrase: unlike a parser that
    collapses a reference to its left edge, this returns the whole stretch
    of time referred to ("june 2027" is a month-wide span, "3 pm" a
    minute-wide one).  ``DateSpan.start_datetime`` / ``end_datetime`` yield
    real ``datetime`` (or ``None`` when out of range).

    ``anchor`` is the "now" relative phrases resolve against (default: the
    wall clock).  Only languages with locale data are supported; others
    raise :class:`NotImplementedError`.

    **Time zones.** Resolution is *wall-clock*: the anchor is read as a local
    civil time and the returned :class:`~chronologia.DateSpan` is naive.  A
    tz-aware ``anchor`` has its ``tzinfo`` dropped (its wall-clock fields are
    used as-is), so "tomorrow at 3pm" is 15:00 on the anchor's clock regardless
    of zone, and a relative offset ("in 20 hours") is wall-clock arithmetic that
    does **not** apply DST transitions.  Localize the naive result yourself if
    you need an absolute instant.

    Returns a :class:`DateSpanResult` -- a ``(span, remainder)`` named tuple
    (unpack it, or read ``.span`` / ``.remainder``) -- or ``None`` when nothing
    matched.

    ``jurisdiction`` (an ISO country code such as ``'PT'``) scopes the
    business-day constructions ("in 5 business days", "the next working day"):
    a business day is a non-weekend weekday that is also not a public holiday of
    that jurisdiction.  With ``jurisdiction=None`` the count is *holiday-blind*
    -- weekend-aware but treating every weekday as a business day -- because
    which weekdays are public holidays cannot be known without a jurisdiction.

    A "from A to B" / "between A and B" range yields the span from the start
    of the left sub-parse to the end of the right one (``june 5th to june
    12th`` -> a seven-day span); the endpoints are two independent parses.

    ``scale`` selects the short/long scale that disambiguates a deep-time
    "billion"-cognate ("a billion years ago" is 10^9 short, 10^12 long):
    ``"short"`` or ``"long"`` hard-override, ``None`` (default) takes the
    dialect norm keyed off ``lang`` -- a full BCP-47 region subtag picks the
    dialect (``pt-BR`` short, ``pt-PT`` long) while loading the same base
    locale, a bare code its naming country's norm.

    ``text`` must be a ``str``; anything else raises :class:`TypeError`.
    Text that names nothing temporal, the empty string included, returns
    ``None``.
    """
    require_text(text, "extract_timespan")
    engine = _timespan_engine(lang)
    scale_mode = _resolve_scale_mode(lang, scale)
    anchor = anchor or datetime.now()
    if isinstance(anchor, datetime):
        anchor = anchor.replace(tzinfo=None)
    # tokenize ONCE: the tokenizer regex runs a single time and the resulting
    # stream is the shared currency.  Range/open-range detection reads the
    # *pre-fold* stream (connectors still visible); folding the whole stream for
    # the single-span core, or a lone endpoint's slice, re-uses these tokens --
    # the tokenizer is never run again on a substring.
    raw = pretokens(text, engine.spec)
    res = _resolve_span(text, raw, engine, anchor, enable, jurisdiction,
                        scale_mode)
    return None if res is None else DateSpanResult(*res)


# A temporal reference GOVERNED BY a negation/exclusion particle ("not
# tomorrow", "any day but Friday", "except Sundays") is NOT a positive date:
# resolving it positively hands back the exact day the user told us to avoid --
# an inverted, hazardous result a scheduler would act on.  Per the residue-veto
# design (docs/design/errors-by-construction.md, #244: "no fabricated date...
# return None, never a wrong span") such a reference is refused (-> None).
#
# The trigger is a negation/exclusion word that GOVERNS the reference: it must
# sit in the CONTIGUOUS run of unconsumed tokens IMMEDIATELY before the span,
# reachable across only the function/scope words the exclusion idiom naturally
# skips (the trigger itself, a bound guard, a scope/quantifier word, a
# connector/article, or a copula filler).  The run STOPS at the first content
# word ("no wait, Tuesday" -> "wait" blocks) or a sentence-ending punctuation
# ("No cats allowed. See you Tuesday." -> the "." blocks), so a trigger lying in
# a different clause or sentence never reaches the reference.  A BOUND phrase
# ("not before Monday", "no later than Friday", "not until Tuesday") is a
# legitimately resolvable constraint, NOT an exclusion: a bound preposition in
# the run vetoes the veto, leaving those phrases byte-identical.  English trigger
# vocab only for now.
def _exclusion_vetoes(governing_text: str, spec) -> bool:
    """True when a negation/exclusion particle governs the reference to its right
    (the given residue carries a trigger and no bound preposition).

    ``governing_text`` must ALREADY be bounded to the residue immediately before
    the matched reference (the ``nseries`` list path passes the gap between two
    adjacent mentions).  A bound preposition (``spec.exclusion_bound_guards``)
    anywhere in it means the phrase is a bound ("before friday"), not an
    exclusion.  The single-span and candidate paths use
    :func:`_exclusion_governing_veto` instead, which derives the bounded region
    from the token stream rather than trusting the caller to slice it.
    """
    triggers = spec.exclusion_triggers
    if not triggers:
        return False
    words = re.findall(r"[^\W\d_]+", governing_text.lower(), re.UNICODE)
    if not words:
        return False
    if any(w in spec.exclusion_bound_guards for w in words):
        return False
    return any(w in triggers for w in words)


def _sentence_boundary_between(text, start, end) -> bool:
    """True when a sentence-ending punctuation (``.!?;`` or a newline) sits in
    the raw gap ``text[start:end]`` separating two adjacent tokens."""
    if start is None or end is None or end <= start:
        return False
    return any(c in ".!?;\n" for c in text[start:end])


def _exclusion_governing_veto(tokens, consumed, text, spec) -> bool:
    """True when a negation/exclusion particle GOVERNS the winning reference and
    the phrase is not a resolvable bound.

    The governing region is the maximal run of unconsumed tokens IMMEDIATELY
    before the span (leftmost consumed token) in which every token is skippable
    -- a trigger, a bound guard, a scope/quantifier word, a connector/article, or
    a copula filler.  The walk stops at the first content word or a sentence
    boundary, so a trigger in another clause or sentence does not reach the date.

    A bound preposition anywhere in the run (``spec.exclusion_bound_guards``)
    marks a resolvable bound ("no later than Friday") -> no veto.  A hard trigger
    (a negation or a prepositional exclusion: not/no/except/unless/than and the
    per-locale equivalents) vetoes whenever it governs.  A coordinating trigger
    (``spec.exclusion_coord``, English "but") vetoes only when the run also
    carries a scope word ("every day but Tuesday" -> exclude Tuesday); standing
    alone it is a clause conjunction ("... but Tuesday is free") or a discourse
    opener ("But Tuesday works") and vetoes nothing.

    Vocabularies are per-locale data; a locale that declares no triggers makes
    the guard a no-op there rather than silently applying English particles.
    """
    triggers = spec.exclusion_triggers
    if not triggers or not consumed:
        return False
    span_start = min(consumed)
    skippable = set(triggers) | set(spec.exclusion_bound_guards) \
        | set(spec.exclusion_scope) | set(spec.exclusion_coord) \
        | set(spec.exclusion_filler)
    for forms in spec.connectors.values():
        skippable |= set(forms)
    run = []
    next_start = tokens[span_start].char_start if span_start < len(tokens) else None
    i = span_start - 1
    while i >= 0:
        tok = tokens[i]
        if tok.index in consumed:
            i -= 1
            continue
        if _sentence_boundary_between(text, tok.char_end, next_start):
            break
        w = tok.text.lower()
        if w not in skippable:
            break
        run.append(w)
        next_start = tok.char_start
        i -= 1
    if not run:
        return False
    words = set(run)
    if words & set(spec.exclusion_bound_guards):
        return False
    hard = set(triggers) - set(spec.exclusion_coord)
    if words & hard:
        return True
    if (words & set(spec.exclusion_coord)) and (words & set(spec.exclusion_scope)):
        return True
    return False


_veto_reentry = threading.local()


def _impossible_date_veto(tokens, consumed, text, engine, anchor):
    """Whether the winning reading strands an IMPOSSIBLE day-of-month numeral --
    proof the parse is incomplete and must be refused (residue-veto design,
    #244) rather than surfaced as a fabricated broader span with the day dropped.

    Two shapes trigger:
      * an unconsumed numeral immediately followed by an unconsumed "of"
        connector, where either the "of" abuts the winning span or the
        "<number> of ..." fragment does not itself resolve to a valid date
        ("the 32nd of February 2017", "the 29th of February" in a non-leap year);
      * the connector-less "<number> <month>" order (Italian "32 aprile",
        German "32. April", Russian "32 апреля"): a bare numeral > 31 that abuts
        the winning span and does not itself name a valid date.
    A stranded but VALID date (a second mention, "... al 5 de junio de 2020")
    resolves on its own and does not veto.  Shared by _resolve_span (the
    single-winner path) and extract_candidates so the two public APIs never
    disagree on the top answer.
    A thread-local re-entrancy guard bounds the self-similar blow-up: both
    trigger shapes re-parse a stranded fragment through the public
    ``extract_timespan`` ("does this resolve to a real date?"), which re-enters
    this veto; a self-similar input ("5th of june 5th of june ...") would
    otherwise recurse ``2**n`` times.  The inner fragment only needs to know
    whether it RESOLVES, not whether it is itself impossible, so the veto is
    skipped while already inside it (one level is enough).
    """
    if getattr(_veto_reentry, "active", False):
        return False
    _veto_reentry.active = True
    try:
        return _impossible_date_veto_inner(tokens, consumed, text, engine, anchor)
    finally:
        _veto_reentry.active = False


def _ordish_scope_word(text, spec):
    """Whether ``text`` is a scope/unit noun the "Nth <unit> of <scope>"
    construction selects ("week", "weekend", "month", "quarter", a weekday
    name, ...) -- used only to recognise a stranded "<ordinal> <unit> of"
    prefix immediately before an unrelated winning reading, below.

    Deliberately excludes plural surfaces ("weeks", "quarters", "weekends"):
    a plural names a COUNT, not a scoped ordinal (``_resolve_scoped_ordinal``
    refuses a plural selected unit the same way), so "3 weeks of vacation in
    July" must not be mistaken for a stranded ordinal-scope attempt.
    """
    if text in spec.plural_units or text in ("weekends", "quarters"):
        return False
    return (text in spec.units or text in spec.scope_units
            or text in spec.weekend_words
            or text in spec.connectors.get("quarter_word", frozenset())
            or text in spec.weekdays)


def _impossible_date_veto_inner(tokens, consumed, text, engine, anchor):
    of_surfaces = set(engine.spec.connectors.get("of", ()))
    # Match-start positions of every construction the matcher recognises
    # anywhere in the stream (not just the tokens the WINNING reading
    # consumed): a scoped-ordinal attempt whose ordinal never bound (0,
    # negative -- the ORD slot requires >=1) leaves its "of <scope>" tail to
    # be read as an unrelated, independently-resolving reference ("weekend"
    # alone, ignoring "of june"); composition then picks whichever of the two
    # readings sits earliest in the text, silently discarding the other
    # (here "june") rather than the stranded numeral it was actually scoping.
    # A numeral+unit+"of" run immediately followed by ANY recognised
    # reference start -- whether or not that reference is the eventual
    # composition winner -- is the same honest-refusal shape as "abuts
    # winner" below, just one composition layer further out.
    veto_cb = lambda m: _candidate_veto(tokens, m, engine.spec)  # noqa: E731
    match_starts = {m.span[0] for m in engine.matcher.match(tokens, veto_cb)}
    for i in range(len(tokens) - 1):
        if not (tokens[i].index not in consumed and tokens[i].is_number):
            continue
        j = i + 1
        skipped_unit = False
        # an ordinal-scope construction ("the 0th WEEK of may", "the 13th
        # QUARTER of 2026") names one unit/scope noun between the numeral and
        # the "of" connector; skip a single such word (consumed or not -- it
        # may have been separately swallowed by an unrelated shorter match,
        # e.g. a bare "weekend" reading) so this reaches the connector the
        # same way the plain "<number> of ..." shape below does. An ordinal
        # that never bound at all (0, negative -- the ORD slot requires
        # >=1) never becomes a scoped_ordinal candidate in the first place,
        # so this is the only way such a stranding is ever detected.
        if j < len(tokens) and _ordish_scope_word(tokens[j].text, engine.spec):
            j += 1
            skipped_unit = True
        if not (j < len(tokens) and tokens[j].index not in consumed
                and tokens[j].text in of_surfaces):
            continue
        if j + 1 < len(tokens) and (tokens[j + 1].index in consumed
                                    or tokens[j + 1].index in match_starts):
            return True                              # qualifier abuts winner
        if skipped_unit:
            # Shape 2 below (a stranded fragment that does not itself resolve
            # to a date) is NOT extended to the unit-skipping case: the
            # fragment scan below stops at the next CONSUMED token anywhere
            # later in the sentence, which -- once a unit word may sit
            # between the numeral and "of" -- can run across unrelated
            # clauses ("the first week of school starts in September") and
            # false-refuse a sentence that has nothing to do with a scoped
            # ordinal. Only the direct-abutment check above applies here.
            continue
        cs = tokens[i].char_start
        ce = None
        for t in tokens[i:]:
            if t.index in consumed or t.char_start is None:
                break
            ce = t.char_end
        if cs is not None and ce is not None:
            frag = text[cs:ce]
            if extract_timespan(frag, engine.spec.lang, anchor) is None:
                return True                          # impossible stranded date
    for i, t in enumerate(tokens):
        if t.index in consumed or not t.is_number or t.value is None \
                or t.value != int(t.value) or t.value <= 31:
            continue
        # a number immediately followed by a unit word ("48 hours", "90
        # seconds") is a duration/count, not an attempted day-of-month --
        # its own trailing unit disambiguates it, so it never reaches the
        # "does this look like an impossible date" fallback below.
        if (i + 1 < len(tokens) and tokens[i + 1].index not in consumed
                and tokens[i + 1].text in (set(engine.spec.units)
                                           | set(engine.spec.singular_units))):
            continue
        abuts = ((i > 0 and tokens[i - 1].index in consumed)
                 or (i + 1 < len(tokens) and tokens[i + 1].index in consumed))
        if abuts and extract_timespan(t.text, engine.spec.lang, anchor) is None:
            return True                              # impossible day-of-month
    return False


def _is_scope_noun(text, spec):
    """Whether ``text`` is a scope noun the ``scoped_ordinal`` frame's outer
    ``SCOPE_UNIT`` slot accepts -- a decade/century/millennium word or a
    calendar unit above the sub-day scale (year/month/week/day).  This is the
    exact surface test the matcher applies for ``SCOPE_UNIT`` (see
    :func:`chronologia.extract.matcher` slot matching), reused here so the veto
    recognises the same scope words the grammar does."""
    if text in spec.scope_units:
        return True
    kind = spec.units.get(text)
    return kind is not None and kind not in ("hour", "minute", "second")


def _trailing_scope_veto(tokens, consumed, spec):
    """Whether the winning reading strands a trailing ``of? <SCOPE_UNIT>`` scope
    it could not bind -- the "last <plural-unit> of <period>" compound.

    ``os últimos dias do ano`` / ``ostatnie dni roku`` ("the last days of the
    year") is not a supported construction: the plural unit vetoes the
    ``scoped_ordinal`` reading (a scoped ordinal is grammatically singular), so
    only the bare relative-period reading ("the last days" = yesterday) is left,
    stranding "of the year" in the remainder.  Where the genitive/contraction
    doubles as the "of" connector this leaks a yesterday span with a scope tail;
    in English the same phrase is refused because ``scoped_ordinal`` claims the
    whole span and its plural veto sinks the parse.  This veto restores the
    consistent honest refusal: a reading that leaves an unbound trailing scope
    noun (optionally introduced by an "of" connector and/or article) immediately
    after the winning span is an incomplete parse and is refused, matching the
    ten locales where the compound already returns ``None``.
    """
    if not consumed:
        return False
    last = max(consumed)
    trailing = [t for t in tokens if t.index > last and t.index not in consumed]
    # the trailing run must abut the winning span (no consumed gap): the scope
    # was trying to bind to the reading that just won.
    if not trailing or trailing[0].index != last + 1:
        return False
    of_surfaces = spec.connectors.get("of", frozenset())
    article_surfaces = spec.connectors.get("article", frozenset())
    i = 0
    while i < len(trailing) and (trailing[i].text in of_surfaces
                                 or trailing[i].text in article_surfaces):
        i += 1
    rest = trailing[i:]
    # exactly one residual scope noun, optionally introduced by a connector
    # ("do ano"/"do mês") or standing on its own genitive ("roku"/"miesiąca").
    return len(rest) == 1 and _is_scope_noun(rest[0].text, spec)


def _stranded_ordinal_scope_veto(tokens, consumed, spec):
    """Whether the winning reading strands a trailing ``of? article? ORD
    SCOPE_UNIT`` tail it could not bind -- "the weekend of the 5th month",
    "the last weekend of the 13th month".

    ``weekend_of_month`` only binds a NAMED month (its ``MONTH`` slot); it has
    no order for an ORDINAL month number ("the 5th month"), so that shape is
    not a supported composition (see ``weekend_of_month``'s grammar comment --
    wiring the ``scoped_ordinal`` ordinal-month machinery into a weekend scope
    would need new grammar, not a small extension).  With no full-span match,
    the bare ``weekend_ref``/``rel_span_weekend`` reading wins on "weekend"
    alone and strands "of the 5th/13th month" -- an anchor-relative weekend
    with the intended scope silently dropped, exactly the leak this veto
    closes by refusing outright rather than surfacing the truncated span.

    Mirrors :func:`_trailing_scope_veto`'s shape but the residual STARTS WITH
    two tokens (an ordinal numeral then a scope noun) instead of being one
    bare scope noun, so it needs its own check rather than a shared one. The
    tail may carry arbitrary text AFTER those two tokens (a year, "next
    year", a trailing clause) -- the shape only needs to be a *prefix* of the
    stranded tail, since any of those trailers still means the ordinal-scope
    composition was intended but unsupported.
    """
    if not consumed:
        return False
    last = max(consumed)
    trailing = [t for t in tokens if t.index > last and t.index not in consumed]
    if not trailing or trailing[0].index != last + 1:
        return False
    of_surfaces = spec.connectors.get("of", frozenset())
    article_surfaces = spec.connectors.get("article", frozenset())
    i = 0
    while i < len(trailing) and (trailing[i].text in of_surfaces
                                 or trailing[i].text in article_surfaces):
        i += 1
    rest = trailing[i:]
    return (len(rest) >= 2 and rest[0].is_number and (rest[0].value or 0) >= 1
            and _is_scope_noun(rest[1].text, spec))


def _stranded_explicit_anchor_veto(tokens, consumed, text, spec, anchor):
    """Whether the winning reading strands a trailing ``from <date>`` explicit
    anchor it could not bind -- "the next 2 quarters from 500 BC".

    ``rel_span_quarter``/``rel_span``/``rel_period`` are always anchored to
    the CALL anchor (today) -- they carry no "from <explicit date>" order, so
    a trailing "from <date>" naming a DIFFERENT anchor is not a supported
    composition (that would need ``rel_span``'s calendar-aligned counting to
    accept an arbitrary start date, a bigger change than the marker fix that
    lets "from" double as an "after"-synonym for the offset-WITH-reference
    shape -- see ``apply_anchored_offset``). With no full-span match, the
    present-anchored reading wins alone and strands "from <date>" -- a
    silently wrong present-day span with the intended anchor dropped. Refuses
    outright rather than surfacing the truncated span, the same honest-None
    policy as :func:`_trailing_scope_veto`/:func:`_stranded_ordinal_scope_veto`.
    """
    if not consumed:
        return False
    last = max(consumed)
    trailing = [t for t in tokens if t.index > last and t.index not in consumed]
    if not trailing or trailing[0].index != last + 1:
        return False
    of_surfaces = spec.connectors.get("of", frozenset())
    article_surfaces = spec.connectors.get("article", frozenset())
    from_surfaces = spec.connectors.get("from", frozenset())
    i = 0
    while i < len(trailing) and (trailing[i].text in of_surfaces
                                 or trailing[i].text in article_surfaces):
        i += 1
    if i >= len(trailing) or trailing[i].text not in from_surfaces:
        return False
    i += 1
    rest = trailing[i:]
    if not rest:
        return False
    cs, ce = rest[0].char_start, rest[-1].char_end
    if cs is None or ce is None:
        return False
    frag = text[cs:ce]
    return extract_timespan(frag, spec.lang, anchor) is not None


def _stranded_fraction_prefix_veto(tokens, consumed, spec):
    """Whether the winning reading strands a LEADING ``article? NUM
    FRACTION_WORD of?`` prefix it could not bind -- "first half of leap
    february 2028", "third quarter of somewhat march".

    ``half_period``'s MONTH order / ``quarter_of_month`` (see
    ``base_grammar.py``) bind ``of? MONTH`` directly adjacent -- no order
    tolerates a word interposed between "of" and the month name.  #658 closed
    the ADJACENT stranding ("first half of february" winning the bare month
    alone); an interposed word ("first half of LEAP february 2028") reopens
    the exact same leak from a different angle -- neither ``half_period`` nor
    ``quarter_of_month`` matches, so the bare ``calendar_date`` reading wins
    on "february 2028" alone and strands "first half of leap" ahead of it, a
    silently wrong (too-wide) answer.

    Mirrors :func:`_stranded_ordinal_scope_veto`'s prefix-tolerant shape
    (#651) but on the LEADING side of the winning span rather than the
    trailing one: the run of unconsumed tokens immediately BEFORE the winner
    (no consumed gap) only needs to *begin* with ``article? NUM
    FRACTION_WORD of?`` -- any further filler words ("leap") before the
    winning span are tolerated, since they still mean the ordinal-fraction
    composition was intended but unsupported.  Refuses outright rather than
    surfacing the truncated span, don't try to understand "leap" -- refusal
    beats silent-wide.
    """
    if not consumed:
        return False
    first = min(consumed)
    if first == 0:
        return False
    i = first - 1
    while i >= 0 and tokens[i].index not in consumed:
        i -= 1
    lead = [t for t in tokens[i + 1:first]]
    if not lead:
        return False
    article_surfaces = spec.connectors.get("article", frozenset())
    j = 0
    while j < len(lead) and lead[j].text in article_surfaces:
        j += 1
    if j >= len(lead) or not (lead[j].is_number and (lead[j].value or 0) >= 1):
        return False
    j += 1
    fraction_words = (set(spec.connectors.get("half", ()))
                      | set(spec.connectors.get("quarter_word", ())))
    if j >= len(lead) or lead[j].text not in fraction_words:
        return False
    j += 1
    # a trailing "of?" is optional -- some locales' month-fraction surface is
    # connector-less ("erste Hälfte Februar") -- but any presence of it here
    # is consumed as part of the recognised prefix, not counted as filler.
    of_surfaces = spec.connectors.get("of", frozenset())
    if j < len(lead) and lead[j].text in of_surfaces:
        j += 1
    return True


def _new_year_definite_article_veto(tokens, match, spec) -> bool:
    """True when a bare ``new_year_ref`` match is immediately preceded by the
    definite article ("the new year", "in the new year").

    Bare "new year" is New Year's Day; the DEFINITE-article form is the
    ambiguous "coming year" period, NOT the holiday, so it must not resolve to
    Jan 1.  The ``new_year_ref`` order carries no ``article`` slot, so "the" is
    never folded into the match -- this veto drops the reading whose left
    neighbour is the definite article, in BOTH public APIs, keeping them in
    agreement (both return the un-holiday reading -> None here).

    An EXPLICIT year ("the new year 2027") is not ambiguous at all -- there is
    only one Jan 1 named "2027", holiday or period reading agree on the same
    date -- so a bound ``YEARANY`` slot survives the veto same as "the hebrew
    new year 5786" already does (that construction carries no such veto).
    Bare "the new year" (no year number) keeps the ambiguous-period veto.
    """
    if match.construction != "new_year_ref":
        return False
    if "YEARANY" in match.slots:
        return False
    start = match.span[0]
    if start == 0:
        return False
    articles = spec.connectors.get("article", frozenset())
    return tokens[start - 1].text.lower() in articles


def _bare_be_trailing_veto(tokens, match, spec) -> bool:
    """True when a bare-"BE" Buddhist-Era match ("2560 BE") is followed by more
    tokens -- i.e. "be" is really the common English verb, not the abbreviation.

    "be" is an extremely common word and the tokenizer lower-cases surfaces, so
    a plain NUM-adjacency guard (enough for "bc"/"bp") would misread ordinary
    text: "in 2020 be ready" -> Buddhist Era 2020 (1477 CE).  The BE
    abbreviation is a clause-final postfix on the year ("2560 BE"), whereas the
    verb "be" leads into a continuation ("... be ready").  Restricting the bare
    abbreviation to end-of-clause (nothing trailing) keeps "2560 BE" while
    refusing the verb collision -- a clean miss on the rarer "2560 BE was ..."
    is strictly better than a silent-wrong on everyday "... be ...".  The
    spelled "Buddhist Era 2560" surface carries no such restriction.

    An explicit year-word cue leading the match ("the year 2560 BE") already
    disambiguates -- "year" cannot itself lead into the English verb "be", so
    trailing tokens after such a cued match are never the verb collision, and
    the veto must not fire there ("the year 2560 BE or so" stays the era).
    """
    if match.construction != "era_buddhist_be":
        return False
    year_words = spec.connectors.get("year_word", frozenset())
    start, end = match.span
    if any(tok.text in year_words for tok in tokens[start:end]):
        return False
    return end < len(tokens)


def _stray_capitalized_be_veto(tokens, match, spec) -> bool:
    """True for a ``year_ref`` match immediately followed by a capitalized,
    stray "BE" -- the token surface the tokenizer lower-cases into "be" but
    whose ``cap`` flag still marks it as written upper-case in the source.

    When :func:`_bare_be_trailing_veto` declines a bare "NUM BE" reading (no
    year-word cue, more text trailing), the plain ``year_ref`` candidate for
    that same NUM is still in the running and, being un-vetoed, wins the
    overlap contest -- turning "2560 BE or so" into a confidently WRONG plain
    year 2560 (543 years off) with "BE" stranded in the remainder.  An
    ordinary verb "be" ("2020 be ready") is written lower-case and must keep
    binding the plain year as today; only the upper-case abbreviation surface
    is suspicious enough to withhold a confident year and prefer a clean miss.
    """
    if match.construction != "year_ref":
        return False
    end = match.span[1]
    return end < len(tokens) and tokens[end].text == "be" and tokens[end].cap


def _stray_capitalized_am_veto(tokens, match, spec) -> bool:
    """True for a ``year_ref`` match immediately followed by a capitalized,
    stray "AM" -- the Anno Mundi abbreviation the tokenizer lower-cases into
    the same surface as the meridiem marker, but whose ``cap`` flag still
    marks it as written upper-case in the source.

    R102 added a ``year_ref`` order that lets an explicit "year" word license
    a below-window (< 1000, ``SMALLYEAR``) bare number ("in year 5") so it is
    never silently stranded on the "in a year" relative reading.  That same
    order also now claims the leading "in the year 1" of "in the year 1 AM",
    stranding the capitalized "AM" instead of leaving the whole phrase for the
    (BCE, out-of-range, correctly declining) Anno Mundi era reading.

    Scoped to the ``SMALLYEAR`` slot only: a ``GYEAR`` (>= 1000) match
    stranding a trailing "AM"/"BE"/etc is long-standing, pinned behaviour
    ("in the year 5780 AM" -> plain year 5780, cosmetic remainder) and must
    stay untouched -- only the new below-window reading is suspicious enough
    to withhold. A lower-case "am" is the ordinary meridiem marker and must
    keep composing with a plain year+clock reading as before; only the
    upper-case abbreviation is suspicious enough to withhold the confident
    small-year reading and prefer a clean miss -- the same asymmetry
    :func:`_stray_capitalized_be_veto` already applies to the Buddhist Era
    "BE" collision.
    """
    if match.construction != "year_ref" or "SMALLYEAR" not in match.slots:
        return False
    end = match.span[1]
    return end < len(tokens) and tokens[end].text == "am" and tokens[end].cap


def _stray_year_zero_veto(tokens, match, spec) -> bool:
    """True for a ``relative_offset`` "year" match immediately followed by a
    bare "0" -- e.g. "in year 0".

    ``SMALLYEAR`` (the R102/#663 fix for "in year 5") deliberately refuses a
    raw "0" (``matcher.py``'s ``SMALLYEAR`` branch: ``raw[0] != '0'``) because
    bare "year 0" carries no astronomical-year-0 binding -- it already
    resolves to ``None``. Without this veto, the R102 fix's own carve-out
    reopens the original R102 hole for N=0 only: "in year" alone still
    matches the plain relative-offset grammar ("in a year", +1y from the
    anchor) and "0" is left stranded, unconsumed, in the remainder -- the
    exact silent-wrong #663 was written to close for every OTHER N. Refusing
    the relative reading here keeps "in year 0" declining to ``None``,
    consistent with the pinned bare "year 0" -> ``None``, rather than
    inventing a binding the bare surface doesn't have.
    """
    if match.construction != "relative_offset":
        return False
    unit = match.slots.get("UNIT")
    if unit is None or spec.units.get(unit.text) != "year":
        return False
    end = match.span[1]
    return (end < len(tokens) and tokens[end].is_number
            and tokens[end].raw.rstrip(".") == "0")


def _candidate_veto(tokens, match, spec) -> bool:
    """Combined pre-selection veto: readings whose surrounding context makes
    them the WRONG parse ("the new year" is the period not the holiday; a
    non-clause-final "be" is the verb not the era; a plain year stranding a
    capitalized "BE"/"AM" is a declined era, not a confident year; "in year"
    stranding a bare "0" is the original R102 stranding hole reopened for the
    one value SMALLYEAR refuses).  Applied before the overlap contest so the
    shorter correct reading (a year_ref, or nothing) survives.
    """
    return (_new_year_definite_article_veto(tokens, match, spec)
            or _bare_be_trailing_veto(tokens, match, spec)
            or _stray_capitalized_be_veto(tokens, match, spec)
            or _stray_capitalized_am_veto(tokens, match, spec)
            or _stray_year_zero_veto(tokens, match, spec))


def _resolve_span(text, raw, engine, anchor, enable=(), jurisdiction=None,
                  scale_mode="short"):
    """The single recursive resolver over the token stream.

    One entry, three composition cases tried in precedence order; each wider
    case resolves its operand sub-spans by recursing back through this same
    resolver's inner cases, so a bounded/open range is *one derivation* over
    resolved sub-spans rather than a bolt-on run after the fact:

    * **RANGE** ("from A to B" / "between A and B") -- the span from the left
      endpoint's start to the right endpoint's end, each endpoint resolved by
      recursing on its own token slice (:func:`_extract_range`);
    * **OPEN_RANGE** ("until X" / "since X") -- one recursively-resolved
      endpoint plus the "now" anchor (:func:`_extract_open_range`);
    * **SINGLE** -- the single-span core: matcher/resolver plus the
      business-day, anchored-offset, ordinal-count and week-of composition
      cases, then the lone date + clock fold (:func:`_resolve_core`).

    ``raw`` is the *pre-fold* stream (connectors still visible so a range
    splits on the ``to``/``and`` the number fold would otherwise swallow); the
    SINGLE case folds it.  A range/open-range endpoint recurses through the
    SINGLE case only (via :func:`_resolve_endpoint`): endpoints are deliberately
    **not** re-entered into range detection, so a pathological connector chain
    cannot exhaust the stack.  Returns ``(span, remainder)`` or ``None``.
    """
    # a "since A until B" directional range is tried FIRST: its leading "since"
    # would otherwise let the plain closed-range path split on "until" and roll
    # both endpoints forward, silently dropping "since"'s past-anchoring.
    dir_rng = _extract_directional_range(text, raw, engine, anchor, scale_mode)
    if dir_rng is not None:
        return dir_rng
    rng = _extract_range(text, raw, engine, anchor, scale_mode)
    if rng is not None:
        return rng
    opn = _extract_open_range(text, raw, engine, anchor, scale_mode)
    if opn is not None:
        return opn
    # bare "now" / "right now" is the anchor instant, a zero-width span; a bare
    # "new year" is New Year's Day.  Both are recognised whole-utterance only, so
    # neither fires inside a longer phrase ("now and then", "hebrew new year").
    if _is_now_slice(raw, engine.spec):
        return _now_span(anchor), ""
    if _is_new_year_slice(raw, engine.spec):
        return _new_year_span(anchor), ""
    tokens = fold_tokens(raw, engine.spec, text)
    core = _resolve_core(tokens, engine, anchor, enable, jurisdiction, text,
                         scale_mode)
    if core is None:
        return None
    span, consumed = core
    # veto a reference governed by a leading negation/exclusion particle: a
    # trigger reachable across only the skippable run immediately before the span
    # (a whole-prefix scan would falsely veto a trigger in another clause).
    if _exclusion_governing_veto(tokens, consumed, text, engine.spec):
        return None
    # Impossible-date veto (residue-veto design, #244): a stranded
    # "<number> of ..." fragment in the remainder -- a day-of-month qualifier
    # the core could not bind because the day is impossible (a 32nd, the 29th
    # of a non-leap February, the Nth day of a year that is too short) -- is
    # proof the reading is incomplete.  Rather than fabricate a broader
    # plausible span (the whole month or year) and drop the day, refuse the
    # parse.
    #
    # The trigger is an UNCONSUMED numeral immediately followed by an
    # UNCONSUMED "of" connector.  Two shapes veto:
    #   * the "of" abuts the winning span (its next token was consumed) -- the
    #     day qualifier was trying to bind to the very span that won
    #     ("the 32nd of February 2017" -> "February 2017" + "the 32nd of");
    #   * the fragment stands alone but does NOT itself resolve to a valid
    #     date ("the 29th of February" in a non-leap year).
    # A stranded but VALID date (a second mention, "... al 5 de junio de 2020")
    # resolves on its own and is left in the remainder untouched.
    if _impossible_date_veto(tokens, consumed, text, engine, anchor):
        return None
    remainder = render_remainder(text, [t for t in tokens
                                        if t.index not in consumed])
    # A half-open span whose start falls before the datetime era (year <= 0)
    # but whose end lands on a representable year projects to (None, date) --
    # a malformed None-start span.  When such a partial parse also strands
    # text (an era-year phrase the core could not fully consume, e.g.
    # "in the year 1 BC"), the reading is untrustworthy: refuse it cleanly
    # rather than surface the broken half-open span.
    if (remainder.strip()
            and span.start_datetime is None
            and span.end_datetime is not None):
        return None
    return span, remainder


def _make_resolve_ref(tokens, engine, anchor, enable, jurisdiction, text,
                      scale_mode="short"):
    """Build the composed-reference resolver threaded into the post-passes.

    A post-pass (business-day / anchored-offset / week-of) locates its
    reference by a flat position-keyed scan of the resolved-match list, which
    only sees *matcher-native* references.  This callback is the additive
    fallback for a reference that is itself a **composed** construction (an
    offset "the monday after christmas", an nth-weekday-of-month, ...): it
    recurses the token slice starting at ``start`` through the single-span
    core -- the identical path a whole utterance takes -- and returns
    ``(start_datetime, consumed_positions)`` where ``consumed_positions`` are
    indices into the *original* ``tokens`` stream, or ``None``.

    The recursion re-folds its slice, so the core hands back slice-local,
    zero-based consumed positions; these are mapped back to original-stream
    positions by character extent (a folded slice preserves each token's
    ``char_start``/``char_end``), so the outer remainder stays correct even
    when the fold merged tokens.
    """
    if text is None:
        return None

    def resolve_ref(start):
        sub = tokens[start:]
        if not sub:
            return None
        folded = fold_tokens(sub, engine.spec, text)
        core = _resolve_core(folded, engine, anchor, enable, jurisdiction, text,
                             scale_mode)
        if core is None:
            return None
        span, consumed_local = core
        intervals = [(folded[i].char_start, folded[i].char_end)
                     for i in consumed_local
                     if i < len(folded) and folded[i].char_start is not None]
        orig = set()
        for op in range(start, len(tokens)):
            ot = tokens[op]
            if ot.char_start is None or ot.char_end is None:
                continue
            if any(cs <= ot.char_start and ot.char_end <= ce
                   for cs, ce in intervals):
                orig.add(op)
        return span.start, orig

    return resolve_ref


def _compose(resolved, engine, tokens):
    """Pick the single winning reading from the post-passed ``resolved`` matches.

    Returns ``(res, label_consumed, rep)``:

    * a lone date + lone clock compose (the minute-wide clock placed on the day
      the date names): "june 5th at 3pm";
    * a lone daypart + lone date compose (the band narrows the day the date
      names): "yesterday morning";
    * a bare weekday next to a lone LITERAL calendar date is a LABEL on it
      ("Monday, March 2"): the date is authoritative -- it becomes the date the
      clock/daypart composes onto (and wins outright otherwise) and the
      weekday's tokens are folded into ``label_consumed`` so the label never
      strands.  ``weekday_ref`` is itself a composable date (so "Monday at 3pm"
      takes a clock), so a genuine date+weekday pair shows up as one weekday and
      one NON-weekday date;
    * otherwise the earliest match in text order wins.

    ``rep`` is the match that best represents the winner -- used by
    :func:`extract_candidates` to score the composed reading -- so the two
    public APIs never disagree on the composed primary.
    """
    clocks = [(m, r) for m, r in resolved if m.construction == "clock_time"]
    dates = [(m, r) for m, r in resolved
             if m.construction in _COMPOSABLE_DATES]
    dayparts = [(m, r) for m, r in resolved
                if m.construction == "daypart_ref"]
    weekdays = [(m, r) for m, r in resolved
                if m.construction == "weekday_ref"]
    non_weekday_dates = [(m, r) for m, r in dates
                         if m.construction != "weekday_ref"]
    # Composition is only legitimate when the two parts are ADJACENT -- a lone
    # clock/daypart/weekday-label folds onto a date only if nothing unrelated
    # sits between them.  Otherwise a distant time bleeds across arbitrary text
    # ("since monday and also 10:00" must NOT read Monday 10:00; "from A to B
    # and also 10:00" must not collapse to that clock).  A token between the two
    # spans is allowed only when it is itself consumed by one of the resolved
    # matches (the daypart in "monday morning at 3pm") or is a bare glue
    # connector (at / on / of / the -- the clock usually already absorbs "at").
    spec = engine.spec
    # Glue = function words that legitimately join a date to a time within one
    # reference (at / on / of / the, a daypart preposition like Spanish "por la
    # mañana", French "du" in "le matin du 3 mars").  A surface is glue if it
    # belongs to ANY connector key that is not a pure SEPARATOR -- the
    # conjunctions and range words that join two DISTINCT references (and / or /
    # to / from / between / until / since).  Keyed this way, a preposition that
    # doubles as a separator surface (French "du" is also "from", Catalan "al"
    # is also "to") stays glue via its non-separator sense, while "and"/"y" --
    # which appear ONLY under a separator key -- correctly break adjacency.
    _sep_keys = {"and", "or", "to", "from", "between", "until", "since"}
    _glue = {s for _k, _vals in spec.connectors.items()
             if _k not in _sep_keys for s in _vals}
    _covered = set()
    for m, _r in resolved:
        _covered.update(range(*m.span))

    def _adjacent(a, b):
        (lo, hi) = sorted((a.span, b.span))
        return all(i in _covered or tokens[i].text in _glue
                   for i in range(lo[1], hi[0]))

    label_consumed = set()
    if (len(weekdays) == 1 and len(non_weekday_dates) == 1
            and non_weekday_dates[0][0].construction
            in _WEEKDAY_LABELABLE_DATES
            and _adjacent(non_weekday_dates[0][0], weekdays[0][0])):
        eff_dates = non_weekday_dates
        label_consumed = set(range(*weekdays[0][0].span))
    else:
        eff_dates = dates
    # A week-of-widened date is a seven-day span, not a day: composing a
    # pinpoint clock (or a daypart band) onto it would silently collapse the
    # week back to one minute (or one band) on its Monday and swallow the clock
    # tokens whole -- "the week of June 15 at 3pm" would read 2018-06-11 15:00
    # with an empty remainder, discarding the week.  Refuse the composition so
    # the week stands and the clock/daypart stays UNCOMPOSED in the remainder
    # (a non-empty remainder honestly signals the un-placed time).
    _week = len(eff_dates) == 1 and eff_dates[0][1].week_widened
    if (not _week and len(clocks) == 1 and len(eff_dates) == 1
            and _adjacent(eff_dates[0][0], clocks[0][0])):
        res = compose_date_clock(eff_dates[0][1], clocks[0][1])
        rep = eff_dates[0][0]
    elif (not _week and len(dayparts) == 1 and len(eff_dates) == 1
            and not clocks
            and _adjacent(eff_dates[0][0], dayparts[0][0])):
        name = engine.spec.dayparts[dayparts[0][0].slots["DAYPART"].text]
        res = compose_date_daypart(eff_dates[0][1], dayparts[0][1], name)
        rep = eff_dates[0][0]
    elif label_consumed and not clocks and not dayparts:
        rep, res = eff_dates[0]
    else:
        rep, res = min(resolved, key=lambda mr: mr[0].span[0])
    return res, label_consumed, rep


def _resolve_core(tokens, engine, anchor, enable=(), jurisdiction=None,
                  text=None, scale_mode="short"):
    """The single-span resolution over an already-tokenized stream.

    The whole of the old ``extract_timespan`` body *below* range detection --
    match, resolve, the business-day / anchored-offset / ordinal-count /
    week-of post-passes, and the lone date + clock composition -- returning
    ``(span, consumed)`` where ``consumed`` is the set of claimed token
    positions (the caller renders the remainder from the unconsumed ones).
    Factored out so a range endpoint resolves through the *identical* path a
    whole utterance does, from a re-based slice of the same stream.
    """
    resolved = []
    veto = lambda m: _candidate_veto(tokens, m, engine.spec)   # noqa: E731
    for match in engine.matcher.match(tokens, veto):
        # construction-group gate: a construction tagged ``"group": <g>`` in
        # lang.json is OFF unless ``g`` is in ``enable``.  The raw-Latin date
        # formulas live in the ``"classical"`` group -- unambiguous everyday
        # surfaces carry no group and are always on.
        group = engine.spec.construction_flags.get(
            match.construction, {}).get("group")
        if group is not None and group not in enable:
            continue
        res = engine.resolver.resolve(match, anchor, scale_mode)
        if res is not None:
            resolved.append((match, res))
    # business-day counting ("in 5 business days", "the next working day",
    # "3 working days after christmas"); jurisdiction scopes the holiday lookup.
    # Runs before the anchored-offset pass so a "N working days after <date>"
    # phrase composes on the resolved reference here, rather than being read as
    # a bare "N days after <date>" unit offset.
    resolve_ref = _make_resolve_ref(tokens, engine, anchor, enable,
                                     jurisdiction, text, scale_mode)
    resolved = apply_business_days(tokens, resolved, engine.spec, anchor,
                                   jurisdiction, resolve_ref)
    # anchored arithmetic: rewrite a date reference carrying a stranded
    # "N units after"/"the weekday before" pre-amble (composition on the
    # already-resolved reference), then synthesise any anchor-relative
    # ordinal-count phrase ("3 fridays from now") the bare matcher missed.
    resolved = apply_anchored_offset(tokens, resolved, engine.spec)
    count = apply_ordinal_count(tokens, engine.spec, anchor)
    if count is not None:
        claimed = set(range(*count[0].span))
        resolved = [(m, r) for m, r in resolved
                    if not any(i in claimed for i in range(*m.span))]
        resolved.append(count)
    if not resolved:
        return None
    # widen a date carrying the locale's "week of" marker to its whole week
    resolved = _apply_week_of(tokens, resolved, engine.spec)
    res, label_consumed, rep = _compose(resolved, engine, tokens)
    consumed = set(res.consumed) | label_consumed
    # Trailing-scope veto: a bare relative-period reading ("os últimos dias" =
    # "the last days") that strands an unbound "of? <SCOPE_UNIT>" tail ("do ano",
    # "roku") is the unsupported "last <plural-unit> of <period>" compound.  The
    # plural unit already vetoed the scoped_ordinal reading it apes; refusing the
    # leftover relative reading restores the honest None that en and the ten
    # other locales already return (see _trailing_scope_veto).
    if (rep.construction == "rel_period"
            and _trailing_scope_veto(tokens, consumed, engine.spec)):
        return None
    # A bare weekend reading ("weekend"/"the last N weekends") that strands an
    # unbound "of the Nth month" scope tail is the unsupported ordinal-month
    # weekend compound (see _stranded_ordinal_scope_veto) -- refuse rather
    # than surface the anchor-relative weekend with the scope phrase dropped.
    if (rep.construction in ("weekend_ref", "rel_span_weekend")
            and _stranded_ordinal_scope_veto(tokens, consumed, engine.spec)):
        return None
    # A present-anchored rel_span/rel_period/rel_span_quarter reading that
    # strands an unbound "from <date>" explicit-anchor tail is the
    # unsupported "N units/quarters from <date>" compound (see
    # _stranded_explicit_anchor_veto) -- refuse rather than surface a
    # present-day span with the intended anchor dropped.
    if (text is not None
            and rep.construction in ("rel_span", "rel_period", "rel_span_quarter")
            and _stranded_explicit_anchor_veto(tokens, consumed, text,
                                               engine.spec, anchor)):
        return None
    # A bare ``calendar_date`` reading (a NAMED month, with or without a
    # year) that strands a leading "ORD half/quarter of?" prefix it could
    # not bind is the unsupported "first half of LEAP february 2028" shape
    # -- an interposed word between "of" and the month reopens #658's
    # stranding leak from a different angle (see
    # _stranded_fraction_prefix_veto) -- refuse rather than surface the
    # too-wide bare-month span with the fraction ordinal dropped.
    if (rep.construction == "calendar_date"
            and _stranded_fraction_prefix_veto(tokens, consumed, engine.spec)):
        return None
    return res.value, consumed


@dataclass(frozen=True)
class Candidate:
    """One plausible reading the matcher considered, with its confidence.

    Not just the selected winner: :func:`extract_candidates` surfaces the
    runner-up parses the matcher already enumerated (before the longest-span /
    precedence overlap resolution collapses them to one), each carrying the
    :attr:`confidence` score that ranks it.

    * ``span`` -- the :class:`~chronologia.astrodate.DateSpan` this reading
      resolves to;
    * ``remainder`` -- the text left over once this reading claims its tokens;
    * ``confidence`` -- the deterministic score in ``(0, 1]``
      (see :mod:`chronologia.extract.confidence`); **not** a probability;
    * ``construction`` -- the trace name of the construction that matched
      (``"calendar_date"``, ``"weekday_ref"``, ...).
    """

    span: DateSpan
    remainder: str
    confidence: float
    construction: str


def extract_candidates(
        text: str,
        lang: str = "en-us",
        anchor: Optional[datetime] = None,
        limit: int = 5,
        scale: Optional[str] = None,
) -> List[Candidate]:
    """Every plausible parse the matcher considered, ranked by confidence.

    Where :func:`extract_timespan` returns only the single selected reading,
    this exposes the **runner-ups** the matcher already enumerated -- each
    candidate the backtracking walk produced before the longest-span /
    precedence overlap resolution discards the losers -- resolved and scored.

    Returns up to ``limit`` :class:`Candidate` (highest confidence first, ties
    broken by earlier text position then longer span).  The list is empty when
    nothing temporal was found.  ``anchor`` is the "now" relative phrases
    resolve against (default: the wall clock).

    ``text`` must be a ``str``; anything else raises :class:`TypeError`.
    Text that names nothing temporal, the empty string included, returns an
    empty list.
    """
    require_text(text, "extract_candidates")
    engine = _timespan_engine(lang)
    scale_mode = _resolve_scale_mode(lang, scale)
    anchor = anchor or datetime.now()
    if isinstance(anchor, datetime):
        anchor = anchor.replace(tzinfo=None)
    tokens = engine.tokenize(text)
    # Composed readings: the business-day / anchored-offset / ordinal-count
    # post-passes extract_timespan runs are re-run here so the candidate set can
    # never disagree with the single-winner API -- without this, "in 5 business
    # days" / "3 fridays from now" returned [] (a reading exists) and
    # "5 days after christmas" ranked Christmas Day itself top, silently dropping
    # "5 days after".  Mirrors the post-pass block of _resolve_core (the
    # single-span hot path is deliberately left untouched).
    composed = []
    veto = lambda m: _candidate_veto(tokens, m, engine.spec)   # noqa: E731
    for m in engine.matcher.match(tokens, veto):
        group = engine.spec.construction_flags.get(
            m.construction, {}).get("group")
        if group is not None:
            continue          # classical group is off for the default API
        r = engine.resolver.resolve(m, anchor, scale_mode)
        if r is not None:
            composed.append((m, r))
    resolve_ref = _make_resolve_ref(tokens, engine, anchor, (), None, text,
                                    scale_mode)
    composed = apply_business_days(tokens, composed, engine.spec, anchor, None,
                                   resolve_ref)
    composed = apply_anchored_offset(tokens, composed, engine.spec)
    ocount = apply_ordinal_count(tokens, engine.spec, anchor)
    if ocount is not None:
        claimed = set(range(*ocount[0].span))
        composed = [(m, r) for m, r in composed
                    if not any(i in claimed for i in range(*m.span))]
        composed.append(ocount)
    if composed:
        composed = _apply_week_of(tokens, composed, engine.spec)
    # The composed WINNER (date+clock / date+daypart / weekday-label) that
    # _resolve_core selects -- surfaced here via the SAME _compose helper so the
    # candidate set always contains extract_timespan's exact answer, not just
    # the un-composed parts.  The representative sub-match is widened to span the
    # WHOLE composed reading and mapped to the composed resolution, so
    # confidence() scores its full coverage (not just the sub-part -- otherwise a
    # bare partial reading can carry a higher confidence VALUE than the correct
    # composed answer); its consumed set (plus any weekday-label tokens) is
    # remembered so the remainder excludes everything the winner folded in.
    label_extra = {}
    primary = None
    if composed:
        win_res, win_label, rep = _compose(composed, engine, tokens)
        consumed_all = set(win_res.consumed) | win_label
        lo, hi = min(consumed_all), max(consumed_all) + 1
        wide = replace(rep, span=(lo, hi))
        composed = [(wide, win_res) if m is rep else (m, r)
                    for m, r in composed]
        label_extra[id(wide)] = consumed_all
        primary = id(wide)   # extract_timespan's selected answer -> rank it first
    composed_res = {id(m): r for m, r in composed}

    def _resolve_one(m):
        if id(m) in composed_res:
            return composed_res[id(m)]
        return engine.resolver.resolve(m, anchor, scale_mode)

    scored = []
    seen = set()
    # the runner-up enumeration must honour the SAME construction-group gate the
    # composed loop does -- otherwise a group-gated construction (the classical
    # Latin grammar, off by default) leaks in as a candidate that extract_timespan
    # would never return.
    runner_ups = [c.match for c in engine.matcher._candidates(tokens)
                  if engine.spec.construction_flags.get(
                      c.match.construction, {}).get("group") is None
                  and not _candidate_veto(tokens, c.match, engine.spec)]
    matches = [m for m, _ in composed] + runner_ups
    for sc in _score_candidates(matches, _resolve_one, engine.spec):
        match, res, conf = sc.match, sc.resolution, sc.confidence
        is_composed = id(match) in composed_res
        key = (match.construction, match.span, res.value)
        if key in seen:
            continue
        seen.add(key)
        consumed = label_extra.get(id(match), set(res.consumed))
        # skip a reading governed by a leading negation/exclusion particle
        # ("not tomorrow"): the excluded reference is not a positive date.  The
        # SAME bounded governing-region logic as the single-winner path, so the
        # two public APIs agree on which readings are vetoed.
        if _exclusion_governing_veto(tokens, consumed, text, engine.spec):
            continue
        # the same impossible-date veto _resolve_span applies to the single
        # winner: a candidate that strands an impossible day-of-month numeral
        # ("the ides of march 44 BC" -> roman_date + a stranded "44 BC") is a
        # fabricated reading extract_timespan refuses, so it must not be surfaced
        # here either -- otherwise the two public APIs disagree on the top answer.
        if _impossible_date_veto(tokens, consumed, text, engine, anchor):
            continue
        remainder = render_remainder(text, [t for t in tokens
                                            if t.index not in consumed])
        # rank: the composed PRIMARY (extract_timespan's own selected reading)
        # is first so the two APIs agree on the top answer; then confidence, a
        # composed reading ahead of the bare partial it was built from, earlier
        # text position, and longer span.
        rank = (0 if id(match) == primary else 1, -conf,
                0 if is_composed else 1, match.span[0], -match.length)
        scored.append((rank, Candidate(res.value, remainder, conf,
                                       match.construction)))
    # Range and open-range readings ("june 5 to june 12", "between monday and
    # friday", "since 2019", "until friday") are composed by _resolve_span the
    # same way extract_timespan resolves them, but the matcher core never
    # enumerates them -- so without this the ranked candidates omit
    # extract_timespan's own answer entirely and top-rank a stray single-
    # endpoint reading instead.  Detect the range on the SAME pre-fold stream
    # extract_timespan uses and surface it as the PRIMARY candidate (rank 0),
    # dropping any single candidate whose span the range subsumes so the same
    # span is not shown twice.
    raw = pretokens(text, engine.spec)
    range_ans = _extract_directional_range(text, raw, engine, anchor,
                                           scale_mode) \
        or _extract_range(text, raw, engine, anchor, scale_mode)
    range_kind = "date_range"
    if range_ans is None:
        range_ans = _extract_open_range(text, raw, engine, anchor, scale_mode)
        range_kind = "open_range"
    if range_ans is not None:
        rspan, rrem = range_ans
        # the range's confidence reflects ITS OWN support: the strongest
        # endpoint reading that falls WITHIN its span -- never the strongest
        # unrelated construction elsewhere in the text (a trailing ISO literal
        # the range does not even consume must not launder its score in).
        within = [c for _, c in scored
                  if c.span.start >= rspan.start and c.span.end <= rspan.end]
        rconf = max([c.confidence for c in within], default=0.9)
        # drop a single candidate that resolved to the SAME span, so the
        # identical span is not shown twice ("since 2019" and its bare year
        # reading); endpoints strictly inside the range stay as runner-ups.
        scored = [(rk, c) for rk, c in scored
                  if not (c.span.start == rspan.start
                          and c.span.end == rspan.end)]
        # rank the range STRICTLY first (-1): it is extract_timespan's own
        # answer, and must beat a meridiem-blind subtractive clock_time reading
        # of the same phrase ("5 to 9 am") that would otherwise tie on
        # confidence and win by insertion order, leaving the two APIs disagreeing.
        scored.append(((-1, -rconf, 0, 0, -len(tokens)),
                       Candidate(rspan, rrem, rconf, range_kind)))
    scored.sort(key=lambda e: e[0])
    return [c for _, c in scored[:limit]]
