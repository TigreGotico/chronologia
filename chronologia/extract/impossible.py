"""Opt-in report of dates the calendar rejects.

By default an impossible date ("the 32nd of February", "every 31st of April",
"the sixth Monday of May") is declined like any phrase that is not a date: the
public extractors return ``None`` or an empty list.  A caller that must tell
the two apart passes ``impossible="raise"`` and gets an
:class:`ImpossibleDateError` instead.

The readers record why they refuse a reading through :func:`decline` while a
``"raise"`` call is running; :func:`reports_impossible` wraps each public
extractor and raises when the call found no reading and a reader recorded a
refusal.  A call that finds a reading returns it, as in the default mode.
Outside a ``"raise"`` call :func:`decline` does nothing.
"""
from __future__ import annotations

import calendar
import functools
import inspect
from contextvars import ContextVar
from datetime import date
from typing import List, Optional

from chronologia.astrodate import (_MONTH_NAMES_FULL, _WEEKDAY_NAMES_FULL,
                                   _days_in_month)
from chronologia.recurrence import RuleNeverOccursError

MODES = ("none", "raise")


class ImpossibleDateError(ValueError):
    """A phrase names a date that cannot exist.

    ``text`` is the whole string handed to the extractor (not the span of it
    that named the date), ``lang`` its language and
    ``reason`` a short plain-English account of why the calendar rejects it.
    """

    def __init__(self, text: str, lang: str, reason: str):
        super().__init__(f"{reason}: {text!r}")
        self.text = text
        self.lang = lang
        self.reason = reason


_refusals: ContextVar[Optional[List[str]]] = ContextVar("refusals", default=None)


def decline(reason: Optional[str]) -> None:
    """Record ``reason`` for the running ``"raise"`` call, if any.

    A refusal that has no calendar cause passes ``None`` and is not recorded.
    Returns ``None`` so a reader writes ``return decline(...)`` where it
    already wrote ``return None``.
    """
    found = _refusals.get()
    if reason is not None and found is not None:
        found.append(reason)


def raising() -> bool:
    """Whether a ``"raise"`` call is running, so a refusal is being recorded."""
    return _refusals.get() is not None


def ordinal(n: int) -> str:
    suffix = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def scope_name(month: Optional[int], year: Optional[int]) -> str:
    """"May 2026", "May" or "2026": the period a missing day or ordinal belongs to."""
    parts = (_MONTH_NAMES_FULL[month - 1] if month else None, year)
    return " ".join(str(part) for part in parts if part is not None)


def no_such(scope: str, n: int, what: str) -> str:
    """"May has no 6th Monday", "2026 has no 60th Monday", "2017 has no 53rd week"."""
    which = "last" if n == -1 else ordinal(abs(n)) + (" to last" if n < 0 else "")
    return f"{scope} has no {which} {what}"


def no_such_weekday(scope: str, n: int, weekday: int) -> str:
    return no_such(scope, n, _WEEKDAY_NAMES_FULL[weekday])


# The most of a unit one month or one year can hold over the 400-year cycle.
_MOST_IN_MONTH = {"weekend": 5, "day": 31, "week": 6}
_MOST_IN_YEAR = {"business day": 262, "day": 366, "week": 53, "month": 12}
# Most weekdays a month holds: 31-day months reach 23, 30-day months 22,
# February 21 (a leap February starting on a Monday).
_MOST_WEEKDAYS_IN_MONTH = {2: 21, 4: 22, 6: 22, 9: 22, 11: 22}


def ordinal_cap(n: int, unit, month: Optional[int] = None,
                year: Optional[int] = None, per: str = "month",
                zero: bool = False) -> Optional[str]:
    """Why no ``per`` ("month" or "year") holds an ``n``-th ``unit``, or ``None``.

    ``unit`` is a weekday number (Monday=0) or a unit name ("business day",
    "weekend", "day", "week", "month").  ``month`` and ``year`` name the
    period.  Without ``year`` the cap is the most any such period holds, so a
    period the speaker did not name may still hold ``n``.  With ``year`` a
    weekday is counted in that period; any other unit is refused, since the
    caller already searched the period.  ``zero`` refuses a 0th ordinal too.
    """
    if year is not None and isinstance(unit, int):
        days = _days_in_month(year, month) if month else 365 + calendar.isleap(year)
        most = (days - (unit - date(year, month or 1, 1).weekday()) % 7 - 1) // 7 + 1
    elif year is not None:
        most = 0
    elif isinstance(unit, int):
        most = 5 if per == "month" else 53
    elif per == "year":
        most = _MOST_IN_YEAR.get(unit, 0)
    elif unit == "business day":
        most = _MOST_WEEKDAYS_IN_MONTH.get(month, 23)
    elif unit == "day" and month:
        most = _days_in_month(2000, month)
    else:
        most = _MOST_IN_MONTH.get(unit, 0)
    if abs(n) <= most and not (zero and n == 0):
        return None
    scope = scope_name(month, year) or f"a {per}"
    return (no_such_weekday(scope, n, unit) if isinstance(unit, int)
            else no_such(scope, n, unit))


def bad_day(year: Optional[int], month: int, day: int) -> Optional[str]:
    """Why ``day`` is not a day of ``month`` in ``year``, or ``None`` when it is.

    With no ``year`` the month is taken at its longest, so only a day that no
    year has is bad.  A month outside 1..12 is not judged here.
    """
    if not 1 <= month <= 12:
        return None
    if not 1 <= day <= _days_in_month(2000 if year is None else year, month):
        return f"{scope_name(month, year)} has no {ordinal(day)}"
    return None


def reports_impossible(extract):
    """Give a public extractor the keyword-only ``impossible`` parameter.

    ``"none"`` (the default) leaves the extractor as it is.  ``"raise"`` raises
    :class:`ImpossibleDateError` in place of ``None`` (or an empty list) when
    a reader refused a reading because the calendar has no such date.  A call
    that finds some reading returns it.  A call nested inside a
    ``"raise"`` call reports to the outer call.
    """
    signature = inspect.signature(extract)

    @functools.wraps(extract)
    def wrapper(*args, impossible: str = "none", **kwargs):
        if impossible not in MODES:
            raise ValueError(
                f"impossible must be one of {', '.join(map(repr, MODES))}, "
                f"got {impossible!r}")
        if impossible == "none" or _refusals.get() is not None:
            return extract(*args, **kwargs)
        found: List[str] = []
        token = _refusals.set(found)
        try:
            result = extract(*args, **kwargs)
        except RuleNeverOccursError:
            # a rule built from a refused date can fail downstream; the refusal is its cause
            if not found:
                raise
            result = None
        finally:
            _refusals.reset(token)
        if found and not result:
            given = signature.bind(*args, **kwargs)
            given.apply_defaults()
            raise ImpossibleDateError(given.arguments["text"],
                                      given.arguments["lang"], found[0])
        return result

    wrapper.__signature__ = signature.replace(parameters=[
        *signature.parameters.values(),
        inspect.Parameter("impossible", inspect.Parameter.KEYWORD_ONLY,
                          default="none", annotation=str)])
    return wrapper
