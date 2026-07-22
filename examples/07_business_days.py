"""07 — Counting business days, honestly.

Run it with::

    python examples/07_business_days.py

A **business day** (or working day) is a weekday that is not a public holiday.
There is no single worldwide definition — which days are holidays depends on
the **jurisdiction** — so the library does not ship a black-box
"add_business_days". Instead it gives you the honest ingredient,
``is_civil_holiday``, and you compose the policy you actually want. This
example shows that composition in a dozen lines.
"""
from datetime import date, timedelta

from chronologia import is_civil_holiday


def is_business_day(day, jurisdiction):
    """A weekday (Mon-Fri) that is not a public holiday in ``jurisdiction``."""
    if day.weekday() >= 5:          # 5 = Saturday, 6 = Sunday
        return False
    return not is_civil_holiday(day, jurisdiction)


def business_days_between(start, end, jurisdiction):
    """Count business days in the half-open range [start, end)."""
    count, day = 0, start
    while day < end:
        if is_business_day(day, jurisdiction):
            count += 1
        day += timedelta(days=1)
    return count


# The US Independence Day week: July 4th 2024 is a Thursday holiday.
print("Business days, US, week of 2024-07-01 .. 2024-07-08:")
for d in range(1, 8):
    day = date(2024, 7, d)
    tag = "business day" if is_business_day(day, "US") else "off"
    print(f"  {day} {day:%a}  {tag}")

# Mon Tue Wed (work) / Thu = July 4th holiday / Fri (work) / Sat Sun (weekend).
count = business_days_between(date(2024, 7, 1), date(2024, 7, 8), "US")
print("\nBusiness days that week:", count)
assert count == 4

print("\nOK — a working-day policy composed from the library's holiday facts.")
