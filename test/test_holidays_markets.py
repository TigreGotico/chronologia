"""Financial-market holiday calendars: XECB (ECB/TARGET2), XNYS (NYSE) and
IFEU (ICE Futures Europe) -- matching vacanza/holidays 0.101's
``list_supported_financial()`` market support.

These jurisdictions are FINANCIAL MARKETS, not ISO-3166-1 countries: an
institution's own trading/settlement calendar rather than a national civil
calendar. English is correct as their primary name -- each institution
(the ECB, the NYSE, ICE) publishes its own calendar in English, so this is
not a translation-fallback situation the way a non-English country's ``.tab``
would be.

vacanza registers several of these under more than one short code for the
identical calendar (``ECB``/``TAR`` both mean the TARGET2 settlement system;
``NYSE`` is the New York Stock Exchange's own ticker mnemonic). Rather than
ship duplicate ``.tab`` files, ``chronologia.civil_holidays.MARKET_ALIASES``
resolves the short codes onto the canonical file (``XECB``/``XNYS``) that
owns the rules -- exercised directly below.

Sourcing discipline
--------------------
Every ``.tab`` header cites the exchange/institution's own primary published
rules PDF or reference page, and explicitly flags "derived from
vacanza/holidays 0.101 (MIT)" -- the same house rule already applied to every
national jurisdiction batch. Every rule was cross-checked against vacanza
0.101's ``financial_holidays()`` output for 2024, 2025 AND 2026 (2026 is the
first year in this window an ``observed`` shift actually fires for either
market: NYSE's Independence Day, nominally Saturday 4 Jul 2026, is observed
Friday 3 Jul 2026).

Every rule is golded independently of the engine's own resolution machinery:

* ``fixed``       -> the rule's own ``(month, day)``, self-evident.
* ``nth_weekday`` -> recomputed here with plain ``datetime``/weekday
  arithmetic (never by reusing :mod:`chronologia.recurrence`), so a bug in
  the RRULE engine would still be caught.
* ``easter``      -> ``easter(year, "gregorian") + offset_days``, recomputed
  from :func:`chronologia.computus.easter` (the house standard already used
  by every other easter-offset gold in this suite).
* ``observed``    -> the nominal date is independently shifted by hand
  (Saturday -> preceding Friday, Sunday -> following Monday for the ``us``
  policy; Sunday -> following Monday only for IFEU's ``sun_mon`` policy) and
  asserted against a year where the shift actually fires.
"""
import os
from datetime import timedelta

import pytest

from chronologia import AstroDate, holidays_for, load_calendar
from chronologia.civil_holidays import MARKET_ALIASES, _DATA_DIR
from chronologia.computus import easter
from test_holiday_golds import _reg

MARKETS = ("XECB", "XNYS", "IFEU")


# ==========================================================================
# Register every rule's 2024/2025 dates into the shared HOLIDAY_GOLDS
# registry (test_holiday_golds._every_tab_rule_key() enforces that every
# .tab-shipped rule has a gold; these are the same dates asserted, kind by
# kind, in the tests below -- registered here so that cross-suite ratchet
# also covers these three new markets).
# ==========================================================================
for _year, (_gf, _em) in ((2024, ((3, 29), (4, 1))), (2025, ((4, 18), (4, 21)))):
    _reg("XECB", None, "New Year's Day", _year, 1, 1)
    _reg("XECB", None, "Good Friday", _year, *_gf)
    _reg("XECB", None, "Easter Monday", _year, *_em)
    _reg("XECB", None, "Labour Day", _year, 5, 1)
    _reg("XECB", None, "Christmas Day", _year, 12, 25)
    _reg("XECB", None, "Christmas Holiday", _year, 12, 26)

_reg("IFEU", None, "New Year's Day", 2024, 1, 1)
_reg("IFEU", None, "New Year's Day", 2025, 1, 1)
_reg("IFEU", None, "Good Friday", 2024, 3, 29)
_reg("IFEU", None, "Good Friday", 2025, 4, 18)
_reg("IFEU", None, "Christmas Day", 2024, 12, 25)
_reg("IFEU", None, "Christmas Day", 2025, 12, 25)

_reg("XNYS", None, "New Year's Day", 2024, 1, 1)
_reg("XNYS", None, "New Year's Day", 2025, 1, 1)
_reg("XNYS", None, "Martin Luther King Jr. Day", 2024, 1, 15)
_reg("XNYS", None, "Martin Luther King Jr. Day", 2025, 1, 20)
_reg("XNYS", None, "Washington's Birthday", 2024, 2, 19)
_reg("XNYS", None, "Washington's Birthday", 2025, 2, 17)
_reg("XNYS", None, "Good Friday", 2024, 3, 29)
_reg("XNYS", None, "Good Friday", 2025, 4, 18)
_reg("XNYS", None, "Memorial Day", 2024, 5, 27)
_reg("XNYS", None, "Memorial Day", 2025, 5, 26)
_reg("XNYS", None, "Juneteenth National Independence Day", 2024, 6, 19)
_reg("XNYS", None, "Juneteenth National Independence Day", 2025, 6, 19)
_reg("XNYS", None, "Independence Day", 2024, 7, 4)
_reg("XNYS", None, "Independence Day", 2025, 7, 4)
_reg("XNYS", None, "Labor Day", 2024, 9, 2)
_reg("XNYS", None, "Labor Day", 2025, 9, 1)
_reg("XNYS", None, "Thanksgiving Day", 2024, 11, 28)
_reg("XNYS", None, "Thanksgiving Day", 2025, 11, 27)
_reg("XNYS", None, "Christmas Day", 2024, 12, 25)
_reg("XNYS", None, "Christmas Day", 2025, 12, 25)


# ==========================================================================
# Calendar loads and basic shape
# ==========================================================================
@pytest.mark.parametrize("market", MARKETS)
def test_market_calendar_loads_and_has_rules(market):
    cal = load_calendar(os.path.join(_DATA_DIR, f"{market.lower()}.tab"))
    assert cal.rules
    assert cal.jurisdiction == market


def test_market_aliases_resolve_to_shipped_canonical_files():
    for alias, canonical in MARKET_ALIASES.items():
        path = os.path.join(_DATA_DIR, f"{canonical.lower()}.tab")
        assert os.path.exists(path), f"{alias} -> {canonical}: no such .tab"


@pytest.mark.parametrize("alias,canonical", list(MARKET_ALIASES.items()))
def test_alias_and_canonical_produce_identical_holidays(alias, canonical):
    for year in (2024, 2025):
        alias_dates = {(h.name, h.date) for h in holidays_for(alias, year)}
        canon_dates = {(h.name, h.date) for h in holidays_for(canonical, year)}
        assert alias_dates == canon_dates


# ==========================================================================
# In-test independent weekday/easter arithmetic helpers
# ==========================================================================
def _nth_weekday(year, month, n, weekday):
    """The n-th (n=-1 -> last) `weekday` (Mon=0..Sun=6) of `month`/`year`.

    Implemented with plain calendar arithmetic, independent of
    :mod:`chronologia.recurrence`, per the house rule that nth_weekday golds
    must not re-run the engine on itself.
    """
    first = AstroDate(year, month, 1)
    first_wd = first.weekday()
    if n > 0:
        delta = (weekday - first_wd) % 7 + (n - 1) * 7
        return first + timedelta(days=delta)
    # n == -1: last such weekday in the month
    if month == 12:
        next_month = AstroDate(year + 1, 1, 1)
    else:
        next_month = AstroDate(year, month + 1, 1)
    last_day = next_month - timedelta(days=1)
    delta = (last_day.weekday() - weekday) % 7
    return last_day - timedelta(days=delta)


def _us_observed(date):
    """5 U.S.C. 6103: Saturday -> preceding Friday, Sunday -> following Monday."""
    wd = date.weekday()
    if wd == 5:
        return date - timedelta(days=1)
    if wd == 6:
        return date + timedelta(days=1)
    return date


def _sun_mon_observed(date):
    """Sunday -> following Monday; otherwise unshifted."""
    return date + timedelta(days=1) if date.weekday() == 6 else date


def _dates_for(market, year):
    return {h.name: h.date for h in holidays_for(market, year)}


# ==========================================================================
# XECB (European Central Bank / TARGET2) -- fixed + easter offsets, no
# observed shift (TARGET2 simply does not fall on a weekend-adjacent policy;
# vacanza applies none for this market).
# ==========================================================================
@pytest.mark.parametrize("year", [2024, 2025])
def test_xecb_new_years_day(year):
    got = _dates_for("XECB", year)
    assert got["New Year's Day"] == AstroDate(year, 1, 1)


@pytest.mark.parametrize("year", [2024, 2025])
def test_xecb_good_friday(year):
    got = _dates_for("XECB", year)
    expected = easter(year, "gregorian") + timedelta(days=-2)
    assert got["Good Friday"] == expected


@pytest.mark.parametrize("year", [2024, 2025])
def test_xecb_easter_monday(year):
    got = _dates_for("XECB", year)
    expected = easter(year, "gregorian") + timedelta(days=1)
    assert got["Easter Monday"] == expected


@pytest.mark.parametrize("year", [2024, 2025])
def test_xecb_labour_day(year):
    got = _dates_for("XECB", year)
    assert got["Labour Day"] == AstroDate(year, 5, 1)


@pytest.mark.parametrize("year", [2024, 2025])
def test_xecb_christmas_day(year):
    got = _dates_for("XECB", year)
    assert got["Christmas Day"] == AstroDate(year, 12, 25)


@pytest.mark.parametrize("year", [2024, 2025])
def test_xecb_christmas_holiday(year):
    got = _dates_for("XECB", year)
    assert got["Christmas Holiday"] == AstroDate(year, 12, 26)


def test_xecb_six_holidays_per_year():
    for year in (2024, 2025):
        assert len(_dates_for("XECB", year)) == 6


# ==========================================================================
# XNYS (New York Stock Exchange) -- nth_weekday, easter and `us`-observed
# fixed rules.
# ==========================================================================
@pytest.mark.parametrize("year", [2024, 2025, 2026])
def test_xnys_new_years_day_us_observed(year):
    got = _dates_for("XNYS", year)
    expected = _us_observed(AstroDate(year, 1, 1))
    assert got["New Year's Day"] == expected


@pytest.mark.parametrize("year", [2024, 2025, 2026])
def test_xnys_mlk_day_third_monday_january(year):
    got = _dates_for("XNYS", year)
    expected = _nth_weekday(year, 1, 3, 0)
    assert got["Martin Luther King Jr. Day"] == expected


@pytest.mark.parametrize("year", [2024, 2025, 2026])
def test_xnys_washingtons_birthday_third_monday_february(year):
    got = _dates_for("XNYS", year)
    expected = _nth_weekday(year, 2, 3, 0)
    assert got["Washington's Birthday"] == expected


@pytest.mark.parametrize("year", [2024, 2025, 2026])
def test_xnys_good_friday_easter_minus_2(year):
    got = _dates_for("XNYS", year)
    expected = easter(year, "gregorian") + timedelta(days=-2)
    assert got["Good Friday"] == expected


@pytest.mark.parametrize("year", [2024, 2025, 2026])
def test_xnys_memorial_day_last_monday_may(year):
    got = _dates_for("XNYS", year)
    expected = _nth_weekday(year, 5, -1, 0)
    assert got["Memorial Day"] == expected


@pytest.mark.parametrize("year", [2024, 2025, 2026])
def test_xnys_juneteenth_us_observed(year):
    got = _dates_for("XNYS", year)
    expected = _us_observed(AstroDate(year, 6, 19))
    assert got["Juneteenth National Independence Day"] == expected


def test_xnys_juneteenth_absent_before_2022():
    # NYSE only began observing Juneteenth once the 2021 Act took effect;
    # the exchange's own 2021 calendar (a Saturday nominal date that year)
    # carries no Juneteenth closure at all.
    got = _dates_for("XNYS", 2021)
    assert "Juneteenth National Independence Day" not in got


@pytest.mark.parametrize("year", [2024, 2025])
def test_xnys_independence_day_us_observed(year):
    got = _dates_for("XNYS", year)
    expected = _us_observed(AstroDate(year, 7, 4))
    assert got["Independence Day"] == expected


def test_xnys_independence_day_2026_saturday_observed_friday():
    # 4 July 2026 is a Saturday -> observed the preceding Friday, 3 July 2026.
    nominal = AstroDate(2026, 7, 4)
    assert nominal.weekday() == 5   # Saturday, confirms the shift fires
    got = _dates_for("XNYS", 2026)
    assert got["Independence Day"] == AstroDate(2026, 7, 3)


@pytest.mark.parametrize("year", [2024, 2025, 2026])
def test_xnys_labor_day_first_monday_september(year):
    got = _dates_for("XNYS", year)
    expected = _nth_weekday(year, 9, 1, 0)
    assert got["Labor Day"] == expected


@pytest.mark.parametrize("year", [2024, 2025, 2026])
def test_xnys_thanksgiving_fourth_thursday_november(year):
    got = _dates_for("XNYS", year)
    expected = _nth_weekday(year, 11, 4, 3)
    assert got["Thanksgiving Day"] == expected


@pytest.mark.parametrize("year", [2024, 2025])
def test_xnys_christmas_day_us_observed(year):
    got = _dates_for("XNYS", year)
    expected = _us_observed(AstroDate(year, 12, 25))
    assert got["Christmas Day"] == expected


# ==========================================================================
# IFEU (ICE Futures Europe) -- fixed + easter, sun_mon-observed fixed rules.
# ==========================================================================
@pytest.mark.parametrize("year", [2024, 2025])
def test_ifeu_new_years_day_sun_mon_observed(year):
    got = _dates_for("IFEU", year)
    expected = _sun_mon_observed(AstroDate(year, 1, 1))
    assert got["New Year's Day"] == expected


def test_ifeu_new_years_day_2023_sunday_observed_monday():
    # 1 Jan 2023 is a Sunday -> observed the following Monday, 2 Jan 2023
    # (verified against vacanza/holidays 0.101 IFEU output).
    nominal = AstroDate(2023, 1, 1)
    assert nominal.weekday() == 6   # Sunday, confirms the shift fires
    got = _dates_for("IFEU", 2023)
    assert got["New Year's Day"] == AstroDate(2023, 1, 2)


@pytest.mark.parametrize("year", [2024, 2025])
def test_ifeu_good_friday_easter_minus_2(year):
    got = _dates_for("IFEU", year)
    expected = easter(year, "gregorian") + timedelta(days=-2)
    assert got["Good Friday"] == expected


@pytest.mark.parametrize("year", [2024, 2025])
def test_ifeu_christmas_day_sun_mon_observed(year):
    got = _dates_for("IFEU", year)
    expected = _sun_mon_observed(AstroDate(year, 12, 25))
    assert got["Christmas Day"] == expected


def test_ifeu_christmas_day_2022_sunday_observed_monday():
    # 25 Dec 2022 is a Sunday -> observed the following Monday, 26 Dec 2022
    # (verified against vacanza/holidays 0.101 IFEU output).
    nominal = AstroDate(2022, 12, 25)
    assert nominal.weekday() == 6   # Sunday, confirms the shift fires
    got = _dates_for("IFEU", 2022)
    assert got["Christmas Day"] == AstroDate(2022, 12, 26)


def test_ifeu_three_holidays_per_year():
    for year in (2024, 2025):
        assert len(_dates_for("IFEU", year)) == 3


# ==========================================================================
# Completeness ratchet -- every financial market vacanza/holidays 0.101
# supports must resolve to either a shipped .tab file, a MARKET_ALIASES
# entry pointing at one, or a documented SKIP_LIST reason. Mirrors the
# batch-5 country ratchet (test_holidays_batch5.test_catalog_covers_every_
# vacanza_supported_country) at market scope, so the catalog can never
# silently drift out of sync with a future vacanza release.
# ==========================================================================
#: Vacanza-supported financial-market codes not yet modelled here, with the
#: reason -- honest scope, not an oversight. This mission covered the three
#: canonical markets whose rules were spelled out (ECB/TARGET2, NYSE, ICE
#: Futures Europe); the remaining exchanges are tracked for a future batch.
SKIP_LIST = {
    "XMEX": "Bolsa Mexicana de Valores -- not yet modelled, future batch",
    "BMV": "Bolsa Mexicana de Valores alias -- not yet modelled, future batch",
    "XBOM": "Bombay Stock Exchange -- not yet modelled, future batch",
    "BSE": "Bombay Stock Exchange alias -- not yet modelled, future batch",
    "BVMF": "Brasil Bolsa Balcao -- not yet modelled, future batch",
    "B3": "Brasil Bolsa Balcao alias -- not yet modelled, future batch",
    "XCME": "Chicago Mercantile Exchange -- not yet modelled, future batch",
    "CME": "Chicago Mercantile Exchange alias -- not yet modelled, future batch",
    "XETR": "Germany Exchange (Xetra) -- not yet modelled, future batch",
    "XFRA": "Germany Exchange (Frankfurt) -- not yet modelled, future batch",
    "XHKG": "Hong Kong Stock Exchange -- not yet modelled, future batch",
    "HKEX": "Hong Kong Stock Exchange alias -- not yet modelled, future batch",
    "SEHK": "Hong Kong Stock Exchange alias -- not yet modelled, future batch",
    "XJPX": "Japan Exchange Group -- not yet modelled, future batch",
    "JPX": "Japan Exchange Group alias -- not yet modelled, future batch",
    "TSE": "Japan Exchange Group alias -- not yet modelled, future batch",
    "OSE": "Japan Exchange Group alias -- not yet modelled, future batch",
    "XNAS": "Nasdaq -- not yet modelled, future batch",
    "XNSE": "National Stock Exchange of India -- not yet modelled, future batch",
    "NSE": "National Stock Exchange of India alias -- not yet modelled, future batch",
    "XSHG": "Shanghai Stock Exchange -- not yet modelled, future batch",
    "SSE": "Shanghai Stock Exchange alias -- not yet modelled, future batch",
    "XSHE": "Shenzhen Stock Exchange -- not yet modelled, future batch",
    "SZSE": "Shenzhen Stock Exchange alias -- not yet modelled, future batch",
    "XSWX": "SIX Swiss Exchange -- not yet modelled, future batch",
    "SIX": "SIX Swiss Exchange alias -- not yet modelled, future batch",
    "XTSE": "Toronto Stock Exchange -- not yet modelled, future batch",
    "TSX": "Toronto Stock Exchange alias -- not yet modelled, future batch",
}


def test_catalog_covers_every_vacanza_supported_financial_market():
    import holidays as _pkg
    supported = set(_pkg.list_supported_financial())
    shipped = {f[:-4].upper() for f in os.listdir(_DATA_DIR) if f.endswith(".tab")}
    covered = shipped | set(MARKET_ALIASES) | set(SKIP_LIST)
    uncovered = supported - covered
    assert not uncovered, (
        f"vacanza-supported financial markets with neither a .tab file, a "
        f"MARKET_ALIASES entry, nor a documented SKIP_LIST reason: "
        f"{sorted(uncovered)}")


def test_skip_list_entries_are_not_also_shipped_or_aliased():
    shipped = {f[:-4].upper() for f in os.listdir(_DATA_DIR) if f.endswith(".tab")}
    overlap = set(SKIP_LIST) & (shipped | set(MARKET_ALIASES))
    assert not overlap, f"SKIP_LIST entries already covered: {overlap}"
