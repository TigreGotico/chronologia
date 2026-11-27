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
from chronologia.extract.timespan import (WHOLE_REFUSAL, _candidate_veto,
                                          _compose_core,
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


def _daypart_across_days(tokens: Tuple[Token, ...], spec) -> bool:
    """A part of the day named by a range of days: fr "la nuit de samedi à
    dimanche", "le soir du 3 au 5 mai", "l'après-midi du lundi au vendredi".

    The night from one day into the next, or the evenings of several days,
    is no band of one day, and reading the part of the day alone gives the
    anchor's band with the days left over.  A locale lists the day-part words
    that head such a range in ``marker_daypart_across_days.voc``; a phrase
    with one of them, then a from or of word, a day, a to word and a day in
    the same sentence, has no reading.

    A day is a weekday, a day word or a day number.  After a weekday or a day
    word the right end must be one too: a number there is a clock or an
    address ("le soir de samedi à 9", "au 12 rue Victor Hugo").  A clock range
    ("la nuit de 22 h à 6 h") is not a range of days.
    """
    heads = sorted((h.split() for h in
                    spec.connectors.get("daypart_across_days", ())),
                   key=len, reverse=True)
    if not heads:
        return False
    leads = (set(spec.connectors.get("from", ()))
             | set(spec.connectors.get("of", ())))
    tos = set(spec.connectors.get("to", ()))
    hour_words = (set(spec.connectors.get("oclock", ()))
                  | set(spec.connectors.get("hours", ()))
                  | {s for s, k in spec.units.items()
                     if k in ("hour", "minute", "second")})

    def number_end(i):
        """The index after the number run that starts at ``i``."""
        j = i + 1
        while j < len(tokens) and tokens[j].mention is not None \
                and tokens[j].mention is tokens[i].mention:
            j += 1
        return j

    def day_kind(i):
        if i >= len(tokens) or tokens[i].break_before:
            return None
        tok = tokens[i]
        if tok.text in spec.weekdays or tok.text in spec.named_days:
            return "word"
        if not (tok.is_number or tok.mention is not None) or ":" in tok.text:
            return None
        j = number_end(i)
        return ("num" if j >= len(tokens) or tokens[j].text not in hour_words
                else None)

    def in_endpoint(tok):
        # what may stand inside the left end before the to word: "du 28
        # novembre au", "de samedi 28 à"
        return (tok.text in spec.months or tok.text in spec.weekdays
                or tok.is_number or tok.mention is not None
                or tok.text in leads)

    words = [t.text for t in tokens]
    for i in range(len(tokens)):
        n = next((len(h) for h in heads if words[i:i + len(h)] == h), 0)
        if (not n or i + n + 1 >= len(tokens) or words[i + n] not in leads
                or tokens[i + n].break_before):
            continue
        left = day_kind(i + n + 1)
        if left is None:
            continue
        dated = False
        for j in range(i + n + 2, len(tokens)):
            if tokens[j].break_before:
                break
            if words[j] in tos:
                right = day_kind(j + 1)
                if right == "word":
                    return True
                if right == "num" and left == "num":
                    # after a whole date ("du 28 novembre") a bare number is
                    # a clock ("à 9"); a day needs its month ("au 3 décembre")
                    end = number_end(j + 1)
                    if not dated or (end < len(tokens)
                                     and words[end] in spec.months):
                        return True
                break
            if not in_endpoint(tokens[j]):
                break
            dated = dated or words[j] in spec.months
    return False


def read(text: str, lang: str, anchor: datetime,
         jurisdiction: Optional[str] = None, enable: Tuple[str, ...] = (),
         scale: Optional[str] = None, first: bool = False,
         endpoint: bool = False) -> List[Reading]:
    """Every reading of ``text``; only the first one when ``first`` is set.
    ``endpoint`` marks the payload of a range or "until" word, which is the
    cue that keeps a homograph date word.

    ``anchor`` is a naive datetime.  ``first`` stops before the runner-up
    points are enumerated, which ``extract_timespan`` never needs.
    """
    engine = _timespan_engine(lang)
    spec = engine.spec
    scale_mode = _resolve_scale_mode(lang, scale)
    raw = pretokens(text, spec)
    if _daypart_across_days(raw, spec):
        return []
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
                                     whole=not readings, endpoint=endpoint)
    if resolved is WHOLE_REFUSAL:
        return readings
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
            res = engine.resolver.resolve(match, anchor, scale_mode,
                                           jurisdiction)
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
