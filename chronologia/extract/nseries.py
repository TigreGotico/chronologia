"""Extraction beyond a single span: durations, multi-mention, recurrence.

Three public edges built on the *same* shared pipeline that
:func:`~chronologia.extract.extract_timespan` uses -- the language tokenizer,
number fold and typed vocabulary maps -- so every language is still data only
and the engine core stays language-agnostic:

* :func:`extract_duration` -- a *length* of time ("an hour and a half",
  "2 days 4 hours") as a :class:`datetime.timedelta`, with the leftover text.
* :func:`extract_timespans` -- **all** non-overlapping temporal mentions in a
  sentence, in reading order, each with its token extent (the matcher already
  returns non-overlapping matches; this simply resolves every one instead of
  collapsing to the first).
* :func:`extract_recurrence` -- a recurring phrase ("every friday", "first
  monday of every month") mapped onto the repo's RFC 5545
  :class:`~chronologia.recurrence.Recurrence`, with the leftover text.

Facts stay in the ``locale/<code>/`` vocabulary (weekday names, the ``every``
marker, unit and fraction words); the grammar that assembles those facts is
here, engine-side, so the "N units ago" sign-flip / off-by-a-language bug
class stays unwritable.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, NamedTuple, Optional, Tuple, Union

from chronologia.astrodate import DateSpan
from chronologia.extract.pipeline import fold_tokens, pretokens, require_text
from chronologia.extract.timespan import (_RANGE_BETWEEN, _RANGE_FROM,
                                          _RANGE_TO, _conn_surfaces,
                                          _exclusion_vetoes, _extract_range,
                                          _resolve_scale_mode,
                                          _timespan_engine, extract_timespan)
from chronologia.recurrence import HolidayRecurrence, Recurrence
from chronologia.recurrence import every as _build_every
from chronologia.recurrence import nth_weekday_of_month as _nth_weekday_of_month

# --------------------------------------------------------------------------
# Durations.
# --------------------------------------------------------------------------
#: Fixed-width offset units and their length in seconds.  Month / year / decade
#: are calendar quantities, not fixed durations (a "month" is 28..31 days), so
#: they are deliberately *not* durations -- a phrase naming one yields no
#: duration and is left in the remainder.  The fixed set below tiles exactly.
_DUR_UNIT_SECONDS = {
    "second": 1,
    "minute": 60,
    "hour": 3600,
    "day": 86400,
    "week": 604800,
    "fortnight": 1209600,
}


class DurationResult(NamedTuple):
    """Return of :func:`extract_duration`: a length of time and the leftover text.

    A plain 2-tuple ``(duration, remainder)`` for unpacking, plus the named
    fields ``.duration`` (a :class:`datetime.timedelta`) and ``.remainder``.
    """
    duration: timedelta
    remainder: str


def _fraction_words(spec):
    """Quantifier surfaces standing for a proper fraction (``half`` -> 0.5,
    ``quarter`` -> 0.25) -- a count below one."""
    return {s: v for s, v in spec.quantifiers.items() if 0 < v < 1}


def _article_words(spec):
    """Surfaces that act as bare articles/units-of-one filler (``a``, ``an``,
    ``the``) -- a leading one before a count is skipped, a lone one before a
    unit counts as one."""
    forms = set(spec.connectors.get("article", ()))
    forms |= {s for s, v in spec.quantifiers.items() if v == 1.0}
    return forms


def _and_words(spec):
    return set(spec.connectors.get("and", ()))


def extract_duration(
        text: str,
        lang: str = "en-us",
) -> Optional[DurationResult]:
    """Extract a :class:`datetime.timedelta` length from ``text``.

    Reads the fixed-width units minute / hour / day / week / fortnight, summing
    every count it finds ("2 days 4 hours" -> 52 hours), including fractional
    counts ("half an hour" -> 30 min, "quarter of an hour" -> 15 min) and the
    trailing "... and a half" idiom ("an hour and a half" -> 90 min).  Numbers
    are folded by ``ovos-number-parser`` before matching, so "90 minutes" and
    "ninety minutes" read alike.

    Calendar-ambiguous units (month, year, decade, ...) are **not** durations
    and are left in the remainder.  Returns a :class:`DurationResult` -- a
    ``(duration, remainder)`` named tuple (unpack it, or read ``.duration`` /
    ``.remainder``) -- or ``None`` when the text names no fixed-width length.

    ``text`` must be a ``str``; anything else raises :class:`TypeError`.
    Text that names no length, the empty string included, returns ``None``.
    """
    require_text(text, "extract_duration")
    engine = _timespan_engine(lang)
    spec = engine.spec
    tokens = engine.tokenize(text)
    fracs = _fraction_words(spec)
    articles = _article_words(spec)
    of_words = set(spec.connectors.get("of", ()))
    and_words = _and_words(spec)
    filler = articles | of_words
    n = len(tokens)

    def _read_scale(k):
        """A thousand-scale count at ``k`` -> ``(value, end)`` or ``None``.

        The spelled thousand words ("mil", "bin", "thousand") are withheld from
        the generic number fold because they head the deep-time frame ("mil
        milhões de anos"), so a duration count built on one is not folded for us.
        A fixed-width duration has no deep-time reading, so compose it here:
        ``mil`` = 1000, ``dois mil`` = 2000, ``mil e quinhentos`` = 1500,
        ``bin beş yüz`` = 1500 (an optional leading multiplier, the scale word,
        then an optional trailing hundreds chunk across an optional connector).
        """
        j = k
        mult = None
        if j < n and tokens[j].is_number:
            try:
                mult = float(tokens[j].value)
            except (TypeError, ValueError, OverflowError):
                return None
            j += 1
        if j >= n or tokens[j].text not in spec.scales:
            return None
        val = (mult if mult is not None else 1.0) * spec.scales[tokens[j].text]
        j += 1
        end = j + 1 if j < n and tokens[j].text in and_words else j
        if end < n and tokens[end].is_number:
            try:
                val += float(tokens[end].value)
                j = end + 1
            except (TypeError, ValueError, OverflowError):
                pass
        return val, j

    def _read_additive(k):
        """`` and a half`` / `` and a quarter`` at index ``k`` -> (frac, end)."""
        j = k
        # A Semitic waw/vav conjunction fuses onto the following fraction word as
        # ONE token (Arabic ونصف = و+نصف "and a half", Hebrew וחצي): the tokenizer
        # splits this clitic before a digit but not before a letter word, so the
        # standalone-conjunction test below misses it and the fraction is
        # dropped ("ساعتان ونصف" -> 2:00 instead of 2:30).  Recognise the fused
        # form directly, gated on the remainder being a known fraction word so
        # only <and-word><fraction> matches (a common و-prefixed word like واحد
        # does not fire).
        if j < n:
            for aw in and_words:
                txt = tokens[j].text
                if txt.startswith(aw) and len(txt) > len(aw) \
                        and txt[len(aw):] in fracs:
                    return fracs[txt[len(aw):]], j + 1
        if j < n and tokens[j].text in and_words:
            j += 1
            while j < n and tokens[j].text in articles:
                j += 1
            if j < n and tokens[j].text in fracs:
                return fracs[tokens[j].text], j + 1
            # A fraction the folder already turned into a numeric token (German
            # "eine halbe" -> 0.5) is invisible to the surface-word lookup
            # above, so "eine Stunde und eine halbe" would drop the half.  Read
            # a folded proper fraction (0 < value < 1) here too, matching the
            # English "... and a half" idiom across the inflecting languages.
            if (j < n and tokens[j].is_number and tokens[j].value is not None
                    and 0 < tokens[j].value < 1):
                return float(tokens[j].value), j + 1
        return None, k

    total = 0.0
    found = False
    consumed = set()
    i = 0
    while i < n:
        j = i
        count = None
        frac_lead = False
        # A Semitic dual-noun unit fuses the count "two" with the unit into one
        # token (Arabic ساعتان / ساعتين == two hours, Hebrew שעתיים) -- there is
        # no separate "two" word to read, so it is handled up front as exactly
        # (2 x unit).  A trailing "... and a half" still attaches ("ساعتان
        # ونصف"), matching the ordinary count-then-unit path below.
        dual = spec.dual_units.get(tokens[i].text)
        if dual is not None and dual in _DUR_UNIT_SECONDS:
            secs = 2.0 * _DUR_UNIT_SECONDS[dual]
            end = i + 1
            add2, end2 = _read_additive(end)
            if add2 is not None:
                secs += add2 * _DUR_UNIT_SECONDS[dual]
                end = end2
            total += secs
            found = True
            consumed.update(range(i, end))
            i = end
            continue
        # a leading article: "a day" -> count 1; "a couple of days" -> skip it.
        if tokens[j].text in articles:
            if j + 1 < n and (tokens[j + 1].is_number
                              or tokens[j + 1].text in fracs):
                j += 1
            else:
                count, j = 1.0, j + 1
        if count is None and j < n:
            # a thousand-scale count ("mil e quinhentos dias" = 1500 days) --
            # composed here because the fold withholds the scale word (below).
            scaled = _read_scale(j)
            if scaled is not None:
                count, j = scaled
            elif tokens[j].is_number:
                # A digit run hundreds of characters long folds to an int no
                # C double can hold ("1" * 400): float() itself overflows
                # before a unit is even matched.  Such a count names no real
                # length, so the token is treated as if it weren't numeric
                # and scanning moves on, rather than raising past the caller.
                try:
                    count, j = float(tokens[j].value), j + 1
                except OverflowError:
                    count, j = None, i + 1
                # a fraction word right after the count multiplies it: "three
                # quarters (of an hour)", "eine viertel stunde" (a quarter hour)
                if count is not None and j < n and tokens[j].text in fracs:
                    count, j = count * fracs[tokens[j].text], j + 1
            elif tokens[j].text in fracs:
                count, j, frac_lead = fracs[tokens[j].text], j + 1, True
            elif tokens[j].text in spec.quantifiers:
                count, j = spec.quantifiers[tokens[j].text], j + 1
        if count is None:
            i = max(i + 1, j)
            continue
        # "one and a half hours": the fraction precedes the unit.
        add, j = _read_additive(j)
        if add is not None:
            count += add
        while j < n and tokens[j].text in filler:
            j += 1
        # "half of a hundred days" = 0.5 * 100: a leading fraction ("half"/
        # "quarter") may scale an explicit following count -- across the "of a"
        # filler already skipped above -- rather than an implicit 1.  Guarded to
        # the fraction-lead case so a plain "a hundred days" (count 1 from a
        # number) is untouched, and "half a day" (unit directly after) is too.
        if frac_lead and j < n:
            scaled = _read_scale(j)
            if scaled is not None:
                count *= scaled[0]
                j = scaled[1]
                while j < n and tokens[j].text in filler:
                    j += 1
            elif tokens[j].is_number and tokens[j].value is not None:
                try:
                    count *= float(tokens[j].value)
                    j += 1
                except OverflowError:
                    pass
                while j < n and tokens[j].text in filler:
                    j += 1
        if (j < n and tokens[j].text in spec.units
                and spec.units[tokens[j].text] in _DUR_UNIT_SECONDS):
            unit = spec.units[tokens[j].text]
            secs = count * _DUR_UNIT_SECONDS[unit]
            end = j + 1
            # "an hour and a half": the fraction trails the unit.
            add2, end2 = _read_additive(end)
            if add2 is not None:
                secs += add2 * _DUR_UNIT_SECONDS[unit]
                end = end2
            total += secs
            found = True
            consumed.update(range(i, end))
            i = end
            continue
        i += 1

    if not found:
        return None
    # A connective "and" bridging two consumed components ("two hours *and*
    # fifteen minutes") is part of the compound, not leftover text: fold it in
    # so the remainder carries only genuinely non-duration words.
    for k in range(1, n - 1):
        if (k not in consumed and tokens[k].text in and_words
                and k - 1 in consumed and k + 1 in consumed):
            consumed.add(k)
    # A duration RANGE ("3 to 5 days", "2-4 hours") is read as its UPPER bound
    # -- the widest length the phrase can mean -- since the public return type
    # is a single ``timedelta``, not an interval.  The lower bound plus its
    # range-``to`` separator would otherwise strand a confusing "3 to" in the
    # remainder; fold them in so the leftover carries only genuinely
    # non-duration words.  (A real low..high interval would need an API change
    # and is left as a follow-up.)
    for k in range(1, n - 1):
        if (k not in consumed and tokens[k].text in _RANGE_TO
                and k - 1 not in consumed and tokens[k - 1].is_number
                and k + 1 in consumed):
            consumed.update((k - 1, k))
    from chronologia.extract.pipeline import render_remainder
    remainder = render_remainder(text, [t for t in tokens
                                        if t.index not in consumed])
    # A count within float range can still sum to more seconds than a C int
    # (or timedelta.max, ~999999999 days) can represent -- e.g. a plain
    # digit-run count like 99999999999999999999 days.  That names a real
    # number but not a representable duration, so it is reported as None:
    # the honest "I can't express this length" rather than a raised error
    # or a silently wrong clamp to some arbitrary huge-but-wrong value.
    try:
        return DurationResult(timedelta(seconds=total), remainder)
    except OverflowError:
        return None


# --------------------------------------------------------------------------
# Multi-mention.
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class TimeMention:
    """One temporal mention inside a longer text.

    ``span`` is its :class:`~chronologia.astrodate.DateSpan`; ``text`` the
    surface substring it was read from; ``token_span`` the half-open
    ``(start, end)`` token extent in the tokenised sentence; ``char_span`` the
    half-open ``(start, end)`` **character** extent into the ORIGINAL
    utterance, so ``utterance[char_span[0]:char_span[1]]`` recovers the exact
    substring.  ``char_span`` is derived from the tokenizer's own recorded
    offsets (never by re-searching the string); it is ``None`` only when the
    mention's tokens were all engine-synthesised and carry no offset.

    ``confidence`` is the deterministic score in ``(0, 1]`` that this reading
    is the intended one (see :mod:`chronologia.extract.confidence`); it is
    **not** a probability.  It is excluded from equality/hash (``compare=False``)
    so a mention still compares by its identity (span + extent), never by a
    derived score.
    """
    span: DateSpan
    text: str
    token_span: Tuple[int, int]
    char_span: Optional[Tuple[int, int]] = None
    confidence: float = field(default=1.0, compare=False)


def extract_timespans(
        text: str,
        lang: str = "en-us",
        anchor: Optional[datetime] = None,
        scale: Optional[str] = None,
) -> List[TimeMention]:
    """Every non-overlapping temporal mention in ``text``, in reading order.

    Where :func:`~chronologia.extract.extract_timespan` collapses a sentence
    to a single span, this resolves **all** of them -- "meet friday at 3 or
    monday at noon" yields two mentions.  It reuses the same matcher, whose
    selected matches never overlap; a lone clock time immediately following a
    date mention composes onto it (the minute-wide time on that day), exactly
    as the single-span edge composes them.

    Returns a list of :class:`TimeMention` (empty when nothing matched).

    ``text`` must be a ``str``; anything else raises :class:`TypeError`.
    Text that names nothing temporal, the empty string included, returns an
    empty list.
    """
    require_text(text, "extract_timespans")
    from chronologia.extract.confidence import score_candidates
    from chronologia.extract.resolver import compose_date_clock

    engine = _timespan_engine(lang)
    scale_mode = _resolve_scale_mode(lang, scale)
    anchor = anchor or datetime.now()
    if isinstance(anchor, datetime):
        anchor = anchor.replace(tzinfo=None)
    tokens = engine.tokenize(text)

    scored = list(score_candidates(
        engine.matcher.match(tokens),
        lambda m: engine.resolver.resolve(m, anchor, scale_mode), engine.spec))
    scored.sort(key=lambda sc: sc.match.span[0])
    resolved = [(sc.match, sc.resolution) for sc in scored]

    out: List[Tuple[Tuple[int, int], DateSpan, float]] = []
    for sc in scored:
        match, res, conf = sc.match, sc.resolution, sc.confidence
        # a clock time right after a date mention composes onto that day
        if (match.construction == "clock_time" and out
                and _prev_is_date(resolved, match)):
            prev_match, prev_res = _prev_date(resolved, match)
            merged = compose_date_clock(prev_res, res)
            lo = min(prev_match.span[0], match.span[0])
            hi = max(prev_match.span[1], match.span[1])
            # the composed mention is only as trusted as its weaker half
            out[-1] = ((lo, hi), merged.value, min(out[-1][2], conf))
            continue
        out.append((match.span, res.value, conf))

    # a list of ordinals sharing one trailing scope ("the 2nd, 4th and 6th of
    # July", "the 5th and the 3rd of the month") names one date per ordinal --
    # the shared "of July"/"of the month" distributes to each.  The matcher only
    # binds the *last* ordinal (the one the scope actually abuts), leaving the
    # earlier bare ordinals unmatched; this re-resolves each of them against the
    # same scope and emits a mention, so a three-ordinal list yields three dates
    # instead of silently keeping only the last.
    out.extend(_distribute_shared_scope(scored, tokens, engine, anchor))
    out.sort(key=lambda e: e[0][0])

    # a "from A to B" / "between A and B" pair of mentions is ONE range span,
    # not two loose endpoints: collapse adjacent mentions the single-span range
    # detector accepts, reusing the identical machinery so list-vs-range ("monday
    # and wednesday" stays two, "between monday and wednesday" becomes one) is
    # decided exactly as the single edge decides it.
    out = _merge_ranges(out, tokens, text, engine, anchor)

    # drop any mention governed by a leading negation/exclusion particle ("not
    # tomorrow", "any day but Friday"): the excluded reference is not a positive
    # date.  The governing residue is the text between the previous mention and
    # this one, so a bound ("not before Monday") is left untouched.
    kept = []
    prev_end = 0
    for (lo, hi), value, conf in out:
        cs = _char_span(tokens, lo, hi)
        start = cs[0] if cs else None
        if (start is not None
                and _exclusion_vetoes(text[prev_end:start], engine.spec)):
            if cs:
                prev_end = cs[1]
            continue
        if cs:
            prev_end = cs[1]
        kept.append(((lo, hi), value, conf))

    return [TimeMention(value, " ".join(t.raw for t in tokens[lo:hi]), (lo, hi),
                        _char_span(tokens, lo, hi), conf)
            for (lo, hi), value, conf in kept]


def _merge_ranges(out, tokens, text, engine, anchor):
    """Collapse each adjacent mention pair the single-span range detector reads
    as one "from A to B" / "between A and B" span into a single range mention.

    The pass reuses :func:`~chronologia.extract._extract_range` verbatim: for a
    consecutive pair it slices the *pre-fold* token stream over the region from
    the left mention (extended left over a leading ``from``/``between``
    connector when one sits right before it) to the right mention, and offers
    that slice to the range detector.  A slice the detector accepts becomes one
    mention (span from the range, token/char extent widened to cover the
    connectors); a slice it rejects -- a bare "and"/"or" list, two unrelated
    clauses -- leaves both mentions untouched.  A merged pair consumes both
    endpoints, so a range never chains into a third mention ("from monday to
    friday, then next tuesday" -> the range plus next tuesday, two mentions).
    """
    if len(out) < 2:
        return out
    from chronologia.extract.pipeline import pretokens

    spec = engine.spec
    raw = pretokens(text, spec)
    # leads that open a range, longest first, ``between`` before ``from`` so a
    # between-led "and" is reachable; both are matched as whole token runs.
    leads = (_conn_surfaces(spec, "between", _RANGE_BETWEEN)
             + _conn_surfaces(spec, "from", _RANGE_FROM))

    def _lead_start(a_lo):
        # the token index at which a ``from``/``between`` connector immediately
        # preceding mention ``a_lo`` begins, or ``a_lo`` when there is none.
        for words in leads:
            k = len(words)
            if a_lo - k >= 0 \
                    and [t.text for t in tokens[a_lo - k:a_lo]] == words:
                return a_lo - k
        return a_lo

    def _slice(cs, ce):
        return tuple(t for t in raw
                     if t.char_start is not None and t.char_end is not None
                     and t.char_start >= cs and t.char_end <= ce)

    merged = []
    i = 0
    while i < len(out):
        if i + 1 < len(out):
            (a_lo, a_hi), _, a_conf = out[i]
            (b_lo, b_hi), _, b_conf = out[i + 1]
            lead_lo = _lead_start(a_lo)
            cs = tokens[lead_lo].char_start
            ce = tokens[b_hi - 1].char_end
            if cs is not None and ce is not None:
                got = _extract_range(text, _slice(cs, ce), engine, anchor)
                if got is not None:
                    merged.append(((lead_lo, b_hi), got[0],
                                   min(a_conf, b_conf)))
                    i += 2
                    continue
        merged.append(out[i])
        i += 1
    return merged


#: the day/ordinal constructions a shared trailing scope distributes across --
#: "the 2nd, 4th and 6th of July" (calendar_date, DAY+MONTH) and "the 5th and
#: the 3rd of the month" (month_day_ref, ORD + "of the month").  Both name one
#: day-in-a-month whose leading token is the day number, so a preceding bare
#: ordinal composes with the same scope to name another date in the same month.
_SHARED_SCOPE_CONSTRUCTIONS = {"calendar_date", "month_day_ref"}


def _distribute_shared_scope(scored, tokens, engine, anchor):
    """Re-resolve each earlier ordinal in a shared-trailing-scope list.

    Only English triggers this: the list connectors and articles walked over
    ("and"/"or", "the"/"a") are English surfaces, and gating here keeps every
    other locale byte-identical.  For a matched day-in-a-month mention whose
    day is the first token of its span, the tokens after that day are the
    *scope* ("of July", "of the month"); a run of bare ordinal number tokens
    immediately before the mention -- separated only by list connectors and
    articles -- each compose with that scope into their own date mention.

    A genuine range ("from the 2nd to the 6th of July") never reaches here: the
    range detector binds "from"/"to"/"between" natively and this reads only a
    bare ``and``/``or`` list.  Returns extra ``(token_span, DateSpan, conf)``
    tuples for the caller to fold into the mention list.
    """
    if not engine.spec.lang.split("-")[0].lower() == "en":
        return []
    from chronologia.extract.numfold_engine import reindex

    connectors = {"and", "or"}
    articles = {"the", "a", "an"}
    claimed = {i for sc in scored
               for i in range(sc.match.span[0], sc.match.span[1])}
    extra = []
    for sc in scored:
        match = sc.match
        if match.construction not in _SHARED_SCOPE_CONSTRUCTIONS:
            continue
        lo, hi = match.span
        day_idx = next((i for i in range(lo, hi) if tokens[i].is_number), None)
        if day_idx is None:
            continue
        scope = tokens[day_idx + 1:hi]
        if not scope:
            continue
        # walk left over the bare ordinal list, skipping connectors/articles
        j = lo - 1
        while j >= 0:
            tok = tokens[j]
            if tok.is_number and j not in claimed:
                synth = reindex((tok,) + tuple(scope))
                sm = list(engine.matcher.match(synth))
                got = next((m for m in sm
                            if m.construction == match.construction), None)
                if got is not None:
                    res = engine.resolver.resolve(got, anchor)
                    if res is not None:
                        extra.append(((j, j + 1), res.value, sc.confidence))
            elif tok.text in connectors or tok.text in articles:
                pass
            else:
                break
            j -= 1
    return extra


def _char_span(tokens, lo, hi):
    """The character extent of ``tokens[lo:hi]`` in the original utterance.

    Reads the first and last token's recorded tokenizer offsets -- never a
    string re-search.  ``None`` when either edge token carries no offset (a
    fully engine-synthesised mention)."""
    if lo >= hi:
        return None
    start, end = tokens[lo].char_start, tokens[hi - 1].char_end
    if start is None or end is None:
        return None
    return (start, end)


def _prev_is_date(resolved, clock_match):
    from chronologia.extract.resolver import DATE_CONSTRUCTIONS
    prev = _prev_date(resolved, clock_match)
    return prev is not None and prev[0].construction in DATE_CONSTRUCTIONS


def _prev_date(resolved, clock_match):
    """The match immediately preceding ``clock_match`` in reading order."""
    ordered = [m for m, _ in resolved]
    idx = ordered.index(clock_match)
    if idx == 0:
        return None
    for m, r in reversed(resolved[:idx]):
        return m, r
    return None


# --------------------------------------------------------------------------
# Natural-language recurrence -> RFC 5545.
# --------------------------------------------------------------------------
_UNIT_FREQ = {"day": "DAILY", "week": "WEEKLY", "month": "MONTHLY",
              "year": "YEARLY", "fortnight": "WEEKLY"}


class RecurrenceResult(NamedTuple):
    """Return of :func:`extract_recurrence`: a rule and the leftover text.

    A plain 2-tuple ``(recurrence, remainder)`` for unpacking, plus the named
    fields ``.recurrence`` and ``.remainder``.  ``.recurrence`` is normally a
    serialisable :class:`~chronologia.recurrence.Recurrence`; a **movable**
    feast ("every easter") yields a
    :class:`~chronologia.recurrence.HolidayRecurrence` instead (it expands to
    real dates but has no RFC 5545 ``RRULE``).
    """
    recurrence: Union[Recurrence, HolidayRecurrence]
    remainder: str


def extract_recurrence(
        text: str,
        lang: str = "en-us",
        anchor: Optional[datetime] = None,
) -> Optional[RecurrenceResult]:
    """Map a recurring phrase onto an RFC 5545 :class:`~chronologia.recurrence.Recurrence`.

    Handles the civil recurrence idioms -- "every friday", "every other week",
    "every 2 weeks", "every weekday", "daily"/"weekly"/"monthly"/"yearly", and
    the ordinal "first monday of every month" / "last friday of every month"
    (and "the third thursday of november") -- reading weekday names, unit words
    and the ``every`` marker from the locale.

    **Date-anchored** recurrence composes the *single-span engine* to read the
    date part rather than re-implementing a date grammar:

    * "every 10th of may" / "every may 10" / "every year on may 10" ->
      ``YEARLY;BYMONTH=5;BYMONTHDAY=10`` (the day+month the engine resolves are
      lifted onto ``BYMONTH``/``BYMONTHDAY``);
    * "the 10th of every month" / "every month on the 10th" ->
      ``MONTHLY;BYMONTHDAY=10``;
    * "every christmas" -> the fixed holiday's real rule
      ``YEARLY;BYMONTH=12;BYMONTHDAY=25``; a **movable** feast ("every easter",
      "every eid al-fitr") -> a :class:`~chronologia.recurrence.HolidayRecurrence`
      (it expands through the holiday engine but cannot serialize to an RRULE).

    A **clock pin** is folded onto the rule: an "at 9" / "at 9:30" / "at noon"
    trailing a rule sets ``BYHOUR`` (and ``BYMINUTE``) -- "daily at 9" ->
    ``FREQ=DAILY;BYHOUR=9``, "every wednesday at 9:30" ->
    ``FREQ=WEEKLY;BYDAY=WE;BYHOUR=9;BYMINUTE=30``.

    A trailing bound is folded onto the rule: an ``until``/``till`` marker plus
    a date sets ``UNTIL`` ("every friday until june"); a ``for`` marker plus a
    fixed-width duration sets ``COUNT`` -- the number of occurrences the
    duration spans at the rule's frequency ("daily for two weeks" -> COUNT=14,
    "every monday for 6 weeks" -> COUNT=6).

    Returns a :class:`RecurrenceResult` -- a ``(recurrence, remainder)`` named
    tuple (unpack it, or read ``.recurrence`` / ``.remainder``) -- or ``None``
    when no recurrence is found.

    ``text`` must be a ``str``; anything else raises :class:`TypeError`.
    Text that names no recurrence, the empty string included, returns
    ``None``.
    """
    require_text(text, "extract_recurrence")
    ctx = _recur_ctx(text, lang, anchor)
    tokens = ctx.tokens

    # A placement-free rate ("twice a week", "twice daily") names a frequency
    # *count per period* -- and RFC 5545 has no such part: COUNT is a total,
    # not a per-period rate.  Fabricating BYDAY (inventing Mon/Wed/Fri the
    # speaker never said) would corrupt any round-trip, so a bare rate is
    # refused outright rather than stranded into a misleading DAILY partial.
    # A rate that *does* name its days ("twice a week on monday") is a placed
    # reading and is left for the on-weekday finder below.
    if any(tok.text in ctx.rate_words for tok in tokens) \
            and _recur_on_weekdays(ctx) is None:
        return None

    # first match wins; the order of ``_FINDERS`` is load-bearing -- see the
    # constraints recorded where it is defined.
    # first match wins; the order of ``_FINDERS`` is load-bearing -- see the
    # constraints recorded where it is defined.
    for finder in _FINDERS:
        hit = finder(ctx)
        if hit is not None:
            rec, consumed = hit
            # a finder may CLAIM its frame yet name no valid recurrence (an
            # impossible recurring date, "every 31st of april"): it returns a
            # None rule so the greedy catch-alls after it do not re-read the
            # same tokens into a wrong rule.  The claim is authoritative -- stop.
            if rec is None:
                return None
            rec, consumed = _apply_bounds(rec, consumed, ctx, lang, anchor)
            rec, consumed = _apply_clock(rec, consumed, ctx, lang, anchor)
            from chronologia.extract.pipeline import render_remainder
            remainder = render_remainder(text, [t for t in tokens
                                                if t.index not in consumed])
            return RecurrenceResult(rec, remainder)
    return None




def _apply_clock(rec, consumed, ctx, lang, anchor):
    """Fold a trailing clock ("at 9", "at 9:30", "at noon") onto ``rec`` as a
    ``BYHOUR``/``BYMINUTE`` pin, extending ``consumed`` over the clock (and a
    leading ``at`` marker).

    A :class:`~chronologia.recurrence.HolidayRecurrence` carries no clock pin,
    so it is left untouched.  The clock is read by the *same* engine
    ``clock_time`` construction the single-span edge uses (composition, not a
    new grammar); its resolved minute-wide span supplies the hour and minute.
    """
    from dataclasses import replace as _replace
    if isinstance(rec, HolidayRecurrence):
        return rec, consumed
    engine = _timespan_engine(lang)
    tokens = ctx.tokens
    for m in engine.matcher.match(tokens):
        if m.construction not in ("clock_time", "military_time"):
            continue
        if any(i in consumed for i in range(*m.span)):
            continue
        res = engine.resolver.resolve(m, anchor or datetime.now())
        if res is None:
            continue
        c = res.value.start
        rec = _replace(rec, byhour=(c.hour,),
                       byminute=((c.minute,) if c.minute else ()))
        lo, hi = m.span
        while lo - 1 >= 0 and tokens[lo - 1].text in ctx.at_words \
                and (lo - 1) not in consumed:
            lo -= 1
        return rec, consumed | set(range(lo, hi))
    return rec, consumed


def _marker_runs(tokens, surfaces, consumed):
    """Every ``(i, j)`` token span (unconsumed, contiguous) whose words are a
    marker ``surface``.  A surface may be **multi-word** ("timp de",
    "в продължение на", "po dobu"): it is compared word-for-word against the
    token stream.  Longest surface first, so a multi-word marker wins over a
    single-word prefix of it."""
    n = len(tokens)
    runs = []
    for surf in sorted(surfaces, key=lambda s: -len(s.split())):
        words = surf.lower().split()
        k = len(words)
        if not k:
            continue
        for i in range(n - k + 1):
            span = range(i, i + k)
            if any(x in consumed for x in span):
                continue
            if [tokens[x].text for x in span] == words:
                runs.append((i, i + k))
    return runs


def _bound_payload(rec, consumed, tokens, marker, lang, anchor, grounder):
    """Ground a bound whose ``marker`` (a ``(i, j)`` token span) sits either
    *before* its payload (a leading marker: "until <date>", "timp de
    <duration>") or *after* it (a postposed marker: Estonian "<duration>
    jooksul", Frisian "<duration> lang").

    The engine tries the leading reading first, then the postposed one, and
    keeps whichever the ``grounder`` (date for UNTIL, duration for COUNT)
    accepts.  Returns ``(new_rec, extra_consumed)`` or ``None``."""
    i, j = marker
    n = len(tokens)

    # leading: payload is the unconsumed run to the right of the marker
    lo, hi = j, n
    while lo < hi and lo in consumed:
        lo += 1
    tail = " ".join(t.raw for t in tokens[lo:hi]
                    if t.index not in consumed)
    hit = grounder(rec, tail.strip()) if tail.strip() else None
    if hit is not None:
        return hit, set(range(i, n))

    # postposed: payload is the unconsumed run to the left of the marker
    hi2 = i
    lo2 = hi2
    while lo2 - 1 >= 0 and (lo2 - 1) not in consumed:
        lo2 -= 1
    head = " ".join(t.raw for t in tokens[lo2:hi2]
                    if t.index not in consumed)
    hit = grounder(rec, head.strip()) if head.strip() else None
    if hit is not None:
        return hit, set(range(lo2, j))
    return None


def _apply_bounds(rec, consumed, ctx, lang, anchor):
    """Fold a trailing ``until <date>`` (-> UNTIL) or ``for <duration>``
    (-> COUNT) bound onto ``rec``, extending ``consumed`` over the words it
    reads.  A bound the engine cannot ground (an unparseable date, a
    calendar-ambiguous duration under a MONTHLY/YEARLY rule) is left untouched
    in the remainder rather than guessed.

    Both markers may be **multi-word** ("timp de", "в продължение на") and may
    be **postposed** -- the marker following the date/duration rather than
    leading it (Finnish "asti"/"saakka", Estonian "jooksul", Frisian "lang").
    Whether a language's marker leads or trails is a fact of that language's
    surface; the engine tries the leading reading first, then the postposed
    one, per marker."""
    from dataclasses import replace as _replace
    tokens = ctx.tokens

    def _ground_until(rec, text):
        got = extract_timespan(text, lang, anchor=anchor)
        if got is None:
            return None
        return _replace(rec, until=got[0].start)

    def _ground_count(rec, text):
        dur = extract_duration(text, lang)
        if dur is None:
            return None
        count = _count_from_duration(rec.freq, dur[0])
        if count is None:
            return None
        return _replace(rec, count=count)

    for surfaces, grounder in ((ctx.until_words, _ground_until),
                               (ctx.for_words, _ground_count)):
        for marker in _marker_runs(tokens, surfaces, consumed):
            got = _bound_payload(rec, consumed, tokens, marker, lang, anchor,
                                 grounder)
            if got is not None:
                rec, extra = got
                consumed = consumed | extra
                break

    # A trailing explicit occurrence count -- "<N> times" -- on an otherwise
    # complete rule is a total COUNT ("every day 3 times" -> COUNT=3), the one
    # RFC 5545 count part.  It differs from a *rate* ("3 times a day", "twice a
    # week"): a rate names occurrences *per period* and has no RFC 5545 part, so
    # it is refused upstream and never reaches a grounded rule here.  The number
    # must sit immediately before the count word, and nothing temporal may
    # follow it -- a "<N> times a <period>" rate keeps its period unit
    # unconsumed to the right, which this guard rejects, leaving it untouched.
    # "0 times" is degenerate (no occurrences): it is declined outright, left in
    # the remainder rather than emitted as COUNT=0.
    n = len(tokens)
    # COUNT and UNTIL are mutually exclusive in RFC 5545: if an explicit bound
    # already set UNTIL ("every day 5 times until March"), do NOT also add the
    # trailing count -- that would build an invalid rule and raise out of the
    # public extractor.  UNTIL wins; the "N times" stays in the remainder.
    if (ctx.count_words and isinstance(rec, Recurrence)
            and rec.count is None and rec.until is None):
        for i in range(n):
            if i in consumed or tokens[i].text not in ctx.count_words:
                continue
            p = i - 1
            if p < 0 or p in consumed or not tokens[p].is_number:
                continue
            if any(k not in consumed for k in range(i + 1, n)):
                continue  # "<N> times a day": a per-period rate, not a total
            cnt = int(tokens[p].value)
            if cnt < 1:
                break  # "0 times": degenerate, no COUNT=0
            rec = _replace(rec, count=cnt)
            consumed = consumed | {p, i}
            break

    return rec, consumed


def _count_from_duration(freq, td):
    """Occurrence count a fixed-width duration spans at ``freq``: one per day
    for DAILY, one per whole week for WEEKLY.  MONTHLY/YEARLY need a
    calendar-ambiguous duration the fixed-width extractor never yields, so they
    return ``None`` (no COUNT bound)."""
    if freq == "DAILY":
        return td.days or None
    if freq == "WEEKLY":
        return (td.days // 7) or None
    return None


@dataclass(frozen=True)
class _RecurCtx:
    tokens: tuple
    every: set
    other: set
    weekday_word: set
    articles: set
    of_words: set
    freq: dict
    units: dict
    weekdays: dict
    months: dict
    rel_markers: dict
    until_words: set = frozenset()
    for_words: set = frozenset()
    at_words: set = frozenset()
    weekend_word: set = frozenset()
    weekend_start: int = 5
    on_words: set = frozenset()
    once_words: set = frozenset()
    per_words: set = frozenset()
    habitual_words: set = frozenset()
    and_words: set = frozenset()
    rate_words: set = frozenset()
    count_words: set = frozenset()
    quarter_word: set = frozenset()
    holidays: dict = None
    lang: str = "en-us"
    anchor: Optional[datetime] = None
    #: the *pre-fold* token stream (numbers not yet merged across ``and``).
    #: A finder that must see an ordinal *list* -- "first and third monday" --
    #: reads this, because the number fold collapses that run to a single token
    #: before any folded-stream finder sees it (the same reason range detection
    #: reads the pre-fold stream).
    pretokens: tuple = ()
    #: the spec, kept so a pre-fold finder can fold a lone ordinal on its own.
    spec: object = None


def _recur_ctx(text, lang, anchor):
    """Build the recurrence context for ``text`` -- the shared input every
    finder reads.  Split out so a finder can be exercised on its own (the
    finder-order test does exactly that)."""
    engine = _timespan_engine(lang)
    spec = engine.spec
    tokens = engine.tokenize(text)
    C = spec.connectors
    ctx = _RecurCtx(
        tokens=tokens,
        every=set(C.get("every", ())),
        other=set(C.get("recur_other", ())),
        weekday_word=set(C.get("weekday", ())),
        articles=_article_words(spec),
        of_words=set(C.get("of", ())),
        freq=_freq_map(C),
        units=spec.units,
        weekdays=spec.weekdays,
        months=spec.months,
        rel_markers=spec.rel_markers,
        until_words=set(C.get("until", ())),
        for_words=set(C.get("recur_for", ())),
        at_words=set(C.get("at", ())),
        weekend_word=set(C.get("weekend", ())),
        weekend_start=spec.conventions.weekend_start,
        on_words=set(C.get("on", ())),
        once_words=set(C.get("recur_once", ())),
        per_words=set(C.get("recur_per", ())),
        habitual_words=set(C.get("recur_habitual", ())),
        and_words=set(C.get("and", ())),
        rate_words=set(C.get("recur_rate", ())),
        count_words=set(C.get("recur_count", ())),
        quarter_word=set(C.get("quarter_word", ())),
        holidays=dict(spec.holidays),
        lang=lang,
        anchor=anchor,
        pretokens=pretokens(text, spec),
        spec=spec,
    )
    return ctx


def _freq_map(connectors):
    """Lone frequency adverbs -> ``(FREQ, interval)``.

    ``biweekly``/``fortnightly`` follow the standard scheduling/RRULE
    convention of "every two weeks" (``WEEKLY;INTERVAL=2``) -- the sense
    Merriam-Webster's usage note calls the more common reading of
    "biweekly", as opposed to the rarer "twice a week" sense (which this
    resolver does not attempt: a frequency-*count* reading needs a
    different RRULE shape -- BYSETPOS/COUNT-per-period -- than the plain
    INTERVAL bump every other adverb here needs, so it is left as a
    documented follow-up rather than forced in).  ``quarterly`` is a
    calendar quarter, i.e. every three months (``MONTHLY;INTERVAL=3``).
    """
    out = {}
    for key, freq in (("freq_daily", "DAILY"), ("freq_weekly", "WEEKLY"),
                      ("freq_monthly", "MONTHLY"), ("freq_yearly", "YEARLY")):
        for s in connectors.get(key, ()):
            out[s] = (freq, 1)
    for s in connectors.get("freq_biweekly", ()):
        out[s] = ("WEEKLY", 2)
    for s in connectors.get("freq_quarterly", ()):
        out[s] = ("MONTHLY", 3)
    return out


def _weekend_byday(ctx):
    """The locale's weekend as a ``BYDAY`` tuple.

    The weekend is not Saturday+Sunday everywhere -- the locale ships a
    ``weekend_start`` convention (Thursday in ``ar``/``he``, Friday in ``fa``)
    and the weekend is the two days running from it.  Deriving the pair here
    keeps every weekend reading -- "on weekends", "every weekend" -- on the one
    convention the business-day and anchored-span code already reads.
    """
    s = ctx.weekend_start
    return ((None, s % 7), (None, (s + 1) % 7))


def _weekday_here(ctx, tok, plural_ok):
    """The weekday a token names, optionally allowing a derived ``-s`` plural.

    Weekday plurals are **positionally licensed**, never global.  Some plural
    weekday surfaces are ambiguous out of context -- pt "domingos" is also a
    common surname, and a bare "sextas" makes unrelated ordinal-count readings
    match -- so they cannot enter the weekday vocabulary.  Inside a frame that
    a surname could not occupy (an ``every`` determiner plus an ordinal or a
    "last" marker directly before the word) the ambiguity is gone, and the
    plural is read there and only there.

    The plural is *derived* (surface + ``-s``), not listed, so it follows the
    vocabulary automatically; the compound weekdays that pluralise both
    elements ("quintas-feiras") are already listed surfaces.
    """
    wd = ctx.weekdays.get(tok.text)
    if wd is not None or not plural_ok:
        return wd
    s = tok.text
    return ctx.weekdays.get(s[:-1]) if s.endswith("s") else None


def _recur_nth_weekday(ctx):
    """``<ordinal|last> <weekday> of [every] (month|<month name>)``.

    The weekday slot is either a *named* weekday ("the last friday of every
    month" -> ``BYDAY=-1FR``) or the business-day class noun ("the last weekday
    of every month" -> the canonical last-business-day idiom
    ``BYDAY=MO,TU,WE,TH,FR;BYSETPOS=-1``).  The class-noun reading only fires
    with an explicit ordinal/"last" marker and the ``of [every] month`` tail --
    the bare "every weekday" (a plain weekly workweek) is left to
    :func:`_recur_every`.
    """
    t = ctx.tokens
    n = len(t)
    for w in range(1, n):
        # a derived plural is licensed only under an "every" determiner, which
        # must sit in the article run leading into the ordinal.
        li0 = w - 1
        start0 = li0
        while start0 > 0 and (t[start0 - 1].text in ctx.articles
                              or t[start0 - 1].text in ctx.every):
            start0 -= 1
        plural_ok = any(t[k].text in ctx.every for k in range(start0, li0))
        business = t[w].text in ctx.weekday_word
        wd = None if business else _weekday_here(ctx, t[w], plural_ok)
        if wd is None and not business:
            continue
        li = w - 1
        ordn = None
        if t[li].is_number:
            ordn = int(t[li].value)
        elif (t[li].text in ctx.rel_markers
              and ctx.rel_markers[t[li].text] == -1):
            ordn = -1
        else:
            continue
        r = w + 1
        if not (r < n and t[r].text in ctx.of_words):
            continue
        r += 1
        while r < n and (t[r].text in ctx.every or t[r].text in ctx.articles):
            r += 1
        start = li
        while start > 0 and (t[start - 1].text in ctx.articles
                             or t[start - 1].text in ctx.every):
            start -= 1
        if r < n and t[r].text in ctx.months:
            if business:
                rec = _business_day_of_month(ordn, month=ctx.months[t[r].text])
            else:
                rec = _nth_weekday_of_month(ordn, wd,
                                            month=ctx.months[t[r].text])
            return rec, set(range(start, r + 1))
        if r < n and t[r].text in ctx.units and ctx.units[t[r].text] == "month":
            if business:
                return _business_day_of_month(ordn), set(range(start, r + 1))
            return _nth_weekday_of_month(ordn, wd), set(range(start, r + 1))
    return None


def _business_day_of_month(ordn, month=None):
    """The ``ordn``-th business day of the month as a ``BYSETPOS`` rule.

    The canonical RFC 5545 idiom for "the last (or first) weekday of the
    month": ``BYDAY=MO,TU,WE,TH,FR`` selects the workweek and ``BYSETPOS``
    picks the ``ordn``-th of that set within each period ("last weekday" ->
    ``BYSETPOS=-1``).  With ``month`` given it restricts to a single calendar
    month (a yearly rule), mirroring :func:`_nth_weekday_of_month`.
    """
    byday = tuple((None, k) for k in range(5))  # MO..FR
    if month is not None:
        return _build_every("yearly", bymonth=month, byday=byday,
                            bysetpos=(ordn,))
    return _build_every("monthly", byday=byday, bysetpos=(ordn,))


def _fold_group_value(ctx, group):
    """The integer a pre-fold ordinal group folds to, or ``None``.

    One list element may be one pre-fold token (spelled "first") or several (a
    digit ordinal "1st" tokenizes as ``1`` + ``st``, the suffix a separate
    token that only the number fold rejoins).  Folding the group's slice on its
    own -- exactly as range detection folds a lone endpoint slice -- recovers
    the value in both shapes.  Returns ``None`` unless the group folds to a
    single positive integer.
    """
    if not group:
        return None
    raw = " ".join(t.raw for t in group)
    folded = fold_tokens(tuple(group), ctx.spec, raw)
    if len(folded) != 1 or not folded[0].is_number:
        return None
    val = folded[0].value
    return int(val) if float(val) == int(val) and int(val) > 0 else None


#: tokens that bound the ordinal region to the left of the weekday -- the frame
#: words that can never be part of an ordinal ("of the month", a determiner,
#: another weekday, a unit or month name).
def _list_region_stop(ctx, tok):
    return (tok.text in ctx.articles or tok.text in ctx.every
            or tok.text in ctx.of_words or tok.text in ctx.on_words
            or tok.text in ctx.weekdays or tok.text in ctx.units
            or tok.text in ctx.months)


def _recur_nth_weekday_list(ctx):
    """``<ord> and <ord> [and <ord>...] <weekday> [of [every] month]``.

    A *list* of ordinal weekdays -- "the first and third monday of every month"
    -- is one BYDAY list under RFC 5545 3.3.10: ``BYDAY=1MO,3MO``.  The number
    fold merges the ordinal run across the ``and`` connector ("first and third"
    -> a single token ``3``) before any folded-stream finder can see the list,
    so this finder reads the *pre-fold* stream (:attr:`_RecurCtx.pretokens`) --
    the same workaround range detection uses -- recovers each ordinal by folding
    its ``and``-separated group in isolation, and maps the recovered span back
    onto the folded tokens for the consumed set.

    An ordinal *list* implies the monthly nth-weekday reading whether or not the
    "of the month" tail is present (a list cannot be an INTERVAL), so the tail
    is optional -- consistent with the single-ordinal "the third tuesday of the
    month" being monthly, and never fabricating the bogus INTERVAL the folded
    stream would otherwise yield.
    """
    p = ctx.pretokens
    n = len(p)
    for w in range(1, n):
        wd = ctx.weekdays.get(p[w].text)
        if wd is None:
            continue
        # the ordinal region is the block of tokens just left of the weekday,
        # bounded by the frame words that can never be part of an ordinal.
        lo = w
        while lo > 0 and not _list_region_stop(ctx, p[lo - 1]):
            lo -= 1
        block = p[lo:w]
        if not block:
            continue
        # split the block on ``and`` into list elements, folding each group.
        groups, cur = [], []
        for tok in block:
            if tok.text in ctx.and_words:
                groups.append(cur)
                cur = []
            else:
                cur.append(tok)
        groups.append(cur)
        vals = [_fold_group_value(ctx, g) for g in groups]
        if len(vals) < 2 or any(v is None for v in vals):
            continue
        # a determiner/article run may lead into the first ordinal.
        start = lo
        while start > 0 and (p[start - 1].text in ctx.articles
                             or p[start - 1].text in ctx.every):
            start -= 1
        # optional "of [the|every] month" tail after the weekday.
        end = w
        r = w + 1
        if r < n and p[r].text in ctx.of_words:
            m = r + 1
            while m < n and (p[m].text in ctx.every
                             or p[m].text in ctx.articles):
                m += 1
            if m < n and p[m].text in ctx.units \
                    and ctx.units[p[m].text] == "month":
                end = m
        cs = p[start].char_start
        ce = p[end].char_end
        if cs is None or ce is None:
            continue
        byday = tuple((v, wd) for v in vals)
        rec = _build_every("monthly", byday=byday)
        consumed = {tok.index for tok in ctx.tokens
                    if tok.char_start is not None and tok.char_end is not None
                    and tok.char_start >= cs and tok.char_end <= ce}
        return rec, consumed
    return None


def _is_ordinal_surface(tok):
    """Whether a folded number token was written as an **ordinal**.

    The number fold normalises "1st" / "1º" / "1.º" to the value ``1``, but the
    tokenizer keeps the original surface in ``raw``.  An ordinal surface is
    digits followed by a non-digit tail ("1st", "10th", "1º"); a bare cardinal
    ("2") has no tail, and a decimal ("1.5") ends in digits.  This is a surface
    fact, so it reads the same in any language that writes ordinals as a
    digit run plus a suffix -- no per-language table.
    """
    import re
    if not tok.is_number:
        return False
    return bool(re.fullmatch(r"\d+\D+", tok.raw.strip().lower()))


def _of_month_tail(ctx, r):
    """End index after an optional ``of [the|every] month`` tail at ``r``.

    Returns ``r`` unchanged when there is no such tail -- the tail is *allowed*
    but never *required*, which is exactly what makes the elliptical "every
    last friday" read like its fuller sibling "every last friday of the month".
    """
    t = ctx.tokens
    n = len(t)
    if r < n and t[r].text in ctx.of_words:
        k = r + 1
        while k < n and (t[k].text in ctx.articles or t[k].text in ctx.every):
            k += 1
        if k < n and t[k].text in ctx.units and ctx.units[t[k].text] == "month":
            return k + 1
    return r


def _recur_once(ctx):
    """``[one] once a <unit> [on <weekday>]`` -> the plain per-period frequency.

    "Once per period" *is* "every period": one occurrence per week is exactly
    ``FREQ=WEEKLY``, so the count word adds no RRULE part of its own.  An
    optional trailing "on <weekday>" pins the day (``BYDAY``).

    The ``once`` marker may be **multi-word** and may be a bare *counter noun*
    that only means "once" when a count of one precedes it: English writes one
    word ("once"), Portuguese writes the count plus the noun ("uma vez", one
    time).  The marker is therefore matched as a word run (longest first, as
    every multi-word marker in this module is), and a **number one**
    immediately before it is read as part of the phrase.  A count *other* than
    one before the marker is rejected outright, so "duas vezes por semana"
    (twice a week) stays unread.

    Only the count *one* maps cleanly.  "twice a week" / "three times a month"
    are frequency-**counts** needing a different RRULE shape (BYSETPOS or a
    per-period COUNT) than the plain frequency here, so they are deliberately
    left unread rather than forced into a wrong interval -- the same line
    ``_freq_map`` draws for the "twice a week" sense of "biweekly".
    """
    t = ctx.tokens
    n = len(t)
    for i, j in sorted(_marker_runs(t, ctx.once_words, set())):
        if i - 1 >= 0 and t[i - 1].is_number:
            if float(t[i - 1].value) != 1.0:
                continue  # "duas vezes por semana": a per-period *count*
            i -= 1
        while j < n and (t[j].text in ctx.articles or t[j].text in ctx.per_words):
            j += 1
        if not (j < n and t[j].text in ctx.units):
            continue
        unit = ctx.units[t[j].text]
        kw = {}
        if unit == "fortnight":
            freq, kw = "WEEKLY", {"interval": 2}
        else:
            freq = _UNIT_FREQ.get(unit)
        if freq is None:
            continue
        end = j + 1
        # optional "on <weekday>": "once a week on monday".
        if (end + 1 < n and t[end].text in ctx.on_words
                and t[end + 1].text in ctx.weekdays):
            kw["byday"] = ((None, ctx.weekdays[t[end + 1].text]),)
            end += 2
        return _build_every(freq, **kw), set(range(i, end))
    return None


def _collect_weekdays(ctx, start, plural_ok):
    """Read a run of weekday names beginning at ``start`` -> ``(days, end)``.

    A recurrence enumeration lists its days with the language's ``and``/``&``
    connective (and, in prose, commas -- which the tokenizer already drops):
    "monday, wednesday and friday", "tuesday and thursday".  The run is read
    day-by-day, skipping any ``and`` connectors between them, so every named
    weekday is collected rather than only the first.  ``days`` is the list of
    weekday codes in reading order; ``end`` the index just past the last day.
    Returns ``None`` when ``start`` is not a weekday at all.
    """
    t = ctx.tokens
    n = len(t)
    wd = _weekday_here(ctx, t[start], plural_ok) if start < n else None
    if wd is None:
        return None
    days = [wd]
    end = start + 1
    while True:
        k = end
        while k < n and t[k].text in ctx.and_words:
            k += 1
        nxt = _weekday_here(ctx, t[k], plural_ok) if k < n else None
        if nxt is None:
            break
        days.append(nxt)
        end = k + 1
    return days, end


def _leading_rate_span(ctx, on_idx):
    """Token span of a redundant "<N> times a <period>" rate leading into an
    ``on <weekdays>`` placement, or the empty set when there is none.

    "3 times a week on monday, wednesday and friday" names its days outright,
    so the rate is redundant with the placement and RFC 5545 expresses only
    the days (``BYDAY=MO,WE,FR``).  The rate is consumed -- not stranded in the
    remainder -- but only when the whole region before ``on`` is a rate: a
    period unit plus a count (a number, or a ``twice``/``thrice`` rate word),
    with nothing else temporal (a weekday, month or ``every`` never appear in a
    rate).  Anything else is left untouched.
    """
    t = ctx.tokens
    if on_idx <= 0:
        return set()
    seg = range(0, on_idx)
    has_count = any(t[k].is_number or t[k].text in ctx.rate_words for k in seg)
    has_unit = any(t[k].text in ctx.units
                   and ctx.units[t[k].text] in _UNIT_FREQ for k in seg)
    benign = all(
        t[k].is_number or t[k].text in ctx.rate_words
        or t[k].text in ctx.articles or t[k].text in ctx.per_words
        or t[k].text in ctx.units
        or not (t[k].text in ctx.weekdays or t[k].text in ctx.every
                or t[k].text in ctx.months or t[k].text in ctx.freq)
        for k in seg)
    if has_count and has_unit and benign:
        return set(seg)
    return set()


def _recur_on_weekdays(ctx):
    """``on <weekday>[, <weekday> ...]`` -> ``WEEKLY;BYDAY=<days>``.

    The English habitual "on mondays" / "on mondays, wednesdays and fridays"
    is a weekly rule on the named days -- the plural weekday surface (or a
    two-or-more-day list) is what marks it as a recurrence rather than a single
    coming date ("on monday" alone stays a one-off, unread here).  Weekday
    plurals are read positionally, exactly as the ``every``/habitual frames
    read them, never entering the global weekday vocabulary.

    A redundant rate leading into the placement ("3 times a week on monday,
    wednesday and friday") is consumed rather than blocking the parse.
    """
    t = ctx.tokens
    n = len(t)
    for i in range(n):
        if t[i].text not in ctx.on_words:
            continue
        got = _collect_weekdays(ctx, i + 1, True)
        if got is None:
            continue
        days, end = got
        singular_first = t[i + 1].text in ctx.weekdays
        if len(days) < 2 and singular_first and not _leading_rate_span(ctx, i):
            continue  # "on monday": a single coming date, not a rule
        byday = tuple((None, wd) for wd in days)
        consumed = set(range(i, end)) | _leading_rate_span(ctx, i)
        return _build_every("weekly", byday=byday), consumed
    return None


def _recur_every(ctx):
    """``every [other|N] (<weekday> | <unit> | weekday-word)``, plus the
    **elliptical** nth-weekday / day-of-month readings that drop the
    "of the month" tail ("every last friday", "every 1st").

    The ellipsis fires only under an explicit ``every`` marker: a bare "last
    friday" is a single past date, not a recurrence, and stays unread here.
    """
    t = ctx.tokens
    n = len(t)
    for i in range(n):
        if t[i].text not in ctx.every:
            continue
        j = i + 1
        interval = 1
        num_val = num_idx = None
        saw_article = False
        # an article, an "other" marker and an explicit count may appear in any
        # order before the target noun ("every other week", "toutes les deux
        # semaines", "cada dos semanas").
        while j < n:
            if t[j].text in ctx.articles:
                saw_article, j = True, j + 1
            elif t[j].text in ctx.other:
                interval, j = 2, j + 1
            elif t[j].is_number:
                interval = num_val = int(t[j].value)
                num_idx, j = j, j + 1
            else:
                break

        # "every 0 <unit>" names no valid recurrence: an interval must be >= 1.
        # Report it as None (the honest "this expresses no recurrence") rather
        # than letting the 0 reach Recurrence's validator and raise -- extract_*
        # never raises on user text.
        if num_val is not None and num_val < 1:
            return None

        # -- ellipsis: "every last <weekday>" --------------------------------
        # a "last" relative marker (never a count, so `interval` is untouched)
        # directly before a weekday is the -1st weekday of the month, exactly
        # as "the last friday of every month" already reads.
        if (num_val is None and j + 1 < n
                and t[j].text in ctx.rel_markers
                and ctx.rel_markers[t[j].text] == -1
                and _weekday_here(ctx, t[j + 1], True) is not None):
            wd = _weekday_here(ctx, t[j + 1], True)
            return (_nth_weekday_of_month(-1, wd),
                    set(range(i, _of_month_tail(ctx, j + 2))))

        # -- ellipsis: "every <ordinal> <weekday>" ---------------------------
        # "every first friday" is the 1st friday of the month: an *interval* of
        # one would be degenerate (plain "every friday"), so the ordinal is the
        # only reading that carries meaning.
        #
        # From two upwards the two readings genuinely compete -- "every third
        # tuesday" is every third tuesday (a 3-week interval) as readily as the
        # third tuesday of the month -- so the monthly reading fires only on the
        # positive evidence of an explicit "of the month" tail.  Without it the
        # count falls through to the interval reading below.
        if num_val is not None and j < n:
            wd = _weekday_here(ctx, t[j], True)
            end = _of_month_tail(ctx, j + 1)
            if wd is not None and (num_val == 1 or end > j + 1):
                return _nth_weekday_of_month(num_val, wd), set(range(i, end))

        # -- ellipsis: "every <ordinal> [of the month]" -> BYMONTHDAY --------
        # A count *followed by a unit* is an interval ("every 2 weeks") and is
        # never read here.  Otherwise the count is a day of the month, but only
        # on positive evidence: an explicit "of the month" tail, or an ordinal
        # surface ("1st").  A bare cardinal ("every 2") stays unread rather
        # than being guessed into a BYMONTHDAY.
        #
        # A count followed by a *weekday* is likewise never a day of the month:
        # "every 3rd tuesday" names tuesdays, not the 3rd of the month with a
        # stray weekday left over.  The ordinal surface must not buy an escape
        # here that the spelled surface ("every third tuesday") does not get --
        # both fall through to the interval reading below, which is the ruling
        # the elliptical nth-weekday branch above already applies.
        if (num_val is not None and 1 <= num_val <= 31
                and not (j < n and t[j].text in ctx.units)
                and not (j < n and _weekday_here(ctx, t[j], True) is not None)):
            end = _of_month_tail(ctx, j)
            if end > j or _is_ordinal_surface(t[num_idx]):
                return (_build_every("monthly", bymonthday=num_val),
                        set(range(i, end)))

        # -- "every the days <N> [of the month]" -> BYMONTHDAY ---------------
        # A *day* unit carrying a trailing day number is a day-of-month rule,
        # not a daily one: "todos os dias 1" (the 1st of every month) against
        # "todos os dias" (every day).  The trailing number is the only thing
        # that tells them apart, so the bare form keeps its DAILY reading and
        # only the numbered one diverts here.
        #
        # The determiner is *required*: the reading fires on the articled form
        # ("todos **os** dias 1") and not on the bare one ("todo dia 1"), which
        # a native European Portuguese speaker rejects for this sense.  English
        # never writes an article after "every", so this is unreachable there.
        if (saw_article and num_val is None
                and j + 1 < n and t[j].text in ctx.units
                and ctx.units[t[j].text] == "day"
                and t[j + 1].is_number and 1 <= int(t[j + 1].value) <= 31):
            return (_build_every("monthly", bymonthday=int(t[j + 1].value)),
                    set(range(i, _of_month_tail(ctx, j + 2))))

        if j >= n:
            continue
        iv = {"interval": interval} if interval != 1 else {}
        if t[j].text in ctx.weekday_word:
            byday = tuple((None, k) for k in range(5))
            return _build_every("weekly", byday=byday, **iv), set(range(i, j + 1))
        # the sibling class noun: "every weekend" is the very same determiner
        # plus class-noun frame as "every weekday", and reads the same way.
        # The days come from the locale's own weekend convention, not from a
        # hardcoded SA+SU.
        if t[j].text in ctx.weekend_word:
            return (_build_every("weekly", byday=_weekend_byday(ctx), **iv),
                    set(range(i, j + 1)))
        # "every quarter" -> a calendar quarter is three months, so the rule is
        # MONTHLY;INTERVAL=3 (the same reading the lone "quarterly" adverb gets
        # in _freq_map).  "every other quarter" bumps the interval to every
        # sixth month.  The quarter noun is its own vocabulary and is read ONLY
        # under this "every" determiner -- the bare "quarter" is a duration
        # fraction (a quarter of an hour) or a clock fraction (quarter past),
        # never a recurrence, so those readings are untouched.
        if t[j].text in ctx.quarter_word:
            return (_build_every("monthly", interval=interval * 3),
                    set(range(i, j + 1)))
        # A derived weekday plural ("tous les lundis", "todas as segundas") is
        # licensed here: this is already the "every"-determiner frame, so the
        # same positional licence _recur_nth_weekday uses applies, and the guard
        # goes through _weekday_here (which strips the -s) rather than the bare
        # weekday dict -- otherwise the plural is invisible and the phrase
        # silently misreads (French "tous les lundis ..." fell through to a
        # YEARLY date reading).  The plural is licensed ONLY for the plain
        # "every <weekday>" frame (no ordinal count): a tail-less ordinal plus a
        # plural weekday ("todos os terceiros domingos") stays deliberately
        # ambiguous per #217 and must fall through to None, so when a count was
        # read the strict bare-dict check applies (the singular still gets its
        # interval reading, the plural is left unread).
        allow_plural = num_val is None
        if (t[j].text in ctx.weekdays
                or (allow_plural and _weekday_here(ctx, t[j], True) is not None)):
            days, end = _collect_weekdays(ctx, j, allow_plural)
            byday = tuple((None, wd) for wd in days)
            return (_build_every("weekly", byday=byday, **iv),
                    set(range(i, end)))
        if t[j].text in ctx.units:
            unit = ctx.units[t[j].text]
            if unit == "fortnight":
                interval *= 2
                unit = "week"
                iv = {"interval": interval}
            freq = _UNIT_FREQ.get(unit)
            if freq is not None:
                # An "every N <unit>" interval may carry a trailing placement
                # qualifier that pins WHICH day the recurrence lands on: a
                # weekly interval takes "on <weekday(s)>" -> BYDAY ("every 2
                # weeks on tuesday"), a monthly one "on [the] <Nth>" ->
                # BYMONTHDAY ("every 3 months on the 5th").  Without this the
                # qualifier was stranded in the remainder and, with BYDAY/
                # BYMONTHDAY empty, occurrences() silently fell back to the
                # anchor's own weekday/day -- a wrong result.
                #
                # This capture is NOT universal: it fires only where the
                # locale ships an "on" connector (marker_on.voc -> ctx.on_words
                # via spec.connectors["on"]).  Locales that mark the placement
                # with a preposition (en "on", de "am", nl "op", pl "we", cs
                # "v", el "την", pt "à/no/...") or a leading article (fr "le",
                # es "el") supply that surface; morphological locales that fuse
                # the weekday into a case ending (fi "tiistaina") have no
                # separate word to list, so the qualifier stays in the
                # remainder there by construction.
                nxt = j + 1
                if nxt < n and t[nxt].text in ctx.on_words:
                    if freq == "WEEKLY":
                        got = _collect_weekdays(ctx, nxt + 1, True)
                        if got is not None:
                            days, wend = got
                            byday = tuple((None, wd) for wd in days)
                            return (_build_every("weekly", byday=byday, **iv),
                                    set(range(i, wend)))
                    elif freq == "MONTHLY":
                        k = nxt + 1
                        while k < n and t[k].text in ctx.articles:
                            k += 1
                        if k < n and t[k].is_number \
                                and 1 <= int(t[k].value) <= 31:
                            return (_build_every(
                                        "monthly",
                                        bymonthday=int(t[k].value), **iv),
                                    set(range(i, _of_month_tail(ctx, k + 1))))
                return _build_every(freq, **iv), set(range(i, j + 1))
    return None


def _recur_freq_word(ctx):
    """A lone ``daily`` / ``weekly`` / ``monthly`` / ``yearly`` / ``quarterly``
    / ``biweekly`` / ``fortnightly`` word, or ``[on] weekdays`` / ``[on]
    weekends``."""
    t = ctx.tokens
    for i, tok in enumerate(t):
        if tok.text in ctx.freq:
            freq, interval = ctx.freq[tok.text]
            iv = {"interval": interval} if interval != 1 else {}
            return _build_every(freq, **iv), {i}
    for i, tok in enumerate(t):
        # "on" is *required* here (not merely swallowed if present): a bare
        # "weekday"/"weekend" names a single day ("it's a weekday", "the
        # weekend was fun"), not a recurrence -- only the explicit "on
        # weekdays"/"on weekends" adverbial reads as one.
        if i - 1 < 0 or t[i - 1].text not in ctx.on_words:
            continue
        byday = None
        if tok.text in ctx.weekday_word:
            byday = tuple((None, k) for k in range(5))  # MO..FR
        elif tok.text in ctx.weekend_word:
            byday = _weekend_byday(ctx)
        if byday is None:
            continue
        return _build_every("weekly", byday=byday), {i - 1, i}
    return None


def _recur_habitual_weekday(ctx):
    """``<habitual preposition> <weekday>`` -> ``WEEKLY;BYDAY=<weekday>``.

    Some languages mark a habitual weekday with a **preposition** rather than
    a quantifier: European Portuguese "à segunda-feira" / "às segundas-feiras"
    (on Mondays) is the ordinary way to say "every monday", in both the
    singular and the plural.  Source: Ciberdúvidas da Língua Portuguesa,
    «À(s) segunda(s)-feira(s)», Eunice Marta, 1 June 2012 --
    https://ciberduvidas.iscte-iul.pt/consultorio/perguntas/as-segundas-feiras/31385
    -- which answers that both numbers convey "all Mondays" and that it is the
    **preposition** that carries the habitual sense: a bare article does not.

    Three things follow from that, and each is load-bearing here:

    * The marker is its own ``recur_habitual`` vocabulary, holding only the
      ``a + article`` contractions (pt à/às/ao/aos).  It deliberately does
      **not** hold the ``em + article`` ones (na/no/nas/nos): "na
      segunda-feira" is *on Monday*, one particular date, and that a-vs-em
      contrast is exactly the distinction the source draws.  Keeping them in
      separate vocabularies makes the wrong reading unwritable rather than
      merely unlikely.
    * The same contraction is also the clock marker ("às 9" = at nine), so the
      rule fires only when a **weekday** follows.  A number after it is a
      clock time and is left for the clock pin to read, which is what lets one
      sentence carry both uses.
    * A weekday plural is recognised **only** in this position (the surface
      plus its ``-s`` plural, derived, not listed).  Bare plural weekday
      surfaces cannot go into the global weekday vocabulary -- pt "domingos"
      is also a common surname, and a bare "sextas" makes unrelated
      ordinal-count readings match -- but under an explicit habitual
      preposition there is no such ambiguity.

    Runs **last** of the finders: a phrase that already reads as a fuller rule
    ("uma vez por semana à segunda") is claimed by that rule first, so this
    only ever fires on the bare habitual phrase.
    """
    if not ctx.habitual_words:
        return None
    t = ctx.tokens
    n = len(t)
    # the weekday surfaces this position accepts: the vocabulary's own, plus
    # the regular "-s" plural of each single-word surface ("domingo" ->
    # "domingos", "segundas feiras" is already vocabulary).
    surfaces = dict(ctx.weekdays)
    for surf, wd in ctx.weekdays.items():
        surfaces.setdefault(surf + "s", wd)
    for i in range(n - 1):
        if t[i].text not in ctx.habitual_words:
            continue
        wd = surfaces.get(t[i + 1].text)
        if wd is None:
            continue
        return (_build_every("weekly", byday=((None, wd),)),
                set(range(i, i + 2)))
    return None


def _recur_holiday(ctx):
    """``every <holiday>`` -> the holiday's yearly recurrence.

    A *fixed*-date holiday (Christmas, New Year, Halloween) becomes a real
    ``YEARLY;BYMONTH;BYMONTHDAY`` rule; an ``n``-th-weekday holiday
    (Thanksgiving) a ``YEARLY;BYMONTH;BYDAY=<n><WD>`` rule -- both are genuine
    RFC 5545 rules.  A **movable** feast (Easter and its cycle, the Islamic
    ``eid`` feasts, Passover, Diwali ...) has no such rule, so it becomes a
    :class:`~chronologia.recurrence.HolidayRecurrence`.
    """
    if not ctx.holidays:
        return None
    from chronologia.civil_holidays import (FixedRule, NthWeekdayRule,
                                            WELL_KNOWN_BY_KEY)
    t = ctx.tokens
    n = len(t)
    for i in range(n):
        if t[i].text not in ctx.every:
            continue
        j = i + 1
        while j < n and t[j].text in ctx.articles:
            j += 1
        if j >= n:
            continue
        key = ctx.holidays.get(t[j].text)
        if key is None:
            continue
        wk = WELL_KNOWN_BY_KEY.get(key)
        if wk is None:
            continue
        kind = wk.kind
        consumed = set(range(i, j + 1))
        if isinstance(kind, FixedRule):
            return (_build_every("yearly", bymonth=kind.month,
                                 bymonthday=kind.day), consumed)
        if isinstance(kind, NthWeekdayRule) and kind.post_offset == 0:
            return (_build_every("yearly", bymonth=kind.month,
                                 byday=((kind.n, kind.weekday),)), consumed)
        # movable feast: no RFC 5545 rule can express it.
        return HolidayRecurrence(key), consumed
    return None


def _recur_date_anchored(ctx):
    """Date-anchored recurrence, reusing the single-span engine for the date.

    * ``every [year] [on] <date>``  -> ``YEARLY;BYMONTH;BYMONTHDAY``
      ("every 10th of may", "every may 10", "every year on may 10");
    * ``<day> of every month`` / ``every month [on the] <day>``
      -> ``MONTHLY;BYMONTHDAY``.

    The month/day are lifted from whatever the ``calendar_date`` construction
    resolves -- no new date grammar is written here.
    """
    t = ctx.tokens
    n = len(t)
    engine = _timespan_engine(ctx.lang)
    anchor = ctx.anchor or datetime.now()
    if isinstance(anchor, datetime):
        anchor = anchor.replace(tzinfo=None)
    date_matches = [m for m in engine.matcher.match(t)
                    if m.construction == "calendar_date"]

    # -- monthly: a day-of-month tied to "every month" --------------------
    for i in range(n):
        if t[i].text not in ctx.every:
            continue
        j = i + 1
        while j < n and t[j].text in ctx.articles:
            j += 1
        if not (j < n and t[j].text in ctx.units
                and ctx.units[t[j].text] == "month"):
            continue
        # "<N> of every month" / "the last [day] of every month": a preposed
        # ordinal (or "last" marker) just BEFORE "every".  Checked FIRST -- a
        # preposed day-of-month is the specific reading and must win over a
        # trailing number that is really an occurrence count ("the 15th of every
        # month 3 times", es "el 15 de cada mes 3 veces": read day 15, leave the
        # count for the post-pass).  Doing this before the forward scan is
        # locale-independent, unlike the count-word guard on that scan (the
        # count words are only defined for some locales).  An explicit "day"
        # noun may sit between the ordinal and "of" -- skip it.
        k = i - 1
        while k >= 0 and (t[k].text in ctx.of_words or t[k].text in ctx.articles
                          or (t[k].text in ctx.units
                              and ctx.units[t[k].text] == "day")):
            k -= 1
        day_val = None
        if k >= 0 and t[k].is_number and 1 <= int(t[k].value) <= 31:
            day_val = int(t[k].value)
        elif (k >= 0 and t[k].text in ctx.rel_markers
              and ctx.rel_markers[t[k].text] == -1):
            day_val = -1          # "the last [day] of every month" -> month end
        if day_val is not None:
            start = k
            # swallow a leading determiner and an explicit "day" unit naming
            # the number ("no dia 1 de cada mês", on day 1 of every month --
            # the same rule English writes as "on the 1st of every month").
            while start - 1 >= 0 and (
                    t[start - 1].text in ctx.articles
                    or (t[start - 1].text in ctx.units
                        and ctx.units[t[start - 1].text] == "day")):
                start -= 1
            return (_build_every("monthly", bymonthday=day_val),
                    set(range(start, j + 1)))
        # "every month (on)(the) <N>": a POSTPOSED number within a short window,
        # only when there was no preposed ordinal above.  A number that is
        # really the trailing occurrence count ("every month 5 TIMES") is left
        # for the COUNT post-pass (guarded by the locale's count words).
        r = j + 1
        steps = 0
        while r < n and not t[r].is_number and steps < 3:
            r += 1
            steps += 1
        if (r < n and t[r].is_number and 1 <= int(t[r].value) <= 31
                and not (r + 1 < n and t[r + 1].text in ctx.count_words)):
            return (_build_every("monthly", bymonthday=int(t[r].value)),
                    set(range(i, r + 1)))

    # -- yearly: a full calendar date *immediately* after "every [year] [on]"
    # The date must start right after the every-skeleton (articles, an optional
    # year unit, and one optional filler such as "on") -- otherwise a date
    # buried in a trailing bound clause ("every friday *until june*") would be
    # misread as the anchor.
    for i in range(n):
        if t[i].text not in ctx.every:
            continue
        j = i + 1
        while j < n and t[j].text in ctx.articles:
            j += 1
        if j < n and t[j].text in ctx.units and ctx.units[t[j].text] == "year":
            j += 1
        # the date must start at (or just after) the skeleton: the only tokens
        # tolerated in the gap are articles or a short filler run ("on"/"in") --
        # never a weekday, number or unit that would belong to a different rule.
        dm = None
        for m in date_matches:
            if m.span[0] < j:
                continue
            gap = t[j:m.span[0]]
            if len(gap) <= 2 and all(
                    g.text in ctx.articles
                    or (not g.is_number
                        and _weekday_here(ctx, g, True) is None
                        and g.text not in ctx.units and g.text not in ctx.every)
                    for g in gap):
                dm = m
                break
        if dm is None:
            continue
        # Read the month/day straight from the matched calendar_date slots
        # rather than resolving to a concrete datetime: a *recurring* date is
        # well-formed independently of whether the anchor's own year contains
        # it, so "every 29th of february" (a leap-day rule) must map to
        # YEARLY;BYMONTH=2;BYMONTHDAY=29 whatever the anchor.  The single-span
        # resolver builds datetime(anchor.year, 2, 29) and returns None in a
        # non-leap year, which used to drop this frame and let the greedy
        # _recur_every catch-all mis-read it as a monthly BYMONTHDAY firing 11x
        # a year.
        month_tok = dm.slots.get("MONTH")
        if month_tok is None or month_tok.text not in engine.spec.months:
            continue
        month = engine.spec.months[month_tok.text]
        day_tok = dm.slots.get("DAY")
        day = int(day_tok.value) if day_tok else 1
        try:
            rule = _build_every("yearly", bymonth=month, bymonthday=day)
        except ValueError:
            # the named date recurs in no year ("every 31st of april").  This is
            # still the specific yearly-date frame -- consume it and report no
            # recurrence, rather than fall through to a wrong MONTHLY;BYMONTHDAY.
            return (None, set(range(i, dm.span[1])))
        return (rule, set(range(i, dm.span[1])))
    return None


# Recurrence finders, first match wins.  The order below is load-bearing, and
# it is NOT the order the functions are defined in above, so tidying the
# file into definition order would silently change what these phrases mean.
# Two constraints hold, measured by reordering this tuple against the whole
# recurrence corpus (every adjacent swap passes; the two moves named here do
# not) -- and enforced by ``test/test_recurrence_finder_order.py``:
#
# * ``_recur_every`` must run AFTER the specific finders.  It is a greedy
#   catch-all: an ``every`` marker plus almost any following count or unit
#   satisfies it, so run first it claims the determiner out of a *longer*
#   specific frame and strands the rest in the remainder -- "every 10th of may"
#   (a yearly date, not a monthly one), "first monday of every month",
#   "jeden 25. dezember", "el 10 de cada mes", "le 10 de chaque mois",
#   "no dia 15 de cada mês".
# * ``_recur_habitual_weekday`` must run LAST.  A habitual phrase carries a
#   frequency *count* ("uma vez por semana à segunda" -- once a week, on
#   monday) whose weekday tail belongs to the more specific reading; run first
#   it wins the weekday alone and drops the count.
#
# The remaining five are mutually commutable -- their frames do not overlap --
# so there is no precedence ranking to state here, only those two edges.  A
# table for seven functions would invent structure that is not there.
_FINDERS = (_recur_nth_weekday_list, _recur_nth_weekday, _recur_holiday,
            _recur_date_anchored,
            _recur_once, _recur_on_weekdays, _recur_every, _recur_freq_word,
            _recur_habitual_weekday)
