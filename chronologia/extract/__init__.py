"""Natural-language date extraction: text -> :class:`~chronologia.DateSpan`.

The declarative construction engine that turns a date written the way a
human writes it ("the 15th of Ramadan 1446", "next winter", "66 million
years ago") into the *referential width* of the phrase -- a half-open
:class:`~chronologia.astrodate.DateSpan`, not a single collapsed instant.

The public edge is :func:`extract_timespan`; :func:`explain` opens a debug
window over the same pipeline.  Every language is data only -- a
``chronologia/locale/<code>/`` directory of ``.voc`` vocabulary files plus
one ``lang.json`` stanza; the engine core (tokenizer, normaliser,
compiler, matcher, resolver, loader) is shared and language-agnostic.
"""
from __future__ import annotations

import os
import re
import threading
from datetime import datetime, timedelta
from typing import Dict, List, NamedTuple, Optional, Tuple

from chronologia.astrodate import AstroDate, DateSpan
from chronologia.extract.compiler import ConstructionCompiler
from chronologia.extract.explain import ExplainTrace, explain
from chronologia.extract.loader import LOCALE_DIR, load_lang_spec
from chronologia.extract.matcher import ConstructionMatcher
from chronologia.extract.model import (Conventions, Direction, LangSpec,
                                           Match, Resolution, SlotElement,
                                           SlotOrder, Token, TokenizerModes)
from chronologia.extract.normaliser import TemporalNormaliser
from chronologia.extract.anchored import (apply_anchored_offset,
                                              apply_ordinal_count)
from chronologia.extract.business import apply_business_days
from chronologia.extract.pipeline import (fold_tokens, prematch_tokens,
                                              pretokens, render_remainder,
                                              require_text)
from chronologia.extract.resolver import (DATE_CONSTRUCTIONS, Resolver,
                                              compose_date_clock,
                                              compose_date_daypart, _WEEK_START)
from chronologia.extract.tokenizer import Tokenizer

__all__ = [
    "Conventions", "Direction", "LangSpec", "Match", "Resolution",
    "SlotElement", "SlotOrder", "Token", "TokenizerModes",
    "Tokenizer", "TemporalNormaliser", "ConstructionCompiler",
    "ConstructionMatcher", "Resolver", "load_lang_spec",
    "ExplainTrace", "explain", "DateTimeEngine",
    "extract_timespan", "extract_candidates", "Candidate",
    "extract_duration", "extract_timespans", "extract_recurrence",
    "TimeMention", "TimeSpanResult", "DurationResult", "RecurrenceResult",
]


class TimeSpanResult(NamedTuple):
    """Return of :func:`extract_timespan`: a span and the leftover text.

    A plain 2-tuple ``(span, remainder)`` for unpacking, plus the named fields
    ``.span`` (a :class:`~chronologia.astrodate.DateSpan`) and ``.remainder``.
    """
    span: DateSpan
    remainder: str


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
    code = lang.split("-")[0].lower()
    engine = _TIMESPAN_ENGINES.get(code)
    if engine is not None:
        return engine
    with _ENGINE_LOCK:
        # re-check under the lock: another thread may have built it while we
        # waited, so a language is only ever compiled once
        engine = _TIMESPAN_ENGINES.get(code)
        if engine is None:
            if not os.path.exists(os.path.join(LOCALE_DIR, code, "lang.json")):
                raise NotImplementedError(
                    f"extract_timespan has no locale data for {lang!r}; only "
                    f"languages with locale/<code>/lang.json are supported so far")
            engine = DateTimeEngine(load_lang_spec(code))
            _TIMESPAN_ENGINES[code] = engine
        return engine


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

#: the constructions a lone ``clock_time`` composes onto (its minute-wide time
#: placed on the day the date names).  A single composable-date set so the
#: synthesised day-wide results of the post-passes -- a business-day count
#: ("in 5 business days at 3pm"), an anchor-relative weekday count ("3 fridays
#: from now at noon"), the weekend-after-next -- fold with a trailing clock
#: exactly as a matcher-native date does, rather than being second-class to the
#: ``DATE_CONSTRUCTIONS`` the matcher itself emits.
_COMPOSABLE_DATES = DATE_CONSTRUCTIONS | {
    "business_days", "weekday_count", "weekend_after_next"}


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
    return (_TIGHT_DASH.fullmatch(gap) is not None
            and _is_written_year(tokens[p - 1]) and _is_written_year(tokens[p]))


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


def _extract_range(text, tokens, engine, anchor):
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
    to_surf = _conn_surfaces(spec, "to", _RANGE_TO)
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
    lead_required = {s.lower() for s in spec.connectors.get("to", ())
                     if s in spec.connectors.get("at", ())}

    def endpoint(sub):
        return _range_endpoint(text, sub, engine, anchor)

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
            if led:
                got = _compose_clock_range(text, left_tok, right_tok,
                                           engine, anchor)
            if got is None:
                got = _compose_range(left_tok, right_tok, endpoint, spec)
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
                got = _compose_range(left_tok, right_tok, endpoint, spec)
            if got is not None:
                return _with_prefix(got, prefix)
    return None


def _range_endpoint(text, sub, engine, anchor):
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
    """
    pinned = any(t.is_number and t.value is not None and t.value >= 100
                 for t in sub)
    weekday = any(t.text in engine.spec.weekdays for t in sub)
    got = _resolve_endpoint(text, sub, engine, anchor)
    if got is not None:
        span, rem = got
        width = span.end - span.start
        if width < timedelta(days=1):
            kind = "clock"
        elif width <= timedelta(days=1) and weekday:
            kind = "weekday"
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


def _variant_endpoint(text, sub, engine, anchor):
    """:func:`_resolve_endpoint` over a slice carrying synthesised tokens.

    Identical to the real path except that the remainder is rendered from the
    *original* tokens only -- a synthesised meridiem has no extent in the
    utterance and must never surface as leftover text.
    """
    folded = fold_tokens(tuple(sub), engine.spec, text)
    core = _resolve_core(folded, engine, anchor)
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


def _compose_range(left_tok, right_tok, endpoint, spec):
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
    if end <= start and not left[3]:
        pulled = _minus_one_year(start)
        if pulled is not None and pulled < right_span.end:
            start, end = pulled, right_span.end
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


def _resolve_endpoint(text, sub, engine, anchor):
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
    core = _resolve_core(folded, engine, anchor)
    if core is None:
        return None
    span, consumed = core
    remainder = render_remainder(text, [t for t in folded
                                        if t.index not in consumed])
    return span, remainder


def _extract_open_range(text, tokens, engine, anchor):
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
        return (_resolve_endpoint(text, sub, engine, anchor)
                or _bare_weekday_endpoint(sub, engine, anchor))

    def until_span(ep):
        return DateSpan(now, ep[0].end) if ep is not None and ep[0].end > now \
            else None

    def since_span(ep):
        # "since X" is PAST-anchored: it names the most recent occurrence of X
        # at-or-before now, so a prefer_future endpoint resolution (which flings
        # a near-past date a whole year forward -- "since july 6" -> next July)
        # is pulled back cycle by cycle until it lands in the past.  This makes
        # prefer_future a property the *construction* overrides, not a global
        # toggle "since" has to fight.
        if ep is None:
            return None
        start = ep[0].start
        while start > now:
            pulled = _minus_one_year(start)
            if pulled is None:
                break
            start = pulled
        return DateSpan(start, now) if start < now else None

    def lead(surf, build):
        # the marker leads; its tokens are dropped, the endpoint keeps its own
        # leftover (the framing word is never part of the remainder)
        k = _match_conn_at(tokens, 0, surf)
        if not k:
            return None
        ep = endpoint(tokens[k:])
        span = build(ep) if ep is not None else None
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
                span = build(ep) if ep is not None else None
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
                ep = endpoint(tuple(tokens[:-1]) + (stripped,))
                span = build(ep) if ep is not None else None
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


def _bare_weekday_endpoint(sub, engine, anchor):
    """A lone weekday ("monday") as a range endpoint only: a day-wide span for
    the next occurrence on or after the anchor day.  A bare weekday never
    parses on its own (too ambiguous) -- it is only trusted inside a range,
    where the framing supplies the intent.  Reads a *token slice*."""
    if len(sub) != 1 or sub[0].text not in engine.spec.weekdays:
        return None
    ahead = (engine.spec.weekdays[sub[0].text] - anchor.weekday()) % 7
    day = (anchor.replace(hour=0, minute=0, second=0, microsecond=0)
           + timedelta(days=ahead))
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
                    widened = (m, Resolution(week, consumed))
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
) -> Optional[TimeSpanResult]:
    """Extract a :class:`~chronologia.DateSpan` from natural-language ``text``.

    Returns the referential *width* of a date phrase: unlike a parser that
    collapses a reference to its left edge, this returns the whole stretch
    of time referred to ("june 2027" is a month-wide span, "3 pm" a
    minute-wide one).  ``DateSpan.start_datetime`` / ``end_datetime`` yield
    real ``datetime`` (or ``None`` when out of range).

    ``anchor`` is the "now" relative phrases resolve against (default: the
    wall clock).  Only languages with locale data are supported; others
    raise :class:`NotImplementedError`.

    Returns a :class:`TimeSpanResult` -- a ``(span, remainder)`` named tuple
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

    ``text`` must be a ``str``; anything else raises :class:`TypeError`.
    Text that names nothing temporal, the empty string included, returns
    ``None``.
    """
    require_text(text, "extract_timespan")
    engine = _timespan_engine(lang)
    anchor = anchor or datetime.now()
    if isinstance(anchor, datetime):
        anchor = anchor.replace(tzinfo=None)
    # tokenize ONCE: the tokenizer regex runs a single time and the resulting
    # stream is the shared currency.  Range/open-range detection reads the
    # *pre-fold* stream (connectors still visible); folding the whole stream for
    # the single-span core, or a lone endpoint's slice, re-uses these tokens --
    # the tokenizer is never run again on a substring.
    raw = pretokens(text, engine.spec)
    res = _resolve_span(text, raw, engine, anchor, enable, jurisdiction)
    return None if res is None else TimeSpanResult(*res)


def _resolve_span(text, raw, engine, anchor, enable=(), jurisdiction=None):
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
    rng = _extract_range(text, raw, engine, anchor)
    if rng is not None:
        return rng
    opn = _extract_open_range(text, raw, engine, anchor)
    if opn is not None:
        return opn
    tokens = fold_tokens(raw, engine.spec, text)
    core = _resolve_core(tokens, engine, anchor, enable, jurisdiction, text)
    if core is None:
        return None
    span, consumed = core
    remainder = render_remainder(text, [t for t in tokens
                                        if t.index not in consumed])
    return span, remainder


def _make_resolve_ref(tokens, engine, anchor, enable, jurisdiction, text):
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
        core = _resolve_core(folded, engine, anchor, enable, jurisdiction, text)
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


def _resolve_core(tokens, engine, anchor, enable=(), jurisdiction=None,
                  text=None):
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
    for match in engine.matcher.match(tokens):
        # construction-group gate: a construction tagged ``"group": <g>`` in
        # lang.json is OFF unless ``g`` is in ``enable``.  The raw-Latin date
        # formulas live in the ``"classical"`` group -- unambiguous everyday
        # surfaces carry no group and are always on.
        group = engine.spec.construction_flags.get(
            match.construction, {}).get("group")
        if group is not None and group not in enable:
            continue
        res = engine.resolver.resolve(match, anchor)
        if res is not None:
            resolved.append((match, res))
    # business-day counting ("in 5 business days", "the next working day",
    # "3 working days after christmas"); jurisdiction scopes the holiday lookup.
    # Runs before the anchored-offset pass so a "N working days after <date>"
    # phrase composes on the resolved reference here, rather than being read as
    # a bare "N days after <date>" unit offset.
    resolve_ref = _make_resolve_ref(tokens, engine, anchor, enable,
                                     jurisdiction, text)
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
    # a lone date + lone clock in the same text compose (the minute-wide
    # clock time placed on the day the date names): "june 5th at 3pm"
    clocks = [(m, r) for m, r in resolved if m.construction == "clock_time"]
    dates = [(m, r) for m, r in resolved
             if m.construction in _COMPOSABLE_DATES]
    # a lone daypart + lone date compose too: the band narrows the day the date
    # names ("yesterday morning" -> yesterday's morning band), fixing the silent
    # drop where the daypart word used to strand in the remainder.
    dayparts = [(m, r) for m, r in resolved
                if m.construction == "daypart_ref"]
    if len(clocks) == 1 and len(dates) == 1:
        res = compose_date_clock(dates[0][1], clocks[0][1])
    elif len(dayparts) == 1 and len(dates) == 1 and not clocks:
        name = engine.spec.dayparts[dayparts[0][0].slots["DAYPART"].text]
        res = compose_date_daypart(dates[0][1], dayparts[0][1], name)
    else:
        # earliest match in text order wins the public result
        _, res = min(resolved, key=lambda mr: mr[0].span[0])
    return res.value, set(res.consumed)


from dataclasses import dataclass as _dataclass  # noqa: E402

from chronologia.extract.confidence import score_candidates as _score_candidates  # noqa: E402


@_dataclass(frozen=True)
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
    anchor = anchor or datetime.now()
    if isinstance(anchor, datetime):
        anchor = anchor.replace(tzinfo=None)
    tokens = engine.tokenize(text)
    scored = []
    seen = set()
    matches = (c.match for c in engine.matcher._candidates(tokens))
    for sc in _score_candidates(matches,
                                lambda m: engine.resolver.resolve(m, anchor),
                                engine.spec):
        match, res, conf = sc.match, sc.resolution, sc.confidence
        key = (match.construction, match.span, res.value)
        if key in seen:
            continue
        seen.add(key)
        consumed = set(res.consumed)
        remainder = render_remainder(text, [t for t in tokens
                                            if t.index not in consumed])
        # rank: confidence first, then earlier text position, then longer span
        rank = (-conf, match.span[0], -match.length)
        scored.append((rank, Candidate(res.value, remainder, conf,
                                       match.construction)))
    scored.sort(key=lambda e: e[0])
    return [c for _, c in scored[:limit]]


# N-series edges (durations, multi-mention, recurrence) live in their own
# module; imported here so ``chronologia.extract`` is the single public edge.
from chronologia.extract.nseries import (  # noqa: E402
    DurationResult, RecurrenceResult, TimeMention, extract_duration,
    extract_recurrence, extract_timespans)
