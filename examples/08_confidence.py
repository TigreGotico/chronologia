"""08 — When a phrase is ambiguous: ranked candidates.

Run it with::

    python examples/08_confidence.py

Human dates are often ambiguous. "Spring 2025" could mean the season, or it
could be read as just the year. Rather than silently pick one,
``extract_candidates`` returns *all* the readings it found, ranked by
**confidence** — a score from 0 to 1 saying how sure the library is. The
best reading is first.

Each ``Candidate`` carries:

* ``span`` — the stretch of time this reading resolves to;
* ``confidence`` — the 0-to-1 score;
* ``construction`` — the *kind* of reading (a ``season_ref``, a ``year_ref``…);
* ``remainder`` — words the reading did not consume.
"""
from datetime import datetime

from chronologia import extract_candidates

anchor = datetime(2024, 1, 1)

candidates = extract_candidates("spring 2025", "en", anchor, limit=5)
print("Readings of 'spring 2025', best first:\n")
for c in candidates:
    print(f"  {c.confidence:.2f}  {c.construction:12}  "
          f"{c.span.start_datetime.date()} -> {c.span.end_datetime.date()}")

# There is more than one reading, and they come back sorted high-to-low.
assert len(candidates) >= 2
scores = [c.confidence for c in candidates]
assert scores == sorted(scores, reverse=True)

# The winner is the season reading — a spring, not a whole year.
best = candidates[0]
print(f"\nBest reading: {best.construction} at {best.confidence:.2f}")
assert best.construction == "season_ref"

print("\nOK — ambiguity surfaced and ranked, never silently resolved.")
