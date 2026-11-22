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

import functools
import inspect
from contextvars import ContextVar
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
