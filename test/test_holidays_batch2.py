"""Batch-2: 25 more new national jurisdictions (next population-priority
countries not yet covered after batch-1's 65), extending toward parity
with vacanza/holidays.

Sourcing discipline
--------------------
Every ``.tab`` header for this batch cites both the country's Wikipedia
"Public holidays in <country>" overview page AND explicitly flags "derived
from vacanza/holidays 0.101 (MIT)" -- the structure (which holidays exist,
their kind, and their dates) was seeded from that independent open-source
package rather than independently re-verified against each government
gazette, per the house rule that permits vacanza-derived data as long as it
is flagged as such rather than passed off as independently verified. Same
sourcing discipline :mod:`test_holidays_batch1` already documents.

Every rule is golded the same way batch-1's ``_register_batch1_country``
already golds NG/BD/RU/.../RO -- by kind, never by re-running the engine on
itself:

* ``fixed``  -> the rule's own ``(month, day)`` [self-evident from the rule].
* ``easter`` -> ``easter(year) + offset_days``, recomputed here from
  :func:`chronologia.computus.easter` (never read off the engine's resolved
  output), so a wrong offset in the ``.tab`` would still be caught.
* ``decree`` -> the rule's own gazetted ``(year, month, day)`` triples
  [self-evident: a decree rule *is* its own dates].

Classification discipline specific to this batch: an ``easter`` rule was only
minted when the vacanza-observed offset from Easter Sunday was IDENTICAL
across both 2024 and 2025 -- a handful of raw vacanza entries land on an
Easter-offset date in exactly one of the two years by pure coincidence (a
fixed civil holiday whose name got merged with an adjacent movable feast, or
a Islamic/lunar holiday that happens to fall near Easter in a single year);
those were deliberately kept as ``decree`` (tabulated, silent outside
2024-2025) rather than promoted to a spurious every-year Easter-linked rule.
Workday-bridge ("ponte" in the Portuguese-language sources this batch draws
on for AO/MZ -- the same phenomenon Russia/Uzbekistan's "moved" shift days
represent in batch-1) entries were dropped at data-build time, out of scope
per house rules. "(estimated)"/"(tentative)" annotation suffixes on
lunar-calendar names were stripped and merged into the base holiday,
matching ma.tab's existing convention for the same phenomenon.
"""
import os
from datetime import timedelta

import pytest

from chronologia import AstroDate, holidays_for, load_calendar
from chronologia.civil_holidays import (_DATA_DIR, DecreeTableRule,
                                        NearestWeekdayRule,
                                        NthWeekdayRule,
                                        EasterOffsetRule, FixedRule)
from chronologia.computus import easter
from test_holiday_golds import HOLIDAY_GOLDS, _reg

BATCH2 = ("JO", "AO", "MZ", "MG", "CM", "CI", "NE", "LK", "BF", "ML", "KZ",
         "MW", "ZM", "SY", "EC", "SN", "KH", "TD", "ZW", "GN", "RW", "BJ",
         "BI", "TG", "HT")


def _register_batch2_country(country):
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
        elif isinstance(k, (NthWeekdayRule, NearestWeekdayRule)):
            # computable recurrences (converted from horizon-limited decree
            # tables in the DATA-001 fix); evaluate the rule for the same two
            # registration years, same as every other computable kind.
            for y in (2024, 2025):
                for ad, _ in k.observances(y):
                    _reg(country, None, rule.name, y, ad.month, ad.day)
        else:
            raise AssertionError(f"unexpected rule kind for {country}/{rule.name}")


for _cc in BATCH2:
    _register_batch2_country(_cc)


def _dateset_for(country, year, subdiv=None):
    out = {}
    for h in holidays_for(country, year, subdiv):
        out.setdefault((h.name, h.subdiv), set()).add(h.date)
    return out


@pytest.mark.parametrize("country,subdiv,name,year,month,day", [
    (c, s, n, y, m, d)
    for (c, s, n), ymds in list(HOLIDAY_GOLDS.items())
    if c in BATCH2
    for (y, m, d) in ymds
])
def test_batch2_gold(country, subdiv, name, year, month, day):
    got = _dateset_for(country, year, subdiv=subdiv)
    assert AstroDate(year, month, day) in got.get((name, subdiv), set()), (
        f"{country}/{name!r} {year}: expected {year}-{month:02d}-{day:02d}, "
        f"got {sorted(got.get((name, subdiv), set()))}")


@pytest.mark.parametrize("country", BATCH2)
def test_batch2_calendar_loads_and_has_rules(country):
    cal = load_calendar(os.path.join(_DATA_DIR, f"{country.lower()}.tab"))
    assert cal.rules
    assert cal.jurisdiction == country
