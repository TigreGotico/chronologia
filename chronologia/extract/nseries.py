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

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, NamedTuple, Optional, Tuple, Union

from chronologia.astrodate import DateSpan
from chronologia.extract.pipeline import fold_tokens, pretokens, require_text
from chronologia.extract.timespan import (_RANGE_BETWEEN, _RANGE_FROM,
                                          _RANGE_TO, _conn_surfaces,
                                          _exclusion_vetoes, _extract_range,
                                          _resolve_scale_mode,
                                          _timespan_engine,
                                          _WEEKDAY_LABELABLE_DATES,
                                          extract_timespan)
from chronologia.recurrence import (HolidayRecurrence, JurisdictionHolidays,
                                     Recurrence)
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
    return _duration_core(text, engine)


def _duration_core(text: str, engine) -> Optional[DurationResult]:
    """The engine-based body of :func:`extract_duration`.

    Factored out so a caller that already holds the per-language
    :class:`~chronologia.extract.timespan.DateTimeEngine` (the trailing
    "for <duration>" extension onto a resolved clock-start span in
    :mod:`chronologia.extract.timespan`) can read a duration without
    re-resolving the language string back into an engine -- the same
    cached engine object is reused, and no lang-string plumbing has to be
    threaded through the single-span resolver just for this.
    """
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
            while j < n and (tokens[j].text in articles
                              or (tokens[j].is_number
                                  and tokens[j].value == 1.0)):
                # A folded "one"-valued number token doubles as the
                # indefinite article before the fraction word in languages
                # where the numeral IS the article ("en" in Swedish "en och
                # en halv timme" == "one and one half hour"): the number
                # fold already turned the second "en" into a bare `1`
                # token, so the textual-article check above never sees it
                # and "en halv" (== "a half") strands as an unconsumed
                # `1 halv` pair, silently truncating the phrase to just the
                # leading "en timme" reading.  Skipping it here restores
                # the trailing-fraction idiom without touching languages
                # whose article is not also a numeral.
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
            elif (tokens[j].text in spec.units
                  and spec.units[tokens[j].text] in _DUR_UNIT_SECONDS
                  and _read_additive(j + 1)[0] is not None):
                # A bare unit with NO leading count, immediately followed by
                # the trailing "... and a half" idiom, implies an
                # article-like count of one ("hodinu a půl" ==
                # "an hour and a half"; "hodinu a pol"): unlike English/
                # Swedish, these languages fold no "an"/"en" indefinite
                # article onto the unit here, so without this the count-scan
                # never starts and the whole phrase is left as remainder.
                # Peeked (not assumed) so a genuinely bare unit outside the
                # idiom is untouched -- ``j`` stays AT the unit so the
                # ordinary unit-match branch below still finds it.
                count = 1.0
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
    # A duration-marking preposition directly adjacent to the bound duration
    # ("for 90 minutes", "für 90 Minuten", "durante 90 minutos") is temporal
    # glue, not leftover text: fold it into ``consumed`` so it
    # does not strand alone in the remainder.  Reuses the SAME
    # ``recur_for``/``marker_recur_for.voc`` vocabulary as the recurrence
    # grammar's "every monday *for* 3 weeks" bound and the timespan module's
    # trailing "... for <duration>" extension -- one marker family, not a
    # parallel one.  Matched only when the marker sits immediately before the
    # duration's own earliest consumed token (after the "and"/range folding
    # above, so "for 3 to 5 days" attaches to the "3", not the "5"): a marker
    # separated by other words ("meet for lunch in 90 minutes") is NOT
    # adjacent and stays in the remainder, since it is not glue for THIS
    # duration.  "in" is deliberately excluded -- it marks a relative OFFSET
    # ("in 90 minutes" == 90 minutes from now), not a bound duration, and is
    # not a member of ``recur_for`` in any locale; consuming it would blur
    # that distinction, so "in 90 minutes" -> remainder "in" is correct as-is.
    if consumed:
        start = min(consumed)
        for words in _conn_surfaces(spec, "recur_for", ("for",)):
            wlen = len(words)
            if wlen and start - wlen >= 0 and [
                    tokens[start - wlen + m].text.lower()
                    for m in range(wlen)] == words:
                consumed.update(range(start - wlen, start))
                break
    # A stranded CALENDAR-grain unit (month/year/decade/...) is not a
    # fixed-width length -- a bare "3 months" already returns None rather
    # than some arbitrary 30-day guess (see the module docstring).  A MIXED
    # compound ("3 months and 2 days") must follow the same refusal, not
    # silently answer with only its fixed-width part ("2 days") and strand
    # "3 months and" -- a partial value with the rest dropped is a wrong
    # answer, not a partial one.  Any unconsumed calendar-unit surface means
    # the phrase named a length this function cannot express in whole; honour
    # the "3 months" convention across the whole compound and refuse.
    for tok in tokens:
        if tok.index in consumed:
            continue
        kind = spec.units.get(tok.text)
        if kind is not None and kind not in _DUR_UNIT_SECONDS:
            return None
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
    confidence_of = {id(sc.match): sc.confidence for sc in scored}

    # Group the resolved matches into CLUSTERS of mutually-adjacent matches --
    # the same adjacency :func:`~chronologia.extract.timespan._compose` (the
    # single-span composer) uses to decide a weekday/daypart/clock belong to
    # ONE reading: connected via glue tokens (at/on/of/the, a daypart
    # preposition, ...) or tokens another match in the group already claims.
    # A genuine clause break -- a comma, "and"/"or"/"then", an unrelated word
    # -- starts a new cluster, so composition never bleeds across separate
    # mentions ("tomorrow at 9 and next friday at 5" stays two clusters).
    # Each multi-match cluster is then handed to :func:`extract_timespan`
    # (via its own char extent, extended over a trailing "for <duration>"
    # into the next cluster's boundary) so it runs through the IDENTICAL
    # composition machinery the single-span edge uses -- weekday+daypart+
    # clock merge, daypart-meridiem, for-duration extension -- rather than a
    # second, narrower copy of it.
    clusters = _cluster_resolved(resolved, tokens, engine.spec, text)

    out: List[Tuple[Tuple[int, int], DateSpan, float]] = []
    for ci, cluster in enumerate(clusters):
        if len(cluster) == 1:
            match, res = cluster[0]
            out.append((match.span, res.value, confidence_of[id(match)]))
            continue
        lo_tok = min(m.span[0] for m, _ in cluster)
        hi_tok = max(m.span[1] for m, _ in cluster)
        start_char = tokens[lo_tok].char_start
        conf = min(confidence_of[id(m)] for m, _ in cluster)
        if ci + 1 < len(clusters):
            nxt_lo = min(m.span[0] for m, _ in clusters[ci + 1])
            boundary = tokens[nxt_lo].char_start
        else:
            boundary = None
        if boundary is None:
            boundary = len(text)
        # the last token of the cluster's own span carries the real char
        # extent MOST of the time; a fully engine-synthesised token (a
        # multiword surface glued at match time with no offset recorded --
        # e.g. pt "meio-dia" folding to a single ``meiodia`` token) leaves
        # ``char_end`` as ``None``.  Walk back to the nearest token in the
        # cluster that DOES carry one; the offset-less tail past it is still
        # part of this cluster's own text, so the boundary already computed
        # above (the next cluster's start, or the end of ``text``) is the
        # correct upper bound to fall back on -- it is exactly the same
        # "how far can this reading's own text run" question ``boundary``
        # already answers for the trailing "for <duration>" extension.
        if tokens[hi_tok - 1].char_end is not None:
            end_char = tokens[hi_tok - 1].char_end
        elif any(tokens[idx].char_end is None
                 for idx in range(lo_tok, hi_tok)):
            end_char = boundary
        else:
            end_char = None
            for idx in range(hi_tok - 1, lo_tok - 1, -1):
                if tokens[idx].char_end is not None:
                    end_char = tokens[idx].char_end
                    break
        if start_char is None or end_char is None:
            # no character offsets to slice by at all (fully
            # engine-synthesised tokens throughout) -- fall back to the
            # uncomposed matches rather than guess.
            for m, r in cluster:
                out.append((m.span, r.value, confidence_of[id(m)]))
            continue
        # compose over the cluster's OWN char extent only (never the trailing
        # clause boundary) so an un-consumed trailing connector ("then",
        # "and") never gets pulled into the composed reading's own extent.
        slice_text = text[start_char:end_char]
        result = extract_timespan(slice_text, lang, anchor=anchor, scale=scale)
        if result is None:
            # composition declined (e.g. a daypart/clock meridiem
            # contradiction) -- keep the matches uncomposed rather than drop
            # them.
            for m, r in cluster:
                out.append((m.span, r.value, confidence_of[id(m)]))
            continue
        consumed_end = max(start_char + len(slice_text) - len(result.remainder),
                            end_char)
        span, consumed_end = _extend_cluster_for_duration(
            result.span, text, consumed_end, boundary, engine)
        hi = hi_tok
        for idx in range(hi_tok, len(tokens)):
            if tokens[idx].char_start is not None and tokens[idx].char_start < consumed_end:
                hi = idx + 1
            else:
                break
        out.append(((lo_tok, hi), span, conf))

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
            # a sentence-final period between the two mentions (a
            # dot-folding, ordinal_dot locale like de/ru drops it from the
            # token stream, same as a comma) means these are two INDEPENDENT
            # clauses, never a "from A to B" range -- "am Montag. ... bis
            # Freitag" must not fuse into one range spanning both sentences.
            # See ``_sentence_period_between``.
            boundary = (a_hi > 0 and b_lo < len(tokens)
                        and _sentence_period_between(tokens, a_hi - 1, b_lo, text))
            if cs is not None and ce is not None and not boundary:
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


def _sentence_period_between(tokens, lo_idx, hi_idx, text):
    """Whether a literal sentence-final ``.`` sits in ``text`` between token
    ``lo_idx`` and token ``hi_idx`` (``lo_idx < hi_idx``, both valid token
    indices).

    The tokenizer never leaves a punctuation character INSIDE a token's own
    char span except when it is genuinely part of the token -- an ordinal dot
    (``ordinal_dot`` mode: ``"15."`` is one token, dot included) or a decimal
    point inside a number.  Every other ``.`` -- above all a sentence-final
    one, "...um 14 Uhr. Bitte..." -- is dropped by the tokenizer entirely and
    so survives only in the character GAP between one token's end and the
    next token's start.  Checking that gap for a literal ``.`` is therefore a
    tokenizer-shape-agnostic sentence-boundary test: it fires on a genuine
    clause break in de/ru (dot-folding, ordinal_dot locales) exactly where an
    ordinal dot ("15. Juni", "3. März um 9 Uhr") does NOT fire, because that
    dot sits inside the ordinal token's own span, never in a gap -- and it is
    equally correct (a no-op) in en/es, which have no ordinal-dot tokens to
    confuse it with in the first place.

    ``lo_idx``/``hi_idx`` name the LAST token before the region and the FIRST
    token after it; every token strictly between them is also checked, so a
    period after any word in a longer gap ("Freitag um 14 Uhr. Bitte reichen
    Sie") is still caught, not just one immediately adjacent to the edges.
    """
    for i in range(lo_idx, hi_idx):
        a, b = tokens[i], tokens[i + 1]
        if a.char_end is None or b.char_start is None:
            continue
        if "." in text[a.char_end:b.char_start]:
            return True
    return False


#: connector keys that join two DISTINCT references rather than gluing one
#: reference's own parts together -- the same split
#: :func:`~chronologia.extract.timespan._compose` uses to decide when a
#: weekday/daypart/clock/date genuinely fuse into one reading.
_CLAUSE_SEP_KEYS = {"and", "or", "to", "from", "between", "until", "since"}


def _clause_glue(spec):
    """Function-word surfaces that legitimately join a date to a time WITHIN
    one reference (at/on/of/the, a daypart preposition, ...) -- every
    connector surface that is not keyed under a pure separator
    (:data:`_CLAUSE_SEP_KEYS`), mirroring the glue set
    :func:`~chronologia.extract.timespan._compose` computes for its own
    adjacency test."""
    return {s for k, vals in spec.connectors.items() if k not in _CLAUSE_SEP_KEYS
            for s in vals}


def _cluster_role(construction):
    """The composition ROLE a construction can fill inside one cluster,
    mirroring :func:`~chronologia.extract.timespan._compose`'s own shape:
    it fuses at most one clock, one daypart, one weekday(-label) and one
    anchor DATE into a single reading -- never two anchor dates.  Everything
    that is not a clock/daypart/weekday is an anchor date candidate.
    """
    if construction == "clock_time":
        return "clock"
    if construction == "daypart_ref":
        return "daypart"
    if construction == "weekday_ref":
        return "weekday"
    return "date"


def _extend_cluster_for_duration(span, text, end_char, boundary, engine):
    """Extend a cluster's composed PINPOINT clock-start span by a trailing
    bare "for <duration>" phrase, bounded to THIS clause's own extent
    (``end_char`` to ``boundary`` -- the next cluster's start, or the end of
    ``text``) so a duration named in a LATER clause is never pulled onto an
    earlier mention.

    Mirrors the rule :func:`~chronologia.extract.timespan.
    _extend_clock_for_duration` applies for a single mention -- fires only
    when the span is exactly the minute-wide reading a lone/composed clock
    produces -- but reads the marker+duration from this clause's own bounded
    tail via :func:`_duration_core`, the same duration reader, rather than
    scanning the rest of the utterance (where a second, later "for ..."
    clause could otherwise bleed onto this one).

    Returns ``(span, consumed_end)`` -- the (possibly unchanged) span and the
    character offset of the end of what it consumed.
    """
    if span.end - span.start != timedelta(minutes=1):
        return span, end_char
    tail = text[end_char:boundary]
    from chronologia.extract.timespan import _for_marker_pattern
    m = _for_marker_pattern(engine.spec).search(tail)
    if m is None:
        return span, end_char
    after = tail[m.end():]
    got = _duration_core(after, engine)
    if got is None:
        return span, end_char
    # ``got.remainder`` is a re-rendered (whitespace/punctuation-collapsed)
    # string, not a char-locatable slice of ``after`` -- a length subtraction
    # would misplace the boundary whenever punctuation like a trailing comma
    # is dropped in the rendering.  Locate the FIRST remainder word back in
    # ``after`` by a whole-word search instead, so the consumed extent stops
    # exactly at the duration phrase and never swallows a leftover connector
    # ("for 2 hours, then again ..." must not consume "then").
    remainder = got.remainder.strip()
    if remainder:
        first_word = remainder.split()[0]
        wm = re.search(r"\b" + re.escape(first_word) + r"\b", after)
        consumed_in_after = wm.start() if wm else len(after)
    else:
        consumed_in_after = len(after)
    consumed_end = end_char + m.end() + consumed_in_after
    return DateSpan(span.start, span.start + got.duration), consumed_end


def _cluster_resolved(resolved, tokens, spec, text=None):
    """Group resolved ``(match, res)`` pairs into clusters of matches the
    single-span composer would fuse into ONE reading.

    Two matches sit in the same cluster when every token strictly between
    them is either already claimed by some match in ``resolved`` (the
    daypart in "monday morning at 3pm") or a bare glue connector
    (:func:`_clause_glue`), AND no stray punctuation (a comma, semicolon, ...)
    sits between them: the tokenizer drops punctuation from the token stream
    entirely, so two matches sitting back-to-back with a comma between them
    ("monday at 9, friday at 5") have an EMPTY token gap that would otherwise
    read as vacuously adjacent.  Anything else -- a separator word
    ("and"/"or"), unrelated prose -- starts a new cluster.  This is exactly
    the adjacency test :func:`~chronologia.extract.timespan._compose` applies
    pairwise, so a clause's matches cluster together the same way the
    single-span edge would compose them, and a genuine clause boundary
    (comma, "then", a distinct "and"-joined mention) reliably splits them.

    Returns a list of clusters (each a list of ``(match, res)`` pairs), in
    reading order.
    """
    if not resolved:
        return []
    glue = _clause_glue(spec)
    ordered = sorted(resolved, key=lambda mr: mr[0].span[0])
    covered = set()
    for m, _r in ordered:
        covered.update(range(*m.span))
    clusters = [[ordered[0]]]
    for prev, nxt in zip(ordered, ordered[1:]):
        (lo_span, hi_span) = sorted((prev[0].span, nxt[0].span))
        gap = range(lo_span[1], hi_span[0])
        adjacent = all(i in covered or tokens[i].text in glue for i in gap)
        if adjacent and text is not None and lo_span[1] > 0 and hi_span[0] < len(tokens):
            # a genuine clause break -- a sentence-final period in a
            # dot-folding (ordinal_dot) locale like de/ru -- leaves an EMPTY
            # token-index gap (the tokenizer drops the period from the token
            # stream entirely, same as it drops a comma) that would otherwise
            # read as vacuously adjacent.  Check the character gap between
            # the two matches' own edge tokens for a literal "." the
            # ordinal-dot/decimal-dot tokens never leave stray (see
            # ``_sentence_period_between``) before trusting the token-index
            # adjacency above.
            if _sentence_period_between(tokens, lo_span[1] - 1, hi_span[0], text):
                adjacent = False
        if adjacent:
            # Cap the cluster to the shape _compose can actually fuse: at
            # most one of each role (clock/daypart/weekday/date).  Two
            # adjacent but otherwise UNRELATED date references ("friday next
            # week", no clock/daypart between them) are not a composable
            # pair -- _compose has no fusion rule for two anchor dates and
            # would silently keep only the earlier one, dropping the other.
            # Refusing the merge here keeps both as their own mentions,
            # exactly as they resolve outside a cluster.
            nxt_role = _cluster_role(nxt[0].construction)
            existing = [(m, _cluster_role(m.construction))
                        for m, _r in clusters[-1]]
            existing_roles = {r for _m, r in existing}
            if nxt_role in existing_roles:
                adjacent = False
            elif nxt_role == "weekday":
                # a weekday only fuses onto an existing DATE as a LABEL
                # ("Monday, March 2") when that date is one of the LITERAL
                # constructions _compose accepts as labelable; a weekday next
                # to a non-labelable date ("friday" + "next week") is not a
                # composable pair and must stay two mentions.
                other_date = next((m for m, r in existing if r == "date"),
                                   None)
                if (other_date is not None
                        and other_date.construction
                        not in _WEEKDAY_LABELABLE_DATES):
                    adjacent = False
            elif nxt_role == "date":
                other_weekday = next((m for m, r in existing
                                      if r == "weekday"), None)
                if (other_weekday is not None
                        and nxt[0].construction not in _WEEKDAY_LABELABLE_DATES):
                    adjacent = False
        if adjacent:
            clusters[-1].append(nxt)
        else:
            clusters.append([nxt])
    return clusters


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
    real dates but has no RFC 5545 ``RRULE``); a whole jurisdiction's calendar
    ("every holiday in Portugal") yields a
    :class:`~chronologia.recurrence.JurisdictionHolidays` (same story: real
    dates, no ``RRULE``).
    """
    recurrence: Union[Recurrence, HolidayRecurrence, JurisdictionHolidays]
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
            rec, consumed = _apply_clock_range(rec, consumed, ctx, lang, anchor)
            rec, consumed = _apply_range_bound(rec, consumed, ctx, lang, anchor)
            # a range bound may CLAIM its clause yet name no valid recurrence
            # (a weekday range that shares no day with an already-set BYDAY
            # base, e.g. "every weekday from saturday to sunday"): declining
            # outright is correct here for the same reason it is in the
            # finder loop above -- a rule that matched nothing (or, worse,
            # everything) would be a silent wrong answer, not a decline.
            if rec is None:
                return None
            rec, consumed = _apply_year_scope(rec, consumed, ctx, lang, anchor)
            # a trailing year scope on a rule this engine has no bound field
            # for (JurisdictionHolidays, HolidayRecurrence) cannot be honestly
            # expressed -- see _apply_year_scope -- so it declines the same
            # way the two cases above do.
            if rec is None:
                return None
            rec, consumed = _apply_clock(rec, consumed, ctx, lang, anchor)
            # a BYHOUR list whose items disagree on the minute cannot be
            # honestly folded onto one RRULE's single BYMINUTE -- see
            # _apply_clock -- so it declines the same way the steps above do.
            if rec is None:
                return None
            from chronologia.extract.pipeline import render_remainder
            remainder = render_remainder(text, [t for t in tokens
                                                if t.index not in consumed])
            return RecurrenceResult(rec, remainder)
    return None




def _apply_clock_range(rec, consumed, ctx, lang, anchor):
    """Fold a "from H to H2" / "from Ham to H2pm" clause into a within-day
    clock WINDOW: ``BYHOUR`` (and ``BYMINUTE``) is set to the window's
    **start** only.

    This engine's ``BYHOUR``/``BYMINUTE`` parts are discrete civil-clock
    PINS -- RFC 5545 has no window-END part -- so a clock range grounds
    exactly the way a plain "at H" pin grounds (:func:`_apply_clock`): one
    ``BYHOUR`` value, taken from the range's left/start endpoint.  Without
    this step the clause is silently misread two ways:

    * ``_apply_range_bound``'s date-range fallback grounds the right
      endpoint as a same-day ``UNTIL`` ("from 9am to 5pm" -> UNTIL=today
      17:00), expiring the whole rule the day it is authored;
    * failing that (a bare "5" does not ground as a date), the tokens fall
      through to :func:`_apply_clock`'s generic ``clock_time`` engine match,
      which reads "9 to 5" as the unrelated "N minutes to H" idiom ("quarter
      to five") -- "9 to 5" -> 4:51, nonsense for a range.

    Both endpoints must resolve as PURE clock times: reading ``"at " +
    text`` for the (1- or 2-token) endpoint span must leave no remainder --
    a genuine date range ("from june to august") leaves "at" stranded
    (``extract_timespan("at august")`` resolves August but returns "at" as
    remainder) and is declined here, left for :func:`_apply_range_bound` to
    ground as ``UNTIL`` instead.  Bare numbers ("9", "5") are read literally,
    the same convention :func:`_apply_clock` already uses for "at 9" / "at
    5" -- no am/pm guessing is invented here.
    """
    from dataclasses import replace as _replace
    if isinstance(rec, (HolidayRecurrence, JurisdictionHolidays)) or rec.until is not None:
        return rec, consumed

    tokens = ctx.tokens
    spec = ctx.spec
    n = len(tokens)
    leads = _conn_surfaces(spec, "between", _RANGE_BETWEEN) \
        + _conn_surfaces(spec, "from", _RANGE_FROM)
    mids = _conn_surfaces(spec, "to", _RANGE_TO) \
        + _conn_surfaces(spec, "and", ("and",))

    def _match(i, words):
        k = len(words)
        if not words or i + k > n or any((i + x) in consumed for x in range(k)):
            return None
        return i + k if [tokens[i + x].text for x in range(k)] == words else None

    def _clock_span(start):
        # a clock endpoint is 1 token ("5") or 2 ("9", "am") -- try the
        # longer reading first so a trailing am/pm word is captured.
        for length in (2, 1):
            end = start + length
            if end > n or any(x in consumed for x in range(start, end)):
                continue
            text = " ".join(t.raw for t in tokens[start:end])
            got = extract_timespan("at " + text, lang, anchor=anchor)
            if got is None or got[1] != "":
                continue
            c = got[0].start
            return end, c.hour, c.minute
        return None

    for i in range(n):
        if i in consumed:
            continue
        j = next((m for lead in leads if (m := _match(i, lead)) is not None), None)
        if j is None:
            continue
        left = _clock_span(j)
        if left is None:
            continue
        k, hour, minute = left
        m_end = next((r for mid in mids
                      if (r := _match(k, mid)) is not None), None)
        if m_end is None:
            continue
        right = _clock_span(m_end)
        if right is None:
            continue
        end, _rh, _rm = right
        rec = _replace(rec, byhour=(hour,),
                       byminute=((minute,) if minute else ()))
        return rec, consumed | set(range(i, end))

    # -- H <and> H2 <between> (postposed) -----------------------------------
    # Turkish, Hungarian and Finnish frame a closed range with the "between"
    # word placed AFTER the pair ("9 ile 17 arasında" == "9 and 17 between")
    # instead of before it, mirroring the postposed range construction
    # :func:`~chronologia.extract.timespan._extract_range` reads via
    # ``marker_between_post.voc``.  Without this branch the leading
    # scan above never matches (there is no leading "between"/"from"), so the
    # clause falls through to :func:`_apply_range_bound`'s bare-number decline
    # and then to :func:`_apply_clock`'s list reader, which grounds BYHOUR off
    # whichever clock-shaped match it meets first -- picking the WRONG (right)
    # endpoint and stranding the connector/marker in the remainder.
    # The convention is the same as the leading branch above: BYHOUR pins to
    # the range's left/start endpoint, read in text order.
    between_post = _conn_surfaces(spec, "between_post", ())
    if between_post:
        # A postposed range's LEFT endpoint may write its hour bare with no
        # unit word of its own ("9 és 17 óra között" -- only the right side
        # spells "óra"); its own trailing marker licenses that bare reading
        # the same way :func:`~chronologia.extract.timespan._compose_clock_range`
        # licenses it for the preposed/single-span reading.  Rather than
        # resolve each endpoint in isolation (which would require the SAME
        # borrowed-unit machinery timespan.py already owns), the whole
        # candidate clause is handed to :func:`extract_timespan` as one
        # string and accepted only when it consumes every word (empty
        # remainder) -- exactly the check :func:`_extract_range` itself uses.
        for p in range(n):
            if p in consumed:
                continue
            mk = next((k for mid in mids if (k := _match(p, mid)) is not None), None)
            if mk is None:
                continue
            marker_end = None
            for q in range(mk, n):
                m2 = next((r for post in between_post
                           if (r := _match(q, post)) is not None), None)
                if m2 is not None:
                    marker_end = m2
                    break
            if marker_end is None:
                continue
            # the left endpoint's start: try the shortest window first (the
            # single token immediately before the "and" connector, the
            # common bare-number case) and only widen leftward when that
            # fails to parse cleanly -- never crossing an already-consumed
            # token, which marks where an earlier finder's own frame ends.
            lo_bound = max((c + 1 for c in consumed if c < p), default=0)
            hit = None
            for i in range(p - 1, lo_bound - 1, -1):
                if i in consumed:
                    break
                clause = " ".join(t.raw for t in tokens[i:marker_end])
                got = extract_timespan(clause, lang, anchor=anchor)
                if got is not None and got[1] == "":
                    hit = (i, got[0].start)
                    break
            if hit is None:
                continue
            i, c = hit
            rec = _replace(rec, byhour=(c.hour,),
                           byminute=((c.minute,) if c.minute else ()))
            return rec, consumed | set(range(i, marker_end))
    return rec, consumed


def _apply_clock(rec, consumed, ctx, lang, anchor):
    """Fold a trailing clock ("at 9", "at 9:30", "at noon") -- or a
    comma/"and"-separated LIST of them ("at 9am and 5pm", "at 9am, 12pm and
    5pm") -- onto ``rec`` as a ``BYHOUR``/``BYMINUTE`` pin, extending
    ``consumed`` over the clock(s) (and a leading ``at`` marker, repeated
    before each list item: "a las 9am y a las 5pm").

    A :class:`~chronologia.recurrence.HolidayRecurrence` carries no clock pin,
    so it is left untouched.  Each clock is read by the *same* engine
    ``clock_time`` construction the single-span edge uses (composition, not a
    new grammar); its resolved minute-wide span supplies the hour and minute.

    RFC 5545's ``BYHOUR`` is multi-valued, so a list of full clocks (each with
    its own meridiem) is read item-by-item -- the tokenizer already drops
    commas, so items are separated by nothing, the locale's "and" connector,
    or a repeated leading marker ("a las"), skipped between items the same
    way ``_collect_weekdays`` skips "and" between weekday names.  ``BYMINUTE``
    is a single value shared by the whole rule (there is no per-BYHOUR minute
    in RFC 5545): when every list item names the SAME minute (including all
    on-the-hour), that minute is used; when items disagree ("9:15 and
    17:45"), the rule cannot be honestly expressed as one RRULE, so this
    declines outright (``None``) rather than silently keeping only one
    item's minute -- the same "claim then decline" convention the finders
    and ``_apply_clock_range``/``_apply_range_bound``/``_apply_year_scope``
    already use.

    A rule may ALSO already carry a ``BYHOUR`` pin from
    :func:`_apply_clock_range` (a "between 9 and 5" / postposed clock range,
    whose consumed span never covers a LATER independent "and also at 7"
    clause).  A clock range's ``BYHOUR`` is a deliberately partial reading --
    the *start* of an interval RFC 5545 has no window-end part for -- so
    folding a further trailing clock list onto it here would either be
    misread as one more list item (silently dropping the range's own
    meaning: "9,7" reads as three unrelated pins, not "9-5 plus 7") or
    silently overwritten outright.  Neither is honest, so a trailing clock
    match found while ``rec`` already carries a ``BYHOUR`` declines the
    whole extraction instead -- refusal over a silently wrong rule, the same
    convention the two decline sites above already follow.
    """
    from dataclasses import replace as _replace
    if isinstance(rec, (HolidayRecurrence, JurisdictionHolidays)):
        return rec, consumed
    engine = _timespan_engine(lang)
    tokens = ctx.tokens
    n = len(tokens)
    matches = sorted(
        (m for m in engine.matcher.match(tokens)
         if m.construction in ("clock_time", "military_time")
         and not any(i in consumed for i in range(*m.span))),
        key=lambda m: m.span[0])
    if matches and rec.byhour:
        return None, consumed
    for idx, m in enumerate(matches):
        res = engine.resolver.resolve(m, anchor or datetime.now())
        if res is None:
            continue
        c = res.value.start
        hours = [c.hour]
        minutes = [c.minute]
        lo, hi = m.span
        j = idx + 1
        while j < len(matches):
            nxt = matches[j]
            if nxt.span[0] < hi or not all(
                    tokens[k].text in ctx.and_words
                    or tokens[k].text in ctx.at_words
                    for k in range(hi, nxt.span[0])):
                break
            nres = engine.resolver.resolve(nxt, anchor or datetime.now())
            if nres is None:
                break
            nc = nres.value.start
            hours.append(nc.hour)
            minutes.append(nc.minute)
            hi = nxt.span[1]
            j += 1
        if len(set(minutes)) > 1:
            return None, consumed
        rec = _replace(rec, byhour=tuple(hours),
                       byminute=((minutes[0],) if minutes[0] else ()))
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
        # An "until" marker's payload may itself carry a leading "before"
        # connector ("until before christmas"): extract_timespan treats a
        # bare "before <holiday>" as an OPEN range (anchor -> holiday), so
        # grounding the untouched text would read .start as the anchor and
        # emit a self-defeating UNTIL=anchor.  Strip the leading before-word
        # first so the payload matches the bare-holiday form the before_words
        # marker path itself grounds ("before christmas" -> "christmas"),
        # keeping "until before X" and "until X" equivalent.
        stripped = text
        low = text.lower().split()
        for surf in ctx.before_words:
            words = surf.lower().split()
            k = len(words)
            if k and low[:k] == words:
                stripped = " ".join(text.split()[k:])
                break
        got = extract_timespan(stripped, lang, anchor=anchor)
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
                               (ctx.before_words, _ground_until),
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


def _apply_range_bound(rec, consumed, ctx, lang, anchor):
    """Fold a stranded "from A to B" / "between A and B" range clause onto
    ``rec``, extending ``consumed`` over the words it reads.

    Reuses the *existing* range connectors (``from``/``between``/``to``/
    ``and``) rather than a new grammar -- it is the same lead/mid vocabulary
    :func:`~chronologia.extract.nseries._merge_ranges` and
    :func:`~chronologia.extract.timespan._extract_range` read for a single-
    span "from A to B".  Two readings, tried in this order:

    * **weekday range** -- both endpoints are bare weekday names ("from
      monday to friday", "from friday to monday"): folds into ``BYDAY``,
      inclusive and wrap-around (friday..monday = FR,SA,SU,MO).  This is the
      idiomatic reading of a weekday-bounded recurrence -- "every day from
      monday to friday" means Mon-Fri, not an unbounded daily rule with the
      clause silently dropped.
    * **date range** -- anything else ("weekly from june to august"): the
      clause is a calendar bound.  Only the *right* endpoint sets a field --
      ``UNTIL`` -- grounded exactly the way a plain "until <date>" bound
      grounds it (:func:`_apply_bounds`'s ``_ground_until``: the resolved
      span's ``start``, so "to august" and "until august" land on the same
      UNTIL).  The left/"from" endpoint names no field ``Recurrence`` has (no
      DTSTART) -- same as the still-unimplemented "starting <date>" today --
      so it is consumed as part of the one clause without contributing a
      value, rather than left stranded in the remainder.

    Declines outright -- rather than guessing -- when ``rec`` already carries
    an ``UNTIL`` (an explicit "until"/"for" bound already claimed the tail)
    or is a :class:`~chronologia.recurrence.HolidayRecurrence` (no RRULE
    fields to fold onto).  A pre-existing ``COUNT`` is cleared when the range
    grounds an ``UNTIL`` -- COUNT and UNTIL are mutually exclusive in RFC
    5545, and UNTIL (the explicit bound) wins, mirroring the same policy in
    :func:`_apply_bounds`.

    R94: a sentence may carry MORE than one stranded range clause -- a
    weekday range AND a date range on top of an already-consumed clock range
    ("every weekday from friday to monday from 9 to 5 from june to august").
    A single first-match-and-stop pass claimed only one clause and left the
    other stranded in the remainder (or, worse, mis-happens to read a bogus
    numeric clause as the date).  This function therefore LOOPS: each
    iteration re-scans for the rightmost still-unclaimed clause (so a genuine
    date-range candidate is preferred over an earlier one, per the ordering
    note below) and claims it -- weekday range -> BYDAY intersection, date
    range -> UNTIL -- then repeats until a full scan claims nothing more. A
    bare-number range ("from 1 to 2") is never accepted as a date-range
    grounding here: unlike "to august"/"to monday", digits alone carry no
    calendar semantics, and accepting them let a leftover numeric range (a
    stray clock-shaped clause :func:`_apply_clock_range` did not claim)
    ground a same-day UNTIL and silently swallow a *real* trailing date
    clause that never got a turn.  Such a clause is left unclaimed here, for
    :func:`_apply_clock` to read afterwards (or to remain stranded in the
    remainder).
    """
    from dataclasses import replace as _replace
    if isinstance(rec, (HolidayRecurrence, JurisdictionHolidays)) or rec.until is not None:
        return rec, consumed

    tokens = ctx.tokens
    spec = ctx.spec
    n = len(tokens)
    leads = _conn_surfaces(spec, "between", _RANGE_BETWEEN) \
        + _conn_surfaces(spec, "from", _RANGE_FROM)
    mids = _conn_surfaces(spec, "to", _RANGE_TO) \
        + _conn_surfaces(spec, "and", ("and",))

    def _match(i, words):
        k = len(words)
        if not words or i + k > n or any((i + x) in consumed for x in range(k)):
            return None
        return i + k if [tokens[i + x].text for x in range(k)] == words else None

    # Lead positions are tried RIGHTMOST first.  A sentence may carry two
    # "from A to B" clauses -- a clock range and a date range ("every monday
    # from 9 to 5 from june to august") -- and the leftmost-first reading
    # greedily pairs the first "from" with whatever unconsumed text follows
    # the nearest "to", which swallows the *second* clause's right endpoint
    # into the first clause's payload text and grounds UNTIL off the wrong
    # (earlier, clock-adjacent) clause.  The date-range clause is reliably
    # the last "from ... to ..." in the sentence -- a trailing clock pin
    # ("from 9 to 5") always precedes it -- so trying lead positions from the
    # right lets the date clause ground first and leaves the clock clause
    # untouched for :func:`_apply_clock` to read afterwards.  This scan
    # re-runs (see the ``while`` loop below) after every successful claim, so
    # a sentence with more than one stranded clause has every clause given a
    # rightmost-first turn, not just the first one found.
    while True:
        claimed = False
        for i in reversed(range(n)):
            if i in consumed:
                continue
            j = next((m for lead in leads
                      if (m := _match(i, lead)) is not None), None)
            if j is None:
                continue
            for k in range(j, n):
                if k in consumed:
                    continue
                m = next((r for mid in mids
                          if (r := _match(k, mid)) is not None), None)
                if m is None:
                    continue
                left = [t for x, t in enumerate(tokens[j:k])
                        if (j + x) not in consumed]
                # the right endpoint's span stops at the next unclaimed
                # lead ("from"/"between") if there is one -- otherwise a
                # further stranded clause further right in the sentence
                # ("... from june to august from 1 to 2") gets swallowed
                # into THIS clause's payload text and corrupts the date it
                # grounds (R94).
                right_end = next(
                    (p for p in range(m, n)
                     if p not in consumed
                     and any(_match(p, lead) is not None for lead in leads)),
                    n)
                right = [t for x, t in enumerate(tokens[m:right_end])
                         if (m + x) not in consumed]
                if not left or not right:
                    continue

                if (len(left) == 1 and len(right) == 1
                        and left[0].text in ctx.weekdays
                        and right[0].text in ctx.weekdays):
                    start_wd = ctx.weekdays[left[0].text]
                    end_wd = ctx.weekdays[right[0].text]
                    days = []
                    d = start_wd
                    while True:
                        days.append(d)
                        if d == end_wd:
                            break
                        d = (d + 1) % 7
                    existing = {wd for _, wd in rec.byday}
                    if existing:
                        # A weekday-set base ("every weekday" = MO-FR) already
                        # names which days can ever match -- a from/to weekday
                        # range layered on top must INTERSECT with that base,
                        # not union onto it.  Unioning is how "every weekday
                        # from friday to monday" (wrap: FR,SA,SU,MO) used to
                        # silently grow to all 7 days -- a weekday rule that
                        # can never actually include a weekend day.  An empty
                        # intersection ("every weekday from saturday to
                        # sunday") names a rule that can never fire; decline
                        # rather than fabricate one that matches nothing (or,
                        # via the old union bug, everything).
                        keep = [wd for wd in days if wd in existing]
                        if not keep:
                            return None, consumed | set(range(i, n))
                        rec = _replace(rec, byday=tuple((None, wd) for wd in keep))
                    else:
                        added = tuple((None, wd) for wd in days)
                        rec = _replace(rec, byday=rec.byday + added)
                    consumed = consumed | set(range(i, n))
                    claimed = True
                    break

                # A bare-number range ("from 1 to 2") carries no calendar
                # semantics of its own -- unlike "to august"/"to monday", it
                # is indistinguishable from a stray clock clause.  Accepting
                # it as a date grounds a bogus same-day UNTIL and, being
                # scanned rightmost-first, would pre-empt a REAL date clause
                # further left from ever getting a turn.  Decline it (leave
                # it unclaimed for :func:`_apply_clock` or the remainder) and
                # keep scanning leftward for a genuine date candidate.
                if all(t.is_number for t in left) and all(t.is_number for t in right):
                    continue

                right_text = " ".join(t.raw for t in right)
                got = extract_timespan(right_text, lang, anchor=anchor)
                if got is None:
                    continue

                # R98: a SECOND genuine date-range candidate claiming UNTIL
                # for the same rule ("every day from june to august from
                # september to october") is ambiguous, not a pick-one -- the
                # rightmost-first scan already grounded UNTIL off ONE clause
                # in an earlier pass of this loop, and this earlier clause is
                # equally a real calendar range.  Silently leaving it
                # unclaimed strands it in the remainder next to a rule that
                # looks confidently correct.  There is no principled way to
                # prefer one calendar bound over the other, so decline the
                # whole extraction (mirrors the empty-intersection decline in
                # the weekday-range branch above).
                if rec.until is not None:
                    return None, consumed | set(range(i, n))

                rec = _replace(rec, until=got[0].start, count=None)
                consumed = consumed | set(range(i, n))
                claimed = True
                break
            if claimed:
                break
        if not claimed:
            break
    return rec, consumed


def _apply_year_scope(rec, consumed, ctx, lang, anchor):
    """Fold a trailing whole-YEAR scope ("next year", "this year", "in 2027",
    a bare "2028") onto ``rec`` as ``UNTIL``, extending ``consumed`` over the
    words it reads, instead of stranding it in the remainder.

    The scope is read by the *same* single-span engine :func:`_apply_bounds`
    already reuses for "until <date>" -- offering the whole unconsumed TAIL of
    the token stream to :func:`extract_timespan` and accepting the hit only
    when it consumes the tail in full (empty remainder) AND the resolved span
    is exactly one calendar year (Jan 1 .. next Jan 1) -- so a genuine
    non-year trailing date ("every friday next month") or a non-temporal
    trailing word ("every monday please") is left untouched here.

    A named year is a CONTAINMENT scope, not an "until" marker, so the bound
    set is the span's own ``end`` (the first instant *after* the scoped
    year) -- "next year" (2027) grounds the identical ``UNTIL`` value
    "until 2028" already grounds via its own ``.start`` (see
    :func:`_apply_bounds`'s ``_ground_until``), so the two conventions agree
    on one instant rather than silently disagreeing by a year.

    ``Recurrence`` has no ``DTSTART`` field -- ``occurrences()`` takes the
    start as a caller-supplied argument, never a stored one -- so only the
    scope's UPPER edge can be expressed here; the lower edge is left to
    whatever ``dtstart`` the caller passes to ``occurrences()``, the same
    documented limitation :func:`_apply_range_bound` already carries for an
    unimplemented "starting <date>" bound.  This is stated in the module docs
    rather than silently assumed.

    A pre-existing ``UNTIL``/``COUNT`` (an explicit "until"/"for" bound
    already claimed the tail, or a range clause already grounded one) is left
    untouched -- UNTIL/COUNT are mutually exclusive in RFC 5545 and the
    explicit bound already present wins, same policy as
    :func:`_apply_bounds` and :func:`_apply_range_bound`.

    :class:`~chronologia.recurrence.HolidayRecurrence` and
    :class:`~chronologia.recurrence.JurisdictionHolidays` carry **no** bound
    field at all -- their ``occurrences()`` takes ``until``/``count`` only as
    CALL arguments, nothing on the object itself to set -- so a year scope on
    either of them cannot be attached to the returned value without silently
    dropping it or inventing a field that does not exist.  Rather than either,
    this REFUSES the whole extraction (returns ``(None, consumed)``, exactly
    like the ambiguous-UNTIL and empty-intersection declines in
    :func:`_apply_range_bound`) when a year scope is found trailing one of
    these -- the honest "I can't express this bound" rather than a value that
    quietly ignores half of what was asked.
    """
    from dataclasses import replace as _replace
    tokens = ctx.tokens
    n = len(tokens)
    hi = n
    lo = hi
    while lo - 1 >= 0 and (lo - 1) not in consumed:
        lo -= 1
    if lo >= hi:
        return rec, consumed
    tail = " ".join(t.raw for t in tokens[lo:hi] if t.index not in consumed)
    if not tail.strip():
        return rec, consumed
    got = extract_timespan(tail.strip(), lang, anchor=anchor)
    if got is None or got[1] != "":
        return rec, consumed
    span = got[0]
    start, end = span.start, span.end
    if not (start.month == 1 and start.day == 1
            and end.month == 1 and end.day == 1
            and end.year == start.year + 1):
        return rec, consumed
    if isinstance(rec, (HolidayRecurrence, JurisdictionHolidays)):
        return None, consumed | set(range(lo, hi))
    if rec.until is not None or rec.count is not None:
        return rec, consumed
    rec = _replace(rec, until=end)
    return rec, consumed | set(range(lo, hi))


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
    #: "before" reads the SAME as "until" in a recurrence tail -- "every
    #: monday before christmas" binds UNTIL exactly like "every monday until
    #: christmas" does (mirrors the bare-timespan side, where "before
    #: <holiday>" is also an open range ending at the holiday).  See
    #: :func:`_apply_bounds`.
    before_words: set = frozenset()
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
    jurisdictions: dict = None
    #: the "to" of the "<ordinal> to last" / "next to last" idiom ("the
    #: second-to-last friday of every month").
    to_words: set = frozenset()
    #: "penultimate" -- a single-word synonym for "second-to-last".
    penult_words: set = frozenset()
    #: a SINGULAR trailing day-word ("günü" -- tr's "on <weekday>-day", one
    #: specific date) that, sitting right after a weekday already collected
    #: inside an explicitly-marked recurrence frame ("her cuma günü" --
    #: "every friday"), is pure filler and must be swallowed rather than
    #: stranded.  See ``_collect_weekdays``.
    day_word: set = frozenset()
    #: the PLURAL of ``day_word`` ("günleri") -- unlike the singular, this
    #: surface is itself the ONLY marker of a bare postposed recurring
    #: weekday ("cuma günleri" -- "on Fridays"), with no leading "her"/"on".
    #: See ``_recur_weekday_dayword_bare``.
    recur_day_word: set = frozenset()
    #: the leading word of the "next to last" idiom ("next" -- distinct from
    #: the REL_MARKER "next" which shifts a whole scope by +1).
    ntolast_next_words: set = frozenset()
    holiday_words: set = frozenset()
    holiday_qualifiers: set = frozenset()
    holiday_all_words: set = frozenset()
    in_words: set = frozenset()
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
        before_words=set(C.get("before", ())),
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
        jurisdictions=dict(spec.jurisdictions),
        holiday_words=set(C.get("holiday_word", ())),
        holiday_qualifiers=set(C.get("holiday_qualifier", ())),
        holiday_all_words=set(C.get("recur_holiday_all", ())),
        in_words=set(C.get("in", ())),
        to_words=set(w for words in _conn_surfaces(spec, "to", _RANGE_TO)
                     for w in words if len(words) == 1),
        penult_words=set(C.get("penult", ())),
        ntolast_next_words=set(C.get("ntolast_next", ())),
        day_word=set(C.get("weekday_word", ())),
        recur_day_word=set(C.get("recur_weekday_word", ())),
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


def _ntolast_ordn(ctx, t, li):
    """Whether the "last" token at ``t[li]`` is really the tail of an
    "<ordinal> to last" / "next to last" idiom -- "the second-to-last friday
    of every month" (-2), "the third-to-last ..." (-3), "the next-to-last
    ..." (-2, same idiom as "second-to-last").

    Returns ``(ordn, phrase_start)`` -- the negative ordinal and the index the
    whole ordinal phrase starts at (so the caller's consumed range covers the
    leading "second-to"/"next-to" instead of stranding it) -- or ``None`` if
    ``t[li]`` is not preceded by this idiom (a bare "last").

    Bounded at -4: "fifth-to-last" and beyond refuse rather than invent a
    reading past what the idiom is ever actually used for.
    """
    if li - 1 < 0 or t[li - 1].text not in ctx.to_words:
        return None
    k = li - 2
    if k < 0:
        return None
    if t[k].is_number:
        v = int(t[k].value)
        return (-v, k) if 2 <= v <= 4 else None
    if t[k].text in ctx.ntolast_next_words:
        return -2, k
    return None


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
        ord_start = li
        # a leading numeric count directly before a BARE "last" ("every 3rd
        # last friday of the month"), captured for the MONTH-scope branches
        # below to reinterpret as ``BYDAY=-N`` (mirroring the "<ordinal>-to-
        # last" idiom); the YEAR-scope branch ignores this and keeps reading
        # the same number as an INTERVAL multiplier instead.
        numeric_last_n = None
        if t[li].is_number:
            ordn = int(t[li].value)
        elif (t[li].text in ctx.rel_markers
              and ctx.rel_markers[t[li].text] == -1):
            # bare "last" (-1), unless it's really the tail of an
            # "<ordinal> to last" / "next to last" idiom -- checked first so
            # that idiom is never mis-read as the bare last-of-month.
            if li - 1 >= 0 and t[li - 1].text in ctx.to_words:
                # this token IS shaped like the idiom's tail ("<X> to last");
                # an out-of-range/unrecognised <X> ("fifth-to-last") must
                # decline the whole reading rather than silently fall back to
                # bare "last" and strand the qualifier -- exactly the defect
                # this idiom support exists to fix.
                found = _ntolast_ordn(ctx, t, li)
                if found is None:
                    # the shape IS the "<X> to last" idiom, just with an
                    # unsupported/out-of-range <X> ("fifth-to-last") -- CLAIM
                    # the reading and decline it (a ``None`` rule), exactly
                    # the convention an impossible ordinal ("every 31st of
                    # april") already uses, so a weaker catch-all finder never
                    # gets a chance to re-read "each month" alone and strand
                    # the whole qualified phrase as remainder behind a bare
                    # MONTHLY rule.  A bare "last" with no leading "to" is NOT
                    # this idiom and keeps scanning normally (the ``else``
                    # branch below, and the plain ``continue`` mismatches
                    # elsewhere in this loop).
                    return None, frozenset()
                ordn, ord_start = found
            else:
                # bare "last" -- may still carry a leading numeric count
                # ("every 3rd last friday of the month"), read below ONLY
                # for the MONTH-scope tail: the YEAR-scope tail reads that
                # same leading number as an INTERVAL multiplier instead
                # ("every 2nd last friday of the year" ->
                # FREQ=YEARLY;INTERVAL=2;BYDAY=-1FR, ordn staying -1).
                # ``ord_start``/``ordn`` stay untouched here so year-scope
                # interval detection (the ``t[start - 1].is_number`` check
                # below) still sees the number; ``numeric_last_n`` records it
                # for the month-scope branches to reinterpret.
                ordn = -1
                if li - 1 >= 0 and t[li - 1].is_number:
                    numeric_last_n = int(t[li - 1].value)
        elif t[li].text in ctx.penult_words:
            # "penultimate <weekday> of every month" -- a fixed synonym for
            # "second-to-last" (-2).
            ordn = -2
        else:
            continue
        r = w + 1
        if not (r < n and t[r].text in ctx.of_words):
            continue
        r += 1
        while r < n and (t[r].text in ctx.every or t[r].text in ctx.articles
                         or (t[r].text in ctx.rel_markers
                             and ctx.rel_markers[t[r].text] == 0)):
            # zero-offset deixis ("this") reads identically to the bare
            # article before the unit noun -- "of this year" == "of the
            # year"; the span path already treats them interchangeably.
            r += 1
        start = ord_start
        while start > 0 and (t[start - 1].text in ctx.articles
                             or t[start - 1].text in ctx.every):
            start -= 1
        # a leading interval prefix ("every other"/"every 2nd") directly
        # before the walked-back head is captured here so the year-scope
        # branch below can fold it into the built rule's INTERVAL;
        # the month-scope and bare-elliptical readings intentionally drop
        # it (their monthly cadence already matches the base "last <wd>"
        # reading), so this value is used only by the year branch.
        year_interval = 1
        if start > 0 and t[start - 1].text in ctx.other:
            year_interval = 2
            start -= 1
        elif start > 0 and t[start - 1].is_number:
            year_interval = int(t[start - 1].value)
            start -= 1
        if year_interval != 1:
            while start > 0 and (t[start - 1].text in ctx.articles
                                 or t[start - 1].text in ctx.every):
                start -= 1
        if (r < n and t[r].text in ctx.rel_markers
                and ctx.rel_markers[t[r].text] != 0
                and r + 1 < n and t[r + 1].text in ctx.units
                and ctx.units[t[r + 1].text] in ("year", "month")):
            # non-zero deixis ("next"/"last") before the year/month noun
            # bounds the phrase to a single period ("of next year"), not an
            # unbounded recurrence -- claim the frame and refuse so a weaker
            # finder never re-reads just the ordinal-weekday head into a
            # rule at the wrong frequency.
            return None, frozenset(range(start, r + 2))
        if (r < n and t[r].text in ctx.rel_markers
                and ctx.rel_markers[t[r].text] != 0
                and r + 1 < n and t[r + 1].text in ctx.units
                and ctx.units[t[r + 1].text] == "week"):
            # "of next/last week" -- same bounded-single-period shape as the
            # year/month case above, refused the same way.
            return None, frozenset(range(start, r + 2))
        if r < n and t[r].text in ctx.units and ctx.units[t[r].text] == "week":
            # unlike month/year, "week" has no zero-offset/bare fold at all:
            # a week has exactly one of any given weekday, so "of the week"/
            # "of this week" is degenerate rather than a well-formed unbounded
            # rule -- refuse here too instead of falling through to the
            # month/year unit branches below (which "week" never matches) and
            # leaving the phrase to a weaker finder.
            return None, frozenset(range(start, r + 1))
        if r < n and (t[r].text in ctx.months
                      or (t[r].text in ctx.units and ctx.units[t[r].text] == "month")):
            # month-scope tail: a leading numeric count reinterprets as
            # ``BYDAY=-N`` here (see ``numeric_last_n`` above) rather than
            # the bare "last" ellipsis (-1) -- N=2 keeps the ellipsis (it is
            # indistinguishable from "second/last <weekday>"), N=3..4 count
            # backward unambiguously, N>=5 refuses (mirrors the "<ordinal>-
            # to-last" idiom's own -4 cap) rather than falling back silently.
            month_ordn = ordn
            if numeric_last_n is not None:
                if numeric_last_n == 2:
                    month_ordn = -1
                elif 3 <= numeric_last_n <= 4:
                    month_ordn = -numeric_last_n
                else:
                    return None, frozenset()
            if t[r].text in ctx.months:
                if business:
                    rec = _business_day_of_month(month_ordn, month=ctx.months[t[r].text])
                else:
                    rec = _nth_weekday_of_month(month_ordn, wd,
                                                month=ctx.months[t[r].text])
                return rec, set(range(start, r + 1))
            if business:
                return _business_day_of_month(month_ordn), set(range(start, r + 1))
            return _nth_weekday_of_month(month_ordn, wd), set(range(start, r + 1))
        if r < n and t[r].text in ctx.units and ctx.units[t[r].text] == "year":
            # "every last monday of the year": the yearly sibling of
            # the "... of [every] month" tail above. Before this branch, "of
            # the year" matched neither the ``ctx.months`` check nor the
            # units-is-"month" one, so the loop's tail check fell through
            # (``continue`` was never reached either -- there was simply no
            # matching branch) and this finder returned ``None`` for the
            # whole phrase; a weaker downstream finder then read only "last
            # monday" as a bare ``MONTHLY;BYDAY=-1MO`` rule and stranded "of
            # the year" as unmatched remainder -- silently downgrading a
            # yearly rule to a monthly one. RFC 5545 gives ``BYDAY`` with a
            # signed ordinal and no ``BYMONTH`` its own well-defined meaning
            # under ``FREQ=YEARLY``: the nth (or, negative, last) matching
            # weekday of the whole year -- exactly the reading "of the year"
            # asks for, so this resolves rather than refuses.
            if business:
                return (_business_day_of_year(ordn, year_interval),
                        set(range(start, r + 1)))
            return (_nth_weekday_of_year(ordn, wd, year_interval),
                    set(range(start, r + 1)))
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


def _nth_weekday_of_year(ordn, wd, interval=1):
    """The ``ordn``-th ``wd`` of the whole calendar year.

    Sibling of :func:`_nth_weekday_of_month` but with no ``bymonth`` at
    all -- RFC 5545 gives a signed ``BYDAY`` ordinal under bare
    ``FREQ=YEARLY`` exactly this meaning ("last monday of the year" ->
    ``FREQ=YEARLY;BYDAY=-1MO``), never ``FREQ=MONTHLY`` (which would repeat
    every month rather than once a year). ``interval`` carries a leading
    "every other"/"every Nth" multiplier: unlike the month-scope
    sibling, an every-N-years cadence is a distinct, expressible frequency
    (``FREQ=YEARLY;INTERVAL=N``), not a degenerate repeat of the base
    reading, so it is folded in rather than dropped.
    """
    kw = {"interval": interval} if interval != 1 else {}
    return _build_every("yearly", byday=((ordn, wd),), **kw)


def _business_day_of_year(ordn, interval=1):
    """The ``ordn``-th business day of the whole calendar year.

    Sibling of :func:`_business_day_of_month` (``month=None``) but yearly
    rather than monthly, for "the last weekday of the year" -- the same
    ``BYSETPOS`` idiom, scoped to ``FREQ=YEARLY`` with no ``BYMONTH``.
    ``interval`` folds a leading "every other"/"every Nth" multiplier, same
    as :func:`_nth_weekday_of_year`.
    """
    byday = tuple((None, k) for k in range(5))  # MO..FR
    kw = {"interval": interval} if interval != 1 else {}
    return _build_every("yearly", byday=byday, bysetpos=(ordn,), **kw)


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
    # a trailing day-word ("günü"/"günleri", tr's "on <weekday>-day[s]") is
    # pure filler once the weekday itself has been read -- it is what marks
    # the phrase as a weekday reference at all, not an independent token --
    # so it is swallowed into the match rather than left to strand in the
    # remainder.  Both the singular and plural surfaces are skipped here
    # (the plural is what LICENSES the bare postposed reading in
    # ``_recur_weekday_dayword_bare``; once a leading marker like "her"/"on"
    # has already licensed the frame, either surface is just filler).
    if end < n and (t[end].text in ctx.day_word or t[end].text in ctx.recur_day_word):
        end += 1
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
        # A bare WEEKLY adverb directly leading into the placement ("weekly
        # on mondays") is redundant with the named days, exactly like the
        # "<N> times a week" rate above -- swallow it too instead of
        # stranding it in the remainder.  Gated to unit interval 1: "every 2
        # weeks on monday" is a DIFFERENT finder's own reading and never
        # reaches here as a bare freq word.
        if i > 0 and t[i - 1].text in ctx.freq and ctx.freq[t[i - 1].text] == ("WEEKLY", 1):
            consumed.add(i - 1)
        return _build_every("weekly", byday=byday), consumed
    return None


def _preposed_monthday(ctx, t, i):
    """A preposed day-of-month sitting just before ``every`` at index ``i`` --
    "the <N> of every 2 months", "the 15th of every quarter", "the last [day]
    of every quarter".  Returns ``(day_val, start)`` where ``day_val`` is 1..31
    or -1 ("last") and ``start`` is the first consumed token, or ``(None, i)``
    when no preposed ordinal is present.  Mirrors the backward scan the
    INTERVAL=1 "N of every month" finder uses, for the interval/quarter frames
    that finder does not reach."""
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
        day_val = -1
    if day_val is None:
        return None, i
    start = k
    while start - 1 >= 0 and (
            t[start - 1].text in ctx.articles
            or (t[start - 1].text in ctx.units
                and ctx.units[t[start - 1].text] == "day")):
        start -= 1
    return day_val, start


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

        # -- ellipsis: "every <N> last <weekday>" (bare, no scope tail) ------
        # a leading interval count directly before the bare "last <weekday>"
        # ellipsis reads elliptically as the very same monthly last-weekday
        # rule the explicit "of the month" tail gets (the interval is
        # dropped there too). Without this branch the count instead fell
        # through to the day-of-month ellipsis below ("every 2nd" ->
        # BYMONTHDAY=2), stranding "last friday" and silently misreading the
        # whole phrase as a day-of-month rule.
        #
        # N=2 is genuinely ambiguous with the "second/last Friday" ellipsis
        # (documented convention: reads as -1, the bare last weekday) and
        # MUST NOT change. For N>=3 that ellipsis is impossible -- there is
        # no "third/last Friday" reading -- so N counts backward from the
        # month's end exactly like the word-form idiom's "<ordinal>-to-last"
        # ("third-to-last friday" -> -3): numeric N maps to BYDAY=-N. This
        # mirrors that idiom's own cap -- bounded at -4, "fifth-to-last" and
        # beyond refuse (:func:`_ntolast_ordn`) -- so N>=5 here refuses too
        # rather than inventing a reading the word forms do not support.
        if (num_val is not None and j + 1 < n
                and t[j].text in ctx.rel_markers
                and ctx.rel_markers[t[j].text] == -1
                and _weekday_here(ctx, t[j + 1], True) is not None):
            if num_val == 2:
                ordn = -1
            elif 3 <= num_val <= 4:
                ordn = -num_val
            else:
                return None, frozenset()
            wd = _weekday_here(ctx, t[j + 1], True)
            return (_nth_weekday_of_month(ordn, wd),
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
            kw = {"interval": interval * 3}
            start, end = i, j + 1
            # a placement qualifier pins the day-of-month, like the "every N
            # months" case: postposed "every quarter on [the] <Nth>" or preposed
            # "the <Nth> of every quarter".
            if j + 1 < n and t[j + 1].text in ctx.on_words:
                k = j + 2
                while k < n and t[k].text in ctx.articles:
                    k += 1
                if k < n and t[k].is_number and 1 <= int(t[k].value) <= 31:
                    kw["bymonthday"] = int(t[k].value)
                    end = _of_month_tail(ctx, k + 1)
            if "bymonthday" not in kw:
                pre_day, pre_start = _preposed_monthday(ctx, t, i)
                if pre_day is not None:
                    kw["bymonthday"], start = pre_day, pre_start
            return _build_every("monthly", **kw), set(range(start, end))
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
                        got = _weekly_byday_qualifier(ctx, nxt)
                        if got is not None:
                            byday, wend = got
                            return (_build_every("weekly", byday=byday, **iv),
                                    set(range(i, wend)))
                    elif freq == "MONTHLY":
                        got = _monthly_bymonthday_qualifier(ctx, nxt)
                        if got is not None:
                            day, mend = got
                            return (_build_every(
                                        "monthly", bymonthday=day, **iv),
                                    set(range(i, mend)))
                # a preposed day-of-month ("the 15th of every 2 months") is the
                # placement qualifier for an interval-months rule that no
                # postposed "on the Nth" carried.  Guarded to interval != 1 so
                # it never overlaps the INTERVAL=1 "N of every month" finder.
                if freq == "MONTHLY" and interval != 1:
                    pre_day, pre_start = _preposed_monthday(ctx, t, i)
                    if pre_day is not None:
                        return (_build_every("monthly", bymonthday=pre_day, **iv),
                                set(range(pre_start, j + 1)))
                return _build_every(freq, **iv), set(range(i, j + 1))
    return None


def _weekly_byday_qualifier(ctx, idx):
    """``on <weekday(s)>`` starting right at token *idx* -> ``(byday, end)``
    or ``None``.  Shared by the ``every <unit> on ...`` interval reading and
    the bare-adverb ("weekly"/"woechentlich"/...) qualifier fold below."""
    t = ctx.tokens
    n = len(t)
    if not (idx < n and t[idx].text in ctx.on_words):
        return None
    got = _collect_weekdays(ctx, idx + 1, True)
    if got is None:
        return None
    days, end = got
    return tuple((None, wd) for wd in days), end


def _weekly_byday_qualifier_loose(ctx, idx):
    """Like :func:`_weekly_byday_qualifier`, plus two markers that the
    ``every``-gated reading never needs because ``every`` already supplies a
    determiner: a bare leading article ("semanalmente **los** lunes") or no
    marker at all (German's fused habitual plural, "woechentlich montags").
    Only the bare-adverb frequency path reads these looser forms -- the
    dedicated ``on <weekday>`` finder (_recur_on_weekdays) already owns the
    unmarked English surface ("on mondays") on its own terms.
    """
    got = _weekly_byday_qualifier(ctx, idx)
    if got is not None:
        return got
    t = ctx.tokens
    n = len(t)
    k = idx
    while k < n and t[k].text in ctx.articles:
        k += 1
    got = _collect_weekdays(ctx, k, True)
    if got is None:
        return None
    days, end = got
    return tuple((None, wd) for wd in days), end


def _monthly_bymonthday_qualifier(ctx, idx):
    """``on [the] <Nth>`` starting right at token *idx* -> ``(day, end)`` or
    ``None``.  Shared by the ``every <unit> on ...`` interval reading and the
    bare-adverb ("monthly"/"monatlich"/...) qualifier fold below."""
    t = ctx.tokens
    n = len(t)
    if not (idx < n and t[idx].text in ctx.on_words):
        return None
    k = idx + 1
    while k < n and t[k].text in ctx.articles:
        k += 1
    if k < n and t[k].is_number and 1 <= int(t[k].value) <= 31:
        return int(t[k].value), _of_month_tail(ctx, k + 1)
    return None


def _month_day_from_date_match(engine, m):
    """Read ``(month, day)`` off a ``calendar_date`` match's MONTH/DAY slots,
    defaulting the day to 1 when the match names a month only (a bare "in
    june" carries no day). Returns ``None`` when the match names no month the
    locale's calendar recognises."""
    month_tok = m.slots.get("MONTH")
    if month_tok is None or month_tok.text not in engine.spec.months:
        return None
    month = engine.spec.months[month_tok.text]
    day_tok = m.slots.get("DAY")
    day = int(day_tok.value) if day_tok else 1
    return month, day


def _yearly_bymonth_qualifier(ctx, engine, date_matches, idx):
    """The first ``calendar_date`` match at or after token *idx* reachable
    across a short ``in``-word/article gap ("annually **in** june") ->
    ``(month, day, end)`` or ``None``.  Reads the very same MONTH/DAY slots
    the ``every year <date>`` finder (_recur_date_anchored) reads off the
    single-span engine's own match, just gated on the adverb path's shorter,
    marker-only gap instead of that finder's full every-skeleton gap."""
    t = ctx.tokens
    for m in date_matches:
        if m.span[0] < idx:
            continue
        gap = t[idx:m.span[0]]
        if len(gap) > 2 or not all(
                g.text in ctx.in_words or g.text in ctx.articles
                for g in gap):
            continue
        md = _month_day_from_date_match(engine, m)
        if md is None:
            continue
        return md[0], md[1], m.span[1]
    return None


def _yearly_recur_qualifiers(ctx, engine, date_matches, idx):
    """Scan a ``YEARLY`` adverb's tail for a month qualifier ("in <month>")
    and a day qualifier ("on [the] <Nth>") in either order, folding both
    when the month is present.

    A day qualifier with no month ("annually on the 1st") returns ``None``
    and stays stranded -- which month it names is unspecified, and
    inventing one would be silently wrong. A month with no explicit day
    defaults the day to 1 (the uniform yearly-in-month encoding); an
    explicit day always overrides that default.
    """
    day = None
    month = None
    day_default = None
    pos = idx
    end = idx
    for _ in range(2):
        if month is None:
            got = _yearly_bymonth_qualifier(ctx, engine, date_matches, pos)
            if got is not None:
                month, day_default, pos = got
                end = pos
                continue
        if day is None:
            got = _monthly_bymonthday_qualifier(ctx, pos)
            if got is not None:
                day, pos = got
                end = pos
                continue
        break
    if month is None:
        return None
    return month, (day if day is not None else day_default), end


def _skip_clock_at(ctx, lang, idx):
    """The end index just past a clock ("at 9"/"at 9:30") construction
    anchored EXACTLY at token *idx*, or ``None`` when none sits there.

    Used only to look PAST an out-of-order clock pin for a further
    qualifier the adjacent scan missed ("weekly **at 9** on monday" --
    the WEEKLY/MONTHLY/YEARLY qualifier scans normally look for their
    qualifier right after the freq word and give up if a clock sits there
    instead). The clock's own tokens are deliberately left OUT of the
    returned span -- this helper never reads the clock's value, so
    :func:`_apply_clock` still resolves and folds the hour afterwards from
    its own unconsumed-token scan.
    """
    t = ctx.tokens
    if not (idx < len(t) and t[idx].text in ctx.at_words):
        return None
    engine = _timespan_engine(lang)
    for m in engine.matcher.match(t):
        if m.construction not in ("clock_time", "military_time"):
            continue
        lo = m.span[0]
        # the clock construction itself may start past a MULTI-token "at"
        # marker its own grammar does not swallow (Spanish "a las 9" tags
        # the clock match from "las", not "a") -- exactly the same gap
        # :func:`_apply_clock` bridges backwards when it extends its own
        # consumed span over a leading "at" marker.
        if lo >= idx and all(t[k].text in ctx.at_words for k in range(idx, lo)):
            return m.span[1]
    return None


def _recur_freq_word(ctx):
    """A lone ``daily`` / ``weekly`` / ``monthly`` / ``yearly`` / ``quarterly``
    / ``biweekly`` / ``fortnightly`` word, or ``[on] weekdays`` / ``[on]
    weekends``.

    The bare adverb carries no determiner of its own, but a trailing
    day/month qualifier reads exactly like the one an explicit "every"
    reading takes ("monthly **on the 15th**" folds BYMONTHDAY=15 the same
    way "every month on the 15th" does; "annually **in june**" folds
    BYMONTH=6 the same way "every year in june" does) -- sharing
    :func:`_weekly_byday_qualifier`, :func:`_monthly_bymonthday_qualifier`
    and :func:`_yearly_bymonth_qualifier` with the ``every``-gated readings
    keeps both paths reading the same qualifier grammar instead of one
    silently dropping it.

    The qualifier scan is order-INSENSITIVE with a leading clock pin:
    "weekly **at 9** on monday" reads the same BYDAY the postposed
    order ("weekly on monday at 9am") already does, and the MONTHLY/YEARLY
    siblings take the same treatment via :func:`_skip_clock_at` since they
    share the same adjacent-only qualifier scan. DAILY has no further
    qualifier of its own, so "daily at 9" was never affected.
    """
    t = ctx.tokens
    n = len(t)
    for i, tok in enumerate(t):
        if tok.text in ctx.freq:
            freq, interval = ctx.freq[tok.text]
            kw = {"interval": interval} if interval != 1 else {}
            end = i + 1
            nxt = i + 1
            if freq == "WEEKLY":
                got = _weekly_byday_qualifier_loose(ctx, nxt)
                if got is not None:
                    kw["byday"], end = got
                else:
                    skip = _skip_clock_at(ctx, ctx.lang, nxt)
                    if skip is not None:
                        got = _weekly_byday_qualifier_loose(ctx, skip)
                        if got is not None:
                            kw["byday"], byday_end = got
                            return (_build_every(freq, **kw),
                                    {i} | set(range(skip, byday_end)))
            elif freq == "MONTHLY":
                got = _monthly_bymonthday_qualifier(ctx, nxt)
                if got is not None:
                    kw["bymonthday"], end = got
                else:
                    skip = _skip_clock_at(ctx, ctx.lang, nxt)
                    if skip is not None:
                        got = _monthly_bymonthday_qualifier(ctx, skip)
                        if got is not None:
                            kw["bymonthday"], day_end = got
                            return (_build_every(freq, **kw),
                                    {i} | set(range(skip, day_end)))
            elif freq == "YEARLY":
                engine = _timespan_engine(ctx.lang)
                date_matches = [m for m in engine.matcher.match(t)
                                 if m.construction == "calendar_date"]
                got = _yearly_recur_qualifiers(ctx, engine, date_matches, nxt)
                if got is not None:
                    kw["bymonth"], kw["bymonthday"], end = got
                else:
                    skip = _skip_clock_at(ctx, ctx.lang, nxt)
                    if skip is not None:
                        got = _yearly_recur_qualifiers(ctx, engine,
                                                        date_matches, skip)
                        if got is not None:
                            kw["bymonth"], kw["bymonthday"], y_end = got
                            return (_build_every(freq, **kw),
                                    {i} | set(range(skip, y_end)))
            return _build_every(freq, **kw), set(range(i, end))
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


def _recur_weekday_dayword_bare(ctx):
    """``<weekday[, weekday ...]> <PLURAL day-word>`` -> WEEKLY;BYDAY=<days>.

    Turkish marks a habitual/recurring weekday with a trailing PLURAL
    day-word ("cuma günleri" -- "on Fridays") instead of a leading
    quantifier or preposition: the weekday itself stays in its ordinary bare
    singular form, and it is the plural "günleri" ("days", of "günü") right
    after it that marks the reading as recurring rather than a single
    upcoming date.  The SINGULAR day-word carries no such licence -- "cuma
    günü" ("on Friday") names one specific date (read, if at all, by
    extract_timespan's grammar engine, see PR #671) and must stay unread
    here, exactly as a bare "cuma" alone does.

    ``_collect_weekdays`` already swallows a trailing day-word of EITHER
    number into its match span (filler, once a frame is already licensed);
    this finder additionally requires that the swallowed word be the
    PLURAL, since here it is the only thing licensing the frame at all.

    Mirrors ``_recur_habitual_weekday``'s preposition-marked habitual
    reading, just postposed and word- rather than preposition-triggered.
    """
    if not ctx.recur_day_word:
        return None
    t = ctx.tokens
    n = len(t)
    for i in range(n):
        got = _collect_weekdays(ctx, i, False)
        if got is None:
            continue
        days, end = got
        # the last weekday's own surface is never a day-word (disjoint
        # vocabularies), so this membership check alone tells apart "a
        # plural day-word was swallowed" from "nothing trailed the weekday
        # at all" / "a singular day-word trailed it" -- no separate
        # bookkeeping of what ``_collect_weekdays`` swallowed is needed.
        if end == 0 or t[end - 1].text not in ctx.recur_day_word:
            continue
        byday = tuple((None, wd) for wd in days)
        return _build_every("weekly", byday=byday), set(range(i, end))
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

    The holiday word may also follow an explicit ``year`` unit and/or an
    ``on``/``en``-style filler word -- "every YEAR ON christmas", "cada AÑO EN
    navidad" -- the same skeleton :func:`_recur_date_anchored` tolerates in
    front of a numeric calendar date.  Without this, that skeleton strands the
    holiday word as unmatched remainder and the bare ``YEARLY`` rule left
    behind fires on the anchor date instead of the holiday -- silently wrong.
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
        # tolerate an explicit interval count before the year unit -- "every
        # 2 YEARS on christmas" -- the same way "every 2 weeks" reads INTERVAL=2
        # for a plain period.  Only consumed as an interval when a year unit
        # immediately follows; otherwise this is some unrelated number and the
        # holiday lookup below (which will fail on a bare digit) declines as
        # before.
        interval = None
        if (j < n and t[j].is_number and j + 1 < n
                and t[j + 1].text in ctx.units
                and ctx.units[t[j + 1].text] == "year"):
            interval = int(t[j].value)
            j += 1
        # "other" is a word-form interval count, same INTERVAL=2 the bare
        # "every other year" reading already gives -- accepted through the
        # SAME ``ctx.other`` vocabulary that reading uses (marker_recur_other,
        # "every other week"), not a hardcoded English word, so any locale
        # that ships that voc file gets this for free.
        elif (j < n and t[j].text in ctx.other and j + 1 < n
              and t[j + 1].text in ctx.units
              and ctx.units[t[j + 1].text] == "year"):
            interval = 2
            j += 1
        if j < n and t[j].text in ctx.units and ctx.units[t[j].text] == "year":
            j += 1
            # tolerate a short filler run before the holiday word -- "on"/"en"
            # style prepositions land in different connector buckets per
            # locale ("on" is English "on", but Spanish routes "en" under
            # "in"), so rather than enumerate every locale's preposition set
            # here, accept the same short non-content run the date-anchored
            # finder tolerates in front of a date: articles, or any other
            # token that is not itself a number/weekday/unit/every-marker
            # (which would belong to a different, unrelated frame).
            steps = 0
            while j < n and steps < 2 and (
                    t[j].text in ctx.articles
                    or (not t[j].is_number
                        and _weekday_here(ctx, t[j], True) is None
                        and t[j].text not in ctx.units
                        and t[j].text not in ctx.every
                        and t[j].text not in ctx.holidays)):
                j += 1
                steps += 1
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
        kw = {"interval": interval} if interval is not None else {}
        if isinstance(kind, FixedRule):
            return (_build_every("yearly", bymonth=kind.month,
                                 bymonthday=kind.day, **kw), consumed)
        if isinstance(kind, NthWeekdayRule) and kind.post_offset == 0:
            return (_build_every("yearly", bymonth=kind.month,
                                 byday=((kind.n, kind.weekday),), **kw), consumed)
        # movable feast: no RFC 5545 rule can express it -- HolidayRecurrence
        # carries no interval field, so "every 2 years on easter" cannot be
        # built at all.  Decline outright (consumed, no rule) rather than let
        # the greedy INTERVAL-only catch-all fall through and silently fire on
        # the anchor date instead of the (uncomputable) holiday.
        if interval is not None:
            return (None, consumed)
        return HolidayRecurrence(key), consumed
    return None


def _recur_jurisdiction_holidays(ctx):
    """``every holiday in <jurisdiction>`` -> the jurisdiction's whole holiday
    calendar, a :class:`~chronologia.recurrence.JurisdictionHolidays`.

    Distinct from :func:`_recur_holiday`: that finder reads a *named* feast
    ("every christmas") through ``ctx.holidays``; this one reads the generic
    noun "holiday"/"holidays" (``ctx.holiday_words``) followed by an "in
    <country>" phrase, and has no single well-known key to look up -- the
    jurisdiction's whole calendar is queried per year instead.

    Skeleton: ``every|all [public] holiday(s) in <jurisdiction>``. An optional
    qualifier word (``ctx.holiday_qualifiers``, e.g. "public") may sit right
    before the holiday noun; it does not change what is matched (the default
    category is already "public"), it is only tolerated so the phrase is not
    stranded. The jurisdiction name must resolve through ``ctx.jurisdictions``
    -- an unmapped country name (no surface anywhere) means this finder simply
    does not match, never a guess.
    """
    if not ctx.jurisdictions or not ctx.holiday_words:
        return None
    t = ctx.tokens
    n = len(t)
    quantifiers = ctx.every | ctx.holiday_all_words
    for i in range(n):
        if t[i].text not in quantifiers:
            continue
        j = i + 1
        while j < n and t[j].text in ctx.articles:
            j += 1
        if j < n and t[j].text in ctx.holiday_qualifiers:
            j += 1
        if not (j < n and t[j].text in ctx.holiday_words):
            continue
        j += 1
        # a short filler run before the jurisdiction name -- "in"/pt "em" or
        # "de" ("cada feriado DE Portugal") plus an optional article ("in the
        # Portugal" never occurs, but "em Portugal" carries no article while
        # some locales might insert one).
        steps = 0
        while j < n and steps < 2 and (
                t[j].text in ctx.in_words or t[j].text in ctx.of_words
                or t[j].text in ctx.articles):
            j += 1
            steps += 1
        if j >= n:
            continue
        code = ctx.jurisdictions.get(t[j].text)
        if code is None:
            continue
        end = j + 1
        # "every holiday in Portugal AND Spain": a connector immediately
        # followed by ANOTHER known jurisdiction surface names more than one
        # jurisdiction -- this class models exactly one (``jurisdiction`` is a
        # single code, not a list).  Silently keeping only the first and
        # leaving "and Spain" in the remainder used to answer a *different*,
        # narrower question than the one asked (Spain's holidays silently
        # dropped) rather than the one actually named.  There is no principled
        # way to pick a winner and no multi-jurisdiction class to build one
        # into (that is a feature for the repo owner, not a bug fix), so this
        # refuses outright -- same policy as the empty-intersection and
        # ambiguous-UNTIL declines in :func:`_apply_range_bound`.  An unknown
        # trailing word after the connector ("... Portugal and next year")
        # does not trigger this -- only a RECOGNISED second jurisdiction does.
        if end < n and t[end].text in ctx.and_words:
            # the second jurisdiction may carry the same short filler run
            # ("da Alemanha", "de Espanha") the first one tolerated above.
            k2 = end + 1
            steps2 = 0
            while k2 < n and steps2 < 2 and (
                    t[k2].text in ctx.in_words or t[k2].text in ctx.of_words
                    or t[k2].text in ctx.articles):
                k2 += 1
                steps2 += 1
            if k2 < n and ctx.jurisdictions.get(t[k2].text) is not None:
                return (None, set(range(i, k2 + 1)))
        return (JurisdictionHolidays(code), set(range(i, end)))
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
        # tolerate an explicit interval count before the year unit -- "every
        # 3 YEARS on may 10" -- same as the plain-holiday reading above; only
        # bound as an interval when a year unit immediately follows.
        interval = None
        if (j < n and t[j].is_number and j + 1 < n
                and t[j + 1].text in ctx.units
                and ctx.units[t[j + 1].text] == "year"):
            interval = int(t[j].value)
            j += 1
        # "other" is a word-form interval count -- same INTERVAL=2 the bare
        # "every other year" reading gives, accepted through the same
        # ``ctx.other`` vocabulary (see _recur_holiday above).
        elif (j < n and t[j].text in ctx.other and j + 1 < n
              and t[j + 1].text in ctx.units
              and ctx.units[t[j + 1].text] == "year"):
            interval = 2
            j += 1
        if j < n and t[j].text in ctx.units and ctx.units[t[j].text] == "year":
            j += 1
        # the date must start at (or just after) the skeleton: the only tokens
        # tolerated in the gap are articles or a short filler run ("on"/"in") --
        # never a weekday, number or unit that would belong to a different rule.
        def _scan_dm(start):
            for m in date_matches:
                if m.span[0] < start:
                    continue
                gap = t[start:m.span[0]]
                if len(gap) <= 2 and all(
                        g.text in ctx.articles
                        or (not g.is_number
                            and _weekday_here(ctx, g, True) is None
                            and g.text not in ctx.units and g.text not in ctx.every)
                        for g in gap):
                    return m
            return None

        # the plain skeleton scan must run FIRST: fused calendar_date shapes
        # ("el 1 de enero", "le 10 mai", "am 10. mai") carry their own day,
        # and letting the qualifier scan go first would swallow that day
        # ("el 1") as a bogus standalone qualifier.
        dm = _scan_dm(j)
        day_pre = None
        if dm is None:
            # a LEADING day qualifier ("every year on the 15th in june"):
            # consume it, resume the date scan beyond it, and apply the day
            # once the month resolves.
            got_pre = _monthly_bymonthday_qualifier(ctx, j)
            if got_pre is not None:
                day_pre, day_pre_end = got_pre
                dm = _scan_dm(day_pre_end)
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
        md = _month_day_from_date_match(engine, dm)
        if md is None:
            continue
        month, day = md
        end = dm.span[1]
        if day_pre is not None:
            # the leading qualifier sits between i and dm.span[1], so it is
            # already consumed -- end does not move for it.
            day = day_pre
        else:
            # trailing day qualifier ("in june on the 15th") overrides the
            # calendar_date match's default day the same way.
            got_post = _monthly_bymonthday_qualifier(ctx, dm.span[1])
            if got_post is not None:
                day, end = got_post
        try:
            kw = {"interval": interval} if interval is not None else {}
            rule = _build_every("yearly", bymonth=month, bymonthday=day, **kw)
        except ValueError:
            # the named date recurs in no year ("every 31st of april").  This is
            # still the specific yearly-date frame -- consume it and report no
            # recurrence, rather than fall through to a wrong MONTHLY;BYMONTHDAY.
            return (None, set(range(i, end)))
        return (rule, set(range(i, end)))
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
            _recur_jurisdiction_holidays,
            _recur_date_anchored,
            _recur_once, _recur_on_weekdays, _recur_every, _recur_freq_word,
            _recur_weekday_dayword_bare, _recur_habitual_weekday)
