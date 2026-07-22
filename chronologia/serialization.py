"""One JSON envelope convention for chronologia's public value types.

Every serializable value type exposes two methods:

* ``value.to_json()`` returns a plain, ``json.dumps``-ready ``dict`` — no
  custom encoder needed.  The dict is an **envelope**: it always carries a
  ``"type"`` key naming the type, alongside that type's fields (nested value
  types appear as nested envelopes).
* ``Type.from_json(data)`` rebuilds the value from such a dict.

This module adds the type-agnostic counterpart :func:`from_json`, which reads
the ``"type"`` tag and dispatches to the right ``from_json`` classmethod, and
:func:`to_json`, a thin ``obj.to_json()`` wrapper — so a heterogeneous list of
values round-trips without the caller having to know each concrete type::

    import json
    from chronologia import to_json, from_json

    blob = json.dumps([to_json(v) for v in values])
    back = [from_json(d) for d in json.loads(blob)]

The envelope shape (``{"type": "<TypeName>", ...fields}``) is the single
documented convention; every type follows it.
"""
from __future__ import annotations

from typing import Any, Callable, Dict

from chronologia.astrodate import AstroDate, DateSpan
from chronologia.calendars import CalendarDate
from chronologia.civil_holidays import CivilHoliday
from chronologia.edtf import EdtfDate
from chronologia.mars import DarianDate, MarsDate
from chronologia.periods import NamedPeriod
from chronologia.recurrence import HolidayRecurrence, Recurrence

__all__ = ["to_json", "from_json"]

#: Maps a ``"type"`` tag to the classmethod that rebuilds it.
_DECODERS: Dict[str, Callable[[dict], Any]] = {
    "AstroDate": AstroDate.from_json,
    "DateSpan": DateSpan.from_json,
    "CalendarDate": CalendarDate.from_json,
    "CivilHoliday": CivilHoliday.from_json,
    "EdtfDate": EdtfDate.from_json,
    "NamedPeriod": NamedPeriod.from_json,
    "Recurrence": Recurrence.from_json,
    "HolidayRecurrence": HolidayRecurrence.from_json,
    "MarsDate": MarsDate.from_json,
    "DarianDate": DarianDate.from_json,
}


def to_json(obj: Any) -> dict:
    """Return ``obj.to_json()`` — the ``json.dumps``-ready envelope dict.

    Raises :class:`TypeError` for a value that carries no ``to_json`` method.
    """
    method = getattr(obj, "to_json", None)
    if not callable(method):
        raise TypeError(
            f"{type(obj).__name__} is not a chronologia JSON value type "
            "(no to_json method)")
    return method()


def from_json(data: dict) -> Any:
    """Rebuild a value from a :func:`to_json` envelope by its ``"type"`` tag.

    Raises :class:`ValueError` when ``data`` is not an envelope or names a
    type this registry does not know.
    """
    if not isinstance(data, dict) or "type" not in data:
        raise ValueError("not a chronologia JSON envelope (missing 'type')")
    tag = data["type"]
    try:
        decoder = _DECODERS[tag]
    except KeyError:
        raise ValueError(f"unknown chronologia JSON type: {tag!r}") from None
    return decoder(data)
