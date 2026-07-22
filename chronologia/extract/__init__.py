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
from typing import Dict, List, Optional, Tuple

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
                                              pretokens, render_remainder)
from chronologia.extract.resolver import (DATE_CONSTRUCTIONS, Resolver,
                                              compose_date_clock, _WEEK_START)
from chronologia.extract.tokenizer import Tokenizer

__all__ = [
    "Conventions", "Direction", "LangSpec", "Match", "Resolution",
    "SlotElement", "SlotOrder", "Token", "TokenizerModes",
    "Tokenizer", "TemporalNormaliser", "ConstructionCompiler",
    "ConstructionMatcher", "Resolver", "load_lang_spec",
    "ExplainTrace", "explain", "DateTimeEngine",
    "extract_timespan", "extract_candidates", "Candidate",
    "extract_duration", "extract_timespans", "extract_recurrence",
    "TimeMention",
]


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

    @staticmethod
    def _compose(pairs) -> List[Resolution]:
        """Fold a lone clock_time onto a lone date construction (date span
        intersect clock -> minute span on that date); otherwise return every
        resolution in text order."""
        clocks = [(m, r) for m, r in pairs if m.construction == "clock_time"]
        dates = [(m, r) for m, r in pairs
                 if m.construction in DATE_CONSTRUCTIONS]
        if len(clocks) == 1 and len(dates) == 1:
            merged = compose_date_clock(dates[0][1], clocks[0][1])
            drop = {id(clocks[0][0]), id(dates[0][0])}
            kept = [(m, r) for m, r in pairs if id(m) not in drop]
            start = min(dates[0][0].span[0], clocks[0][0].span[0])
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


def _dash_between(tokens, p, text):
    """True when a whitespace-flanked hyphen sits in the gap before token ``p``.

    A dash range separator ("junho - agosto", "5 de junho - 12 de junho") is
    punctuation the tokenizer never emits, so it is read straight from the
    character gap between the adjacent tokens' recorded extents -- linear and
    anchored, no raw-string regex over the whole input."""
    a, b = tokens[p - 1].char_end, tokens[p].char_start
    if a is None or b is None:
        return False
    return _DASH_GAP.fullmatch(text[a:b]) is not None


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

    def endpoint(sub):
        return _range_endpoint(text, sub, engine, anchor)

    # -- from A to B -------------------------------------------------------
    lead = _match_conn_at(tokens, 0, from_surf)
    split = _first_to_split(tokens, lead, to_surf, text)
    if split is not None:
        p, k = split
        left_tok, right_tok = tokens[lead:p], tokens[p + k:]
        # a bare "A to B" (no from/between) is only trusted when the left side
        # is not a lone clock fraction word -- avoids hijacking "quarter to five"
        between_lead = _match_conn_at(tokens, 0, between_surf)
        left_words = " ".join(t.text for t in left_tok)
        if lead or between_lead or left_words not in fraction_words:
            got = _compose_range(left_tok, right_tok, endpoint, spec)
            if got is not None:
                return got

    # -- between A and B ---------------------------------------------------
    lead = _match_conn_at(tokens, 0, between_surf)
    if lead:
        split = _first_to_split(tokens, lead, and_surf, text)
        if split is not None:
            p, k = split
            got = _compose_range(tokens[lead:p], tokens[p + k:], endpoint, spec)
            if got is not None:
                return got
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
    left_span, right_span = left[0], right[0]
    start = left_span.start
    # roll a cyclic right endpoint forward into the same cycle as the start; a
    # dated endpoint already carries its year, so it is left untouched.
    end = right_span.end
    if right[2] == "clock":
        rolled = right_span
        while rolled.end <= start:
            rolled = DateSpan(rolled.start + timedelta(days=1),
                              rolled.end + timedelta(days=1))
        end = rolled.end
    elif right[2] == "weekday":
        rolled = right_span
        while rolled.end <= start:
            rolled = DateSpan(rolled.start + timedelta(days=7),
                              rolled.end + timedelta(days=7))
        end = rolled.end
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

    return (lead(until_surf, until_span) or lead(since_surf, since_span)
            or trail(until_surf, until_span) or trail(since_surf, since_span))


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
) -> Optional[Tuple[DateSpan, str]]:
    """Extract a :class:`~chronologia.DateSpan` from natural-language ``text``.

    Returns the referential *width* of a date phrase: unlike a parser that
    collapses a reference to its left edge, this returns the whole stretch
    of time referred to ("june 2027" is a month-wide span, "3 pm" a
    minute-wide one).  ``DateSpan.start_datetime`` / ``end_datetime`` yield
    real ``datetime`` (or ``None`` when out of range).

    ``anchor`` is the "now" relative phrases resolve against (default: the
    wall clock).  Only languages with locale data are supported; others
    raise :class:`NotImplementedError`.

    Returns ``(span, remainder)`` or ``None`` when nothing matched.

    ``jurisdiction`` (an ISO country code such as ``'PT'``) scopes the
    business-day constructions ("in 5 business days", "the next working day"):
    a business day is a non-weekend weekday that is also not a public holiday of
    that jurisdiction.  With ``jurisdiction=None`` the count is *holiday-blind*
    -- weekend-aware but treating every weekday as a business day -- because
    which weekdays are public holidays cannot be known without a jurisdiction.

    A "from A to B" / "between A and B" range yields the span from the start
    of the left sub-parse to the end of the right one (``june 5th to june
    12th`` -> a seven-day span); the endpoints are two independent parses.
    """
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
    return _resolve_span(text, raw, engine, anchor, enable, jurisdiction)


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
    core = _resolve_core(tokens, engine, anchor, enable, jurisdiction)
    if core is None:
        return None
    span, consumed = core
    remainder = render_remainder(text, [t for t in tokens
                                        if t.index not in consumed])
    return span, remainder


def _resolve_core(tokens, engine, anchor, enable=(), jurisdiction=None):
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
    resolved = apply_business_days(tokens, resolved, engine.spec, anchor,
                                   jurisdiction)
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
    if len(clocks) == 1 and len(dates) == 1:
        res = compose_date_clock(dates[0][1], clocks[0][1])
    else:
        # earliest match in text order wins the public result
        _, res = min(resolved, key=lambda mr: mr[0].span[0])
    return res.value, set(res.consumed)


from dataclasses import dataclass as _dataclass  # noqa: E402

from chronologia.extract.confidence import confidence as _confidence  # noqa: E402


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
    """
    engine = _timespan_engine(lang)
    anchor = anchor or datetime.now()
    if isinstance(anchor, datetime):
        anchor = anchor.replace(tzinfo=None)
    tokens = engine.tokenize(text)
    total = len(tokens)
    scored = []
    seen = set()
    for cand in engine.matcher._candidates(tokens):
        match = cand.match
        res = engine.resolver.resolve(match, anchor)
        if res is None:
            continue
        key = (match.construction, match.span, res.value)
        if key in seen:
            continue
        seen.add(key)
        conf = _confidence(match, res, total, engine.spec)
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
    TimeMention, extract_duration, extract_recurrence, extract_timespans)
