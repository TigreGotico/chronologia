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

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Union

from chronologia.astrodate import DateSpan
from chronologia.recurrence import HolidayRecurrence, Recurrence, occurrences

__all__ = ["Event", "extract_event"]

RecurrenceLike = Union[Recurrence, HolidayRecurrence]


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
    """

    summary: str
    span: DateSpan
    duration: Optional[timedelta] = None
    recurrence: Optional[RecurrenceLike] = None


def first_occurrence(recurrence: RecurrenceLike,
                     anchor: datetime) -> Optional[DateSpan]:
    """The first span a recurrence produces on or after ``anchor``.

    Works for both rule kinds: a plain :class:`Recurrence` expands through
    :func:`~chronologia.recurrence.occurrences`; a
    :class:`~chronologia.recurrence.HolidayRecurrence` through its own
    holiday-engine expansion.  ``None`` when the rule yields nothing near the
    anchor (a holiday outside its tabulated range).
    """
    if isinstance(recurrence, HolidayRecurrence):
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

    engine = _timespan_engine(lang)
    tokens = list(engine.tokenize(text))
    stop = _summary_stopwords(engine.spec, lang)
    lo, hi = 0, len(tokens)
    while lo < hi and tokens[lo].text in stop:
        lo += 1
    while hi > lo and tokens[hi - 1].text in stop:
        hi -= 1
    return " ".join(t.raw for t in tokens[lo:hi]).strip()


def extract_event(
        text: str,
        lang: str = "en-us",
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
    """
    from chronologia.extract import (extract_duration, extract_recurrence,
                                     extract_timespan)

    anchor = anchor or datetime.now()
    if isinstance(anchor, datetime):
        anchor = anchor.replace(tzinfo=None)

    recurrence: Optional[RecurrenceLike] = None
    remainder = text
    got_rec = extract_recurrence(text, lang, anchor=anchor)
    if got_rec is not None:
        recurrence, remainder = got_rec

    duration: Optional[timedelta] = None
    got_dur = extract_duration(remainder, lang)
    if got_dur is not None:
        duration, remainder = got_dur

    if recurrence is not None:
        base = first_occurrence(recurrence, anchor)
    else:
        got_span = extract_timespan(remainder, lang, anchor=anchor,
                                    jurisdiction=jurisdiction)
        if got_span is None:
            return None
        base, remainder = got_span

    if base is None:
        return None

    # When a duration is named, the span carries exactly that width; otherwise
    # the span keeps its own implicit width (a day, an hour, a minute...).
    if duration is not None:
        span = DateSpan(base.start, base.start + duration)
    else:
        span = base

    summary = _clean_summary(remainder, lang)
    return Event(summary=summary, span=span, duration=duration,
                 recurrence=recurrence)
