"""04 — Recurring dates and calendar events.

Run it with::

    python examples/04_recurrence_and_events.py

Two related ideas:

* **recurrence** — a rule that repeats, like "every third Tuesday". The
  library models these with the calendar-industry standard **RRULE** (the
  recurrence grammar from RFC 5545, the iCalendar spec). ``extract_recurrence``
  reads such a rule out of a phrase; ``every(...)`` builds one directly; and
  ``occurrences(...)`` expands a rule into the actual dates it fires on.
* **event** — something with a summary *and* a time. ``extract_event`` pulls
  both out of a sentence ("lunch next Tuesday at noon") and hands back an
  ``Event`` you can serialise to an **.ics** file (``to_ical``) — the format
  every calendar app imports.
"""
from datetime import datetime

from chronologia import (every, extract_event, extract_recurrence, occurrences,
                         to_ical)

anchor = datetime(2024, 1, 1)

# Read a recurrence rule out of plain English.
rule, _ = extract_recurrence("every third Tuesday", "en", anchor)
print("Parsed 'every third Tuesday':")
print(f"  freq={rule.freq} interval={rule.interval} byday={rule.byday}")
assert rule.freq == "WEEKLY" and rule.interval == 3

# Build the same kind of rule by hand, then expand it to concrete dates.
weekly = every("WEEKLY", byday="TU")
fires = list(occurrences(weekly, dtstart=datetime(2024, 1, 1), count=3))
print("\nFirst three Tuesdays from 2024-01-01:")
for span in fires:
    print("  ", span.start_datetime.date())
assert [s.start_datetime.date().isoformat() for s in fires] == \
    ["2024-01-02", "2024-01-09", "2024-01-16"]

# Turn a sentence into a calendar event, then into an .ics file.
event = extract_event("lunch next Tuesday at noon", "en", anchor)
print(f"\nEvent summary: {event.summary!r} at "
      f"{event.span.start_datetime.isoformat()}")
ics = to_ical(event)
assert "BEGIN:VCALENDAR" in ics and "SUMMARY:lunch" in ics
print("\n.ics output (paste into any calendar app):\n")
print(ics)

print("OK — recurrences expanded, an event exported to iCalendar.")
