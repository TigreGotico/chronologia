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
    from chronologia.extract.pipeline import render_remainder
    remainder = render_remainder(text, [t for t in tokens
                                        if t.index not in consumed])
    return DurationResult(timedelta(seconds=total), remainder)


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
    from chronologia.extract.confidence import score_candidates
    from chronologia.extract.resolver import (DATE_CONSTRUCTIONS,
                                              compose_date_clock)

    engine = _timespan_engine(lang)
    anchor = anchor or datetime.now()
    if isinstance(anchor, datetime):
        anchor = anchor.replace(tzinfo=None)
    tokens = engine.tokenize(text)
    total = len(tokens)

    scored = list(score_candidates(
        engine.matcher.match(tokens),
        lambda m: engine.resolver.resolve(m, anchor), total, engine.spec))
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

    return [TimeMention(value, " ".join(t.raw for t in tokens[lo:hi]), (lo, hi),
                        _char_span(tokens, lo, hi), conf)
            for (lo, hi), value, conf in out]


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
        at_words=set(C.get("at", ())),
        holidays=dict(spec.holidays),
        lang=lang,
        anchor=anchor,
    )

    for finder in (_recur_nth_weekday, _recur_holiday, _recur_date_anchored,
                   _recur_every, _recur_freq_word):
        hit = finder(ctx)
        if hit is not None:
            rec, consumed = hit
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
    from chronologia.extract import _timespan_engine

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
    from chronologia.extract import extract_timespan
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
    holidays: dict = None
    lang: str = "en-us"
    anchor: Optional[datetime] = None


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
    from chronologia.extract import _timespan_engine
    from chronologia.extract.resolver import DATE_CONSTRUCTIONS  # noqa: F401

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
        # "every month (on)(the) <N>": the next number within a short window.
        r = j + 1
        steps = 0
        while r < n and not t[r].is_number and steps < 3:
            r += 1
            steps += 1
        if r < n and t[r].is_number and 1 <= int(t[r].value) <= 31:
            return (_build_every("monthly", bymonthday=int(t[r].value)),
                    set(range(i, r + 1)))
        # "<N> of every month": the number just before the "every".
        k = i - 1
        while k >= 0 and (t[k].text in ctx.of_words or t[k].text in ctx.articles):
            k -= 1
        if k >= 0 and t[k].is_number and 1 <= int(t[k].value) <= 31:
            start = k
            while start - 1 >= 0 and t[start - 1].text in ctx.articles:
                start -= 1
            return (_build_every("monthly", bymonthday=int(t[k].value)),
                    set(range(start, j + 1)))

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
                    or (not g.is_number and g.text not in ctx.weekdays
                        and g.text not in ctx.units and g.text not in ctx.every)
                    for g in gap):
                dm = m
                break
        if dm is None:
            continue
        res = engine.resolver.resolve(dm, anchor)
        if res is None:
            continue
        start = res.value.start
        return (_build_every("yearly", bymonth=start.month,
                             bymonthday=start.day),
                set(range(i, dm.span[1])))
    return None
