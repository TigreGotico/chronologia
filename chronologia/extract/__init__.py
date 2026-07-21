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
from typing import List, Optional, Tuple

from chronologia.astrodate import AstroDate, DateSpan
from chronologia.extract.compiler import ConstructionCompiler
from chronologia.extract.explain import ExplainTrace, explain
from chronologia.extract.loader import LOCALE_DIR, load_lang_spec
from chronologia.extract.matcher import ConstructionMatcher
from chronologia.extract.model import (Conventions, Direction, LangSpec,
                                           Match, Resolution, SlotElement,
                                           SlotOrder, Token, TokenizerModes)
from chronologia.extract.normaliser import TemporalNormaliser
from chronologia.extract.resolver import (DATE_CONSTRUCTIONS, Resolver,
                                              compose_date_clock)
from chronologia.extract.tokenizer import Tokenizer

__all__ = [
    "Conventions", "Direction", "LangSpec", "Match", "Resolution",
    "SlotElement", "SlotOrder", "Token", "TokenizerModes",
    "Tokenizer", "TemporalNormaliser", "ConstructionCompiler",
    "ConstructionMatcher", "Resolver", "load_lang_spec",
    "ExplainTrace", "explain", "DateTimeEngine",
    "extract_timespan",
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
        # multiword vocab surfaces ("bronze age") that the tokenizer splits;
        # merged back into one token so a single slot can bind them. Longest
        # first so "late bronze age" wins over "bronze age".
        self._multiword = sorted(
            (s for s in spec.periods if " " in s),
            key=lambda s: len(s.split()), reverse=True)

    def tokenize(self, text: str) -> Tuple[Token, ...]:
        tokens = self.normaliser.normalise(self.tokenizer.tokenize(text))
        if self.spec.hook is not None:
            tokens = self.spec.hook(tokens)
        return self._merge_multiword(tokens)

    def _merge_multiword(self, tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
        if not self._multiword:
            return tokens
        phrases = [(s.split(), s) for s in self._multiword]
        out, i = [], 0
        while i < len(tokens):
            for words, surface in phrases:
                n = len(words)
                if [t.text for t in tokens[i:i + n]] == words:
                    raw = " ".join(t.raw for t in tokens[i:i + n])
                    out.append(Token(text=surface, raw=raw, index=len(out)))
                    i += n
                    break
            else:
                out.append(Token(tokens[i].text, tokens[i].raw, len(out),
                                 tokens[i].is_number, tokens[i].value))
                i += 1
        return tuple(out)

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


_TIMESPAN_ENGINES = {}


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


#: range framings, most specific first; each yields (left, right) text
_RANGE_PATTERNS = (
    re.compile(r"^\s*(?:from\s+)?(.+?)\s+(?:to|until|till|through|thru|-)\s+(.+?)\s*$",
               re.IGNORECASE),
    re.compile(r"^\s*between\s+(.+?)\s+and\s+(.+?)\s*$", re.IGNORECASE),
)


def _extract_range(text, lang, anchor):
    """A "from A to B" / "between A and B" span, endpoints from two parses.

    Only fires when *both* sides parse on their own and the left edge is not
    after the right; otherwise returns ``None`` so the normal single-span
    path runs (this keeps "quarter to five" -- a clock, not a range -- from
    being read as a range)."""
    lowered = text.strip().lower()
    between = lowered.startswith("between ")
    has_from = lowered.startswith("from ")
    for pat in _RANGE_PATTERNS:
        m = pat.match(text)
        if not m:
            continue
        left_txt, right_txt = m.group(1), m.group(2)
        # a bare "A to B" (no from/between) is only trusted when neither side
        # is a lone clock fraction word -- avoids hijacking "quarter to five"
        if pat is _RANGE_PATTERNS[0] and not (has_from or between):
            if left_txt.strip().lower() in ("quarter", "half", "a quarter"):
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
        if end < start:
            continue
        rem = " ".join(p for p in (left[1], right[1]) if p).strip()
        return DateSpan(start, end), rem
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


def extract_timespan(
        text: str,
        lang: str = "en-us",
        anchor: Optional[datetime] = None,
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
    tokens = engine.tokenize(text)
    resolved = []
    for match in engine.matcher.match(tokens):
        res = engine.resolver.resolve(match, anchor)
        if res is not None:
            resolved.append((match, res))
    if not resolved:
        return None
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
