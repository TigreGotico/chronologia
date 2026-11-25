"""The readings of a text, which ``extract_timespan`` and ``extract_candidates``
select from.

:func:`read` tokenizes the text once.  A span reading comes first: a range
("from A to B", "between A and B"), an open range ("until X", "since X"), or a
bare "now" or "new year".  The point readings follow in scoring order: the
winner the single-span core composes and every other match the matcher found.
The winner is not always the first point, so a caller selects it by
``primary``.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from typing import FrozenSet, List, Optional, Tuple

from chronologia.astrodate import DateSpan
from chronologia.extract.confidence import score_candidates
from chronologia.extract.model import Match, Token
from chronologia.extract.pipeline import (consumed_extent, fold_tokens,
                                          join_extents, pretokens,
                                          render_remainder)
from chronologia.extract.timespan import (_candidate_veto, _compose_core,
                                          _extract_directional_range,
                                          _extract_open_range, _extract_range,
                                          _is_new_year_slice, _is_now_slice,
                                          _lone_spoken_hour, _new_year_span,
                                          _now_span, _resolve_scale_mode,
                                          _timespan_engine)


@dataclass(frozen=True)
class Reading:
    """One reading of a text.

    ``kind`` is ``"span"``, ``"point"`` or ``"bound"``.  ``claimed`` holds
    the ``index`` of each token of ``tokens`` the reading reads: a span reads
    the stream before the number fold and claims every token inside
    ``chars``, a point reads the folded stream, so a caller that compares a
    span with a point uses ``chars``.  ``primary`` marks the winner of each
    kind: the range and the composed point.  ``selected`` marks a point the
    matcher selected, against a runner-up.  ``confidence`` is set on the
    points of a full read only.

    A range carries its bounds in ``left`` and ``right``; an open range has
    one of them.  A bound reads the stream before the number fold and claims
    exactly the tokens its endpoint reads.  Its ``span`` is the endpoint as
    its own slice reads it, before the range rolls it (see ``RangeBound``).
    """

    kind: str
    span: DateSpan
    remainder: str
    construction: str
    tokens: Tuple[Token, ...]
    claimed: FrozenSet[int]
    chars: Optional[Tuple[int, int]]
    primary: bool = False
    selected: bool = False
    match: Optional[Match] = None
    confidence: Optional[float] = None
    left: Optional[Reading] = None
    right: Optional[Reading] = None


def read(text: str, lang: str, anchor: datetime,
         jurisdiction: Optional[str] = None, enable: Tuple[str, ...] = (),
         scale: Optional[str] = None, first: bool = False) -> List[Reading]:
    """Every reading of ``text``; only the first one when ``first`` is set.

    ``anchor`` is a naive datetime.  ``first`` stops before the runner-up
    points are enumerated, which ``extract_timespan`` never needs.
    """
    engine = _timespan_engine(lang)
    spec = engine.spec
    scale_mode = _resolve_scale_mode(lang, scale)
    raw = pretokens(text, spec)
    readings = []
    # a "since A until B" directional range comes first: its "since" would let
    # the closed range split on "until" and lose the past anchoring
    got = (_extract_directional_range(text, raw, engine, anchor, scale_mode)
           or _extract_range(text, raw, engine, anchor, scale_mode))
    construction = "date_range"
    if got is None:
        got = _extract_open_range(text, raw, engine, anchor, scale_mode)
        construction = "open_range"
    # a bare "now" or "new year" is recognised as the whole utterance only
    if got is None and _is_now_slice(raw, spec):
        got = _now_span(anchor), "", consumed_extent(raw), None, None
        construction = "now"
    if got is None and _is_new_year_slice(raw, spec):
        got = _new_year_span(anchor), "", consumed_extent(raw), None, None
        construction = "new_year"
    if got is not None:
        span, remainder, chars, left, right = got
        claimed = frozenset() if chars is None else frozenset(
            t.index for t in raw if t.char_start is not None
            and chars[0] <= t.char_start and t.char_end <= chars[1])
        readings.append(Reading("span", span, remainder, construction, raw,
                                claimed, chars, primary=True,
                                left=_bound(left, raw, construction),
                                right=_bound(right, raw, construction)))
        if first:
            return readings

    tokens = fold_tokens(raw, spec, text)
    # the composed point answers for the whole utterance only when no span
    # reading claims it; under a range it is one more reading of the words
    resolved, winner = _compose_core(tokens, engine, anchor, enable,
                                     jurisdiction, text, scale_mode,
                                     whole=not readings)
    rep = None
    if winner is not None:
        res, won, rep = winner
        # a clock standing alone reads its next twelve-hour hour
        res = _lone_spoken_hour(res, rep, anchor, spec, tokens,
                                [m for m, _ in resolved], text)
        won = frozenset(won)

    def point(res, match, claimed, **flags):
        remainder = render_remainder(text, [t for t in tokens
                                            if t.index not in claimed])
        return Reading("point", res.value, remainder, match.construction,
                       tokens, claimed, consumed_extent(tokens, claimed),
                       match=match, **flags)

    if first:
        if rep is not None:
            readings.append(point(res, rep, won, primary=True, selected=True))
        return readings

    # The winner is scored as one match over every token it claims, so its
    # confidence covers the whole composed reading and not one part of it.
    wide = None
    if rep is not None:
        wide = replace(rep, span=(min(won), max(won) + 1))
        resolved = [(wide, res) if m is rep else (m, r) for m, r in resolved]
    chosen = {id(m): r for m, r in resolved}
    runner_ups = [c.match for c in engine.matcher._candidates(tokens)
                  if spec.construction_flags.get(
                      c.match.construction, {}).get("group") in (None, *enable)
                  and not _candidate_veto(tokens, c.match, spec)]
    matches = [m for m, _ in resolved] + runner_ups

    def resolve(match):
        res = chosen.get(id(match))
        if res is None:
            res = engine.resolver.resolve(match, anchor, scale_mode)
        if res is None:
            return None
        return _lone_spoken_hour(res, match, anchor, spec, tokens, matches,
                                 text)

    for scored in score_candidates(matches, resolve, spec):
        if scored.match is wide:
            readings.append(point(scored.resolution, rep, won, primary=True,
                                  selected=True,
                                  confidence=scored.confidence))
        else:
            readings.append(point(
                scored.resolution, scored.match,
                frozenset(scored.resolution.consumed),
                selected=id(scored.match) in chosen,
                confidence=scored.confidence))
    return readings


def _bound(bound, raw, construction):
    """The reading of one range bound over the stream ``raw``, or ``None``.

    The bound claims each token that one of its words covers, also in part:
    an affix bound reads its host word without the suffix."""
    if bound is None:
        return None
    claimed = frozenset(t.index for t in raw if t.char_start is not None
                        and any(s < t.char_end and t.char_start < e
                                for s, e in bound.pieces))
    return Reading("bound", bound.span, bound.remainder, construction, raw,
                   claimed, join_extents(*bound.pieces))
