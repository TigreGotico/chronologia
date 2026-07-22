"""01 — Reading a date out of a sentence.

This is the first thing most people want: hand the library an English phrase
and get back the exact stretch of time it means. Run it with::

    python examples/01_extract_basics.py

Three ideas are introduced here, and every later example builds on them:

* **span** — the library never answers with a single instant. A phrase names
  a *stretch* of time (a whole day, a whole month), so the answer is a
  ``DateSpan``: a half-open interval ``[start, end)`` that includes ``start``
  and stops just before ``end``.
* **anchor** — words like "tomorrow" only mean something relative to a "now".
  You supply that "now" as the ``anchor`` argument, so results are
  reproducible instead of depending on today's date.
* **remainder** — the words left over after the date was recognised. Useful
  when the phrase is embedded in a longer sentence.
"""
from datetime import datetime

from chronologia import extract_candidates, extract_timespan

# The anchor is our fixed "now". Pin it so the example prints the same thing
# every time, no matter what day you run it.
anchor = datetime(2024, 1, 1)

# extract_timespan returns (span, leading_words) or None if nothing was found.
span, _ = extract_timespan("the 15th of Ramadan 1446", "en", anchor)
print("15th of Ramadan 1446 :", span.start_datetime.date(), "->",
      span.end_datetime.date(), f"(basis: {span.basis})")
# A single day is one day wide: start on the 15th, end at the start of the 16th.
assert span.start_datetime.date().isoformat() == "2025-03-15"
assert span.end_datetime.date().isoformat() == "2025-03-16"

# "next summer" is a season — a wide span, not a day.
summer, _ = extract_timespan("next summer", "en", anchor)
print("next summer          :", summer.start_datetime.date(), "->",
      summer.end_datetime.date())
assert summer.start_datetime.date().isoformat() == "2024-06-01"

# When the date is buried in a sentence, ask for candidates: each carries the
# span it recognised plus the *remainder* — the words it did not consume.
[best] = extract_candidates("pay the invoice by March 2024", "en", anchor,
                            limit=1)
print("buried date          :", best.span.start_datetime.date(),
      "| remainder:", repr(best.remainder))
assert best.span.start_datetime.date().isoformat() == "2024-03-01"

print("\nOK — a phrase became a span, anchored to a fixed 'now'.")
