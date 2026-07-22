"""Ratchet: every decree rule vacanza/holidays 0.101 still publishes for 2026
must carry a 2026 date in its own ``holiday_data/*.tab`` row.

Context
-------
Every ``decree`` rule (a movable/lunar/estimated-date holiday with no
closed-form rule, tabulated as explicit per-year dates) was originally
populated for 2024-2025 only, leaving jurisdiction holiday lookups and
business-day counting silently wrong for 2026-2027. The ``.tab`` data was
extended (in the same change as this test) to source 2026/2027 dates
directly from vacanza/holidays 0.101 -- the same reference package the
``.tab`` files already cite as their source of truth -- matching each row by
its own ``name`` column against that package's per-country/per-market
output.

Rather than a static, hand-maintained skip list (which would silently rot as
vacanza's own data changes release to release), this ratchet re-derives,
live, whether vacanza actually has a 2026 rendering matching each row's name
today. A row is only allowed to stay 2026-silent if this re-derivation
independently agrees vacanza has nothing to offer it -- so the test fails
loudly the day vacanza adds a forecast for a rule we haven't picked up, and
also fails if the matching logic regresses. A small ``_SKIP`` still covers
the handful of cases independently confirmed to be permanent (categories a
country's vacanza class does not model at all, so no future release can add
data for it) -- documented per entry, not a blanket exemption.

Spot-verified by hand against independently known 2026 dates (cross-checked
against public references, not just vacanza's own output) before trusting
the bulk mechanical extraction:
  * Chinese New Year / Tahun Baru Imlek / Spring Festival 2026-02-17
    (cn.tab "Chunjie" via calendar_date; id.tab "Tahun Baru Imlek" decree row;
    xshg.tab "Spring Festival" decree row -- all three independently land on
    2026-02-17).
  * Diwali (Deepavali) 2026-11-08 (in.tab "Diwali (Deepavali)" decree row).
  * Eid al-Fitr ~2026-03-20 (ae.tab "عيد الفطر" decree row lands 2026-03-20;
    az.tab "Ramazan bayrami (1)" decree row also lands 2026-03-20).
  * Hari Suci Nyepi (Balinese New Year) 2026-03-19 (id.tab decree row).
  * US Election Day (biennial) 2026-11-03 -- pre-existing in the row before
    this extraction, confirmed to already carry the correct 2026 date.
  * Songkran (Thai New Year) 2026-04-13..04-15 (th.tab decree row, 3-day
    cluster).
  * Nauryz meiramy 2026-03-21..03-23 (kz.tab decree row).
  * Ramazan bayrami (2) 2026-03-21 (az.tab, second day of the same cluster,
    positionally matched against vacanza's day-2 occurrence).
  * "San Jorge/Dia de Aragon" 2026-04-23 (es.tab ES-AR regional decree row).
"""
import os
import re
from collections import defaultdict

import holidays
import pytest

from chronologia import load_calendar
from chronologia.civil_holidays import DecreeTableRule, _DATA_DIR

_FINANCIAL_MARKETS = {"XNYS", "XNAS", "XMEX", "XBOM", "XHKG", "XSHG", "XK",
                      "XTSE", "XSWX", "XETR", "XCME", "XECB"}
_VACANZA_CATS = {"bank": "BANK", "government": "GOVERNMENT", "school": "SCHOOL",
                 "optional": "OPTIONAL", "half_day": "HALF_DAY",
                 "unofficial": "UNOFFICIAL", "de_facto": "DE_FACTO",
                 "christian": "CHRISTIAN", "catholic": "CATHOLIC",
                 "orthodox": "ORTHODOX", "hebrew": "HEBREW", "islamic": "ISLAMIC",
                 "hindu": "HINDU", "sabian": "SABIAN", "yazidi": "YAZIDI"}
_DELIM = holidays.constants.HOLIDAY_NAME_DELIMITER
_TRAILING_PAREN = re.compile(r"^(.*)\s\([^()]*\)$")
_NUMBERED = re.compile(r"^(.*)\s\((\d+)\)$")
_BILINGUAL_PART = re.compile(r"^(\w+):(.*)$")

#: (country, subdiv, name) -> justification for staying 2026-silent even
#: though this test's own live re-derivation cannot independently confirm it
#: (usually because the confirmation itself needs the same category-support
#: probe that already made the row unmatchable, so it is documented instead
#: of re-derived to avoid circular reasoning).
_SKIP = {
    ("AT", None, "Karfreitag"):
        "AT's vacanza class has no BANK category at all "
        "(ValueError: Category is not supported: BANK) -- Good Friday is "
        "bank-only in AT, so no category combination yields it.",
    ("BA", "BA-BIH", "Ramazanski Bajram"):
        "vacanza publishes BA's Islamic feasts for forecast years only "
        "under the '(procijenjeno)' estimated name; the unannotated row "
        "exists solely for the officially-confirmed 2024/2025 dates and "
        "the estimated sibling row carries 2026/2027.",
    ("BA", "BA-SRP", "Ramazanski Bajram"):
        "same as BA-BIH: forecast years live on the '(procijenjeno)' "
        "sibling row.",
}


def _has_2026(dates_by_year):
    return 2026 in dates_by_year


def _get_source(jurisdiction, lang, subdiv, categories, years=(2026, 2027)):
    kwargs = {"years": list(years)}
    if lang:
        kwargs["language"] = lang
    if subdiv:
        kwargs["subdiv"] = subdiv.split("-", 1)[1] if "-" in subdiv else subdiv
    cats = [_VACANZA_CATS[c] for c in categories if c in _VACANZA_CATS]

    def _call(use_cats):
        kw = dict(kwargs)
        if use_cats and cats:
            kw["categories"] = tuple(cats)
        fn = (holidays.financial_holidays if jurisdiction in _FINANCIAL_MARKETS
              else holidays.country_holidays)
        return fn(jurisdiction, **kw)

    try:
        return _call(True)
    except Exception:
        try:
            return _call(False)
        except Exception:
            return None


def _name_map(src):
    m = defaultdict(list)
    for d, name in src.items():
        for n in name.split(_DELIM):
            m[n].append((d.year, d.month, d.day))
    return m


def _detect_language(jurisdiction, known_names):
    try:
        cls = getattr(holidays, jurisdiction)
    except AttributeError:
        return None
    best_lang, best_score = None, -1
    for cand in [None] + list(getattr(cls, "supported_languages", ())):
        try:
            kwargs = {"years": [2024, 2025]}
            if cand:
                kwargs["language"] = cand
            src = holidays.country_holidays(jurisdiction, **kwargs)
        except Exception:
            continue
        names = set()
        for d, n in src.items():
            names.update(n.split(_DELIM))
        score = len(known_names & names)
        if score > best_score:
            best_score, best_lang = score, cand
    return best_lang


def _vacanza_has_2026_for(jurisdiction, subdiv, categories, name, known_names):
    """Best-effort live re-derivation: does vacanza 0.101 publish a 2026
    date matching this decree row's name today? Mirrors the extraction
    matcher (exact / numbered-cluster / paren-stripped-annotation / bilingual
    fallbacks) closely enough to answer "yes" whenever the original
    extraction pass would have, without needing a hand-maintained mirror of
    its full unmatched list."""
    lang = None
    if jurisdiction not in _FINANCIAL_MARKETS:
        lang = _detect_language(jurisdiction, known_names)

    def _try(nm):
        src = _get_source(jurisdiction, lang, subdiv, categories)
        if src is None:
            return False
        exact = _name_map(src)
        num_m = _NUMBERED.match(nm)
        if num_m:
            base, idx = num_m.group(1), int(num_m.group(2))
            cands = sorted(d for d in exact.get(base, []) if d[0] == 2026)
            return len(cands) >= idx
        if nm in exact and any(d[0] == 2026 for d in exact[nm]):
            return True
        norm = defaultdict(list)
        for k, ds in exact.items():
            mm = _TRAILING_PAREN.match(k)
            if mm:
                norm[mm.group(1)].extend(ds)
        return any(d[0] == 2026 for d in norm.get(nm, []))

    if " ;; " in name:
        return any(
            (pm := _BILINGUAL_PART.match(part)) and _try(pm.group(2))
            for part in name.split(" ;; ")
        )
    return _try(name)


def _decree_row_params():
    out = []
    for fn in sorted(os.listdir(_DATA_DIR)):
        if not fn.endswith(".tab"):
            continue
        cal = load_calendar(os.path.join(_DATA_DIR, fn))
        known_names = {r.name for r in cal.rules}
        for rule in cal.rules:
            if not isinstance(rule.kind, DecreeTableRule):
                continue
            years = {y for (y, _) in rule.kind.dates}
            if 2024 not in years and 2025 not in years:
                continue  # historical one-off predating this scheme
            out.append((cal.jurisdiction.upper(), rule.subdiv, rule.name,
                        2026 in years, tuple(sorted(rule.categories)),
                        frozenset(known_names)))
    return out


@pytest.mark.parametrize("country,subdiv,name,has_2026,categories,known_names",
                          _decree_row_params())
def test_decree_2024_2025_row_has_2026(country, subdiv, name, has_2026,
                                        categories, known_names):
    """Every 2024/2025-tabulated decree row must carry 2026, unless vacanza
    itself has nothing to offer it (independently re-checked live) or it is
    in the documented, permanently-justified ``_SKIP`` list."""
    if has_2026:
        return
    if (country, subdiv, name) in _SKIP:
        return
    assert not _vacanza_has_2026_for(country, subdiv, categories, name,
                                      known_names), (
        f"{country}/{subdiv}/{name!r}: vacanza/holidays 0.101 now publishes "
        f"a 2026 date for this rule but the .tab row wasn't extended -- "
        f"add it")
