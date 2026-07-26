# Events and iCalendar: one sentence in, a calendar entry out

This guide is for someone who has never used `chronologia` before. It teaches
every term as it appears, and every code block below actually runs (the test
suite executes them), so you can copy any of them verbatim.

By the end you will be able to turn a sentence a person might *say* —
"my weekly meeting every wednesday at 9 for 30 minutes" — into a structured
calendar entry, and write that entry out as a standards-compliant `.ics` file
that Google Calendar, Apple Calendar or Outlook will import.

## What is an `Event`?

An **event** is what you mean by an entry in a calendar. `chronologia` models it
as a small, immutable record with four parts:

- **`summary`** — the human label, the "what" ("my weekly meeting"). Free text.
- **`span`** — *when the first occurrence happens*. A
  [`DateSpan`](getting-started.md) is a half-open interval `[start, end)`: it
  carries both edges, so it knows an event is 30 minutes long, or a whole day.
- **`duration`** — an explicit length (a `datetime.timedelta`), when the text
  named one ("for 30 minutes"). It may be `None`; the span still knows its own
  width.
- **`recurrence`** — *how often it repeats*, as an RFC 5545 rule (see the
  [recurrence guide](recurrence.md)), or `None` for a one-off.

"RFC 5545" is the internet standard for calendar data — the format inside every
`.ics` file. A **recurrence rule** ("RRULE") is its compact way of writing
"every Wednesday": `FREQ=WEEKLY;BYDAY=WE`.

## From a sentence to an `Event`

`extract_event` reads one utterance and fills in all four parts. Give it an
**anchor** — the "now" that relative words resolve against — so the result is
reproducible (here, a Wednesday at noon):

```python
from datetime import datetime, timedelta
from chronologia import extract_event

anchor = datetime(2026, 7, 22, 12, 0)   # a Wednesday
event = extract_event(
    "my weekly meeting every wednesday at 9 for 30 minutes", "en",
    anchor=anchor)

assert event.summary == "my weekly meeting"
assert event.recurrence.to_string() == "FREQ=WEEKLY;BYDAY=WE;BYHOUR=9"
assert event.duration == timedelta(minutes=30)
# the span is the *first* occurrence: the next Wednesday, 09:00–09:30
assert (event.span.start.hour, event.span.start.minute) == (9, 0)
assert event.span.end - event.span.start == timedelta(minutes=30)
```

How does it do that without a hand-written grammar? It **composes** three
extraction edges you have already met, each consuming its own phrase and passing
the leftover text on:

1. `extract_recurrence` reads "every wednesday at 9" → the weekly rule;
2. `extract_duration` reads "for 30 minutes" → the length;
3. whatever text survives, stripped of stranded glue words like "for", is the
   summary.

For a **one-off** event (no repetition) there is no rule, and the span comes
straight from the date in the sentence:

```python
once = extract_event("my birthday party on december 25th", "en", anchor=anchor)
assert once.recurrence is None
assert once.summary == "my birthday party"
assert (once.span.start.month, once.span.start.day) == (12, 25)
```

It is data-driven across languages — the same call works in Portuguese, Spanish,
German and French:

```python
ev = extract_event("minha reunião toda quarta às 9 por 30 minutos", "pt",
                   anchor=anchor)
assert ev.summary == "minha reunião"
assert ev.recurrence.to_string() == "FREQ=WEEKLY;BYDAY=WE;BYHOUR=9"
assert ev.duration == timedelta(minutes=30)
```

## Writing an `.ics` file: `to_ical`

`to_ical` turns an event into the `VCALENDAR`/`VEVENT` text a calendar app
imports. A timed event is written with clock times; an all-day event uses the
`VALUE=DATE` form; the recurrence becomes an `RRULE` line:

```python
from chronologia import to_ical

text = to_ical(event)
assert "BEGIN:VEVENT" in text
assert "DTSTART:20260722T090000" in text
assert "RRULE:FREQ=WEEKLY;BYDAY=WE;BYHOUR=9" in text
assert "SUMMARY:my weekly meeting" in text
```

Every event also gets a **UID** — a unique identifier the standard requires.
`chronologia` derives it from the event's own content (a hash), so serializing
the same event twice yields exactly the same text: no random noise, safe to
compare and cache.

## Reading it back: `from_ical`

`from_ical` parses that text back into an `Event`. It is lenient — it ignores
any calendar property it does not model — and it round-trips the parts it does:

```python
from chronologia import from_ical

restored = from_ical(text)
assert restored.summary == event.summary
assert restored.span == event.span
assert restored.recurrence == event.recurrence
```

## Movable feasts: honest about what a rule cannot say

Some holidays recur every year but have *no* RFC 5545 rule — Easter is computed
by an algorithm (the *computus*), not by "the Nth weekday of a month". For those,
`extract_event` gives you a `HolidayRecurrence`: it still expands to real dates,
but it refuses to pretend it is a rule string. Serializing one to iCal raises,
loudly, instead of writing something false:

```python
from chronologia.recurrence import HolidayRecurrence

easter_event = extract_event("yoga every easter", "en", anchor=anchor)
assert easter_event.recurrence == HolidayRecurrence("easter")

# it expands to concrete dates just fine ...
first = easter_event.recurrence.occurrences(anchor, count=1)
assert next(iter(first)).start.year == 2027

# ... but it will not lie in an RRULE line
try:
    to_ical(easter_event)
    raise AssertionError("expected a refusal")
except ValueError:
    pass   # correct: a movable feast has no RFC 5545 rule
```

## Where to go next

- [Recurrence rules](recurrence.md) — the full RFC 5545 rule object and how to
  expand it into dates.
- [Extraction](extraction.md) — the natural-language edges (`extract_timespan`,
  `extract_duration`, `extract_recurrence`) that `extract_event` composes.
- [Getting started](getting-started.md) — what a `DateSpan` is and how its two
  edges carry the referential width of a phrase.
