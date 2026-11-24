# Events and iCalendar: one sentence in, a calendar entry out

<!-- agent-hint
covers: extracting a titled event from a sentence and writing it as an .ics file
source: chronologia/events.py, chronologia/ical.py
generated: no
verify: .venv/bin/python -c 'exec("import ast,io,re,sys,contextlib as c\np=sys.argv[1];t=open(p).read();ns={};n=bad=0\nfor b in re.findall(r\"\\x60\\x60\\x60python\\n(.*?)\\x60\\x60\\x60\",t,re.S):\n    if \"# doctest: skip\" in b: continue\n    L=b.split(\"\\n\")\n    for s in ast.parse(b).body:\n        o=io.StringIO()\n        with c.redirect_stdout(o): exec(compile(ast.Module([s],[]),p,\"exec\"),ns)\n        n+=isinstance(s,ast.Assert)\n        m=re.match(r\"^\\s*print\\(.*\\)\\s+# (.+)$\",L[s.end_lineno-1]) if isinstance(s,ast.Expr) and s.lineno==s.end_lineno else None\n        if m: n+=1; bad|=m[1].strip()!=o.getvalue().strip()\nsys.exit(bad or n==0)\n")' docs/events.md
see: docs/recurrence.md, docs/extraction.md
-->

This guide is for someone who has never used `chronologia` before. It teaches every term as it appears. Every code block below runs. The test suite executes them, so you can copy any of them as written.

By the end you can turn a sentence a person might *say* into a structured calendar entry. An example is "my weekly meeting every wednesday at 9 for 30 minutes". You can then write the entry as a standards-compliant `.ics` file. Google Calendar, Apple Calendar and Outlook import that file.

## What is an `Event`?

An **event** is what you mean by an entry in a calendar. `chronologia` models it as a small, immutable record with four parts:

- **`summary`**: the human label, the "what" ("my weekly meeting"). Free text.
- **`span`**: *when the first occurrence happens*. A [`DateSpan`](getting-started.md) is a half-open interval `[start, end)`: it carries both edges, so it knows an event is 30 minutes long, or a whole day.
- **`duration`**: an explicit length (a `datetime.timedelta`), when the text named one ("for 30 minutes"). It may be `None`. The span still knows its own width.
- **`recurrence`**: *how often it repeats*, as an RFC 5545 rule (see the [recurrence guide](recurrence.md)), or `None` for a one-off.

"RFC 5545" is the internet standard for calendar data, the format inside every `.ics` file. A **recurrence rule** ("RRULE") is its compact way of writing "every Wednesday": `FREQ=WEEKLY;BYDAY=WE`.

## From a sentence to an `Event`

`extract_event` reads one utterance and fills in all four parts. Give it an **anchor**: the moment that relative words resolve against, so the result is reproducible (here, a Wednesday at noon):

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
# the span is the *first* occurrence: the next Wednesday, 09:00 to 09:30
assert (event.span.start.hour, event.span.start.minute) == (9, 0)
assert event.span.end - event.span.start == timedelta(minutes=30)
```

How does it do that without a hand-written grammar? It **composes** three extraction edges you have already met, each consuming its own phrase and passing the leftover text on:

1. `extract_recurrence` reads "every wednesday at 9" → the weekly rule.
2. `extract_duration` reads "for 30 minutes" → the length.
3. whatever text survives, stripped of stranded glue words like "for", is the summary.

For a **one-off** event (no repetition) there is no rule, and the span comes straight from the date in the sentence:

```python
once = extract_event("my birthday party on december 25th", "en", anchor=anchor)
assert once.recurrence is None
assert once.summary == "my birthday party"
assert (once.span.start.month, once.span.start.day) == (12, 25)
```

A length that counts the date, as in "dentist three days before christmas", is not the event's length. The event is one day, 22 December, with no duration. The length stays a length when "for" introduces it ("for 3 days from tomorrow"). It also stays a length when the date reads the same without it ("at 5pm for 10 minutes").

It is data-driven across languages. The same call works in Portuguese, Spanish, German and French:

```python
ev = extract_event("minha reunião toda quarta às 9 por 30 minutos", "pt",
                   anchor=anchor)
assert ev.summary == "minha reunião"
assert ev.recurrence.to_string() == "FREQ=WEEKLY;BYDAY=WE;BYHOUR=9"
assert ev.duration == timedelta(minutes=30)
```

## Writing an `.ics` file: `to_ical`

`to_ical` turns an event into the `VCALENDAR`/`VEVENT` text a calendar app imports. A timed event is written with clock times. An all-day event uses the `VALUE=DATE` form. The recurrence becomes an `RRULE` line:

```python
from chronologia import to_ical

text = to_ical(event)
assert "BEGIN:VEVENT" in text
assert "DTSTART:20260722T090000" in text
assert "RRULE:FREQ=WEEKLY;BYDAY=WE;BYHOUR=9" in text
assert "SUMMARY:my weekly meeting" in text
```

Every event also gets a **UID**, a unique identifier the standard requires. `chronologia` derives it from the event's own content (a hash). So serializing the same event twice yields exactly the same text: no random noise, safe to compare and cache.

## Reading it back: `from_ical`

`from_ical` parses that text back into an `Event`. It is lenient. It ignores any calendar property it does not model, and it round-trips the parts it does:

```python
from chronologia import from_ical

restored = from_ical(text)
assert restored.summary == event.summary
assert restored.span == event.span
assert restored.recurrence == event.recurrence
```

## Movable feasts: honest about what a rule cannot say

Some holidays recur every year but have *no* RFC 5545 rule. An algorithm (the *computus*) computes Easter. "The Nth weekday of a month" does not. For these holidays, `extract_event` gives you a `HolidayRecurrence`. It still expands to real dates, but it does not pretend to be a rule string. Writing one to iCal raises an error instead of writing something false:

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

- [Recurrence rules](recurrence.md), the full RFC 5545 rule object and how to expand it into dates.
- [Extraction](extraction.md), the natural-language edges (`extract_timespan`, `extract_duration`, `extract_recurrence`) that `extract_event` composes.
- [Getting started](getting-started.md), what a `DateSpan` is and how its two edges carry the referential width of a phrase.

---
[← Adding a language](adding-a-language.md) · [Home](index.md) · [Recurrence rules →](recurrence.md)
