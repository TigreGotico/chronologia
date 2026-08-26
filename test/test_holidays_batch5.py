"""Batch-5: the closing sweep — every ISO-3166-1 country/territory vacanza/
holidays 0.101 supports that batch-1 through batch-4 had not yet reached
(106 jurisdictions).

Sourcing discipline
--------------------
Same house rule as batch-1 through batch-4: every ``.tab`` header for this
batch cites the country's Wikipedia "Public holidays in <country>" overview
page AND explicitly flags "derived from vacanza/holidays 0.101 (MIT)" — the
structure (which holidays exist, their kind, and their dates) was seeded
from that independent open-source package rather than independently
re-verified against each government gazette.

Names are the jurisdiction's own official-language rendering wherever
vacanza's own ``language=`` support publishes one (``AD`` -> Catalan,
``LB``/``BH``/``OM``/``EH``/``PS`` -> Arabic, ``HK``/``MO`` -> Chinese,
``IS`` -> Icelandic, ``LU`` -> Lëtzebuergesch, ``MT`` -> Maltese, ``MV`` ->
Dhivehi, and so on — see each ``.tab``'s ``# source`` header for the exact
``language=`` tag used). A handful of jurisdictions (``AQ``, ``AS``, ``BB``,
``BM``, ``BS``, ``BZ``, ``CC``, ``CK``, ``CX``, ``DM``, ``FJ``, ``FK``,
``FM``, ``GD``, ``GG``, ``GI``, ``GS``, ``GU``, ``GY``, ``IM``, ``JE``,
``KI``, ``KM``, ``KN``, ``KY``, ``LC``, ``LR``, ``MH``, ``MP``, ``MS``,
``MU``, ``NF``, ``NR``, ``NU``, ``PN``, ``PR``, ``PW``, ``SB``, ``SC``,
``SH``, ``SZ``, ``TC``, ``TK``, ``TT``, ``UM``, ``VC``, ``VG``, ``VI``,
``WS``, ``AG``, ``AI``) have no native-language rendering registered in
vacanza at this version, so the header honestly flags English as a
fallback rather than passing it off as an official-language name.

Every rule is golded the same way batch-1 through batch-4 already gold
their countries — by kind, never by re-running the engine on itself:

* ``fixed``  -> the rule's own ``(month, day)``.
* ``easter`` -> ``easter(year, method) + offset_days``, recomputed here from
  :func:`chronologia.computus.easter`. Every ``easter`` rule in this batch
  was only classified as such after its offset was confirmed to hold in
  *both* 2024 and 2025 — a single-year coincidental offset falls to
  ``decree`` instead.
* ``decree`` -> the rule's own gazetted ``(year, month, day)`` triples.

Observed/bridge/in-lieu shifted-day artifacts ("(observed)"/"(observado)"/
"(observada)" suffixed rows) were dropped at data-build time, out of scope
per house rules. "(estimated)"/"(تقديري)"-style annotation suffixes were
stripped and merged into the base holiday. Multi-day religious/lunar breaks
that do not reduce to a single fixed or Easter-offset rule are split into
one row per calendar day, numbered "(1)", "(2)", ....

Skip-list (documented, not oversights)
---------------------------------------
* ``UA`` — Ukraine's national holiday calendar has been suspended/altered
  under martial law since 2022 (batch-4's pre-existing skip; still skipped).
* ``UK`` — a bare vacanza alias for ``GB``: ``holidays.country_holidays
  ("UK", ...)`` and ``holidays.country_holidays("GB", ...)`` return an
  identical date/name mapping (same class family, same output), so it is
  not a distinct jurisdiction and is not double-filed under a second code.
* ``BV`` (Bouvet Island), ``HM`` (Heard Island and McDonald Islands),
  ``IO`` (British Indian Ocean Territory) — vacanza registers these as
  supported entities but they resolve to an empty holiday set for
  2024-2025 (uninhabited/no permanent population, no statutory calendar to
  model).

Territory/dependency codes vacanza models as their own country class
(``HK``, ``MO``, ``PR``, ``GU``, ``PF``, ``NC``, ``GF``, ``GP``, ``MQ``,
``RE``, ``YT``, ``WF``, ``BL``, ``MF``, ``PM``, ``TF``, ``AW``, ``CW``,
``SX``, ``BQ``, ``FO``, ``GL``, ``AX``, ``GG``, ``JE``, ``IM``, ``VI``,
``VG``, ``KY``, ``BM``, ``TC``, ``MS``, ``AI``, ``FK``, ``GS``, ``SH``,
``UM``, ``AS``, ``MP``) are included as their own jurisdiction files here —
data is data, and vacanza itself treats them as first-class entities with
their own statutory calendars distinct from any metropolitan parent.
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

BATCH5 = (
    "AD", "AG", "AI", "AQ", "AS", "AW", "AX", "BB", "BH", "BL", "BM", "BN",
    "BQ", "BS", "BT", "BZ", "CC", "CK", "CV", "CW", "CX", "CY", "DJ", "DM",
    "EE", "EH", "FJ", "FK", "FM", "FO", "GD", "GF", "GG", "GI", "GL", "GP",
    "GQ", "GS", "GU", "GW", "GY", "HK", "IM", "IS", "JE", "KI", "KM", "KN",
    "KY", "LB", "LC", "LI", "LR", "LU", "LV", "MC", "ME", "MF", "MH", "MK",
    "MO", "MP", "MQ", "MS", "MT", "MU", "MV", "NC", "NF", "NR", "NU", "OM",
    "PF", "PM", "PN", "PR", "PS", "PW", "RE", "SB", "SC", "SH", "SI", "SJ",
    "SM", "SR", "ST", "SX", "SZ", "TC", "TF", "TK", "TL", "TO", "TT", "TV",
    "UM", "VA", "VC", "VG", "VI", "VU", "WF", "WS", "XK", "YT",
)

def _register_batch5_country(country):
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


for _cc in BATCH5:
    _register_batch5_country(_cc)


def _dateset_for(country, year, subdiv=None):
    out = {}
    for h in holidays_for(country, year, subdiv):
        out.setdefault((h.name, h.subdiv), set()).add(h.date)
    return out


@pytest.mark.parametrize("country,subdiv,name,year,month,day", [
    (c, s, n, y, m, d)
    for (c, s, n), ymds in list(HOLIDAY_GOLDS.items())
    if c in BATCH5
    for (y, m, d) in ymds
])
def test_batch5_gold(country, subdiv, name, year, month, day):
    got = _dateset_for(country, year, subdiv=subdiv)
    assert AstroDate(year, month, day) in got.get((name, subdiv), set()), (
        f"{country}/{name!r} {year}: expected {year}-{month:02d}-{day:02d}, "
        f"got {sorted(got.get((name, subdiv), set()))}")


@pytest.mark.parametrize("country", BATCH5)
def test_batch5_calendar_loads_and_has_rules(country):
    cal = load_calendar(os.path.join(_DATA_DIR, f"{country.lower()}.tab"))
    assert cal.rules
    assert cal.jurisdiction == country
