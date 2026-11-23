"""One utterance -> one :class:`Event`: the capstone composition.

An :class:`Event` is what a human means by "an appointment": a *summary* (what
it is), a *span* (when its first occurrence starts and ends), an optional
*duration*, and an optional *recurrence*.  :func:`extract_event` builds one from
a single natural-language utterance by **composing the extraction edges already
in the library** -- it writes no new grammar:

    "my weekly meeting every wednesday at 9 for 30 minutes"
        summary    = "my weekly meeting"
        recurrence = FREQ=WEEKLY;BYDAY=WE;BYHOUR=9
        duration   = 30 minutes
        span       = the next Wednesday 09:00 .. 09:30

Mechanism -- the remainders chain
---------------------------------
The three edges run in a fixed order, each consuming its own phrase and handing
the *leftover text* to the next:

1. :func:`~chronologia.extract.extract_recurrence` reads the recurring phrase
   ("every wednesday at 9"); its remainder feeds
2. :func:`~chronologia.extract.extract_duration`, which reads the length ("for
   30 minutes"); its remainder feeds
3. :func:`~chronologia.extract.extract_timespan` (only when there is *no*
   recurrence -- a recurring event takes its span from the rule's first
   occurrence, not from a bare date in the text).

Whatever text survives all three, stripped of the stranded connector words the
edges leave behind ("for", "at", "on", a trailing article), is the **summary**.

The **span** is the event's first concrete occurrence: for a recurring event it
is the recurrence expanded once from the anchor; for a one-off it is the parsed
span.  When a duration is present the span's end is pinned to
``start + duration`` so the span always carries the real width (and the iCal
writer's ``DTEND`` is correct).
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, Union

from chronologia.astrodate import DateSpan
from chronologia.extract.impossible import reports_impossible
from chronologia.recurrence import (HolidayRecurrence, JurisdictionHolidays,
                                    Recurrence, occurrences)

__all__ = ["Event", "extract_event"]

RecurrenceLike = Union[Recurrence, HolidayRecurrence, JurisdictionHolidays]


@dataclass(frozen=True)
class Event:
    """A calendar event: what, when, how long, how often.

    * ``summary`` -- the free-text label ("my weekly meeting"); may be empty.
    * ``span`` -- the :class:`~chronologia.astrodate.DateSpan` of the *first*
      occurrence; its width is the event's duration when one is known.
    * ``duration`` -- an explicit :class:`datetime.timedelta` length, or
      ``None`` when the text named none (the span still carries an implicit
      width -- a day for a day-wide date, an hour for a clock-pinned rule).
    * ``recurrence`` -- a :class:`~chronologia.recurrence.Recurrence` /
      :class:`~chronologia.recurrence.HolidayRecurrence`, or ``None`` for a
      one-off event.
    * ``confidence`` -- the deterministic score in ``(0, 1]`` for the temporal
      reading the event was built from (see
      :mod:`chronologia.extract.confidence`); **not** a probability.  Excluded
      from equality/hash (``compare=False``) so an event compares by what it
      *is*, never by a derived score.
    """

    summary: str
    span: DateSpan
    duration: Optional[timedelta] = None
    recurrence: Optional[RecurrenceLike] = None
    confidence: float = field(default=1.0, compare=False)


def first_occurrence(recurrence: RecurrenceLike,
                     anchor: datetime) -> Optional[DateSpan]:
    """The first span a recurrence produces on or after ``anchor``.

    Works for both rule kinds: a plain :class:`Recurrence` expands through
    :func:`~chronologia.recurrence.occurrences`; a
    :class:`~chronologia.recurrence.HolidayRecurrence` or
    :class:`~chronologia.recurrence.JurisdictionHolidays` through its own
    holiday-engine expansion.  ``None`` when the rule yields nothing near the
    anchor (a holiday outside its tabulated range).
    """
    if isinstance(recurrence, (HolidayRecurrence, JurisdictionHolidays)):
        gen = recurrence.occurrences(anchor, count=1)
    else:
        gen = occurrences(recurrence, anchor, count=1)
    for span in gen:
        return span
    return None


#: Leading/trailing prepositions the date grammar does not itself consume but
#: which read as stranded glue at a summary edge ("lunch on <date>" leaves a
#: dangling "on").  Locale connectors are the primary source; this per-language
#: fallback covers the plain prepositions no ``.voc`` marker names.  Edges only
#: -- interior words are never touched, so a real "day of rest" survives.
_PREP_FALLBACK = {
    "en": {"on", "in", "at", "for", "to", "of", "the", "a", "an"},
    "pt": {"em", "no", "na", "de", "do", "da", "para", "às", "ao", "o", "a"},
    "es": {"en", "el", "la", "de", "del", "al", "a", "para", "los", "las"},
    "de": {"am", "im", "um", "an", "für", "der", "die", "das", "den"},
    "fr": {"le", "la", "les", "à", "au", "aux", "de", "du", "des", "pour"},
}


def _summary_stopwords(spec, lang: str) -> frozenset:
    """Connector surfaces that may be left stranded at a summary's edges."""
    C = spec.connectors
    words = set()
    for name in ("article", "indef", "of", "at", "recur_for", "until",
                 "since", "and", "every", "in", "from", "on", "during"):
        words |= set(C.get(name, ()))
    words |= {s for s, v in spec.quantifiers.items() if v == 1.0}
    words |= _PREP_FALLBACK.get(lang.split("-")[0].lower(), set())
    return frozenset(words)


def _clean_summary(text: str, lang: str) -> str:
    """Strip stranded connector words from the edges of a leftover phrase.

    Interior words are untouched (a summary may legitimately contain "of" or
    "the"); only leading and trailing function words the extraction edges left
    behind are removed, so "my weekly meeting for" -> "my weekly meeting".
    """
    from chronologia.extract import _timespan_engine
    from chronologia.extract.numlayer import mentions, reads

    engine = _timespan_engine(lang)
    tokens = list(engine.tokenize(text))
    stop = _summary_stopwords(engine.spec, lang)
    # a count word that opens a longer number is no stranded article:
    # "un millón de euros" keeps its "un"
    number_ends = ({m.char_span[0]: m.char_span[1] for m in mentions(text, lang)}
                   if reads(lang) else {})
    lo, hi = 0, len(tokens)
    while (lo < hi and tokens[lo].text in stop
           and number_ends.get(tokens[lo].char_start, -1) <= tokens[lo].char_end):
        lo += 1
    while hi > lo and tokens[hi - 1].text in stop:
        hi -= 1
    return " ".join(t.raw for t in tokens[lo:hi]).strip()


def _is_bare_clock_length(text: str, lang: str, anchor: datetime,
                          length_words: Counter) -> bool:
    """True when the length words alone read as a clock time and no offset
    marker joins them to the date.

    A before or after word joins two readings, so only a token that lies
    between two winners and that no winner takes counts: "avant" in "deux
    heures avant midi".  A marker inside a reading is part of it:
    "après-demain" is one day word, and "en mars" one month.  An "in" or
    "ago" word stands before or after its own count, never between the
    length and a date: nl "twee uur in de ochtend" is two hours in the
    morning.
    """
    from chronologia.extract import _timespan_engine, explain

    spec = _timespan_engine(lang).spec
    markers = {word.lower() for name in ("before", "after")
               for surface in spec.connectors.get(name, ())
               for word in surface.split()}
    trace = explain(text, spec, anchor)
    spans = [w.match.span for w in trace.winners]
    if not spans:
        return False
    taken = {i for first, end in spans for i in range(first, end)}
    gap = range(min(first for first, _ in spans), max(end for _, end in spans))
    if any(trace.tokens[i].text.lower() in markers
           for i in gap if i not in taken):
        return False
    return any(w.match.construction == "clock_time"
               and Counter(t.text for t in trace.tokens[slice(*w.match.span)])
               == length_words for w in trace.winners)


def _is_counted_part_of_day(text: str, lang: str, anchor: datetime,
                            length_words: Counter) -> bool:
    """True when a word that no reading takes stands before the length
    words and the clock reading that starts on them goes on into a part of
    the day without a clock suffix: pt "reunião de duas horas e meia de
    manhã", fr "travaillé trois heures le matin".

    A date word or a clock preposition before the count belongs to a
    reading, so "demain neuf heures et demie le soir" is the clock 21:30.
    The clock suffix ("da", "du", "'s", or "de" and an article) ties the
    part of the day to the hour: "deux heures du matin" is 02:00.  Only
    languages that list a ``clock_of`` suffix tell the two forms apart.
    """
    from chronologia.extract import _timespan_engine, explain

    spec = _timespan_engine(lang).spec
    suffixes = spec.connectors.get("clock_of")
    if not suffixes:
        return False
    of_words = spec.connectors.get("of", frozenset())
    articles = spec.connectors.get("article", frozenset())
    trace = explain(text, spec, anchor)
    taken = {i for w in trace.winners for i in range(*w.match.span)}
    size = sum(length_words.values())
    for w in trace.winners:
        first, end = w.match.span
        if (w.match.construction != "clock_time"
                or "MERIDIEM" not in w.match.slots
                or end - first <= size or first == 0
                or first - 1 in taken):
            continue
        words = [t.text for t in trace.tokens[first:end]]
        if Counter(words[:size]) != length_words:
            continue
        tail = words[size:]
        tied = any(word in suffixes or (
            word in of_words and nxt in articles)
            for word, nxt in zip(tail, tail[1:] + [""]))
        if not tied:
            return True
    return False


@reports_impossible
def extract_event(
        text: str,
        lang: str = "en",
        anchor: Optional[datetime] = None,
        jurisdiction: Optional[str] = None,
) -> Optional[Event]:
    """Extract a single :class:`Event` from one natural-language utterance.

    Composes recurrence, duration and span extraction (see the module
    docstring): a recurring event takes its span from the rule's first
    occurrence expanded from ``anchor``; a one-off from the span named in the
    text.  ``jurisdiction`` scopes any business-day span construction, exactly
    as :func:`~chronologia.extract.extract_timespan` documents.

    Returns an :class:`Event`, or ``None`` when the text carries neither a
    recurrence nor a datable span (there is no event to build).

    ``impossible`` is ``"none"`` (default) or ``"raise"``.  With ``"raise"`` a
    phrase naming a date the calendar rejects ("29 February 2017") raises
    :class:`~chronologia.ImpossibleDateError` instead of giving ``None``; a phrase
    that is no date still gives ``None``, and a call that finds a reading
    returns it.

    ``text`` must be a ``str``; anything else raises :class:`TypeError`.
    Text that carries no event, the empty string included, returns ``None``.
    """
    from chronologia.extract import (_timespan_engine, extract_candidates,
                                     extract_duration, extract_timespan)
    from chronologia.extract.nseries import (_NEVER_OCCURS, _duration_core,
                                             _read_recurrence)
    from chronologia.extract.pipeline import require_text

    require_text(text, "extract_event")
    lang = lang.strip().replace("_", "-")

    anchor = anchor or datetime.now()
    if isinstance(anchor, datetime):
        anchor = anchor.replace(tzinfo=None)

    recurrence: Optional[RecurrenceLike] = None
    remainder = text
    got_rec = _read_recurrence(text, lang, anchor)
    if got_rec is _NEVER_OCCURS:
        return None
    if got_rec is not None:
        recurrence, remainder = got_rec

    duration: Optional[timedelta] = None
    date_beside_length: Optional[DateSpan] = None
    got_dur = extract_duration(remainder, lang)
    if got_dur is not None and recurrence is None:
        # "3 days before christmas": the length is the date's offset, not the
        # event's width, when the span reading of the whole text consumes
        # every word the length took and starts on another date than the text
        # without the length.  A length that carries its own "for" marker
        # stays a length, also when the span reading takes the marker: "for 3
        # days from tomorrow", pt "amanhã durante duas horas de manhã" and fr
        # "demain pendant deux heures le matin".  "at 5pm for 10
        # minutes" keeps it, because both readings start at 5pm.  fr "réunion
        # de deux heures demain" keeps it too: "deux heures" alone reads as the
        # clock time 02:00, and no "before"/"after"/"in"/"ago" marker joins the
        # words to the date that remains.  es "reunión de dos horas en
        # marzo" keeps it as well: the span reading takes "dos horas en" as
        # "in two hours" and leaves "marzo", a word the reading of the rest
        # takes, so the whole-text reading lost the date.  That check holds
        # only when the span reading is the length with its offset words, an
        # offset from now: "the day after next 3 pm" reads a date of its own,
        # so its "day" is no length even though "3 pm" is left over.
        try:
            whole = extract_timespan(remainder, lang, anchor=anchor,
                                     jurisdiction=jurisdiction)
            rest = extract_timespan(got_dur.remainder, lang, anchor=anchor,
                                    jurisdiction=jurisdiction)
        except (KeyError, ValueError):
            whole = None
        if whole is not None:
            engine = _timespan_engine(lang)

            def words(phrase: str) -> Counter:
                return Counter(t.text for t in engine.tokenize(phrase))

            all_words = words(remainder)
            length_words = all_words - words(got_dur.remainder)
            span_words = all_words - words(whole.remainder)
            rest_words = Counter() if rest is None else (
                words(got_dur.remainder) - words(rest.remainder))
            spec = engine.spec
            offset_words = Counter({
                word: len(all_words)
                for name in ("before", "after", "in", "ago")
                for surface in spec.connectors.get(name, ())
                for word in words(surface)})
            if not length_words & span_words:
                date_beside_length = whole.span
            bare_offset = not span_words - length_words - offset_words
            for_marked = any(not words(surface) - length_words
                             for surface in spec.connectors.get("recur_for", ()))
            if not for_marked and not length_words - span_words \
                    and not (bare_offset and rest_words - span_words) \
                    and (rest is None or rest.span.start != whole.span.start) \
                    and not (rest is not None and _is_bare_clock_length(
                        remainder, lang, anchor, length_words)) \
                    and not _is_counted_part_of_day(
                        remainder, lang, anchor, length_words):
                got_dur = None
                date_beside_length = None
    if got_dur is not None:
        duration, remainder = got_dur

    # a calendar length after its marker ("for a month and a half") leaves
    # the text before the date reader runs, as a fixed length does, so the
    # date reader cannot take a part of it; its width is read once the start
    # is known
    calendar_text = None
    if duration is None:
        got_cal = _duration_core(remainder, _timespan_engine(lang), anchor,
                                 calendar_needs_marker=True)
        if got_cal is not None:
            calendar_text, remainder = remainder, got_cal[1]

    # A recurring event is rule-driven (a matched ``every`` marker is a strong,
    # unambiguous signal), so it carries full confidence; a one-off inherits
    # the confidence of the best plausible reading of the span-bearing text.
    conf = 1.0
    if recurrence is not None:
        base = first_occurrence(recurrence, anchor)
    else:
        got_span = extract_timespan(remainder, lang, anchor=anchor,
                                    jurisdiction=jurisdiction)
        if got_span is None and calendar_text is not None:
            # the length was a part of the date: da "for et år siden" is
            # "a year ago"
            remainder, calendar_text = calendar_text, None
            got_span = extract_timespan(remainder, lang, anchor=anchor,
                                        jurisdiction=jurisdiction)
        if got_span is None:
            return None
        cands = extract_candidates(remainder, lang, anchor=anchor)
        if cands:
            conf = cands[0].confidence
        base, remainder = got_span
        if (duration is not None and date_beside_length is not None
                and base.start < anchor <= date_beside_length.start):
            # es "reunión de dos horas mañana": without the length "de mañana"
            # reads as this morning, before the anchor
            base = date_beside_length

    if base is None:
        return None

    # a calendar length ("for 3 months") counts from the start of the event;
    # an offset ("in 3 months") has no marker and stays a date
    if calendar_text is not None:
        got_cal = None
        if 1 <= base.start.year <= 9999:
            start = datetime(base.start.year, base.start.month,
                             base.start.day, base.start.hour,
                             base.start.minute, base.start.second,
                             base.start.microsecond)
            got_cal = _duration_core(calendar_text, _timespan_engine(lang),
                                     start, calendar_needs_marker=True)
        if got_cal is not None:
            duration = got_cal[0]
        elif recurrence is not None:
            remainder = calendar_text
        else:
            # a length with no calendar end stays in the summary
            got_span = extract_timespan(calendar_text, lang, anchor=anchor,
                                        jurisdiction=jurisdiction)
            remainder = calendar_text if got_span is None else got_span[1]

    # When a duration is named, the span carries exactly that width; otherwise
    # the span keeps its own implicit width (a day, an hour, a minute...).
    if duration is not None:
        span = DateSpan(base.start, base.start + duration)
    else:
        span = base

    summary = _clean_summary(remainder, lang)
    return Event(summary=summary, span=span, duration=duration,
                 recurrence=recurrence, confidence=conf)
