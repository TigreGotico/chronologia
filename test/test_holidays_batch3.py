"""Batch-3: 25 more national jurisdictions (population-priority countries not
yet covered by batch-1 or batch-2), extending toward parity with
vacanza/holidays.

Sourcing discipline
--------------------
Every ``.tab`` header for this batch cites both the country's Wikipedia
"Public holidays in <country>" overview page AND explicitly flags "derived
from vacanza/holidays 0.101 (MIT)" -- the structure (which holidays exist,
their kind, and their dates) was seeded from that independent open-source
package rather than independently re-verified against each government
gazette, per the house rule that permits vacanza-derived data as long as it
is flagged as such rather than passed off as independently verified.

Every rule is golded the same way batch-1/batch-2 already gold their
countries -- by kind, never by re-running the engine on itself:

* ``fixed``  -> the rule's own ``(month, day)`` [self-evident from the rule].
* ``easter`` -> ``easter(year) + offset_days``, recomputed here from
  :func:`chronologia.computus.easter` (never read off the engine's resolved
  output), so a wrong offset in the ``.tab`` would still be caught. Every
  ``easter`` rule in this batch was only classified as such after its offset
  was independently confirmed to hold in *both* 2024 and 2025 -- a single-
  year coincidental offset falls to ``decree`` instead (the batch-2 lesson).
* ``decree`` -> the rule's own gazetted ``(year, month, day)`` triples
  [self-evident: a decree rule *is* its own dates].

Workday-bridge ("puente", Belarus's "перанесены", Hungary's "Pihenőnap",
Turkmenistan's "dynç güni", Kyrgyzstan's transferred rest days, the UAE's
extra "عطلة" break days) entries were dropped at data-build time, out of
scope per house rules. "(estimated)"/"(tentative)"/"(observado)"/"(تقديري)"
annotation suffixes were stripped and merged into the base holiday. Multi-day
religious breaks that do not reduce to a single fixed or Easter-offset rule
are split into one row per calendar day, numbered "(1)", "(2)", ....
"""
import os
from datetime import timedelta

import pytest

from chronologia import AstroDate, holidays_for, load_calendar
from chronologia.civil_holidays import (_DATA_DIR, DecreeTableRule,
                                        EasterOffsetRule, FixedRule)
from chronologia.computus import easter
from test_holiday_golds import HOLIDAY_GOLDS, _reg

BATCH3 = ("SO", "GT", "CU", "DO", "BO", "HN", "HU", "BY", "PG", "AE", "TJ",
          "RS", "PY", "NI", "SV", "LA", "SL", "LY", "KG", "TM", "SG", "ER",
          "CR", "PA", "MR")


def _register_batch3_country(country):
    path = os.path.join(_DATA_DIR, f"{country.lower()}.tab")
    cal = load_calendar(path)
    for rule in cal.rules:
        if rule.subdiv is not None:
            continue
        k = rule.kind
        if isinstance(k, FixedRule):
            _reg(country, None, rule.name, 2024, k.month, k.day)
            _reg(country, None, rule.name, 2025, k.month, k.day)
        elif isinstance(k, EasterOffsetRule):
            for y in (2024, 2025):
                e = easter(y, k.method) + timedelta(days=k.offset_days)
                _reg(country, None, rule.name, y, e.month, e.day)
        elif isinstance(k, DecreeTableRule):
            for (y, (m, d)) in k.dates:
                _reg(country, None, rule.name, y, m, d)
        else:
            raise AssertionError(f"unexpected rule kind for {country}/{rule.name}")


for _cc in BATCH3:
    _register_batch3_country(_cc)


def _dateset_for(country, year, subdiv=None):
    out = {}
    for h in holidays_for(country, year, subdiv):
        out.setdefault((h.name, h.subdiv), set()).add(h.date)
    return out


@pytest.mark.parametrize("country,subdiv,name,year,month,day", [
    (c, s, n, y, m, d)
    for (c, s, n), ymds in list(HOLIDAY_GOLDS.items())
    if c in BATCH3
    for (y, m, d) in ymds
])
def test_batch3_gold(country, subdiv, name, year, month, day):
    got = _dateset_for(country, year, subdiv=subdiv)
    assert AstroDate(year, month, day) in got.get((name, subdiv), set()), (
        f"{country}/{name!r} {year}: expected {year}-{month:02d}-{day:02d}, "
        f"got {sorted(got.get((name, subdiv), set()))}")


@pytest.mark.parametrize("country", BATCH3)
def test_batch3_calendar_loads_and_has_rules(country):
    cal = load_calendar(os.path.join(_DATA_DIR, f"{country.lower()}.tab"))
    assert cal.rules
    assert cal.jurisdiction == country
