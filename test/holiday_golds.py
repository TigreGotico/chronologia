"""Shared gold registry for civil-holiday data files.

Every rule shipped in ``chronologia/holiday_data/<cc>.tab`` must be pinned by at
least one *gold*: an explicitly expected date for one occurrence, hand-derived
from the country's primary source (never copied from engine output). Each
country test module (``test_holidays_<cc>.py``) builds its gold table and calls
:func:`register`. Two things consume the registry:

* the per-country parametrized ``test_gold_dates`` assert every gold resolves to
  its expected date — for movable holidays the expected date is recomputed
  independently in-test as ``easter(year, method) + easter_offset``;
* the single coverage enforcer
  ``test_civil_holidays.py::test_every_rule_has_a_gold`` walks every rule of
  every *enforced* jurisdiction's ``.tab`` and fails if any ``(subdiv, name)``
  lacks a gold — so a new country cannot ship an unasserted holiday.

**Naming convention (multi-module tolerant).** Gold providers are the test
modules matching ``test_holidays_*.py`` in the ``test/`` directory.
:func:`ensure_all_registered` imports every such module, so the enforcer sees a
fully-populated registry no matter which test file pytest happens to run first
(and picks up modules a later wave adds without edits here).

Legacy pilot files (the Portugal municipal seed, US, SA) predate this registry
and are exempt via :data:`LEGACY_UNENFORCED`.
"""
from __future__ import annotations

import glob
import importlib
import os
from dataclasses import dataclass
from typing import List, Optional, Tuple

#: Pilot jurisdictions that predate per-rule golds (documented exemption).
LEGACY_UNENFORCED = frozenset({"PT", "US", "SA"})


@dataclass(frozen=True)
class Gold:
    """One pinned holiday occurrence.

    ``easter_offset`` (when set) marks a movable holiday: the per-country test
    asserts the expected ``(month, day)`` equals ``easter(year, easter_method)``
    shifted by ``easter_offset``, an independent re-derivation of the date rather
    than a value read back from the rule under test.
    """

    jurisdiction: str
    subdiv: Optional[str]
    name: str
    year: int
    month: int
    day: int
    easter_offset: Optional[int] = None
    easter_method: str = "gregorian"


_REGISTRY: List[Gold] = []


def register(golds) -> None:
    """Add a country module's golds to the shared registry."""
    _REGISTRY.extend(golds)


def all_golds() -> Tuple[Gold, ...]:
    return tuple(_REGISTRY)


def golds_for(jurisdiction: str) -> Tuple[Gold, ...]:
    key = jurisdiction.upper()
    return tuple(g for g in _REGISTRY if g.jurisdiction.upper() == key)


def enforced_jurisdictions() -> frozenset:
    """Jurisdictions that have registered at least one gold."""
    return frozenset(g.jurisdiction.upper() for g in _REGISTRY)


def ensure_all_registered() -> None:
    """Import every ``test_holidays_*.py`` so the registry is fully populated."""
    here = os.path.dirname(__file__)
    for path in sorted(glob.glob(os.path.join(here, "test_holidays_*.py"))):
        importlib.import_module(os.path.basename(path)[:-3])
