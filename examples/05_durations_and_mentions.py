"""05 — Durations, and finding every date in a sentence.

Run it with::

    python examples/05_durations_and_mentions.py

Two things a single ``extract_timespan`` call does *not* cover:

* **duration** — a *length* of time with no fixed start ("three and a half
  hours"). ``extract_duration`` returns a plain ``datetime.timedelta``.
* **mentions** — one sentence can contain several dates. ``extract_timespans``
  (note the plural) returns a list of ``TimeMention`` objects. Each carries
  its resolved ``span`` and a ``char_span`` — the ``(start, end)`` character
  offsets of the words that produced it, so you can highlight them back in the
  original text.
"""
from datetime import datetime, timedelta

from chronologia import extract_duration, extract_timespans

# A bare length of time, no calendar date involved.
length, _ = extract_duration("three and a half hours", "en")
print("Duration of 'three and a half hours':", length)
assert length == timedelta(hours=3, minutes=30)

# A sentence with more than one date in it.
sentence = "monday to friday next week"
mentions = extract_timespans(sentence, "en", datetime(2024, 1, 1))
print(f"\n{len(mentions)} date mentions found in {sentence!r}:")
for m in mentions:
    start, end = m.char_span
    print(f"  {m.char_span}  {sentence[start:end]!r} -> "
          f"{m.span.start_datetime.date()}")
assert len(mentions) >= 2

# char_span lets you underline the recognised words in the source text.
print("\nHighlighting the recognised words:")
print(" ", sentence)
underline = [" "] * len(sentence)
for m in mentions:
    for i in range(*m.char_span):
        underline[i] = "^"
print(" ", "".join(underline))

print("\nOK — a bare duration, and every dated span located by character.")
