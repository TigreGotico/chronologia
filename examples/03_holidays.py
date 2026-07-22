"""03 — Civil holidays: which days a country takes off, and why.

Run it with::

    python examples/03_holidays.py

A **civil holiday** is a day a government (national, regional, or municipal)
declares as a public holiday. This library does not download a holiday list —
it *computes* each holiday from its published rule (a fixed date, "the fourth
Thursday of November", an offset from Easter, or a per-year decree), so it
works for any year in range without a network call.

Terms introduced here:

* **jurisdiction** — who declares the holiday. You name it with a short code:
  ``"US"``, ``"PT"`` (Portugal), or a market code like ``"NYSE"``.
* **subdivision** (``subdiv``) — a region *inside* a jurisdiction (a US state,
  a Portuguese município) that adds its own holidays on top of the national
  ones.
* **category** — a tag such as ``"public"`` or ``"bank"`` you can filter by.
* **basis** — the same honesty label as everywhere else: a holiday computed
  from a rule is ``exact``; one read from an official published table (Saudi
  Umm al-Qura) is ``tabulated``.
"""
from datetime import date

from chronologia import holidays_for, is_civil_holiday

# Every US federal holiday in 2024, computed from its rule.
us_2024 = holidays_for("US", 2024)
print(f"US federal holidays in 2024 ({len(us_2024)} of them):")
for h in us_2024[:5]:
    print(f"  {h.span.start_datetime.date()}  {h.name}  [{h.span.basis}]")
print("  ...")
assert any(h.name == "Independence Day" for h in us_2024)

# Ask a yes/no question about a specific day.
print("\nIs 2024-07-04 a US holiday? ->", is_civil_holiday(date(2024, 7, 4), "US"))
print("Is 2024-07-05 a US holiday? ->", is_civil_holiday(date(2024, 7, 5), "US"))
assert is_civil_holiday(date(2024, 7, 4), "US")
assert not is_civil_holiday(date(2024, 7, 5), "US")

# Market calendars are jurisdictions too — the New York Stock Exchange closes
# on fewer days than the country as a whole.
nyse = holidays_for("NYSE", 2024)
print(f"\nNYSE trading-holiday count in 2024: {len(nyse)} "
      f"(vs {len(us_2024)} US federal days)")
assert len(nyse) < len(us_2024)

print("\nOK — holidays computed from rules, per jurisdiction, with a basis.")
