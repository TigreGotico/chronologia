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

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from chronologia.astrodate import DateSpan
from chronologia.recurrence import Recurrence
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
    "minute": 60,
    "hour": 3600,
    "day": 86400,
    "week": 604800,
    "fortnight": 1209600,
}


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
) -> Optional[Tuple[timedelta, str]]:
    """Extract a :class:`datetime.timedelta` length from ``text``.

    Reads the fixed-width units minute / hour / day / week / fortnight, summing
    every count it finds ("2 days 4 hours" -> 52 hours), including fractional
    counts ("half an hour" -> 30 min, "quarter of an hour" -> 15 min) and the
    trailing "... and a half" idiom ("an hour and a half" -> 90 min).  Numbers
    are folded by ``ovos-number-parser`` before matching, so "90 minutes" and
    "ninety minutes" read alike.

    Calendar-ambiguous units (month, year, decade, ...) are **not** durations
    and are left in the remainder.  Returns ``(duration, remainder)`` or
    ``None`` when the text names no fixed-width length.
    """
    from chronologia.extract import _timespan_engine

    engine = _timespan_engine(lang)
    spec = engine.spec
    tokens = engine.tokenize(text)
    fracs = _fraction_words(spec)
    articles = _article_words(spec)
    of_words = set(spec.connectors.get("of", ()))
    and_words = _and_words(spec)
    filler = articles | of_words
    n = len(tokens)

    def _read_additive(k):
        """`` and a half`` / `` and a quarter`` at index ``k`` -> (frac, end)."""
        j = k
        if j < n and tokens[j].text in and_words:
            j += 1
            while j < n and tokens[j].text in articles:
                j += 1
            if j < n and tokens[j].text in fracs:
                return fracs[tokens[j].text], j + 1
        return None, k

    total = 0.0
    found = False
    consumed = set()
    i = 0
    while i < n:
        j = i
        count = None
        # a leading article: "a day" -> count 1; "a couple of days" -> skip it.
        if tokens[j].text in articles:
            if j + 1 < n and (tokens[j + 1].is_number
                              or tokens[j + 1].text in fracs):
                j += 1
            else:
                count, j = 1.0, j + 1
        if count is None and j < n:
            if tokens[j].is_number:
                count, j = float(tokens[j].value), j + 1
                # a fraction word right after the count multiplies it: "three
                # quarters (of an hour)", "eine viertel stunde" (a quarter hour)
                if j < n and tokens[j].text in fracs:
                    count, j = count * fracs[tokens[j].text], j + 1
            elif tokens[j].text in fracs:
                count, j = fracs[tokens[j].text], j + 1
            elif tokens[j].text in spec.quantifiers:
                count, j = spec.quantifiers[tokens[j].text], j + 1
        if count is None:
            i += 1
            continue
        # "one and a half hours": the fraction precedes the unit.
        add, j = _read_additive(j)
        if add is not None:
            count += add
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
    remainder = " ".join(t.raw for t in tokens
                         if t.index not in consumed).strip()
    return timedelta(seconds=total), remainder


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
    """
    span: DateSpan
    text: str
    token_span: Tuple[int, int]
    char_span: Optional[Tuple[int, int]] = None


def extract_timespans(
        text: str,
        lang: str = "en-us",
        anchor: Optional[datetime] = None,
) -> List[TimeMention]:
    """Every non-overlapping temporal mention in ``text``, in reading order.

    Where :func:`~chronologia.extract.extract_timespan` collapses a sentence
    to a single span, this resolves **all** of them -- "meet friday at 3 or
    monday at noon" yields two mentions.  It reuses the same matcher, whose
    selected matches never overlap; a lone clock time immediately following a
    date mention composes onto it (the minute-wide time on that day), exactly
    as the single-span edge composes them.

    Returns a list of :class:`TimeMention` (empty when nothing matched).
    """
    from chronologia.extract import _timespan_engine
    from chronologia.extract.resolver import (DATE_CONSTRUCTIONS,
                                              compose_date_clock)

    engine = _timespan_engine(lang)
    anchor = anchor or datetime.now()
    if isinstance(anchor, datetime):
        anchor = anchor.replace(tzinfo=None)
    tokens = engine.tokenize(text)

    resolved = []
    for match in engine.matcher.match(tokens):
        res = engine.resolver.resolve(match, anchor)
        if res is not None:
            resolved.append((match, res))
    resolved.sort(key=lambda mr: mr[0].span[0])

    out: List[Tuple[Tuple[int, int], DateSpan]] = []
    for match, res in resolved:
        # a clock time right after a date mention composes onto that day
        if (match.construction == "clock_time" and out
                and _prev_is_date(resolved, match)):
            prev_match, prev_res = _prev_date(resolved, match)
            merged = compose_date_clock(prev_res, res)
            lo = min(prev_match.span[0], match.span[0])
            hi = max(prev_match.span[1], match.span[1])
            out[-1] = ((lo, hi), merged.value)
            continue
        out.append((match.span, res.value))

    return [TimeMention(value, " ".join(t.raw for t in tokens[lo:hi]), (lo, hi),
                        _char_span(tokens, lo, hi))
            for (lo, hi), value in out]


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


def extract_recurrence(
        text: str,
        lang: str = "en-us",
        anchor: Optional[datetime] = None,
) -> Optional[Tuple[Recurrence, str]]:
    """Map a recurring phrase onto an RFC 5545 :class:`~chronologia.recurrence.Recurrence`.

    Handles the civil recurrence idioms -- "every friday", "every other week",
    "every 2 weeks", "every weekday", "daily"/"weekly"/"monthly"/"yearly", and
    the ordinal "first monday of every month" / "last friday of every month"
    (and "the third thursday of november") -- reading weekday names, unit words
    and the ``every`` marker from the locale.

    A trailing bound is folded onto the rule: an ``until``/``till`` marker plus
    a date sets ``UNTIL`` ("every friday until june"); a ``for`` marker plus a
    fixed-width duration sets ``COUNT`` -- the number of occurrences the
    duration spans at the rule's frequency ("daily for two weeks" -> COUNT=14,
    "every monday for 6 weeks" -> COUNT=6).  Sub-day detail a date-level rule
    cannot carry ("daily *at 9*") is left in the remainder.

    Returns ``(recurrence, remainder)`` or ``None`` when no recurrence is found.
    """
    from chronologia.extract import _timespan_engine

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
    )

    for finder in (_recur_nth_weekday, _recur_every, _recur_freq_word):
        hit = finder(ctx)
        if hit is not None:
            rec, consumed = hit
            rec, consumed = _apply_bounds(rec, consumed, ctx, lang, anchor)
            remainder = " ".join(t.raw for t in tokens
                                 if t.index not in consumed).strip()
            return rec, remainder
    return None


def _apply_bounds(rec, consumed, ctx, lang, anchor):
    """Fold a trailing ``until <date>`` (-> UNTIL) or ``for <duration>``
    (-> COUNT) bound onto ``rec``, extending ``consumed`` over the words it
    reads.  A bound the engine cannot ground (an unparseable date, a
    calendar-ambiguous duration under a MONTHLY/YEARLY rule) is left untouched
    in the remainder rather than guessed."""
    from dataclasses import replace as _replace
    tokens = ctx.tokens
    n = len(tokens)

    def _tail(i):
        return " ".join(t.raw for t in tokens[i + 1:])

    for i in range(n):
        if i in consumed or tokens[i].text not in ctx.until_words:
            continue
        from chronologia.extract import extract_timespan
        got = extract_timespan(_tail(i), lang, anchor=anchor)
        if got is not None:
            rec = _replace(rec, until=got[0].start)
            consumed = consumed | set(range(i, n))
        break

    for i in range(n):
        if i in consumed or tokens[i].text not in ctx.for_words:
            continue
        dur = extract_duration(_tail(i), lang)
        if dur is not None:
            count = _count_from_duration(rec.freq, dur[0])
            if count is not None:
                rec = _replace(rec, count=count)
                consumed = consumed | set(range(i, n))
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


def _freq_map(connectors):
    out = {}
    for key, freq in (("freq_daily", "DAILY"), ("freq_weekly", "WEEKLY"),
                      ("freq_monthly", "MONTHLY"), ("freq_yearly", "YEARLY")):
        for s in connectors.get(key, ()):
            out[s] = freq
    return out


def _recur_nth_weekday(ctx):
    """``<ordinal|last> <weekday> of [every] (month|<month name>)``."""
    t = ctx.tokens
    n = len(t)
    for w in range(1, n):
        if t[w].text not in ctx.weekdays:
            continue
        wd = ctx.weekdays[t[w].text]
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
            rec = _nth_weekday_of_month(ordn, wd, month=ctx.months[t[r].text])
            return rec, set(range(start, r + 1))
        if r < n and t[r].text in ctx.units and ctx.units[t[r].text] == "month":
            return _nth_weekday_of_month(ordn, wd), set(range(start, r + 1))
    return None


def _recur_every(ctx):
    """``every [other|N] (<weekday> | <unit> | weekday-word)``."""
    t = ctx.tokens
    n = len(t)
    for i in range(n):
        if t[i].text not in ctx.every:
            continue
        j = i + 1
        interval = 1
        # an article, an "other" marker and an explicit count may appear in any
        # order before the target noun ("every other week", "toutes les deux
        # semaines", "cada dos semanas").
        while j < n:
            if t[j].text in ctx.articles:
                j += 1
            elif t[j].text in ctx.other:
                interval, j = 2, j + 1
            elif t[j].is_number:
                interval, j = int(t[j].value), j + 1
            else:
                break
        if j >= n:
            continue
        iv = {"interval": interval} if interval != 1 else {}
        if t[j].text in ctx.weekday_word:
            byday = tuple((None, k) for k in range(5))
            return _build_every("weekly", byday=byday, **iv), set(range(i, j + 1))
        if t[j].text in ctx.weekdays:
            wd = ctx.weekdays[t[j].text]
            return (_build_every("weekly", byday=((None, wd),), **iv),
                    set(range(i, j + 1)))
        if t[j].text in ctx.units:
            unit = ctx.units[t[j].text]
            if unit == "fortnight":
                interval *= 2
                unit = "week"
                iv = {"interval": interval}
            freq = _UNIT_FREQ.get(unit)
            if freq is not None:
                return _build_every(freq, **iv), set(range(i, j + 1))
    return None


def _recur_freq_word(ctx):
    """A lone ``daily`` / ``weekly`` / ``monthly`` / ``yearly`` word."""
    for i, tok in enumerate(ctx.tokens):
        if tok.text in ctx.freq:
            return _build_every(ctx.freq[tok.text]), {i}
    return None
