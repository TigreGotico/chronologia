"""Versioned structural checker for the locale grammar (``lang.json`` + ``*.voc``).

The locale grammar is a small, implicit contract: every ``lang.json`` states
construction *orders* (slot/connector sequences over a fixed slot alphabet),
conventions, quantifiers, guards, a hook and per-construction flags, and every
order is only reachable if the vocabulary its slots bind against actually ships
in that locale.  Nothing enforced that contract -- a typo'd slot name, a
non-numeric quantifier key or an order referencing a ``.voc`` file that was
never translated simply produced a silently dead construction.

This module derives the *actual* schema from two authorities and checks a
loaded locale against it, LOUDLY (private repo: bad data should break, not
degrade):

* the **slot alphabet** is read straight from :mod:`chronologia.extract.matcher`
  (the ``_bind`` dispatch is the only place that decides what a slot name
  means), so the schema can never drift from the matcher;
* the **known construction names** come from
  :data:`chronologia.extract.compiler.PRECEDENCE` (plus the declared-but-
  unresolved set), the single precedence table every construction is ranked in.

Two entry points:

``validate_config(cfg, lang)``
    Pure structural check over the parsed JSON -- unknown keys, malformed order
    strings (unknown slots, bad optional syntax), non-numeric quantifier keys,
    unknown construction names/groups.  Needs no vocabulary.

``validate_reachability(spec, cfg, lang)``
    Given a loaded :class:`~chronologia.extract.model.LangSpec`, checks that
    every *required* slot / connector of every order has non-empty backing
    vocabulary in the locale -- i.e. the order can actually fire.  A ``.voc``
    referenced by a required slot but missing or empty is a defect.

``validate(cfg, lang, spec)`` runs both and raises
:class:`LocaleSchemaError` aggregating all findings with locale + field
context.  The loader calls it on load.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, FrozenSet, List

from chronologia.extract.compiler import PRECEDENCE, UNIMPLEMENTED

#: bump when the checker's accepted shape changes.
SCHEMA_VERSION = 1


class LocaleSchemaError(ValueError):
    """Raised when a locale violates the derived grammar schema.

    Carries the full list of findings so a single load reports every defect at
    once, each already prefixed with locale + field context.
    """

    def __init__(self, lang: str, errors: List[str]):
        self.lang = lang
        self.errors = list(errors)
        super().__init__(
            f"locale {lang!r} fails the grammar schema (v{SCHEMA_VERSION}):\n"
            + "\n".join(f"  - {e}" for e in self.errors))


def _derive_slot_alphabet() -> FrozenSet[str]:
    """The uppercase slot names the matcher's ``_bind`` recognises.

    Parsed from ``matcher.py`` so the alphabet is exactly what the engine binds
    -- there is no second, hand-maintained list to fall out of sync.
    """
    src = (Path(__file__).with_name("matcher.py")).read_text(encoding="utf-8")
    names = set(re.findall(r'name == "([A-Z_]+)"', src))
    for group in re.findall(r"name in \(([^)]*)\)", src):
        names.update(re.findall(r'"([A-Z_]+)"', group))
    return frozenset(names)


#: every uppercase slot the matcher can bind (derived from matcher.py).
SLOT_ALPHABET: FrozenSet[str] = _derive_slot_alphabet()

#: slots whose value is a numeric / regex literal -- always reachable, they
#: bind no per-locale vocabulary.
NUMERIC_SLOTS: FrozenSet[str] = frozenset({
    "NUM", "DNUM", "DAY", "YEAR", "YEARANY", "GYEAR", "ORD", "SORD", "SUBH", "SUBM", "SUBS",
    "HOUR", "MINUTE", "QUARTS", "MILTIME", "MILTIMEZ", "MILTIMENZ",
    "CLOCK", "ISO", "ISOWEEK", "NUMDATE"})

#: uppercase slots that actually bind a *connector* surface set, not a value map.
CONNECTOR_SLOTS: Dict[str, str] = {
    "PRIDIE": "pridie",
    "NTOLAST": "ordlast",
    "PENULT": "penult",
}

#: slots reachable if *either* the scope-unit or the plain-unit map is present.
DUAL_UNIT_SLOTS: FrozenSet[str] = frozenset({"SEL_UNIT", "SCOPE_UNIT"})

#: slot -> the :class:`LangSpec` attribute holding its vocabulary.  A slot maps
#: here iff it is backed by a ``.voc`` file convention; slots absent from every
#: table above and this map (currently only ``HOLIDAY``, whose surfaces are
#: derived from the holidays engine, not a ``.voc``) are not reachability-checked.
SLOT_VOCAB_ATTR: Dict[str, str] = {
    "UNIT": "units",
    "USG": "singular_units",
    "MARKER": "directions",
    "DIRECTION_MARKER": "directions",
    "DAY_WORD": "named_days",
    "REL_MARKER": "rel_markers",
    "WEEKEND": "weekend_words",
    "WEEKDAY": "weekdays",
    "WEEKDAYFULL": "weekday_full",
    "MONTH": "months",
    "LANDMARK": "clock_landmarks",
    "DAYPART": "dayparts",
    "ZONE": "clock_zones",
    "QUANT": "quantifiers",
    "FRACTION": "clock_fractions",
    "CLOCKMIN": "clock_dir_minutes",
    "CLOCKDIR": "clock_dirs",
    "MERIDIEM": "meridiems",
    "SEASON": "seasons",
    "EVENT": "solar_events",
    "SOLARQUAL": "solar_quals",
    "CMUNIT": "scope_units",
    "CYCLE_DAY": "cycle_positions",
    "ERANAME": "regnal_names",
    "ANCHOR_DAY": "roman_anchors",
    "ARCHON": "archon_names",
    "PERIOD": "periods",
    "SCALE": "scales",
    "PART": "period_parts",
    "DECADE": "decade_words",
}

#: slots the matcher binds but whose surfaces are not shipped as ``.voc`` in the
#: locale (engine-derived), so an order using one is never counted unreachable.
_NON_VOC_SLOTS: FrozenSet[str] = frozenset({"HOLIDAY"})

#: known construction names -- the precedence table plus the declared-but-
#: unresolved set are the only names the engine understands.
KNOWN_CONSTRUCTIONS: FrozenSet[str] = frozenset(PRECEDENCE) | UNIMPLEMENTED

#: construction group tags the group gate recognises (see
#: ``extract.__init__``: a tagged construction is OFF unless its group is
#: enabled; ``classical`` is the raw-Latin date family).
KNOWN_GROUPS: FrozenSet[str] = frozenset({"classical"})

#: per-construction flag keys (everything besides ``orders``).
CONSTRUCTION_FLAG_KEYS: FrozenSet[str] = frozenset(
    {"prefer_future", "group", "calendar", "calendar_year_range"})

TOP_LEVEL_KEYS: FrozenSet[str] = frozenset({
    "tokenizer", "constructions", "conventions", "quantifiers", "guards",
    "hook", "lemmas", "suffix_strip", "day_subdivision", "positions",
    "base_grammar"})

#: marker roles whose POSITIONALITY may be declared -- the open-range and
#: recurrence-bound framing words the engine scans for around a date.  Each maps
#: to a per-locale ``marker_<role>.voc`` surface set.
KNOWN_POSITION_ROLES: FrozenSet[str] = frozenset({"until", "since", "for"})

#: where a marker sits relative to its date: ``pre`` leads it (default),
#: ``post`` trails it as a separate bound word, ``affix`` is a suffix fused onto
#: the date's final surface token.
KNOWN_POSITIONS: FrozenSet[str] = frozenset({"pre", "post", "affix"})
TOKENIZER_KEYS: FrozenSet[str] = frozenset({"split_contractions", "ordinal_dot",
                                          "ordinal_dot_max_digits",
                                          "dotted_date", "decimal_comma"})
CONVENTION_KEYS: FrozenSet[str] = frozenset({
    "week_start", "dmy", "hemisphere", "prefer_future", "bare_half_to",
    "bare_quarter_to", "toward_hour_12h", "bare_half_past", "weekend_start",
    "daypart_proper_noun_guard", "since_directional", "bare_at_markers",
    "offset_clock_composes"})
GUARD_KEYS: FrozenSet[str] = frozenset({"bare_year_min_digits"})


def _order_slots(raw: str, errors: List[str], where: str) -> List[str]:
    """Parse an order string into its element names, recording malformations.

    Returns the *required* (non-optional) element names for downstream
    reachability, and appends a message per malformed / unknown token.
    """
    required: List[str] = []
    for tok in raw.split():
        if tok.count("?") > 1 or ("?" in tok and not tok.endswith("?")):
            errors.append(f"{where}: token {tok!r} has malformed optional "
                          f"suffix (a single trailing '?' only)")
            continue
        optional = tok.endswith("?")
        name = tok[:-1] if optional else tok
        if not name:
            errors.append(f"{where}: empty token in order {raw!r}")
            continue
        if name.isupper():
            if name not in SLOT_ALPHABET:
                errors.append(f"{where}: unknown slot {name!r} in order "
                              f"{raw!r} (not bound by matcher)")
                continue
        elif not re.fullmatch(r"[a-z][a-z_]*", name):
            errors.append(f"{where}: malformed connector literal {name!r} in "
                          f"order {raw!r}")
            continue
        if not optional:
            required.append(name)
    return required


def validate_config(cfg: dict, lang: str) -> List[str]:
    """Structural findings over the parsed ``lang.json`` (no vocabulary needed)."""
    errors: List[str] = []
    ctx = f"[{lang}]"

    for key in cfg:
        if key not in TOP_LEVEL_KEYS:
            errors.append(f"{ctx} unknown top-level key {key!r}")
    for key in cfg.get("tokenizer", {}):
        if key not in TOKENIZER_KEYS:
            errors.append(f"{ctx} unknown tokenizer key {key!r}")
    for key in cfg.get("conventions", {}):
        if key not in CONVENTION_KEYS:
            errors.append(f"{ctx} unknown conventions key {key!r}")
    for key in cfg.get("guards", {}):
        if key not in GUARD_KEYS:
            errors.append(f"{ctx} unknown guards key {key!r}")

    bg = cfg.get("base_grammar", {})
    if not isinstance(bg, dict):
        errors.append(f"{ctx} 'base_grammar' must be an object")
    else:
        from chronologia.extract.base_grammar import (BASE_GRAMMAR,
                                                          BASE_GRAMMAR_KEYS,
                                                          KNOB_SCHEMA)
        for key in bg:
            if key not in BASE_GRAMMAR_KEYS:
                errors.append(f"{ctx} unknown base_grammar key {key!r} "
                              f"(known: {sorted(BASE_GRAMMAR_KEYS)})")
        for name in bg.get("disable", []):
            if name not in BASE_GRAMMAR:
                errors.append(f"{ctx} base_grammar disable names non-base "
                              f"construction {name!r}")
        for section in ("override", "extend"):
            for name in bg.get(section, {}):
                if name not in BASE_GRAMMAR:
                    errors.append(f"{ctx} base_grammar {section} names non-base "
                                  f"construction {name!r}")
        for knob, val in KNOB_SCHEMA.items():
            if knob not in bg:
                continue
            knobval = bg[knob]
            if knob == "marker_position" and isinstance(knobval, dict):
                # per-construction mapping {construction: pre|post|both}
                for name, pos in knobval.items():
                    if name not in BASE_GRAMMAR:
                        errors.append(f"{ctx} base_grammar[{knob!r}] names "
                                      f"non-base construction {name!r}")
                    if pos not in val:
                        errors.append(f"{ctx} base_grammar[{knob!r}][{name!r}]="
                                      f"{pos!r} unknown (known: {sorted(val)})")
            elif knobval not in val:
                errors.append(f"{ctx} base_grammar[{knob!r}]={knobval!r} "
                              f"unknown (known: {sorted(val)})")

    positions = cfg.get("positions", {})
    if not isinstance(positions, dict):
        errors.append(f"{ctx} 'positions' must be an object")
    else:
        for role, pos in positions.items():
            if role not in KNOWN_POSITION_ROLES:
                errors.append(f"{ctx} positions: unknown marker role {role!r} "
                              f"(known: {sorted(KNOWN_POSITION_ROLES)})")
            if pos not in KNOWN_POSITIONS:
                errors.append(f"{ctx} positions[{role!r}]: unknown position "
                              f"{pos!r} (known: {sorted(KNOWN_POSITIONS)})")

    for name, body in cfg.get("constructions", {}).items():
        where = f"{ctx} construction {name!r}"
        if name not in KNOWN_CONSTRUCTIONS:
            errors.append(f"{where}: unknown construction name")
        if not isinstance(body, dict):
            errors.append(f"{where}: body must be an object")
            continue
        orders = body.get("orders")
        if not isinstance(orders, list) or not orders:
            errors.append(f"{where}: 'orders' must be a non-empty list")
        else:
            for raw in orders:
                if not isinstance(raw, str):
                    errors.append(f"{where}: order {raw!r} is not a string")
                    continue
                _order_slots(raw, errors, where)
        for key, val in body.items():
            if key == "orders":
                continue
            if key not in CONSTRUCTION_FLAG_KEYS:
                errors.append(f"{where}: unknown flag {key!r}")
            elif key == "group" and val not in KNOWN_GROUPS:
                errors.append(f"{where}: unknown construction group {val!r} "
                              f"(known: {sorted(KNOWN_GROUPS)})")

    for key, forms in cfg.get("quantifiers", {}).items():
        try:
            float(key)
        except (TypeError, ValueError):
            errors.append(f"{ctx} quantifier key {key!r} is not a numeric string")
        if not isinstance(forms, list):
            errors.append(f"{ctx} quantifier {key!r} value must be a list")

    return errors


def _slot_reachable(name: str, spec) -> bool:
    """Whether a required slot / connector name has backing vocabulary in *spec*."""
    if name.isupper():
        if name in NUMERIC_SLOTS or name in _NON_VOC_SLOTS:
            return True
        if name in CONNECTOR_SLOTS:
            return bool(spec.connectors.get(CONNECTOR_SLOTS[name]))
        if name == "CAL_MONTH":
            return bool(spec.calendar_months)
        if name in DUAL_UNIT_SLOTS:
            return bool(spec.scope_units) or bool(spec.units)
        attr = SLOT_VOCAB_ATTR.get(name)
        if attr is None:
            return True  # slot the matcher binds without locale vocab
        return bool(getattr(spec, attr))
    # a lowercase connector literal binds ``spec.connectors[name]``
    return bool(spec.connectors.get(name))


def validate_reachability(spec, cfg: dict, lang: str) -> List[str]:
    """Findings for orders whose required slot/connector has no vocabulary.

    An order that can never fire (a required ``.voc`` is missing or empty in the
    locale) is a defect: dead data that silently disables a construction.
    """
    errors: List[str] = []
    ctx = f"[{lang}]"
    for name, body in cfg.get("constructions", {}).items():
        for raw in body.get("orders", []):
            if not isinstance(raw, str):
                continue
            where = f"{ctx} construction {name!r} order {raw!r}"
            missing = [el for el in _order_slots(raw, [], where)
                       if not _slot_reachable(el, spec)]
            if missing:
                errors.append(f"{where}: unreachable -- no vocabulary for "
                              f"{', '.join(sorted(set(missing)))}")

    # a declared marker positionality is dead unless the locale actually ships
    # the role's marker surfaces (``marker_<role>.voc``): a ``post``/``affix``
    # ``until`` with no ``marker_until`` vocabulary can never fire.
    for role, pos in cfg.get("positions", {}).items():
        if role in KNOWN_POSITION_ROLES and pos in KNOWN_POSITIONS \
                and not spec.connectors.get(role):
            errors.append(f"{ctx} positions[{role!r}]={pos!r}: unreachable -- "
                          f"no marker_{role} vocabulary in this locale")
    return errors


def validate(cfg: dict, lang: str, spec=None) -> None:
    """Validate a locale, raising :class:`LocaleSchemaError` on any finding.

    ``spec`` is a loaded :class:`LangSpec`; when given, reachability is checked
    too.  The loader passes it, so every load is LOUDLY validated.
    """
    errors = validate_config(cfg, lang)
    if spec is not None:
        errors += validate_reachability(spec, cfg, lang)
    if errors:
        raise LocaleSchemaError(lang, errors)
