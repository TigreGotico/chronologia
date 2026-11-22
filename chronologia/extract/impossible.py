"""Opt-in report of dates the calendar rejects.

By default an impossible date ("the 32nd of February", "every 31st of April",
"the sixth Monday of May") is declined like any phrase that is not a date: the
public extractors return ``None`` or an empty list.  A caller that must tell
the two apart passes ``impossible="raise"`` and gets an
:class:`ImpossibleDateError` instead.

The readers record why they refuse a reading through :func:`decline` while a
``"raise"`` call is running; :func:`reports_impossible` wraps each public
extractor and raises when a reader recorded a refusal during the call.
Outside such a call :func:`decline` does nothing.
"""
from __future__ import annotations

import functools
import inspect
from contextlib import contextmanager
from contextvars import ContextVar
from typing import List, Optional

from chronologia.astrodate import (_MONTH_NAMES_FULL, _WEEKDAY_NAMES_FULL,
                                   _days_in_month)

MODES = ("none", "raise")


class ImpossibleDateError(ValueError):
    """A phrase names a date that cannot exist.

    ``text`` is the text handed to the extractor, ``lang`` its language and
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


@contextmanager
def ignoring_refusals():
    """Run a reading whose refusals say nothing about the phrase.

    ``extract_candidates`` resolves runner-up readings that the best reading
    already outranks; a calendar that rejects one of them is no reason to
    raise.
    """
    token = _refusals.set(None)
    try:
        yield
    finally:
        _refusals.reset(token)


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
    year has is bad.  A month outside 1..12 is not judged: it is as likely a
    number that is no date at all as a mistyped one.
    """
    length = _days_in_month(2000 if year is None else year, month) \
        if 1 <= month <= 12 else day
    if not 1 <= day <= length:
        return f"{scope_name(month, year)} has no {ordinal(day)}"
    return None


def reports_impossible(extract):
    """Give a public extractor the keyword-only ``impossible`` parameter.

    ``"none"`` (the default) leaves the extractor as it is.  ``"raise"`` raises
    :class:`ImpossibleDateError` when a reader refused a reading because the
    calendar has no such date.  A call nested inside a
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
        except ValueError:
            # a rule that never occurs can fail downstream; the refusal is its cause
            if not found:
                raise
        finally:
            _refusals.reset(token)
        if found:
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
