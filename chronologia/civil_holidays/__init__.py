"""Civil (public / regional / municipal) holidays as computed calendar rules.

A civil holiday is a *rule*, not a date: "New Year's Day" is "1 January every
year", "U.S. Labor Day" is "the first Monday of September", "Corpo de Deus" is
"the 60th day after Easter", "Eid al-Fitr" is "1 Shawwal on the Umm al-Qura
table". This package reduces each such rule to :mod:`chronologia`'s existing
machinery — :func:`~chronologia.recurrence.nth_weekday_of_month`,
:func:`~chronologia.computus.easter`, and the tabulated calendars in
:data:`~chronologia.calendars.CALENDARS` — so a holiday for the year -500 falls
out of the same integer arithmetic as one for 2024, with no ``datetime`` window.

Package layout (one module per responsibility, in dependency order)
-------------------------------------------------------------------
* :mod:`.rules` — the per-kind frozen rule classes (:class:`FixedRule`,
  :class:`NthWeekdayRule`, …), the :data:`CATEGORIES` schema and
  :func:`parse_name_cell`.
* :mod:`.shifts` — the weekend / in-lieu policies (:class:`ObservedShift`,
  :class:`SubstitutePolicy`) and their named instances.
* :mod:`.model` — the resolved-rule wrapper :class:`HolidayRule` and the output
  object :class:`CivilHoliday` (plus the span helpers).
* :mod:`.loader` — translation + ``.tab`` data loading, :class:`HolidayCalendar`
  and :func:`load_calendar`.
* :mod:`.registry` — the lazy per-jurisdiction cache and public query API
  (:func:`holidays_for`, :func:`coverage`, :func:`is_civil_holiday`).
* :mod:`.well_known` — the cross-border / jurisdiction-bound well-known
  registries and alias loaders.

This ``__init__`` re-exports every name the historical single-module
``civil_holidays`` exposed, so ``from chronologia.civil_holidays import X`` and
``chronologia.civil_holidays.X`` keep working identically. See each submodule's
docstring for the full design notes originally carried by the module banner.

Internationalisation — three layers
------------------------------------
The golden rule: *a holiday's real name is what its own government calls it.*
1. **Official native names** (primary ``.tab`` data) → :attr:`CivilHoliday.names`.
2. **Display translations** (``translations.tab``) → :attr:`CivilHoliday.translations`.
3. **The resolution API** — :meth:`CivilHoliday.display_name` walks official →
   translation → primary ``name``.
"""
from __future__ import annotations

# Re-export the external imports the historical module exposed at its top level,
# so the package's public namespace stays a superset of the old module's.
import os
import re
import threading
from dataclasses import dataclass, field
from datetime import timedelta
from types import MappingProxyType
from typing import (Dict, FrozenSet, Iterable, Mapping, Optional, Protocol,
                    Tuple, Union, runtime_checkable)

from chronologia.astrodate import (BASIS_EXACT, BASIS_PREDICTED,
                                   BASIS_TABULATED, AstroDate, DateSpan)
from chronologia.calendars import CALENDARS, CalendarRangeError, gregorian_to_jdn
from chronologia.computus import easter
from chronologia.equinoxes import equinox, solar_term
from chronologia.recurrence import (WEEKDAYS, nth_weekday_of_month,
                                    occurrences)

from .rules import (CATEGORIES, CalendarDateRule, DecreeTableRule,
                    EasterOffsetRule, ExcludeRule, FixedRule, NearestWeekdayRule,
                    NthWeekdayRule, OneOffRule, RuleKind, SolarEventRule,
                    _EASTER_METHODS, _EQUINOX_EVENTS, _LANG_TAG,
                    parse_name_cell)
from .shifts import (GB_SUBSTITUTE, IL_INDEPENDENCE_SHIFT, JP_FURIKAE,
                     NL_KINGSDAY_SHIFT, SATURDAY_SUNDAY_TO_MONDAY,
                     SUNDAY_TO_MONDAY, US_OBSERVED_SHIFT, ObservedShift,
                     ShiftPolicy, SubstitutePolicy, _SHIFT_POLICIES)
from .model import (CivilHoliday, HolidayRule, _SPAN_SHAPES, _day_span,
                    _shape_span)
from .loader import (HolidayCalendar, _DATA_DIR, _REQUIRED_HEADERS,
                     _TRANSLATIONS, _TRANSLATIONS_FILE, _TRANSLATIONS_LOCK,
                     _parse_kind, _parse_valid, _translations_for,
                     load_calendar, load_translations)
from .registry import (COVERAGE_FULL, COVERAGE_NONE, COVERAGE_PARTIAL,
                       COVERAGE_PREDICTED, MARKET_ALIASES, _CACHE, _CACHE_LOCK,
                       _calendar_for, coverage, holidays_for, is_civil_holiday)
from .well_known import (JURISDICTION_KNOWN, JURISDICTION_KNOWN_BY_KEY_LANG,
                         JURISDICTION_KNOWN_KEYS, JurisdictionKnownHoliday,
                         WELL_KNOWN, WELL_KNOWN_BY_KEY, WellKnownHoliday,
                         _FD_3SUN_JUN, _FD_ASCENSION, _FD_MAR19, _KnownHoliday,
                         _MD_1SUN_MAY, _MD_2SUN_MAY, _MD_LAST_SUN_MAY, _UNOFF,
                         _WELL_KNOWN_ALIASES, _WELL_KNOWN_FILE, _WELL_KNOWN_LOCK,
                         _well_known_aliases, load_well_known_aliases,
                         well_known_source, well_known_surfaces)

__all__ = [
    "CATEGORIES",
    "FixedRule",
    "NthWeekdayRule",
    "NearestWeekdayRule",
    "EasterOffsetRule",
    "CalendarDateRule",
    "DecreeTableRule",
    "OneOffRule",
    "ExcludeRule",
    "SolarEventRule",
    "ObservedShift",
    "US_OBSERVED_SHIFT",
    "SUNDAY_TO_MONDAY",
    "SATURDAY_SUNDAY_TO_MONDAY",
    "IL_INDEPENDENCE_SHIFT",
    "NL_KINGSDAY_SHIFT",
    "SubstitutePolicy",
    "GB_SUBSTITUTE",
    "JP_FURIKAE",
    "HolidayRule",
    "CivilHoliday",
    "HolidayCalendar",
    "holidays_for",
    "coverage",
    "COVERAGE_FULL",
    "COVERAGE_PARTIAL",
    "COVERAGE_PREDICTED",
    "COVERAGE_NONE",
    "WellKnownHoliday",
    "WELL_KNOWN",
    "WELL_KNOWN_BY_KEY",
    "JurisdictionKnownHoliday",
    "JURISDICTION_KNOWN",
    "JURISDICTION_KNOWN_BY_KEY_LANG",
    "JURISDICTION_KNOWN_KEYS",
    "load_well_known_aliases",
    "well_known_surfaces",
    "well_known_source",
    "is_civil_holiday",
    "load_calendar",
    "load_translations",
    "parse_name_cell",
]
