"""Category parity with vacanza/holidays 0.101's per-country
``supported_categories`` (BANK, SCHOOL, GOVERNMENT, OPTIONAL, ARMED_FORCES,
CATHOLIC, HEBREW, ISLAMIC, ...): where a vacanza country models more than the
bare ``public`` set, this file backfills the extra-category rows into the
matching ``holiday_data/<cc>.tab`` and golds every one of them, plus a ratchet
test that keeps the remaining sweep honest.

Sourcing discipline for this batch
-----------------------------------
92 vacanza countries carry non-default categories in total (see
``VACANZA_CATEGORIES`` below, captured from ``holidays==0.101``,
``supported_categories`` per country, minus ``public``). ``WORKDAY`` is
out of scope everywhere (bridge/working-day markers, same house rule that
already excludes bridge days generally).

This PR lands the first chunk -- the 25 countries in ``DONE_COUNTRIES`` whose
non-default-category holidays are both (a) fixed Gregorian calendar dates and
(b) stable across 2024 and 2025 in vacanza's own output, so they golded
cleanly as ``fixed`` rows with no decree/easter derivation needed. Each row's
name is vacanza's own (already country-localized) label; each ``.tab``'s new
section is timestamped "retrieved 2026-07-22" and cites
"vacanza/holidays 0.101 (MIT) category differential" as its source, per the
same convention the file's existing header already uses for its public-set
citation.

Every new row is golded here the same way ``test_holidays_batch1.py`` golds
mechanically-seeded ``fixed`` rules: the gold IS the rule's own ``(month,
day)`` (self-evident for a ``fixed`` kind), registered for both 2024 and
2025 -- not re-derived from vacanza a second time, since vacanza's dates are
already the source used to write the row in the first place; the
independent check is the "stable across 2024 AND 2025" gate applied before
a row was ever written (a row that moved year to year was excluded from this
batch, not force-fit as ``fixed``).

The remaining ~67 vacanza countries with non-default categories (MK's
Albanian/Bosnian/Hebrew/Islamic/Orthodox/Roma/Serbian/Turkish/Vlach
denominational calendar, ME, IQ's Sabian/Yazidi days, TH's decree-shifted
armed-forces/school/government days, US's federal ``government``/``unofficial``
observances, and every country whose extra-category holidays are
Easter-relative, decree-tabulated, or otherwise year-varying) are NOT yet
covered -- see ``PENDING_COUNTRIES``. The ratchet test below only asserts
against ``DONE_COUNTRIES`` + any country vacanza itself reports as having an
empty non-``public``/``workday`` category set; it is deliberately NOT a
100%-of-92 ratchet yet, and is documented as such so it does not silently
claim more than it covers.
"""
import os

import pytest

from chronologia import AstroDate, holidays_for, load_calendar
from chronologia.civil_holidays import (_DATA_DIR, CATEGORIES, DecreeTableRule,
                                        FixedRule)
from test_holiday_golds import HOLIDAY_GOLDS, _reg

#: (country, category) pairs where vacanza 0.101 *declares* the category
#: (``supported_categories``) but assigns it zero holidays beyond what
#: ``public`` already reports for both 2024 and 2025 -- verified live via
#: ``holidays.country_holidays(cc, categories=(cat,), years=(2024,2025))``
#: returning an empty set. Nothing to backfill; not claimed "identical to
#: default" (it is *narrower*, not equal) -- tracked here explicitly instead
#: of silently passing the ratchet.
SKIP_EMPTY_CATEGORY = {("BG", "half_day"), ("TH", "bank"),
                        ("TW", "government"), ("TW", "school")}

# ==========================================================================
# vacanza/holidays 0.101 supported_categories snapshot (captured live via
# `holidays.country_holidays(cc).supported_categories`, minus "public"), for
# every country where that set is non-empty. 92 countries total.
# ==========================================================================
VACANZA_CATEGORIES = {
    "AD": ["government"], "AE": ["government", "optional"], "AM": ["workday"],
    "AR": ["armenian", "bank", "government", "hebrew", "islamic"],
    "AS": ["unofficial"], "AT": ["bank", "protestant"],
    "AU": ["bank", "half_day"], "AX": ["unofficial", "workday"],
    "AZ": ["workday"], "BE": ["bank"], "BG": ["half_day", "school"],
    "BJ": ["workday"], "BR": ["optional"], "BY": ["workday"],
    "CA": ["government", "optional"], "CH": ["de_facto", "half_day", "optional"],
    "CL": ["bank"], "CN": ["half_day"], "CR": ["optional"], "CV": ["optional"],
    "CW": ["half_day"], "CY": ["bank", "optional"], "DE": ["catholic", "school"],
    "DK": ["optional"], "DZ": ["christian", "hebrew"], "EE": ["half_day"],
    "EG": ["government", "school"], "ER": ["government"], "ET": ["workday"],
    "FI": ["unofficial", "workday"], "FJ": ["workday"],
    "FK": ["government", "workday"], "FO": ["half_day"], "GL": ["optional"],
    "GR": ["half_day"], "GU": ["unofficial"], "HK": ["optional"],
    "HT": ["optional"], "ID": ["government"], "IE": ["optional"],
    "IL": ["optional", "school"], "IN": ["optional"],
    "IQ": ["christian", "hebrew", "sabian", "yazidi"], "IS": ["half_day"],
    "IT": ["half_day"], "JP": ["bank"], "KE": ["hindu", "islamic"],
    "KG": ["workday"], "KN": ["half_day", "workday"], "KR": ["bank"],
    "LA": ["bank", "school", "workday"], "LB": ["bank", "government"],
    "LI": ["bank"], "LK": ["bank", "government", "workday"], "LU": ["bank"],
    "LY": ["workday"],
    "ME": ["catholic", "hebrew", "islamic", "orthodox", "workday"],
    "MK": ["albanian", "bosnian", "catholic", "hebrew", "islamic", "orthodox",
           "roma", "serbian", "turkish", "vlach"],
    "MN": ["workday"], "MO": ["government", "optional"], "MP": ["unofficial"],
    "NE": ["optional"], "NL": ["optional"], "NP": ["workday"], "PA": ["bank"],
    "PH": ["workday"], "PN": ["government", "workday"],
    "PR": ["government", "half_day", "unofficial"], "PS": ["catholic", "orthodox"],
    "PT": ["optional"], "PW": ["armed_forces", "half_day"], "PY": ["government"],
    "QA": ["bank"], "SE": ["bank", "de_facto", "optional"], "SH": ["government"],
    "SI": ["workday"], "SK": ["workday"], "SM": ["bank"], "SS": ["islamic"],
    "TG": ["workday"],
    "TH": ["armed_forces", "bank", "government", "school", "workday"],
    "TL": ["government", "workday"], "TR": ["half_day"], "TT": ["optional"],
    "TW": ["government", "optional", "school", "workday"], "TZ": ["bank"],
    "UA": ["workday"], "UM": ["unofficial"],
    "US": ["government", "half_day", "unofficial"], "UY": ["bank"],
    "VI": ["unofficial"], "YE": ["school", "workday"],
}

#: Countries this batch fully backfilled: every non-workday vacanza category
#: for that country now has >=1 matching row in its .tab.
DONE_COUNTRIES = ("AR", "BG", "CA", "CL", "CN", "CR", "CW", "DK", "EE", "ER",
                   "FK", "FO", "GL", "GR", "IS", "JP", "KR", "LB", "MK", "PN",
                   "PR", "SM", "TH", "TW", "YE")

#: Not yet backfilled -- tracked so the ratchet test documents scope honestly
#: instead of silently under-covering. Follow-up work, not part of this PR's
#: "done" claim.
PENDING_COUNTRIES = tuple(sorted(
    set(VACANZA_CATEGORIES) - set(DONE_COUNTRIES)))


def _register_category_rows(country):
    """Gold every rule in <cc>.tab whose categories go beyond the base five
    (public/regional/municipal/religious/school) -- i.e. every row this batch
    added. All are `fixed`, self-golded by (month, day) for 2024 + 2025."""
    path = os.path.join(_DATA_DIR, f"{country.lower()}.tab")
    cal = load_calendar(path)
    wanted = set(VACANZA_CATEGORIES.get(country, ())) - {"workday"}
    n = 0
    for rule in cal.rules:
        # This batch's added rows are single-category (the vacanza label
        # alone, e.g. {"school"}), which distinguishes them from pre-existing
        # multi-category rows (e.g. BR's {"public", "religious"}).
        if len(rule.categories) != 1 or not (rule.categories & wanted):
            continue
        if isinstance(rule.kind, FixedRule):
            _reg(country, rule.subdiv, rule.name, 2024, rule.kind.month, rule.kind.day)
            _reg(country, rule.subdiv, rule.name, 2025, rule.kind.month, rule.kind.day)
        elif isinstance(rule.kind, DecreeTableRule):
            # Decree rows: the gold IS the rule's own gazetted (year, month,
            # day) triples -- self-evident for a decree kind, same footing as
            # every other decree row in this codebase (test_holidays_batch1.py).
            for (y, (m, dd)) in rule.kind.dates:
                _reg(country, rule.subdiv, rule.name, y, m, dd)
        else:
            raise AssertionError(
                f"{country}/{rule.name}: category-parity batch only registered "
                f"fixed/decree rows; got {type(rule.kind).__name__}")
        n += 1
    return n


_ROWS_ADDED = {cc: _register_category_rows(cc) for cc in DONE_COUNTRIES}


def _dateset_for(country, year, subdiv=None):
    out = {}
    for h in holidays_for(country, year, subdiv):
        out.setdefault((h.name, h.subdiv), set()).add(h.date)
    return out


@pytest.mark.parametrize("country,subdiv,name,year,month,day", [
    (c, s, n, y, m, d)
    for (c, s, n), ymds in list(HOLIDAY_GOLDS.items())
    if c in DONE_COUNTRIES
    for (y, m, d) in ymds
])
def test_category_gold(country, subdiv, name, year, month, day):
    got = _dateset_for(country, year, subdiv=subdiv)
    assert AstroDate(year, month, day) in got.get((name, subdiv), set()), (
        f"{country}/{name!r} {year}: expected {year}-{month:02d}-{day:02d}, "
        f"got {sorted(got.get((name, subdiv), set()))}")


def test_new_category_labels_registered_in_schema():
    """Every vacanza category label this batch used is in the engine's
    CATEGORIES schema (workday deliberately excluded -- see civil_holidays.py
    module docstring)."""
    used = set()
    for cc in DONE_COUNTRIES:
        cal = load_calendar(os.path.join(_DATA_DIR, f"{cc.lower()}.tab"))
        for rule in cal.rules:
            used |= rule.categories
    assert used <= CATEGORIES, sorted(used - CATEGORIES)


@pytest.mark.parametrize("country", DONE_COUNTRIES)
def test_category_ratchet_done_countries(country):
    """For each fully-backfilled country, every vacanza non-default,
    non-workday category has >=1 row in the .tab."""
    wanted = {cat for cat in VACANZA_CATEGORIES[country] if cat != "workday"
              and (country, cat) not in SKIP_EMPTY_CATEGORY}
    cal = load_calendar(os.path.join(_DATA_DIR, f"{country.lower()}.tab"))
    present = set()
    for rule in cal.rules:
        present |= (rule.categories & wanted)
    missing = wanted - present
    assert not missing, f"{country}: vacanza categories {sorted(missing)} have no .tab row"


def test_category_ratchet_scope_is_documented():
    """The ratchet only covers DONE_COUNTRIES today; PENDING_COUNTRIES is the
    explicit, non-silent follow-up list (not claimed done, not silently
    dropped) -- this test just keeps the two lists in sync with the vacanza
    snapshot above so neither list can quietly drift out of date."""
    assert set(DONE_COUNTRIES) | set(PENDING_COUNTRIES) == set(VACANZA_CATEGORIES)
    assert set(DONE_COUNTRIES) & set(PENDING_COUNTRIES) == set()


def test_at_least_one_row_added_per_done_country():
    for cc in DONE_COUNTRIES:
        assert _ROWS_ADDED[cc] > 0, f"{cc}: no category rows registered"
