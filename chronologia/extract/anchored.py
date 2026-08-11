"""Anchored arithmetic: an offset applied to a *resolved reference*.

Two families of construction live here, both built by **composition** on
top of the ordinary resolved matches -- no reference date is re-parsed, the
already-resolved :class:`~chronologia.extract.model.Resolution` object is
transformed (objects-in, objects-out):

* **offset-from-reference** ("two weeks after easter", "3 days before
  christmas", "the monday after christmas", "the friday before easter"):
  a signed unit offset -- or a strict weekday roll -- applied to any
  date-resolving submatch (holiday, calendar date, weekday ref, ...).  The
  reference is *whatever the engine already resolved* immediately after the
  directional marker; this pass finds that marker + a stranded offset
  pre-amble and rewrites the reference's span.

* **ordinal counting from the anchor** ("3 fridays from now", "2 mondays
  ago", "the weekend after next"): the N-th occurrence of a weekday
  strictly after/before *now*, or the weekend one past the next.  These do
  not need a reference match -- they synthesise a resolution straight from
  the token stream, so they fire even when the bare matcher found nothing.

Every surface is read from the language's own vocabulary
(``after``/``before``/``from``/``of`` connectors, ``present`` marker,
``weekdays``, ``units``, ``weekend_words``, ``plural`` suffix): the logic is
generic, the facts are data.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from chronologia.astrodate import AstroDate, DateSpan
from chronologia.extract.model import LangSpec, Match, Resolution, Token
from chronologia.extract.resolver import (DATE_CONSTRUCTIONS, _WEEK_START,
                                              _day_span, _midnight)

Pair = Tuple[Match, Resolution]


def _phrases(surfaces) -> List[List[str]]:
    """Connector surfaces split into word lists, longest first."""
    return sorted((s.split() for s in surfaces), key=len, reverse=True)


def _gap_words(spec: LangSpec) -> frozenset:
    """Function words that may sit between a directional marker and its
    reference: articles, indefinite articles and ``of`` contractions
    (Romance "após **a** páscoa", "antes **do** natal")."""
    return (frozenset(spec.connectors.get("article", ()))
            | frozenset(spec.connectors.get("indef", ()))
            | frozenset(spec.connectors.get("of", ())))


def _astro_is_leap(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def _astro_days_in_month(year: int, month: int) -> int:
    if month == 2 and _astro_is_leap(year):
        return 29
    return (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)[month - 1]


def _astro_add_months(start: AstroDate, months: int) -> AstroDate:
    """``start`` advanced by whole months, in AstroDate's own (proleptic,
    unbounded-year) space -- never round-tripped through stdlib ``datetime``,
    whose ``MINYEAR``/``MAXYEAR`` bounds a BC/deep-time composition would
    overrun (see ``_try_offset``/``_try_offset_postfix``)."""
    total = start.month - 1 + months
    year = start.year + total // 12
    month = total % 12 + 1
    day = min(start.day, _astro_days_in_month(year, month))
    return start.replace(year=year, month=month, day=day)


def _shift(start: AstroDate, unit: str, step: float) -> AstroDate:
    """``start`` advanced by ``step`` of ``unit`` (mirrors the offset resolver),
    entirely in AstroDate space so the arithmetic stays valid for any
    proleptic year (BC, deep time) instead of stdlib ``datetime``'s
    ``MINYEAR``-bounded range."""
    if unit == "minute":
        return start + timedelta(minutes=step)
    if unit == "hour":
        return start + timedelta(hours=step)
    if unit == "day":
        return start + timedelta(days=step)
    if unit == "week":
        return start + timedelta(weeks=step)
    if unit == "fortnight":
        return start + timedelta(weeks=2 * step)
    if unit == "month":
        return _astro_add_months(start, int(step))
    month_steps = {"year": 12, "decade": 120, "century": 1200,
                   "millennium": 12000}
    if unit in month_steps:
        return _astro_add_months(start, int(step) * month_steps[unit])
    raise ValueError(f"unsupported offset unit {unit!r}")


def _roll_weekday(base: AstroDate, target: int, sign: int) -> AstroDate:
    """The named ``target`` weekday strictly after (``sign>0``) or strictly
    before (``sign<0``) the midnight ``base``."""
    if sign > 0:
        ahead = (target - base.weekday()) % 7 or 7
        return base + timedelta(days=ahead)
    back = (base.weekday() - target) % 7 or 7
    return base - timedelta(days=back)


def _astro_day_span(d: AstroDate) -> DateSpan:
    """Day-wide span ``[midnight(d), next midnight)`` for an AstroDate that
    may fall outside stdlib ``datetime``'s representable range (mirrors
    ``resolver._day_span``, which only accepts stdlib ``datetime``)."""
    start = d.replace(hour=0, minute=0, second=0, microsecond=0)
    return DateSpan(start, start + timedelta(days=1))


# -- feature 1: offset-from-reference -------------------------------------

def _parse_preamble(tokens: Tuple[Token, ...], c0: int, spec: LangSpec,
                    gap: frozenset) -> Optional[dict]:
    """Read the offset pre-amble ending just before token ``c0`` (the
    directional marker's first token).

    Two shapes: a unit offset (``[article] [NUM|QUANT] UNIT``) or a weekday
    roll (``[article] WEEKDAY``).  Returns a descriptor or ``None``.
    """
    lead = spec.connectors.get("offset_lead", frozenset())
    j = c0 - 1
    if j < 0:
        return None
    tj = tokens[j]
    if tj.text in spec.units:
        unit = spec.units[tj.text]
        start = j
        qty = 1.0
        if j - 1 >= 0:
            p = tokens[j - 1]
            if p.is_number and p.value is not None:
                qty, start = float(p.value), j - 1
            elif p.text in spec.quantifiers:
                qty, start = spec.quantifiers[p.text], j - 1
        if start - 1 >= 0 and tokens[start - 1].text in gap:
            start -= 1
        # a lead-in preposition heading the offset phrase ("**cu** 3 zile
        # înainte de ...", Romanian "with three days before"): consumed so it
        # is not stranded in the remainder.
        if start - 1 >= 0 and tokens[start - 1].text in lead:
            start -= 1
        return {"kind": "unit", "unit": unit, "qty": qty, "start": start}
    if tj.text in spec.weekdays:
        start = j
        if start - 1 >= 0 and tokens[start - 1].text in gap:
            start -= 1
        return {"kind": "weekday", "weekday": spec.weekdays[tj.text],
                "start": start}
    return None


def _try_offset(tokens, match: Match, res: Resolution, spec: LangSpec,
                dir_phrases, gap) -> Optional[Pair]:
    """Compose an offset onto the reference ``match``/``res`` when a
    directional marker (with a stranded pre-amble) sits just before it."""
    b = match.span[0]
    k = b
    while k - 1 >= 0 and tokens[k - 1].text in gap:      # skip article/of gap
        k -= 1
    for sign, words in dir_phrases:
        n = len(words)
        c0 = k - n
        if c0 < 0 or [t.text for t in tokens[c0:k]] != words:
            continue
        pre = _parse_preamble(tokens, c0, spec, gap)
        if pre is None:
            continue
        s = res.value.start
        base = AstroDate(s.year, s.month, s.day)
        if pre["kind"] == "unit":
            value = _shift(base, pre["unit"], sign * pre["qty"])
            # the offset amount governs the SHIFT, never the result width:
            # "a week after X" is the single civil day one week from X, not a
            # week-wide span.  Every unit resolves to that one shifted day.
            span = _astro_day_span(value)
        else:
            span = _astro_day_span(_roll_weekday(base, pre["weekday"], sign))
        start = pre["start"]
        consumed = tuple(sorted(set(res.consumed) | set(range(start, b))))
        new_match = Match(match.construction, (start, match.span[1]),
                          match.slots, match.calendar)
        return new_match, Resolution(span, consumed)
    return None


#: how far past a date's end a trailing directional postposition may sit: the
#: marker plus a short "[lead] N UNIT" pre-amble and a small gap. Bounds the
#: forward scan so untrusted input can't drive it quadratic (a real postfix
#: offset marker is ~1-4 tokens past the date; this is deliberately generous).
_POSTFIX_SCAN_WINDOW = 24


def _try_offset_postfix(tokens, match: Match, res: Resolution, spec: LangSpec,
                        dir_phrases, gap) -> Optional[Pair]:
    """Compose an offset onto ``match``/``res`` when the directional marker is
    a **postposition** trailing the reference date, as in Hungarian
    ("3 nappal <date> előtt") and Basque ("<date> baino 3 egun lehenago").

    The ``[NUM] UNIT`` pre-amble sits either *between* the date and the trailing
    marker ("<date> baino **3 egun** lehenago", Basque/Turkish word order) or,
    when nothing separates them, *before* the date ("**3 nappal** <date>
    előtt", Hungarian).  Both are read by the same backward pre-amble parser;
    only its starting point differs.
    """
    e = match.span[1]
    # the trailing marker sits at or past the date's end -- immediately after
    # it (Hungarian "N UNIT <date> **előtt**") or past the pre-amble the date
    # is compared against (Basque "<date> baino N egun **lehenago**", Turkish
    # "<date> N gün **önce**").  Scan forward for the first marker phrase, but
    # only within a bounded window: a directional postposition governs the date
    # it trails, so it can only sit a few tokens past it (marker + a short
    # "[lead] N UNIT" pre-amble + gap).  Scanning to end-of-stream made this
    # O(tokens) per resolved match -> O(tokens^2) overall on untrusted input.
    for k in range(e, min(len(tokens), e + _POSTFIX_SCAN_WINDOW)):
        for sign, words in dir_phrases:
            n = len(words)
            if [t.text for t in tokens[k:k + n]] != words:
                continue
            end = k + n
            # pre-amble read backward from the marker: the between-words shape
            # ("<date> [lead] N UNIT <marker>") when the reading reaches back
            # exactly to the date's end; otherwise (nothing between) the
            # leading shape ("N UNIT <date> <marker>"), read backward from the
            # date's own start instead.
            pre = _parse_preamble(tokens, k, spec, gap)
            if pre is not None and pre["start"] == e:
                lo = match.span[0]
            else:
                pre = _parse_preamble(tokens, match.span[0], spec, gap)
                if pre is None:
                    continue
                lo = pre["start"]
            s = res.value.start
            base = AstroDate(s.year, s.month, s.day)
            if pre["kind"] == "unit":
                value = _shift(base, pre["unit"], sign * pre["qty"])
                # the offset governs the SHIFT, not the width: the single
                # shifted civil day, for every unit (see _try_offset).
                span = _astro_day_span(value)
            else:
                span = _astro_day_span(_roll_weekday(base, pre["weekday"], sign))
            consumed = tuple(sorted(set(res.consumed) | set(range(lo, end))))
            new_match = Match(match.construction, (lo, end),
                              match.slots, match.calendar)
            return new_match, Resolution(span, consumed)
    return None


#: hard backstop against any pathological non-convergence of the fixpoint
#: iteration; deep real phrases need only ~depth passes, well under this.
_FIXPOINT_CAP = 32


def _one_offset_pass(tokens, resolved: List[Pair], spec: LangSpec,
                     dir_phrases, gap) -> Tuple[List[Pair], int]:
    """A single composition pass over ``resolved``.

    Returns ``(out, grown)`` where ``grown`` is the number of tokens the
    composed matches gained this pass (0 when nothing composed) -- the
    progress signal the fixpoint loop iterates on.
    """
    composed = {}
    claimed = set()
    grown = 0
    for match, res in resolved:
        if match.construction not in DATE_CONSTRUCTIONS:
            continue
        got = (_try_offset(tokens, match, res, spec, dir_phrases, gap)
               or _try_offset_postfix(tokens, match, res, spec,
                                      dir_phrases, gap))
        if got is not None:
            gained = set(range(*got[0].span)) - set(range(*match.span))
            if not gained:
                # composed but consumed no new token: not real progress -- a
                # composition that would re-consume the same span would loop
                # forever, so treat it as a no-op and leave the match be.
                continue
            composed[id(match)] = got
            claimed.update(gained)
            grown += len(gained)
    if not composed:
        return resolved, 0
    out: List[Pair] = []
    for match, res in resolved:
        if id(match) in composed:
            out.append(composed[id(match)])
        elif not any(i in claimed for i in range(*match.span)):
            out.append((match, res))
    return out, grown


#: calendar-grain units -- advanced through :func:`_astro_add_months` -- keyed
#: to their month multiple (mirrors ``resolver._resolve_relative_offset``'s
#: elif chain and ``_shift``'s ``month_steps``).
_CALENDAR_UNIT_MONTHS = {"month": 1, "year": 12, "decade": 120,
                         "century": 1200, "millennium": 12000}

#: fixed-width units -- advanced through a plain ``timedelta`` -- keyed to
#: their length in seconds (mirrors ``nseries._DUR_UNIT_SECONDS``, plus
#: ``fortnight`` which that table also carries).
_FIXED_UNIT_SECONDS = {"second": 1, "minute": 60, "hour": 3600, "day": 86400,
                       "week": 604800, "fortnight": 1209600}

#: finest-to-coarsest ordering of every offset unit, used to pick the
#: composed span's granularity -- the same convention a BARE single-unit
#: offset already uses (an "in 2 days" is a day-wide span; the compound picks
#: whichever of its units is narrowest, exactly mirroring that rule).
_UNIT_RANK = {u: i for i, u in enumerate(
    ["second", "minute", "hour", "day", "week", "fortnight",
     "month", "year", "decade", "century", "millennium"])}


def _compound_unit_at(tokens, j, spec):
    """A ``[NUM|QUANT|article] UNIT`` chunk starting at ``j`` -> ``(unit,
    qty, end)`` or ``None`` when ``j`` does not open one."""
    n = len(tokens)
    qty = None
    k = j
    if k < n and tokens[k].is_number and tokens[k].value is not None:
        qty, k = float(tokens[k].value), k + 1
    elif k < n and tokens[k].text in spec.connectors.get("article", ()):
        qty, k = 1.0, k + 1
    elif k < n and tokens[k].text in spec.quantifiers:
        qty, k = spec.quantifiers[tokens[k].text], k + 1
    if qty is None:
        qty, k = 1.0, k
    if k < n and tokens[k].text in spec.units:
        unit = spec.units[tokens[k].text]
        if unit in _CALENDAR_UNIT_MONTHS or unit in _FIXED_UNIT_SECONDS:
            return unit, qty, k + 1
    return None


def _compound_unit_before(tokens, end, spec):
    """The mirror of :func:`_compound_unit_at`: a ``[NUM|QUANT|article]
    UNIT`` chunk ENDING exactly at ``end`` (exclusive) -> ``(unit, qty,
    start)`` or ``None`` when no such chunk sits immediately before ``end``.

    Used to fold a LEADING compound chunk into a postposed-marker offset
    ("3 months and 2 days **ago**", where the direction marker closes the
    phrase instead of opening it, so the trailing-scan
    :func:`_compound_unit_at` never sees the leading "3 months and").
    """
    if end <= 0:
        return None
    k = end - 1
    if tokens[k].text not in spec.units:
        return None
    unit = spec.units[tokens[k].text]
    if unit not in _CALENDAR_UNIT_MONTHS and unit not in _FIXED_UNIT_SECONDS:
        return None
    if k - 1 >= 0:
        p = tokens[k - 1]
        if p.is_number and p.value is not None:
            return unit, float(p.value), k - 1
        if p.text in spec.connectors.get("article", ()):
            return unit, 1.0, k - 1
        if p.text in spec.quantifiers:
            return unit, spec.quantifiers[p.text], k - 1
    return unit, 1.0, k


def _scan_trailing_chunks(tokens, idx, spec):
    """Fold every trailing ``[and|,] NUM UNIT`` chunk starting at ``idx``.

    Returns ``(chunks, consumed, end)``: the folded ``(unit, qty)`` pairs (in
    textual order), the token indices they occupy, and the index just past
    the last one consumed (== ``idx`` when nothing folded).
    """
    and_words = frozenset(spec.connectors.get("and", ()))
    lead_words = (frozenset(spec.connectors.get("article", ()))
                 | frozenset(spec.quantifiers))
    n = len(tokens)
    chunks = []
    consumed = set()
    while idx < n:
        j = idx
        if tokens[j].text in and_words:
            j += 1
        elif not (tokens[j].is_number or tokens[j].text in lead_words
                 or tokens[j].text in spec.units):
            # no connector AND the next token doesn't open a bare
            # comma-joined chunk ("1 year, 2 months" -- the comma itself
            # is dropped by the tokenizer, so a fresh chunk starts here
            # with no connector token at all): stop, nothing more to fold.
            break
        got = _compound_unit_at(tokens, j, spec)
        if got is None:
            break
        unit, qty, end = got
        chunks.append((unit, qty))
        consumed.update(range(idx, end))
        idx = end
    return chunks, consumed, idx


def _scan_leading_chunks(tokens, idx, spec):
    """The backward mirror of :func:`_scan_trailing_chunks`: fold every
    leading ``NUM UNIT [and|,]`` chunk ending exactly at ``idx``.

    Returns ``(chunks, consumed, start)``: the folded ``(unit, qty)`` pairs
    (in textual order), the token indices they occupy, and the index of the
    first one consumed (== ``idx`` when nothing folded).
    """
    and_words = frozenset(spec.connectors.get("and", ()))
    chunks = []
    consumed = set()
    while idx > 0:
        j = idx - 1
        used_connector = tokens[j].text in and_words
        chunk_end = j if used_connector else idx
        got = _compound_unit_before(tokens, chunk_end, spec)
        if got is None:
            break
        unit, qty, start = got
        chunks.insert(0, (unit, qty))
        consumed.update(range(start, idx))
        idx = start
    return chunks, consumed, idx


def apply_compound_offset(tokens, resolved: List[Pair], spec: LangSpec,
                          anchor: datetime) -> List[Pair]:
    """Compose a MIXED-grain offset compound ("in 3 months and 2 days",
    "in a year and a day", "1 year, 2 months and 3 days") into ONE point,
    instead of the bare :func:`~chronologia.extract.resolver._resolve_relative_offset`
    reading only its own leading ``NUM UNIT`` and stranding every further
    ``[and|,] NUM UNIT`` chunk in the remainder.

    Every chunk shares the leading offset's sign (direction marker):
    "in 3 months and 2 days" both add, "3 months and 2 days ago" both
    subtract -- a compound never mixes directions, so one marker covers the
    whole phrase.

    Composition happens in TWO passes over the summed chunks, not one
    sequential walk, so the result never depends on the TEXTUAL order the
    units were said in ("in 3 months and 2 days" and the reversed "in 2 days
    and 3 months" land on the identical instant): every calendar-grain
    chunk (month/year/decade/century/millennium) is summed to a single
    month-count and applied first, in :class:`AstroDate`'s own proleptic
    space (never stdlib ``datetime``, whose year bounds a BC/deep-time
    composition would overrun); every fixed-width chunk (second .. fortnight)
    is summed to a single ``timedelta`` and applied second. Calendar-then-
    fixed is the natural reading order in any case ("3 months and 2 days"
    means the 15th, 3 months on, plus 2 more days) and, applied AFTER the
    month roll, never re-triggers month-end clamping.

    The composed span is a POINT of the FINEST unit named anywhere in the
    compound ("in 3 months and 2 days" -> a DAY-wide span, matching what a
    bare "in 2 days" already returns) -- the same granularity convention the
    single-unit reading already follows, just extended to the widest (finest)
    grain present.

    A postposed marker ("3 months and 2 days **ago**") closes the phrase
    instead of opening it, so any LEADING ``NUM UNIT [and|,]`` chunk sits
    BEFORE the matched span rather than after it -- folded here by scanning
    :func:`_scan_leading_chunks` backward from the match whenever the marker
    is the match's own last token.  Both scans run (a compound could, in
    principle, carry chunks on both sides); the direction marker's sign
    covers every folded chunk regardless of which side it came from, so
    "3 months and 2 days ago" and "2 days and 3 months ago" land on the
    identical instant, same as the forward-only compounds already do.

    A second, sibling family folds into a rolling ``rel_span`` ("the next 2
    weeks and 3 days", "the last 2 weeks and 3 days"): unlike
    ``relative_offset``'s single point, ``rel_span`` already resolves to a
    ``[today, far)`` / ``[far, today)`` span (:meth:`_resolve_rel_span`), so
    a trailing chunk EXTENDS the rolling ``far`` end further in the same
    direction as the ``next``/``last`` marker, rather than composing a new
    point.

    A lone, un-extended match (no chunk found on either side) is returned
    untouched; only constructions actually carrying a composable chunk are
    rewritten.
    """
    out = []
    for m, r in resolved:
        if m.construction == "rel_span":
            out.append(_fold_rel_span(tokens, m, r, spec))
            continue
        if m.construction != "relative_offset":
            out.append((m, r))
            continue
        marker_tok = m.slots.get("MARKER")
        if marker_tok is None or marker_tok.text not in spec.directions:
            out.append((m, r))
            continue
        sign = spec.directions[marker_tok.text]
        usg_tok = m.slots.get("USG")
        if usg_tok is not None:
            unit0 = spec.singular_units.get(usg_tok.text)
        else:
            unit_tok = m.slots.get("UNIT")
            unit0 = spec.units.get(unit_tok.text) if unit_tok is not None else None
        if unit0 is None or (unit0 not in _CALENDAR_UNIT_MONTHS
                             and unit0 not in _FIXED_UNIT_SECONDS):
            out.append((m, r))
            continue
        num_tok = m.slots.get("NUM")
        quant_tok = m.slots.get("QUANT")
        if num_tok is not None and quant_tok is not None:
            qty0 = float(num_tok.value) * spec.quantifiers[quant_tok.text]
        elif num_tok is not None:
            qty0 = float(num_tok.value)
        elif quant_tok is not None:
            qty0 = spec.quantifiers[quant_tok.text]
        else:
            qty0 = 1.0
        chunks = [(unit0, qty0)]
        consumed = set(range(*m.span))
        trail_chunks, trail_consumed, _ = _scan_trailing_chunks(
            tokens, m.span[1], spec)
        chunks.extend(trail_chunks)
        consumed.update(trail_consumed)
        # a POSTPOSED marker (the match's own last token) closes the phrase,
        # so a leading chunk sits before the match, not after it -- only
        # scanned in that shape; a preposed marker ("in 3 months") already
        # has nothing meaningful before it to fold.
        if marker_tok.index == m.span[1] - 1:
            lead_chunks, lead_consumed, _ = _scan_leading_chunks(
                tokens, m.span[0], spec)
            chunks = lead_chunks + chunks
            consumed.update(lead_consumed)
        if len(chunks) < 2:
            out.append((m, r))
            continue
        total_months = sum(sign * qty * _CALENDAR_UNIT_MONTHS[u]
                           for u, qty in chunks if u in _CALENDAR_UNIT_MONTHS)
        total_seconds = sum(sign * qty * _FIXED_UNIT_SECONDS[u]
                            for u, qty in chunks if u in _FIXED_UNIT_SECONDS)
        base = AstroDate.from_datetime(anchor)
        cur = _astro_add_months(base, int(round(total_months))) \
            if total_months else base
        if total_seconds:
            cur = cur + timedelta(seconds=total_seconds)
        finest = min((u for u, _ in chunks), key=lambda u: _UNIT_RANK[u])
        end_pt = _shift(cur, finest, 1)
        new_res = Resolution(DateSpan(cur, end_pt), tuple(sorted(consumed)),
                             r.week_widened)
        out.append((m, new_res))
    return out


def _fold_rel_span(tokens, m: Match, r: Resolution, spec: LangSpec) -> Pair:
    """Extend a resolved ``rel_span`` ("the next/last N units") by any
    trailing ``[and|,] NUM UNIT`` chunk ("the next 2 weeks **and 3 days**"),
    otherwise stranded in the remainder.

    ``rel_span`` already resolves to a rolling ``[today, far)`` (``next``) or
    ``[far, today)`` (``last``) span; a trailing chunk pushes ``far`` further
    in the SAME direction as the ``next``/``last`` marker -- calendar-grain
    chunks first (in :class:`AstroDate` space), fixed-width chunks second,
    mirroring the point-offset compound's own two-pass convention.
    """
    rel_tok = m.slots.get("REL_MARKER")
    rel = spec.rel_markers.get(rel_tok.text) if rel_tok is not None else None
    if not rel:
        return m, r
    chunks, chunk_consumed, _ = _scan_trailing_chunks(tokens, m.span[1], spec)
    if not chunks:
        return m, r
    sign = 1 if rel > 0 else -1
    total_months = sum(sign * qty * _CALENDAR_UNIT_MONTHS[u]
                       for u, qty in chunks if u in _CALENDAR_UNIT_MONTHS)
    total_seconds = sum(sign * qty * _FIXED_UNIT_SECONDS[u]
                        for u, qty in chunks if u in _FIXED_UNIT_SECONDS)
    lo, hi = r.value.start, r.value.end
    far = hi if rel > 0 else lo
    if total_months:
        far = _astro_add_months(far, int(round(total_months)))
    if total_seconds:
        far = far + timedelta(seconds=total_seconds)
    new_span = DateSpan(lo, far) if rel > 0 else DateSpan(far, hi)
    consumed = set(r.consumed) | chunk_consumed
    return m, Resolution(new_span, tuple(sorted(consumed)), r.week_widened)


def apply_anchored_offset(tokens, resolved: List[Pair],
                          spec: LangSpec) -> List[Pair]:
    """Rewrite every date reference carrying a stranded offset pre-amble,
    iterating the composition to a **fixpoint**.

    A single pass composes exactly one outer offset pre-amble onto each date
    reference ("the day after <ref>").  Nesting of arbitrary depth ("the day
    after the day after the day after tomorrow") needs one pass per layer, so
    the pass is repeated until a pass composes nothing new (the result equals
    its input) -- each iteration strictly consuming more tokens, absorbing one
    further outer layer.  Depth<=2 and non-nested phrases are unchanged: their
    second pass finds nothing to compose and stops immediately.

    A stray sub-match over a pre-amble (a bare weekday read as its own
    ``weekday_ref``, say) is dropped so the composed reference wins.
    """
    after = spec.connectors.get("after", frozenset())
    before = spec.connectors.get("before", frozenset())
    # ``marker_offset_after.voc`` supplies per-locale "after"-synonyms that
    # apply ONLY to this offset-WITH-explicit-anchor shape ("2 weeks from
    # june 1st" == "2 weeks after june 1st").  It is a deliberate opt-in
    # vocab, NOT the locale's generic "from" connector: in many locales the
    # same surface marks "the week OF <date>" (uk "тиждень від 4 липня"),
    # and reading it as an offset there shifts the span a whole unit.  A
    # locale without the file keeps its generic "from" untouched by this
    # pass; the recurrence "from X to Y" grammar (nseries.py) and the
    # date_range construction are never affected either way -- they match
    # their own token patterns and never reach this pass.
    from_as_after = spec.connectors.get("offset_after", frozenset())
    if not after and not before and not from_as_after:
        return resolved
    gap = _gap_words(spec)
    dir_phrases = ([(1, w) for w in _phrases(after | from_as_after)]
                   + [(-1, w) for w in _phrases(before)])
    # iterate to a fixpoint: a pass that grows nothing (grown == 0) is the
    # signal to stop; the strictly-monotonic token growth guarantees
    # termination, with _FIXPOINT_CAP as a hard backstop.
    for _ in range(_FIXPOINT_CAP):
        resolved, grown = _one_offset_pass(tokens, resolved, spec,
                                           dir_phrases, gap)
        if grown == 0:
            break
    return resolved


# -- feature 2: ordinal counting from the anchor --------------------------

def _weekday_of(text: str, spec: LangSpec) -> Optional[int]:
    """A weekday index for ``text``, tolerating a trailing plural suffix
    ("fridays" -> friday)."""
    if text in spec.weekdays:
        return spec.weekdays[text]
    for suf in spec.connectors.get("plural", ()):
        if suf and text.endswith(suf) and text[:-len(suf)] in spec.weekdays:
            return spec.weekdays[text[:-len(suf)]]
    return None


def _nth_weekday(anchor: datetime, target: int, n: int, sign: int) -> datetime:
    """The ``n``-th occurrence of ``target`` weekday strictly after
    (``sign>0``) or before (``sign<0``) ``anchor``."""
    base = _midnight(anchor)
    if sign > 0:
        ahead = (target - anchor.weekday()) % 7 or 7
        return base + timedelta(days=ahead + 7 * (n - 1))
    back = (anchor.weekday() - target) % 7 or 7
    return base - timedelta(days=back + 7 * (n - 1))


def _match_at(tokens, i: int, surfaces) -> int:
    """Number of tokens a (possibly multi-word) surface consumes at ``i``,
    longest first; 0 if none matches ("a partir de", "il y a")."""
    best = 0
    for words in _phrases(surfaces):
        n = len(words)
        if i + n <= len(tokens) \
                and [t.text for t in tokens[i:i + n]] == words:
            best = max(best, n)
    return best


def _count_weekday(tokens, spec: LangSpec, anchor) -> Optional[Pair]:
    """"3 fridays from now" / "2 mondays ago" -> the N-th weekday from now.

    The trailing marker is either a past marker ("ago") or a future
    "<from> <now>" pair; both are matched as phrases, so multi-word
    connectors ("a partir de agora", "à partir de maintenant") work.
    """
    from_words = spec.connectors.get("from", frozenset())
    present = spec.connectors.get("present", frozenset())
    ago = (frozenset(spec.connectors.get("ago", ()))
           | frozenset(s for s, v in spec.directions.items() if v < 0))
    for i, t in enumerate(tokens):
        if not (t.is_number and t.value and t.value >= 1):
            continue
        w = i + 1
        if w >= len(tokens):
            continue
        wd = _weekday_of(tokens[w].text, spec)
        if wd is None:
            continue
        p = w + 1
        ago_n = _match_at(tokens, p, ago)
        if ago_n:
            sign, start, end = -1, i, p + ago_n
        elif (i > 0 and tokens[i - 1].text in ago
                and tokens[w].text not in spec.units):
            # a LEADING past marker before the count: Romance puts the past
            # particle first ("hace 2 lunes" == 2 mondays ago, "il y a 2
            # lundis"), where the trailing scan never sees it.  Consume it too.
            # Skip when the "weekday" is ALSO a unit surface: Romanian "luni" is
            # both Monday and "months", and "acum 2 luni" is 2 MONTHS ago -- let
            # the unit-offset reading win rather than fabricate a Monday count.
            sign, start, end = -1, i - 1, p
        else:
            from_n = _match_at(tokens, p, from_words)
            pres_n = _match_at(tokens, p + from_n, present) if from_n else 0
            if not pres_n:
                continue
            sign, start, end = 1, i, p + from_n + pres_n
        value = _nth_weekday(anchor, wd, int(t.value), sign)
        return (Match("weekday_count", (start, end), {}),
                Resolution(_day_span(value), tuple(range(start, end))))
    return None


def _weekend_span(anchor, spec: LangSpec, rel: int) -> DateSpan:
    """The two-day weekend ``rel`` weeks from the anchor's own weekend."""
    base = _midnight(anchor)
    start_idx = _WEEK_START.get(spec.conventions.week_start, 0)
    week_start = base - timedelta(days=(anchor.weekday() - start_idx) % 7)
    wknd = spec.conventions.weekend_start
    first = (week_start + timedelta(days=(wknd - start_idx) % 7)
             + timedelta(weeks=rel))
    s = AstroDate.from_datetime(first)
    return DateSpan(s, s + timedelta(days=2))


def _weekend_after_next(tokens, spec: LangSpec, anchor) -> Optional[Pair]:
    """"the weekend after next": skip one weekend, take the following one."""
    after = spec.connectors.get("after", frozenset())
    if not after or not spec.weekend_words:
        return None
    nextw = frozenset(s for s, v in spec.rel_markers.items() if v > 0)
    gap = _gap_words(spec)
    n = len(tokens)
    for i, t in enumerate(tokens):
        if t.text not in spec.weekend_words or i + 1 >= n \
                or tokens[i + 1].text not in after:
            continue
        # "weekend after next" -- an article/of gap may sit between the
        # directional marker and the "next" it counts past ("nach *dem*
        # nächsten", "après *le* prochain", "depois *do* próximo")
        k = i + 2
        while k < n and tokens[k].text in gap:
            k += 1
        if k < n and tokens[k].text in nextw:
            start = i - 1 if i - 1 >= 0 and tokens[i - 1].text in gap else i
            match = Match("weekend_after_next", (start, k + 1), {})
            return match, Resolution(_weekend_span(anchor, spec, 2),
                                     tuple(range(start, k + 1)))
    return None


def _weekday_after_next(tokens, spec: LangSpec, anchor) -> Optional[Pair]:
    """"the <weekday> after next": the occurrence of the weekday one week past
    its next one -- next <weekday> + 7 days.

    The same skip-one "after next" family as "the day/weekend after next"
    (#303/#307), extended to the WEEKDAY unit.  The bare matcher reads the
    weekday as its own ``weekday_ref`` (next occurrence) and strands "the
    after next" -- a silent-wrong that pointed "the Saturday after next" at
    *next* Saturday instead of the one after.  Composed here beside the
    weekend skip-one so both share the anchor-relative machinery.
    """
    after = spec.connectors.get("after", frozenset())
    if not after:
        return None
    nextw = frozenset(s for s, v in spec.rel_markers.items() if v > 0)
    gap = _gap_words(spec)
    n = len(tokens)
    for i, t in enumerate(tokens):
        wd = _weekday_of(t.text, spec)
        if wd is None or i + 1 >= n:
            continue
        an = _match_at(tokens, i + 1, after)          # "after" (possibly multiword)
        if not an:
            continue
        k = i + 1 + an
        while k < n and tokens[k].text in gap:        # article/of gap before "next"
            k += 1
        if k < n and tokens[k].text in nextw:
            start = i - 1 if i - 1 >= 0 and tokens[i - 1].text in gap else i
            value = _nth_weekday(anchor, wd, 1, 1) + timedelta(days=7)
            match = Match("weekday_after_next", (start, k + 1), {})
            return match, Resolution(_day_span(value),
                                     tuple(range(start, k + 1)))
    return None


def _weekend_before_last(tokens, spec: LangSpec, anchor) -> Optional[Pair]:
    """"the weekend before last": the mirror of ``_weekend_after_next`` -- two
    weekends into the PAST, the weekend before *last* weekend (rel == -2).

    The bare matcher reads only "the weekend" (its own ``weekend_ref``, rel 0
    == this/upcoming weekend) and strands "before last" -- a silent-wrong that
    pointed the phrase at the future.  Composed here beside the forward
    skip-one so the two directions share one anchor-relative weekend engine.
    """
    before = spec.connectors.get("before", frozenset())
    if not before or not spec.weekend_words:
        return None
    lastw = frozenset(s for s, v in spec.rel_markers.items() if v < 0)
    gap = _gap_words(spec)
    n = len(tokens)
    for i, t in enumerate(tokens):
        if t.text not in spec.weekend_words or i + 1 >= n \
                or tokens[i + 1].text not in before:
            continue
        k = i + 2
        while k < n and tokens[k].text in gap:      # article/of gap before "last"
            k += 1
        if k < n and tokens[k].text in lastw:
            start = i - 1 if i - 1 >= 0 and tokens[i - 1].text in gap else i
            match = Match("weekend_before_last", (start, k + 1), {})
            return match, Resolution(_weekend_span(anchor, spec, -2),
                                     tuple(range(start, k + 1)))
    return None


def _weekend_ago(tokens, spec: LangSpec, anchor) -> Optional[Pair]:
    """"<N> weekends ago" / "a weekend ago": the weekend N whole weekends before
    the anchor's own weekend (rel == -N).  "one/a weekend ago" == last weekend
    (rel -1); "two weekends ago" the weekend before that (rel -2).

    Mirrors ``_count_weekday`` ("2 mondays ago") for the weekend unit, which
    the bare matcher otherwise read as an upcoming ``weekend_ref`` with the
    count word stranded.
    """
    if not spec.weekend_words:
        return None
    ago = (frozenset(spec.connectors.get("ago", ()))
           | frozenset(s for s, v in spec.directions.items() if v < 0))
    if not ago:
        return None
    indef = frozenset(spec.connectors.get("indef", ()))
    n = len(tokens)
    for i, t in enumerate(tokens):
        if t.text not in spec.weekend_words:
            continue
        a = _match_at(tokens, i + 1, ago)
        if not a:
            continue
        end = i + 1 + a
        # the count preceding the weekend word: a digit ("two"), a quantifier
        # ("a"/"couple"), or an indefinite article ("a weekend ago" == one).
        start, qty = i, 1
        j = i - 1
        if j >= 0 and tokens[j].is_number and tokens[j].value is not None:
            qty, start = int(tokens[j].value), j
        elif j >= 0 and tokens[j].text in spec.quantifiers:
            qty, start = int(spec.quantifiers[tokens[j].text]), j
        elif j >= 0 and tokens[j].text in indef:
            start = j
        if qty < 1:
            continue
        match = Match("weekend_ago", (start, end), {})
        return match, Resolution(_weekend_span(anchor, spec, -qty),
                                 tuple(range(start, end)))
    return None


def _nth_weekday_after_daymonth(tokens, spec: LangSpec, anchor) -> Optional[Pair]:
    """"the <ordinal> <weekday> after the <day-of-month>": the N-th ``weekday``
    whose date is strictly greater than that day-of-month.

    The day-of-month names the anchor's OWN calendar month (a within-month
    reference -- "the 15th" here is *this* month's 15th, not a prefer-future
    roll), and the ordinal selects which occurrence of the weekday past it:
    "the first Friday after the 15th" is the 1st Friday whose date > the 15th,
    "the second ..." the 2nd.  A missing ordinal means the first.

    Without this the bare matcher reads the weekday as a stray ``weekday_ref``
    (its own next occurrence) and strands the ordinal and the day-of-month in
    the remainder -- a silent-wrong.  Composed here (rather than by the offset
    pass) because the anchor day-of-month does not itself resolve to a bare
    date, so there is no reference match to roll from; the weekday-stepping
    reuses :func:`_nth_weekday`, the same helper the count constructions use.
    """
    after = spec.connectors.get("after", frozenset())
    if not after:
        return None
    gap = _gap_words(spec)
    n = len(tokens)
    for i, t in enumerate(tokens):
        wd = _weekday_of(t.text, spec)
        if wd is None:
            continue
        k = i + 1
        an = _match_at(tokens, k, after)          # "after" (possibly multiword)
        if not an:
            continue
        k += an
        while k < n and tokens[k].text in gap:    # skip article/of gap
            k += 1
        if k >= n:
            continue
        dtok = tokens[k]                          # the day-of-month digit
        if not (dtok.is_number and dtok.value is not None):
            continue
        day = int(dtok.value)
        if not 1 <= day <= 31:
            continue
        # only a BARE day-of-month anchors here.  A day followed by a month
        # ("monday after 1 april") is a full calendar date the offset pass
        # already rolls the weekday onto -- leave it to that pass rather than
        # re-reading the day as *this* month's.  A day followed by a WEEKDAY is
        # not a day-of-month at all but an ordinal count on that weekday ("the
        # 2nd MONDAY"): reading its "2" as June 2 fabricated a wrong date, so
        # bail here too and let the ordinal-weekday reading (or None) stand.
        m = k + 1
        while m < n and tokens[m].text in gap:
            m += 1
        if m < n and (tokens[m].text in spec.months
                      or tokens[m].text in spec.weekdays):
            continue
        # an optional ordinal ("first"/"second" -> 1/2, folded to a digit)
        # leads the weekday; absent, the first occurrence is meant.
        start, count = i, 1
        j = i - 1
        if j >= 0 and tokens[j].is_number and tokens[j].value is not None:
            val = int(tokens[j].value)
            if val >= 1:
                count, start = val, j
        if start - 1 >= 0 and tokens[start - 1].text in gap:  # leading article
            start -= 1
        try:
            base = datetime(anchor.year, anchor.month, day)
        except ValueError:                        # no such day this month
            continue
        value = _nth_weekday(base, wd, count, 1)
        end = k + 1
        return (Match("nth_weekday_after", (start, end), {}),
                Resolution(_day_span(value), tuple(range(start, end))))
    return None


def apply_ordinal_count(tokens, spec: LangSpec, anchor) -> Optional[Pair]:
    """The anchor-relative counting constructions (weekday count, weekend
    after next, Nth weekday after a day-of-month); the first that fires wins."""
    return (_count_weekday(tokens, spec, anchor)
            or _weekday_after_next(tokens, spec, anchor)
            or _weekend_after_next(tokens, spec, anchor)
            or _weekend_before_last(tokens, spec, anchor)
            or _weekend_ago(tokens, spec, anchor)
            or _nth_weekday_after_daymonth(tokens, spec, anchor))
