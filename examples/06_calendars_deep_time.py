"""06 — Other calendars, dates BC, and deep time.

Run it with::

    python examples/06_calendars_deep_time.py

Everything so far spoke the everyday (Gregorian) calendar. Underneath, the
library reckons across *any* calendar and across all of time. This example is
"objects in, objects out" — no manual day-number plumbing.

Terms introduced here:

* **calendar** — an agreement about how to name days (Hebrew, Islamic, the
  Roman/Julian calendar). ``AstroDate.from_calendar`` reads a date written in
  one of them and gives you a normal date object back.
* **AstroDate** — a drop-in ``datetime`` whose year is unbounded, so it can
  hold dates before year 1 (which ``datetime`` cannot). Astronomers number
  1 BC as year 0, so 44 BC is year ``-43``.
* **basis** — the honesty label on every span: ``exact`` (computed from a
  rule), ``tabulated`` (from a published table), ``reconstructed`` (pieced
  together by scholars).
* **BP** — "Before Present", the archaeological/geological convention that
  counts years back from 1950.
"""
from chronologia import (AstroDate, CALENDARS, calibrate_c14, lookup,
                         resolve_bp)

# A date written in the Islamic calendar, read back as an ordinary date.
eid = CALENDARS["islamic_civil"].date(1446, 9, 15)  # 15 Ramadan 1446
print("15 Ramadan 1446 (Islamic) =", eid.date())
assert eid.date().isoformat() == "2025-03-15"

# The Ides of March, 44 BC — written in the Roman (Julian) calendar.
ides = AstroDate.from_calendar("julian", -43, 3, 15)
print("Ides of March 44 BC weekday =", ides.weekday(), "(2 = Wednesday)")
assert ides.weekday() == 2

# Deep time: "when was the Jurassic?" The answer is a span tens of millions of
# years wide, straight from the official geological chart (hence 'tabulated').
jurassic = lookup("jurassic")
print(f"\nJurassic: {jurassic.span.start.year:,} to "
      f"{jurassic.span.end.year:,}  [{jurassic.span.basis}]")
assert jurassic.span.basis == "tabulated"

# Precision is read from how you write the number. "66 Ma" claims accuracy to
# the nearest million years, so the span is a million years wide.
rounded = resolve_bp("66", "Ma")   # Ma = millions of years ago
print("\n'66 Ma' span width (days):", int(rounded.width.days), "~= 1,000,000 yr")
assert abs(rounded.width.days / 365.2425 - 1_000_000) < 1

# A radiocarbon age is NOT calendar years — it must be calibrated. The result
# is 'reconstructed', because it leans on a published calibration curve.
charcoal = calibrate_c14(3500)
print("Calibrated 3500 BP radiocarbon age -> basis:", charcoal.basis)
assert charcoal.basis == "reconstructed"

print("\nOK — many calendars, dates before year 1, and time by the megayear.")
