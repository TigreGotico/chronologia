"""``explain(text, spec, anchor)`` -- the pipeline's debug window.

Replays tokenizer -> normaliser -> matcher -> resolver and reports, in
one immutable trace: the tokens seen, every candidate construction, which
matches were selected (with their resolved value), and *why* each losing
candidate lost -- longer rival span or higher-precedence rival on an
overlapping span.  This is the antidote to "engine regexes become
undebuggable": constructions are named slots, and the trace shows the
contest.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple

from chronologia.extract.compiler import ConstructionCompiler
from chronologia.extract.matcher import Candidate, ConstructionMatcher
from chronologia.extract.model import LangSpec, Match, Resolution, Token
from chronologia.extract.normaliser import TemporalNormaliser
from chronologia.extract.resolver import Resolver
from chronologia.extract.tokenizer import Tokenizer

# module-level compiler so repeated explain() calls reuse the cache
_COMPILER = ConstructionCompiler()


@dataclass(frozen=True)
class LostMatch:
    match: Match
    reason: str


@dataclass(frozen=True)
class WonMatch:
    match: Match
    resolution: Optional[Resolution]


@dataclass(frozen=True)
class ExplainTrace:
    text: str
    tokens: Tuple[Token, ...]
    winners: Tuple[WonMatch, ...]
    losers: Tuple[LostMatch, ...]

    def report(self) -> str:
        lines = [f"text: {self.text!r}",
                 "tokens: " + " ".join(t.text for t in self.tokens)]
        for w in self.winners:
            binding = {k: v.text for k, v in w.match.slots.items()}
            if w.match.calendar:
                binding["calendar"] = w.match.calendar
            val = w.resolution.value if w.resolution else "unresolved"
            lines.append(f"  MATCH {w.match.construction} "
                         f"span={w.match.span} slots={binding} -> {val}")
        for lost in self.losers:
            lines.append(f"  lost  {lost.match.construction} "
                         f"span={lost.match.span}: {lost.reason}")
        return "\n".join(lines)

    def __str__(self) -> str:
        return self.report()


def _reason(cand: Candidate, winners) -> str:
    span = range(*cand.match.span)
    for w in winners:
        if any(i in range(*w.match.span) for i in span):
            if w.match.length > cand.match.length:
                return (f"overlaps {w.match.construction} span={w.match.span} "
                        f"which is longer")
            return (f"overlaps {w.match.construction} span={w.match.span} "
                    f"of higher precedence")
    return "not selected"


def explain(text: str, spec: LangSpec, anchor: datetime) -> ExplainTrace:
    compiled = _COMPILER.compile(spec)
    tokens = TemporalNormaliser(spec).normalise(
        Tokenizer(spec.tokenizer).tokenize(text))
    matcher = ConstructionMatcher(compiled)
    candidates = matcher._candidates(tokens)
    selected = matcher._select(candidates)
    resolver = Resolver(spec)
    winners = tuple(WonMatch(c.match, _safe_resolve(resolver, c.match, anchor))
                    for c in selected)
    chosen = {id(c) for c in selected}
    losers = tuple(LostMatch(c.match, _reason(c, selected))
                   for c in candidates if id(c) not in chosen)
    return ExplainTrace(text, tokens, winners, losers)


def _safe_resolve(resolver, match, anchor):
    try:
        return resolver.resolve(match, anchor)
    except NotImplementedError:
        return None
