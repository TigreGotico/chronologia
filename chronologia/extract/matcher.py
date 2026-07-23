"""Tokens -> matches, with precedence and longest-span resolution.

Each construction order is matched by a plain backtracking walk over its
:class:`SlotElement` sequence (optional slots try both present and
skipped; the longest consumption wins).  Slot binding is a single lookup
into the language's typed vocab maps -- there are no per-language regexes
to debug, only named slots.

Overlap resolution follows the doc: among competing matches the longest
span wins, ties broken by precedence (era > scoped > calendar > ...).
Selected matches never overlap.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Tuple

from chronologia.extract.compiler import CompiledSpec
from chronologia.extract.model import (LangSpec, Match, SlotElement,
                                           Token)

_ISO = re.compile(r"\d{4}-\d{2}-\d{2}")
_CLOCK = re.compile(r"\d{1,2}:\d{2}(?::\d{2})?")


def _calendar_for_surface(spec: LangSpec, surface: str):
    """Which registered calendar owns a calendar-month surface (surfaces are
    unique across calendars within a language, so the first hit is the
    only hit)."""
    for cal_key, months in spec.calendar_months.items():
        if surface in months:
            return cal_key
    return None


@dataclass(frozen=True)
class MatchCandidate:
    match: Match
    precedence: int


def _bind(element: SlotElement, token: Token, spec: LangSpec) -> bool:
    name = element.name
    if not element.is_slot:
        return token.text in spec.connectors.get(name, frozenset())
    if name == "NUM":
        return token.is_number
    if name == "UNIT":
        return token.text in spec.units
    if name in ("MARKER", "DIRECTION_MARKER"):
        return token.text in spec.directions
    if name == "DAY_WORD":
        return token.text in spec.named_days
    if name == "REL_MARKER":
        return token.text in spec.rel_markers
    if name == "WEEKEND":
        return token.text in spec.weekend_words
    if name == "WEEKDAY":
        return token.text in spec.weekdays
    if name == "WEEKDAYFULL":
        return token.text in spec.weekday_full
    if name == "HOLIDAY":
        return token.text in spec.holidays
    if name == "MONTH":
        return token.text in spec.months
    if name == "CAL_MONTH":
        return any(token.text in months
                   for months in spec.calendar_months.values())
    if name == "DAY":
        return token.is_number and 1 <= (token.value or 0) <= 31
    if name == "YEAR":
        return token.is_number and ((token.value or 0) >= 32
                                    or len(token.raw.rstrip(".")) >= 4)
    if name == "GYEAR":
        # a standalone Gregorian year: a bare 4-5 digit run (1000-99999), so
        # small integers ("5", "123") and digit soup ("1234567890") never read
        # as a year when nothing else anchors them
        raw = token.raw.rstrip(".")
        # a leading zero marks a clock reading ("0600"), never a year
        return (token.is_number and raw.isdigit() and 4 <= len(raw) <= 5
                and raw[0] != "0")
    if name in ("MILTIME", "MILTIMEZ"):
        raw = token.raw.rstrip(".")
        if not (token.is_number and raw.isdigit() and len(raw) == 4):
            return False
        hh, mm = int(raw[:2]), int(raw[2:])
        if not (0 <= hh <= 23 and 0 <= mm <= 59):
            return False
        # MILTIMEZ (the bare, no-"hours" form) only fires with a leading zero,
        # so "1500" stays a year while "0600" reads as a clock
        return raw[0] == "0" if name == "MILTIMEZ" else True
    if name == "LANDMARK":
        return token.text in spec.clock_landmarks
    if name == "DAYPART":
        return token.text in spec.dayparts
    if name == "ZONE":
        # the base acronym ("utc"/"gmt") must be a known zone surface; any
        # trailing signed offset ("utc+2") rides on the same token and is
        # parsed at resolve time.
        base = re.match(r"[a-z]+", token.text)
        return base is not None and base.group(0) in spec.clock_zones
    if name == "QUANT":
        return token.text in spec.quantifiers
    if name == "ISO":
        return _ISO.fullmatch(token.text) is not None
    # -- clock_time slots --------------------------------------------------
    if name == "CLOCK":
        return _CLOCK.fullmatch(token.text) is not None
    if name == "HOUR":
        return token.is_number and 0 <= (token.value or 0) <= 24
    if name == "MINUTE":
        return token.is_number and 0 <= (token.value or 0) <= 59
    if name == "FRACTION":
        return token.text in spec.clock_fractions
    if name == "CLOCKDIR":
        return token.text in spec.clock_dirs
    if name == "MERIDIEM":
        return token.text in spec.meridiems
    # -- season_ref / scoped_ordinal slots ---------------------------------
    if name == "SEASON":
        return token.text in spec.seasons
    if name in ("ORD", "SORD"):
        return token.is_number and (token.value or 0) >= 1
    if name in ("SUBH", "SUBM", "SUBS"):
        return token.is_number and (token.value or 0) >= 0
    if name == "SEL_UNIT":
        return token.text in spec.scope_units or token.text in spec.units
    if name == "CMUNIT":
        # a century or millennium scope unit ONLY -- the postposed Romance
        # ordinal ("século XII", "secolo XII") binds this, never a plain unit
        # like "anno"/"semana" (which would hijack a year or ISO-week reading)
        return spec.scope_units.get(token.text) in ("century", "millennium")
    if name == "SCOPE_UNIT":
        # the outer scope of an ordinal ("the third CENTURY") is never a
        # sub-day unit -- excluding hour/minute keeps "15 uur"/"15 uhr" a
        # clock, not a spurious "15th hour" scoped ordinal (matters where a
        # unit word doubles as the o'clock word, e.g. Dutch "uur").
        if token.text in spec.scope_units:
            return True
        kind = spec.units.get(token.text)
        return kind is not None and kind not in ("hour", "minute", "second")
    # -- day-cycle / regnal / roman slots ----------------------------------
    if name == "CYCLE_DAY":
        return token.text in spec.cycle_positions
    if name == "ERANAME":
        return token.text in spec.regnal_names
    if name == "ANCHOR_DAY":
        return token.text in spec.roman_anchors
    if name == "ARCHON":
        return token.text in spec.archon_names
    if name == "PRIDIE":
        return token.text in spec.connectors.get("pridie", frozenset())
    # -- deep-time / named-period slots ------------------------------------
    if name == "PERIOD":
        return token.text in spec.periods
    if name == "SCALE":
        return token.text in spec.scales
    if name == "PART":
        return token.text in spec.period_parts
    if name == "DECADE":
        return token.text in spec.decade_words
    return False


def _connector_span(name: str, tokens: Tuple[Token, ...], ti: int,
                    spec: LangSpec) -> int:
    """Longest run of tokens from ``ti`` matching a connector surface.

    A connector surface may be **multi-word** ("vor christus", "v. chr.",
    "before the present"): it is compared word-for-word against the token
    stream, punctuation-split the same way the tokenizer splits it (dots
    dropped).  Returns the number of tokens consumed (0 if none matched).
    """
    surfaces = spec.connectors.get(name)
    if not surfaces or ti >= len(tokens):
        return 0
    best = 0
    for surf in surfaces:
        words = surf.lower().replace(".", " ").split()
        n = len(words)
        if n and ti + n <= len(tokens) and all(
                tokens[ti + k].text == words[k] for k in range(n)):
            best = max(best, n)
    return best


def _walk(elements: Tuple[SlotElement, ...], tokens: Tuple[Token, ...],
          ei: int, ti: int, spec: LangSpec,
          slots: Dict[str, Token]) -> List[Tuple[int, Dict[str, Token]]]:
    if ei == len(elements):
        return [(ti, dict(slots))]
    el = elements[ei]
    results: List[Tuple[int, Dict[str, Token]]] = []
    if el.is_slot:
        if ti < len(tokens) and _bind(el, tokens[ti], spec):
            bound = dict(slots)
            bound[el.name] = tokens[ti]
            results += _walk(elements, tokens, ei + 1, ti + 1, spec, bound)
    else:
        consumed = _connector_span(el.name, tokens, ti, spec)
        if consumed:
            results += _walk(elements, tokens, ei + 1, ti + consumed, spec,
                             slots)
    if el.optional:
        results += _walk(elements, tokens, ei + 1, ti, spec, slots)
    return results


class ConstructionMatcher:
    """Runs a compiled table over a token stream."""

    def __init__(self, compiled: CompiledSpec):
        self.compiled = compiled
        self.spec = compiled.spec

    def _candidates(self, tokens: Tuple[Token, ...]) -> List[MatchCandidate]:
        out: List[MatchCandidate] = []
        for precedence, name, order in self.compiled.table:
            for start in range(len(tokens)):
                ends = _walk(order.elements, tokens, 0, start, self.spec, {})
                if not ends:
                    continue
                end, slots = max(ends, key=lambda r: r[0])
                if end > start:
                    if "CAL_MONTH" in slots:
                        cal = _calendar_for_surface(
                            self.spec, slots["CAL_MONTH"].text)
                    elif "HOLIDAY" in slots:
                        # trace the well-known binding (key + provenance) so
                        # explain() shows which holiday and which source named it
                        key = self.spec.holidays.get(slots["HOLIDAY"].text)
                        src = self.spec.holiday_sources.get(key, "")
                        cal = f"{key} <{src}>" if key else None
                    else:
                        cal = None
                    out.append(MatchCandidate(
                        Match(name, (start, end), slots, calendar=cal),
                        precedence))
        return out

    @staticmethod
    def _select(candidates: List[MatchCandidate]) -> List[MatchCandidate]:
        """Pick the non-overlapping winners: longest span, then precedence.

        This is the parse-winner contest, and it is deliberately
        **resolution-independent** -- it runs on the raw enumerated candidates
        before the resolver is consulted, so the winner stands even for
        readings the resolver later declines.  It is *not* the same question as
        confidence ranking (:func:`chronologia.extract.confidence.confidence`),
        which scores already-*resolved* readings for the candidate API: the two
        legitimately disagree (a bare ``calendar_date`` may out-score the
        anchored-offset reading that wins the parse), and they are kept as two
        explicit layers rather than one algorithm.  See ``docs/extraction.md``.
        """
        ordered = sorted(candidates,
                         key=lambda c: (-c.match.length, c.precedence,
                                        c.match.span[0]))
        taken: set = set()
        chosen: List[MatchCandidate] = []
        for cand in ordered:
            span = range(*cand.match.span)
            if any(i in taken for i in span):
                continue
            taken.update(span)
            chosen.append(cand)
        chosen.sort(key=lambda c: c.match.span[0])
        return chosen

    def match(self, tokens: Tuple[Token, ...]) -> Tuple[Match, ...]:
        return tuple(c.match for c in self._select(self._candidates(tokens)))
