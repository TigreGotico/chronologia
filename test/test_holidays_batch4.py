"""Batch-4: 25 more national jurisdictions (population-priority countries not
yet covered by batch-1, batch-2 or batch-3), extending toward parity with
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

Every rule is golded the same way batch-1/2/3 already gold their
countries -- by kind, never by re-running the engine on itself:

* ``fixed``  -> the rule's own ``(month, day)`` [self-evident from the rule].
* ``easter`` -> ``easter(year, method) + offset_days``, recomputed here from
  :func:`chronologia.computus.easter` (never read off the engine's resolved
  output), so a wrong offset in the ``.tab`` would still be caught. Every
  ``easter`` rule in this batch was only classified as such after its offset
  was independently confirmed to hold in *both* 2024 and 2025 -- a single-
  year coincidental offset falls to ``decree`` instead (the batch-2 lesson).
  Orthodox-calendar clusters (Bulgaria, Georgia, Moldova, Bosnia, Albania)
  use the ``julian_gregorian_date`` method.
* ``decree`` -> the rule's own gazetted ``(year, month, day)`` triples
  [self-evident: a decree rule *is* its own dates].

Workday-bridge (Azerbaijan's "İstirahət günü", every "(observed)"/"(müşahidə
olunur)"/"(почивен ден)"/"(ditë pushimi e shtyrë)"/"(補假)" shifted-day
variant, Gabon's ad-hoc "Jour férié" placeholders) entries were dropped at
data-build time, out of scope per house rules. One-off, non-recurring events
(Namibia's two state funerals) were dropped for the same reason; one-off
*election* days (Azerbaijan presidential/municipal, Namibia's general
election) were kept as decree rows, matching the precedent already set by
South Korea's National Assembly election day. "(estimated)"/"(تقديري)"
annotation suffixes were stripped and merged into the base holiday. Multi-day
religious/lunar breaks that do not reduce to a single fixed or Easter-offset
rule are split into one row per calendar day, numbered "(1)", "(2)", ....

Ukraine (UA) was reached in population-priority order but is skipped: its
national holiday calendar has been suspended/altered under martial law since
2022, so this batch does not model it.
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

BATCH4 = ("KP", "TW", "TN", "SS", "AZ", "BG", "CG", "CF", "NZ", "KW", "HR",
          "GE", "MD", "MN", "BA", "LT", "AM", "AL", "JM", "GM", "QA", "NA",
          "BW", "GA", "LS")


def _register_batch4_country(country):
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


for _cc in BATCH4:
    _register_batch4_country(_cc)


def _dateset_for(country, year, subdiv=None):
    out = {}
    for h in holidays_for(country, year, subdiv):
        out.setdefault((h.name, h.subdiv), set()).add(h.date)
    return out


@pytest.mark.parametrize("country,subdiv,name,year,month,day", [
    (c, s, n, y, m, d)
    for (c, s, n), ymds in list(HOLIDAY_GOLDS.items())
    if c in BATCH4
    for (y, m, d) in ymds
])
def test_batch4_gold(country, subdiv, name, year, month, day):
    got = _dateset_for(country, year, subdiv=subdiv)
    assert AstroDate(year, month, day) in got.get((name, subdiv), set()), (
        f"{country}/{name!r} {year}: expected {year}-{month:02d}-{day:02d}, "
        f"got {sorted(got.get((name, subdiv), set()))}")


@pytest.mark.parametrize("country", BATCH4)
def test_batch4_calendar_loads_and_has_rules(country):
    cal = load_calendar(os.path.join(_DATA_DIR, f"{country.lower()}.tab"))
    assert cal.rules
    assert cal.jurisdiction == country
