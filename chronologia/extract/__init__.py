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

import re
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
from chronologia.extract.pipeline import prematch_tokens
from chronologia.extract.resolver import (DATE_CONSTRUCTIONS, Resolver,
                                              compose_date_clock, _WEEK_START)
from chronologia.extract.tokenizer import Tokenizer

__all__ = [
    "Conventions", "Direction", "LangSpec", "Match", "Resolution",
    "SlotElement", "SlotOrder", "Token", "TokenizerModes",
    "Tokenizer", "TemporalNormaliser", "ConstructionCompiler",
    "ConstructionMatcher", "Resolver", "load_lang_spec",
    "ExplainTrace", "explain", "DateTimeEngine",
    "extract_timespan",
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


def _timespan_engine(lang: str) -> "DateTimeEngine":
    """Return the :class:`DateTimeEngine` for ``lang``.

    Raises :class:`NotImplementedError` for languages that have no engine
    locale data (``chronologia/locale/<code>/lang.json``).
    """
    import os

    code = lang.split("-")[0].lower()
    if code not in _TIMESPAN_ENGINES:
        if not os.path.exists(os.path.join(LOCALE_DIR, code, "lang.json")):
            raise NotImplementedError(
                f"extract_timespan has no locale data for {lang!r}; only "
                f"languages with locale/<code>/lang.json are supported so far")
        _TIMESPAN_ENGINES[code] = DateTimeEngine(load_lang_spec(code))
    return _TIMESPAN_ENGINES[code]


#: default (English) range framing words, always available so English
#: behaviour is unchanged.  A language adds its own surfaces via the
#: ``from``/``to``/``between``/``and`` connectors (``marker_from.voc`` ...),
#: which are unioned in per language -- ranges are not English-only.
_RANGE_FROM = ("from",)
_RANGE_TO = ("to", "until", "till", "through", "thru", "-")
_RANGE_BETWEEN = ("between",)
_RANGE_AND = ("and",)
#: leading markers of an open-ended range -- "until friday" (open start,
#: bounded below by "now") and "since 2019" (open end, bounded above by
#: "now").  Languages add their own surfaces via the ``until``/``since``
#: connectors; the English defaults keep English working with no locale data.
_RANGE_UNTIL = ("until", "till", "through", "thru")
_RANGE_SINCE = ("since",)


def _range_words(spec, name, defaults):
    forms = set(defaults)
    forms |= set(spec.connectors.get(name, ()))
    return tuple(sorted((re.escape(f) for f in forms if f),
                        key=len, reverse=True))


def _range_patterns(spec):
    """(from-A-to-B, between-A-and-B) regexes for a language, most specific
    first.  Framing words are the English defaults unioned with the
    language's own ``from``/``to``/``between``/``and`` connector surfaces."""
    to_alt = "|".join(_range_words(spec, "to", _RANGE_TO))
    from_alt = "|".join(_range_words(spec, "from", _RANGE_FROM))
    between_alt = "|".join(_range_words(spec, "between", _RANGE_BETWEEN))
    and_alt = "|".join(_range_words(spec, "and", _RANGE_AND))
    return (
        re.compile(rf"^\s*(?:(?:{from_alt})\s+)?(.+?)\s+(?:{to_alt})\s+(.+?)\s*$",
                   re.IGNORECASE),
        re.compile(rf"^\s*(?:{between_alt})\s+(.+?)\s+(?:{and_alt})\s+(.+?)\s*$",
                   re.IGNORECASE),
    )


def _starts_with_any(lowered, words):
    return any(lowered.startswith(w.lower() + " ") for w in words)


def _extract_range(text, lang, anchor):
    """A "from A to B" / "between A and B" span, endpoints from two parses.

    Only fires when *both* sides parse on their own and the left edge is not
    after the right; otherwise returns ``None`` so the normal single-span
    path runs (this keeps "quarter to five" -- a clock, not a range -- from
    being read as a range)."""
    spec = _timespan_engine(lang).spec
    patterns = _range_patterns(spec)
    lowered = text.strip().lower()
    between = _starts_with_any(lowered, _RANGE_BETWEEN + tuple(
        spec.connectors.get("between", ())))
    has_from = _starts_with_any(lowered, _RANGE_FROM + tuple(
        spec.connectors.get("from", ())))
    # lone clock-fraction words that a bare "A to B" must never treat as a
    # range endpoint (would hijack "quarter to five" / "čtvrt na päť")
    fraction_words = set(spec.clock_fractions) | {"quarter", "half", "a quarter"}
    for pat in patterns:
        m = pat.match(text)
        if not m:
            continue
        left_txt, right_txt = m.group(1), m.group(2)
        # a bare "A to B" (no from/between) is only trusted when neither side
        # is a lone clock fraction word -- avoids hijacking "quarter to five"
        if pat is patterns[0] and not (has_from or between):
            if left_txt.strip().lower() in fraction_words:
                continue
        left = extract_timespan(left_txt, lang, anchor) \
            or _bare_weekday_endpoint(left_txt, lang, anchor)
        right = extract_timespan(right_txt, lang, anchor) \
            or _bare_weekday_endpoint(right_txt, lang, anchor)
        # a bare left endpoint ("3" in "between 3 and 5 pm") borrows the
        # right endpoint's trailing meridiem so both read on the same clock
        if left is None and right is not None:
            merid = _trailing_meridiem(right_txt, lang)
            if merid is not None and left_txt.strip():
                left = extract_timespan(f"{left_txt} {merid}", lang, anchor)
        if left is None or right is None:
            continue
        start = left[0].start
        end = right[0].end
        # end before start: the right endpoint wraps into the next cycle --
        # a clock crossing midnight ("10 pm to 2 am") rolls a day; a weekday
        # ("monday to friday") rolls a week.  Roll the right span forward by
        # its own granularity until it lands after the start.
        step = (timedelta(days=1)
                if right[0].end - right[0].start < timedelta(days=1)
                else timedelta(days=7))
        rolled = right[0]
        for _ in range(8):
            if rolled.end > start:
                break
            rolled = DateSpan(rolled.start + step, rolled.end + step)
        end = rolled.end
        # prefer-future asymmetry: a range that straddles the anchor -- its
        # left endpoint just behind "now", its right just ahead -- resolves the
        # left a whole year into the future (prefer_future) while the right
        # stays put, inverting the span past what the week/day roll above can
        # repair.  Pull the left endpoint back one year so both endpoints read
        # in the same nearest cycle ("july 20 to july 25" spoken on july 22
        # stays this year rather than leaping to the next).
        if end < start:
            pulled = _minus_one_year(start)
            if pulled is not None and pulled < right[0].end:
                start, end = pulled, right[0].end
        if end < start:
            continue
        rem = " ".join(p for p in (left[1], right[1]) if p).strip()
        return DateSpan(start, end), rem
    return None


def _minus_one_year(astro):
    """The same day one calendar year earlier, or ``None`` when that day does
    not exist (Feb 29) or falls out of the representable range."""
    try:
        return astro.replace(year=astro.year - 1)
    except (ValueError, OverflowError):
        return None


def _extract_open_range(text, lang, anchor):
    """An open-ended range: "until friday" (open start) / "since 2019" (open
    end).  Only fires on a leading ``until``/``since`` marker whose remainder
    parses as a date endpoint.

    The known endpoint keeps the closed-range endpoint convention -- an
    ``until`` endpoint contributes its ``.end`` (it is included in full, as the
    right endpoint of "from A to B" is), a ``since`` endpoint its ``.start`` --
    and the open side is pinned to the anchor instant ("now").  So "until
    friday" is ``[now, friday_end)`` and "since 2019" is ``[2019-01-01, now)``.
    """
    spec = _timespan_engine(lang).spec
    stripped = text.strip()
    lowered = stripped.lower()
    now = AstroDate.from_datetime(anchor)
    until_words = set(_RANGE_UNTIL) | set(spec.connectors.get("until", ()))
    since_words = set(_RANGE_SINCE) | set(spec.connectors.get("since", ()))

    def _endpoint(rest):
        return (extract_timespan(rest, lang, anchor)
                or _bare_weekday_endpoint(rest, lang, anchor))

    for w in sorted(until_words, key=len, reverse=True):
        if w and lowered.startswith(w.lower() + " "):
            ep = _endpoint(stripped[len(w):].strip())
            if ep is not None and ep[0].end > now:
                return DateSpan(now, ep[0].end), ep[1]
    for w in sorted(since_words, key=len, reverse=True):
        if w and lowered.startswith(w.lower() + " "):
            ep = _endpoint(stripped[len(w):].strip())
            if ep is not None and ep[0].start < now:
                return DateSpan(ep[0].start, now), ep[1]
    return None


def _bare_weekday_endpoint(text, lang, anchor):
    """A lone weekday ("monday") as a range endpoint only: a day-wide span for
    the next occurrence on or after the anchor day.  A bare weekday never
    parses on its own (too ambiguous) -- it is only trusted inside a range,
    where the framing supplies the intent."""
    engine = _timespan_engine(lang)
    toks = engine.tokenize(text.strip())
    if len(toks) != 1 or toks[0].text not in engine.spec.weekdays:
        return None
    ahead = (engine.spec.weekdays[toks[0].text] - anchor.weekday()) % 7
    day = (anchor.replace(hour=0, minute=0, second=0, microsecond=0)
           + timedelta(days=ahead))
    start = AstroDate.from_datetime(day)
    return DateSpan(start, start + timedelta(days=1)), ""


def _trailing_meridiem(text, lang):
    """The am/pm surface word ending ``text``, or None -- for propagating a
    shared meridiem onto a bare range endpoint."""
    engine = _timespan_engine(lang)
    toks = engine.tokenize(text)
    if toks and toks[-1].text in engine.spec.meridiems:
        return toks[-1].raw
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
    rng = _extract_range(text, lang, anchor)
    if rng is not None:
        return rng
    opn = _extract_open_range(text, lang, anchor)
    if opn is not None:
        return opn
    tokens = engine.tokenize(text)
    resolved = []
    for match in engine.matcher.match(tokens):
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
             if m.construction in DATE_CONSTRUCTIONS]
    if len(clocks) == 1 and len(dates) == 1:
        res = compose_date_clock(dates[0][1], clocks[0][1])
        match = dates[0][0]
    else:
        # earliest match in text order wins the public result
        match, res = min(resolved, key=lambda mr: mr[0].span[0])
    consumed = set(res.consumed)
    remainder = " ".join(t.raw for t in tokens
                         if t.index not in consumed).strip()
    return res.value, remainder


# N-series edges (durations, multi-mention, recurrence) live in their own
# module; imported here so ``chronologia.extract`` is the single public edge.
from chronologia.extract.nseries import (  # noqa: E402
    TimeMention, extract_duration, extract_recurrence, extract_timespans)
