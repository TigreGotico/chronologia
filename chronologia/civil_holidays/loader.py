"""Data-file loading: translations, the calendar object, and the ``.tab`` parser.

Rules live in ``chronologia/holiday_data/<country>.tab`` — a documented text
format (see :func:`load_calendar`) with a provenance header (official source
URL + retrieval date) per file, one rule per line, an optional subdivision
column. Display translations live in ``holiday_data/i18n/translations.tab``
(see :func:`load_translations`). :class:`HolidayCalendar` holds one
jurisdiction's rules and resolves them (including the calendar-wide substitute
pass) into :class:`~chronologia.civil_holidays.model.CivilHoliday` objects.
"""
from __future__ import annotations

import os
import threading
from dataclasses import dataclass, replace
from typing import Dict, Iterable, Optional, Tuple

from chronologia.astrodate import _BASIS_RANK
from .model import CivilHoliday, HolidayRule, _day_span, _shape_span
from .rules import (CalendarDateRule, DecreeTableRule, EasterOffsetRule,
                    ExcludeRule, FixedRule, NearestWeekdayRule, NthWeekdayRule,
                    OneOffRule, RuleKind, SolarEventRule, parse_name_cell)
from .shifts import SubstitutePolicy, _SHIFT_POLICIES

# --------------------------------------------------------------------------
# Translations layer.
# --------------------------------------------------------------------------
_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                         "holiday_data")
_REQUIRED_HEADERS = ("jurisdiction", "source", "retrieved")
#: civil-holidays .tab schema versions this build can read. A file whose
#: ``# civil-holidays <version>`` banner is not listed here fails loudly rather
#: than being silently mis-parsed after a format evolution.
_SUPPORTED_SCHEMA_VERSIONS = frozenset({"v1"})
_TRANSLATIONS_FILE = os.path.join(_DATA_DIR, "i18n", "translations.tab")


def load_translations(path: str = _TRANSLATIONS_FILE
                      ) -> Dict[Tuple[str, str], Dict[str, str]]:
    """Parse ``holiday_data/translations.tab`` into ``(JURIS, name) -> {lang: text}``.

    **File format** (``# civil-holidays-translations v1``). ``#``-lines are
    comments; each data row is pipe-delimited ``jurisdiction | name | lang |
    text``. ``jurisdiction`` is the upper-case code (``PT``); ``name`` is the
    holiday's **primary** ``name`` (its official native name — the join key back
    to the rule); ``lang`` is a BCP-47-ish code; ``text`` is the *translation*.

    These are display renderings, not official names — the honest distinction the
    header records with ``source: translation``. A missing file yields ``{}``.
    """
    out: Dict[Tuple[str, str], Dict[str, str]] = {}
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            cols = [c.strip() for c in line.split("|")]
            if len(cols) < 4:
                raise ValueError(
                    f"malformed translation line (need 4 columns): {line!r}")
            juris, name, lang, text = cols[0], cols[1], cols[2], cols[3]
            out.setdefault((juris.upper(), name), {})[lang] = text
    return out


_TRANSLATIONS: Optional[Dict[Tuple[str, str], Dict[str, str]]] = None
_TRANSLATIONS_LOCK = threading.Lock()


def _translations_for(jurisdiction: str, name: str) -> Dict[str, str]:
    global _TRANSLATIONS
    if _TRANSLATIONS is None:
        with _TRANSLATIONS_LOCK:
            if _TRANSLATIONS is None:
                _TRANSLATIONS = load_translations()
    return _TRANSLATIONS.get((jurisdiction.upper(), name), {})


# --------------------------------------------------------------------------
# The calendar object and the data-file loader.
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class HolidayCalendar:
    """The set of holiday rules for one jurisdiction, loaded from a data file."""

    jurisdiction: str
    rules: Tuple[HolidayRule, ...]
    source: str = ""
    retrieved: str = ""

    def holidays(self, year: int, subdiv: Optional[str] = None,
                 categories: Optional[Iterable[str]] = None,
                 strict_horizon: bool = False
                 ) -> Tuple[CivilHoliday, ...]:
        """Resolve every applicable rule for ``year`` into :class:`CivilHoliday`.

        ``subdiv`` selects a subdivision: a rule applies when it is
        jurisdiction-wide (``subdiv is None``) *or* its ``subdiv`` matches the
        requested one. ``categories`` keeps only holidays sharing at least one
        of the requested categories.

        ``strict_horizon`` (default ``False``) requires authoritative-only
        results: a decree-tabulated holiday past its own horizon is *omitted*
        instead of being predicted (basis ``predicted``). Every computable
        holiday (fixed date, nth-weekday, Easter-offset, …) is unaffected — it
        has no horizon and always resolves. See :meth:`HolidayRule.resolve`.
        """
        want = frozenset(categories) if categories is not None else None
        applicable = []
        # Subtractive pass: an ExcludeRule scoped to the requested subdivision
        # names an inherited holiday to drop (US-ND / US-UM omit Columbus Day).
        # It is collected here — never emitted — so the additive pass below skips
        # any holiday whose name it excludes.
        excluded: set = set()
        for rule in self.rules:
            if rule.subdiv is not None and rule.subdiv != subdiv:
                continue
            if isinstance(rule.kind, ExcludeRule):
                excluded.add(rule.kind.target)
                continue
            if want is not None and not (rule.categories & want):
                continue
            applicable.append(rule)
        applicable = [r for r in applicable if r.name not in excluded]

        out = []
        # Nominal (base) occurrences first — they populate the ``taken`` set the
        # substitute pass rolls forward past, so a substitute never collides with
        # another holiday (the UK Christmas/Boxing cascade, Japan furikae).
        subst_work = []  # (nominal_date, rule) awaiting a substitute day
        for rule in applicable:
            trans = _translations_for(self.jurisdiction, rule.name)
            for date, basis in rule.resolve(year, strict_horizon=strict_horizon):
                out.append(CivilHoliday(
                    name=rule.name,
                    span=_shape_span(date, basis, rule.span_shape),
                    jurisdiction=self.jurisdiction,
                    subdiv=rule.subdiv,
                    categories=rule.categories,
                    basis=basis,
                    names=rule.names,
                    translations=trans))
                if isinstance(rule.shift, SubstitutePolicy):
                    subst_work.append((date, basis, rule))

        taken = {h.span.start for h in out}
        for date, basis, rule in sorted(subst_work, key=lambda t: t[0]):
            sub = rule.shift.substitute_for(date, frozenset(taken))
            if sub is None:
                continue
            taken.add(sub)
            label = rule.shift.label
            trans = _translations_for(self.jurisdiction, rule.name)
            out.append(CivilHoliday(
                name=rule.name + label,
                span=_day_span(sub, basis),
                jurisdiction=self.jurisdiction,
                subdiv=rule.subdiv,
                categories=rule.categories,
                basis=basis,
                names={lang: text + label for lang, text in rule.names.items()},
                translations={lang: text + label
                              for lang, text in trans.items()}))
        # Collapse rows that resolved to the SAME civil day (name, span, subdiv)
        # and differ only in CATEGORY or in PROVENANCE into one entry carrying
        # the union of categories and the most authoritative basis.  A holiday
        # the data lists once per category (HK Chinese New Year as both public
        # and optional) and a computable holiday that a redundant decree table
        # re-states only to attach a secondary category (GU Good Friday as
        # `unofficial`, PT Carnaval as `optional`, LB Hariri Day as `bank`) are
        # the same day, not two holidays -- a consumer must never see a literal
        # duplicate.  Basis is NOT part of the identity: the same day computed
        # AND tabulated is one holiday, kept at its strongest basis (exact >
        # tabulated > predicted).  Rows that differ in subdiv (a national plus a
        # subdivision declaration) or in span width (a full day plus a half-day)
        # stay distinct -- genuinely different civil scope or referent.
        merged = {}
        for h in out:
            key = (h.name, h.span.start, h.span.end, h.subdiv)
            if key in merged:
                prev = merged[key]
                keep = h if (_BASIS_RANK.get(h.basis, 9)
                             < _BASIS_RANK.get(prev.basis, 9)) else prev
                merged[key] = replace(keep,
                                      categories=prev.categories | h.categories)
            else:
                merged[key] = h
        out = list(merged.values())
        out.sort(key=lambda h: (h.span.start, h.name))
        return tuple(out)


def _parse_kind(kind: str, args: str) -> RuleKind:
    parts = args.split()
    if kind == "fixed":
        m, d = int(parts[0]), int(parts[1])
        return FixedRule(m, d)
    if kind == "nth_weekday":
        month, n, wd = int(parts[0]), int(parts[1]), int(parts[2])
        post = int(parts[3]) if len(parts) > 3 else 0
        return NthWeekdayRule(month, n, wd, post)
    if kind == "weekday_onbefore":
        return NearestWeekdayRule(int(parts[0]), int(parts[1]), int(parts[2]),
                                  direction=-1)
    if kind == "weekday_onafter":
        return NearestWeekdayRule(int(parts[0]), int(parts[1]), int(parts[2]),
                                  direction=+1)
    if kind == "easter":
        offset = int(parts[0])
        method = parts[1] if len(parts) > 1 else "gregorian"
        return EasterOffsetRule(offset, method)
    if kind == "calendar_date":
        return CalendarDateRule(parts[0], int(parts[1]), int(parts[2]))
    if kind in ("equinox", "solar_term"):
        tz = float(parts[1]) if len(parts) > 1 else 0.0
        return SolarEventRule(parts[0], tz)
    if kind == "decree":
        dates = []
        for token in parts:
            y, m, d = (int(x) for x in token.split("-"))
            dates.append((y, (m, d)))
        return DecreeTableRule(tuple(dates))
    if kind == "one_off":
        y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
        citation = " ".join(parts[3:])
        return OneOffRule(y, m, d, citation)
    if kind == "exclude":
        return ExcludeRule(args.strip())
    raise ValueError(f"unknown rule kind {kind!r}")


def _parse_valid(token: Optional[str]) -> Tuple[Optional[int], Optional[int]]:
    """Parse a ``valid`` column into ``(from_year, until_year)`` bounds.

    Grammar: ``"2024-"`` (from 2024 on), ``"-2015"`` (until 2015), ``"2016-2020"``
    (both bounds), ``"2024"`` (that single year only), empty/``None`` (unbounded).
    """
    if not token:
        return (None, None)
    if "-" in token:
        lo, hi = token.split("-", 1)
        return (int(lo) if lo.strip() else None,
                int(hi) if hi.strip() else None)
    y = int(token)
    return (y, y)


def load_calendar(path: str) -> HolidayCalendar:
    """Parse a ``holiday_data/*.tab`` file into a :class:`HolidayCalendar`.

    **File format** (``# civil-holidays v1``). ``#``-prefixed lines are comments;
    header metadata is written as ``# name: value`` and the loader **requires**
    ``jurisdiction``, ``source`` (official URL) and ``retrieved`` (date) to be
    present — provenance is mandatory. Each data row is pipe-delimited::

        kind | name | args | categories | subdiv | observed | valid | span | predict

    * ``kind`` — ``fixed`` / ``nth_weekday`` / ``easter`` / ``calendar_date`` /
      ``equinox`` / ``solar_term`` / ``decree`` / ``one_off`` / ``exclude``
      (see the per-kind classes for the ``args`` grammar). A ``one_off`` row's
      ``args`` is ``<year> <month> <day> <citation…>`` — the citation is the
      rest of the field and is mandatory. An ``exclude`` row's ``args`` is the
      exact ``name`` of the inherited holiday to *remove* for its ``subdiv``
      (the additive engine's one subtractive kind — see :class:`ExcludeRule`);
      its own ``name`` column repeats that target for readability.
    * ``name`` — the official holiday name(s), verbatim from the cited source. A
      single plain name is the common case; a multi-official jurisdiction may
      give ``;;``-separated ``lang:``-tagged alternates (``zh:春节 ;; en:Spring
      Festival``) — see :func:`parse_name_cell`. The first alternate is the
      primary ``name``; every tagged one populates :attr:`HolidayRule.names`.
      Display *translations* are a separate layer (``translations.tab``), never
      mixed into this column.
    * ``categories`` — space-separated subset of :data:`CATEGORIES`.
    * ``subdiv`` — optional subdivision code (empty = jurisdiction-wide).
    * ``observed`` — optional named policy: a relocating shift (``us`` /
      ``sun_mon`` / ``sat_sun_mon`` / ``il_independence``) OR an in-lieu
      substitute (``gb_substitute`` / ``jp_furikae`` / ``au_substitute``);
      empty = none.
    * ``valid`` — optional validity range (``"2024-"`` / ``"-2015"`` /
      ``"2016-2020"`` / ``"2024"``; empty = always in force).
    * ``span`` — optional span shape: ``day`` (default, a whole-day holiday),
      ``half_pm`` (the free afternoon ``[12:00, 24:00)`` — the "offices close at
      noon" pre-holiday half-day) or ``half_am`` (``[00:00, 12:00)``). The
      resolved :class:`CivilHoliday`'s span carries the real 12-hour width.
    * ``predict`` — optional :data:`WELL_KNOWN` key naming the computable rule
      that predicts a ``decree`` holiday's date beyond its tabulated horizon
      (basis ``predicted``); empty = honest silence past the horizon. See
      :attr:`HolidayRule.predict`.
    """
    meta: Dict[str, str] = {}
    rules = []
    saw_version = False
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.rstrip("\n")
            if not line.strip():
                continue
            if line.lstrip().startswith("#"):
                body = line.lstrip()[1:].strip()
                low = body.lower()
                if ((low == "civil-holidays" or low.startswith("civil-holidays "))
                        and ":" not in body):
                    version = body[len("civil-holidays"):].strip()
                    if version not in _SUPPORTED_SCHEMA_VERSIONS:
                        raise ValueError(
                            f"{os.path.basename(path)}: unsupported "
                            f"civil-holidays schema version {version!r}; this "
                            f"build reads {sorted(_SUPPORTED_SCHEMA_VERSIONS)}")
                    saw_version = True
                elif ":" in body:
                    k, v = body.split(":", 1)
                    meta.setdefault(k.strip(), v.strip())
                continue
            cols = [c.strip() for c in line.split("|")]
            if len(cols) < 4:
                raise ValueError(
                    f"malformed rule line (need >=4 columns): {line!r}")
            kind, name_cell, args, cats = cols[0], cols[1], cols[2], cols[3]
            name, names = parse_name_cell(name_cell)
            subdiv = cols[4] if len(cols) > 4 and cols[4] else None
            obs_name = cols[5] if len(cols) > 5 and cols[5] else None
            valid = cols[6] if len(cols) > 6 and cols[6] else None
            span_shape = cols[7] if len(cols) > 7 and cols[7] else "day"
            predict = cols[8] if len(cols) > 8 and cols[8] else None
            # The observed column names one shift policy — a relocating
            # ObservedShift or an in-lieu SubstitutePolicy; the applying site
            # dispatches by type.
            shift = None
            if obs_name is not None:
                shift = _SHIFT_POLICIES.get(obs_name)
                if shift is None:
                    raise ValueError(
                        f"unknown observed/substitute policy {obs_name!r}")
            from_year, until_year = _parse_valid(valid)
            categories = frozenset(cats.split())
            rules.append(HolidayRule(
                name=name,
                kind=_parse_kind(kind, args),
                categories=categories,
                subdiv=subdiv,
                shift=shift,
                from_year=from_year,
                until_year=until_year,
                span_shape=span_shape,
                predict=predict,
                names=names))
    if not saw_version:
        raise ValueError(
            f"{os.path.basename(path)}: missing '# civil-holidays <version>' "
            f"schema banner (expected one of {sorted(_SUPPORTED_SCHEMA_VERSIONS)})")
    missing = [h for h in _REQUIRED_HEADERS if h not in meta]
    if missing:
        raise ValueError(
            f"{os.path.basename(path)}: missing provenance header(s) {missing}")
    return HolidayCalendar(
        jurisdiction=meta["jurisdiction"],
        rules=tuple(rules),
        source=meta.get("source", ""),
        retrieved=meta.get("retrieved", ""))
