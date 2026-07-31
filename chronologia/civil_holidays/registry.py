"""Query/registry API — the lazy per-jurisdiction cache and public entry points.

:func:`holidays_for` / :func:`is_civil_holiday` are the primary public entry
points; :func:`coverage` exposes the decree-table horizon so a caller can tell
an honest gap from a fabricated date. Calendars are parsed lazily from
``holiday_data/<code>.tab`` and cached per jurisdiction (with a market-code
alias layer in front of the path resolution).
"""
from __future__ import annotations

import os
import threading
from typing import Dict, Iterable, Optional, Tuple

from chronologia.astrodate import AstroDate

from .loader import HolidayCalendar, _DATA_DIR, load_calendar
from .model import CivilHoliday

_CACHE: Dict[str, HolidayCalendar] = {}
#: guards the lazy, per-jurisdiction ``.tab`` calendar cache so concurrent
#: first-lookups of different jurisdictions from separate threads each parse
#: their file exactly once.
_CACHE_LOCK = threading.Lock()

#: Financial-market jurisdiction codes are not ISO-3166-1 countries — they are
#: institutions (a stock exchange, a central bank's settlement system, a
#: futures exchange) that vacanza/holidays 0.101 registers under several
#: interchangeable codes for the *same* calendar (its MIC/ticker plus any
#: short-name aliases). Rather than duplicate one calendar's rules across
#: several identical ``.tab`` files, each alias here resolves to the single
#: canonical code that owns the shipped file. ``jurisdiction`` stays
#: free-form (no 2-letter assumption anywhere in the loader), so this is a
#: pure lookup layered in front of the ``.tab`` path resolution.
MARKET_ALIASES: Dict[str, str] = {
    # European Central Bank / TARGET2 settlement calendar -- vacanza's XECB.
    "ECB": "XECB",
    "TAR": "XECB",
    # New York Stock Exchange -- vacanza's XNYS.
    "NYSE": "XNYS",
    # Chicago Mercantile Exchange -- vacanza's XCME.
    "CME": "XCME",
    # Frankfurt Stock Exchange -- same calendar as Xetra, vacanza's XETR.
    "XFRA": "XETR",
    # SIX Swiss Exchange -- vacanza's XSWX.
    "SIX": "XSWX",
    # Toronto Stock Exchange -- vacanza's XTSE.
    "TSX": "XTSE",
    # Hong Kong Stock Exchange -- vacanza's XHKG.
    "HKEX": "XHKG",
    "SEHK": "XHKG",
    # Japan Exchange Group -- vacanza's XJPX.
    "JPX": "XJPX",
    "TSE": "XJPX",
    "OSE": "XJPX",
    # Shenzhen Stock Exchange -- same calendar as Shanghai, vacanza's XSHG.
    "XSHE": "XSHG",
    "SSE": "XSHG",
    "SZSE": "XSHG",
    # National Stock Exchange of India / Bombay Stock Exchange -- same
    # SEBI-gazetted calendar, vacanza's XBOM.
    "BSE": "XBOM",
    "XNSE": "XBOM",
    "NSE": "XBOM",
    # Brasil Bolsa Balcao -- vacanza's BVMF.
    "B3": "BVMF",
    # Bolsa Mexicana de Valores -- vacanza's XMEX.
    "BMV": "XMEX",
}


def _calendar_for(jurisdiction: str) -> HolidayCalendar:
    key = jurisdiction.upper()
    key = MARKET_ALIASES.get(key, key)
    cal = _CACHE.get(key)
    if cal is not None:
        return cal
    with _CACHE_LOCK:
        cal = _CACHE.get(key)
        if cal is None:
            path = os.path.join(_DATA_DIR, f"{key.lower()}.tab")
            if not os.path.exists(path):
                raise KeyError(
                    f"no holiday data for jurisdiction {jurisdiction!r}")
            cal = _CACHE[key] = load_calendar(path)
        return cal


def holidays_for(jurisdiction: str, year: int, subdiv: Optional[str] = None,
                 categories: Optional[Iterable[str]] = None,
                 strict_horizon: bool = False
                 ) -> Tuple[CivilHoliday, ...]:
    """Every civil holiday in ``jurisdiction`` for ``year`` (objects out).

    ``subdiv`` (e.g. ``"PT-LIS"``) adds that subdivision's holidays to the
    jurisdiction-wide set; ``categories`` filters to holidays sharing at least
    one requested category. Returns a chronologically sorted tuple of
    :class:`CivilHoliday`.

    ``strict_horizon`` (default ``False``) requires authoritative-only results:
    a decree-tabulated holiday past its own horizon is omitted rather than
    predicted (basis ``predicted``). Use it when a fabricated future date mixed
    in with facts would be worse than an honest gap; computable holidays are
    unaffected. See :func:`coverage` to inspect the horizon.

    :raises KeyError: no data file for ``jurisdiction``.
    """
    return _calendar_for(jurisdiction).holidays(
        year, subdiv, categories, strict_horizon=strict_horizon)


#: The four coverage verdicts :func:`coverage` reports (see its docstring).
COVERAGE_FULL = "full"
COVERAGE_PARTIAL = "partial"
COVERAGE_PREDICTED = "predicted"
COVERAGE_NONE = "none"


def coverage(jurisdiction: str, year: int,
             subdiv: Optional[str] = None) -> str:
    """How well ``jurisdiction`` is covered for ``year`` — the horizon detector.

    Decree-tabulated holidays (Islamic feasts, the Chinese cluster, gazette-only
    shift days) are authoritative only across the years they tabulate. Past that
    horizon a bare :func:`holidays_for` call can silently drop them, so a caller
    who trusts the empty result is trusting a time bomb. ``coverage`` makes the
    horizon inspectable, returning one of:

    * ``"full"`` — no applicable decree rule is past its horizon this year
      (everything resolves from a tabulated table or a computable rule).
    * ``"predicted"`` — every applicable decree rule that *is* past its horizon
      carries a ``predict`` annotation, so the year is fully bridged through the
      calendars with basis ``predicted`` (no silent gap remains).
    * ``"partial"`` — at least one applicable decree rule is past its horizon
      with no prediction (a genuine gazette-only gap), while other holidays
      still resolve.
    * ``"none"`` — no holiday resolves for the year at all.

    ``subdiv`` / no ``categories`` scoping matches :func:`holidays_for`.
    """
    cal = _calendar_for(jurisdiction)
    resolved = cal.holidays(year, subdiv)
    if not resolved:
        return COVERAGE_NONE
    past_unpredicted = False
    past_predicted = False
    for rule in cal.rules:
        if rule.subdiv is not None and rule.subdiv != subdiv:
            continue
        if not rule.in_force(year):
            continue
        if not rule.past_horizon(year):
            continue
        if rule.predict is not None:
            past_predicted = True
        else:
            past_unpredicted = True
    if past_unpredicted:
        return COVERAGE_PARTIAL
    if past_predicted:
        return COVERAGE_PREDICTED
    return COVERAGE_FULL


def is_civil_holiday(date, jurisdiction: str,
                     subdiv: Optional[str] = None,
                     categories: Optional[Iterable[str]] = None) -> bool:
    """True when ``date`` (AstroDate/date/datetime) is a civil holiday.

    Considers jurisdiction-wide holidays plus, when ``subdiv`` is given, that
    subdivision's holidays. ``categories`` filters the same way
    :func:`holidays_for` does (``None`` = every category, the historical
    default).
    """
    point = AstroDate(date.year, date.month, date.day)
    # an observed shift can relocate a holiday into an ADJACENT calendar year --
    # New Year's Day, when 1 Jan is a Saturday, is observed on 31 Dec of the
    # PREVIOUS year (e.g. NYSE/Nasdaq closed Fri 31 Dec 2021) -- and that
    # observance lives in the next year's bucket.  Consult the neighbouring
    # years too, filtering by span.contains, so a cross-year shift is not a
    # false negative.  span.contains only matches the query day, so a genuine
    # neighbour-year holiday can never be a false positive here.
    for y in (point.year - 1, point.year, point.year + 1):
        for holiday in holidays_for(jurisdiction, y, subdiv, categories):
            if holiday.span.contains(point):
                return True
    return False
