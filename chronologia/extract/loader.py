"""Load a :class:`LangSpec` from ``locale/<lang>/lang.json`` + ``*.voc``.

Same loading convention as ``eras_scan.load_era_patterns`` -- vocab files
are read through ``ovos_spec_tools.LocaleResources`` so ``(a|b)`` /
``[optional]`` expansion applies uniformly.

Slot *values* are facts encoded in the filename (the loader's only
convention, keeping behaviour out of the JSON):

======================  ===========================================
filename                meaning
======================  ===========================================
``month_<n>.voc``       month number ``n`` (1..12)
``weekday_<n>.voc``     weekday index ``n`` (0 == Monday)
``unit_<kind>.voc``     offset unit ``kind`` (day/week/month/year/...)
``named_day_<off>.voc`` named day at day-offset ``off`` (signed)
``marker_past.voc``     direction marker, sign -1
``marker_future.voc``   direction marker, sign +1
``marker_next.voc``     relative marker, +1 week
``marker_last.voc``     relative marker, -1 week
``marker_this.voc``     relative marker, current week
``marker_<x>.voc``      connector vocab named ``x`` (e.g. ``of``)
======================  ===========================================

``lang.json`` states facts only: tokenizer switches, construction orders
and per-construction flags, conventions, lemma/suffix tables, guards, and
optional dotted bindings (``numbers``, ``hook``).
"""
from __future__ import annotations

import glob
import json
import os
from importlib import import_module
from typing import Callable, Dict, Optional

from ovos_spec_tools import LocaleResources

from chronologia.calendars import CALENDARS
from chronologia.extract.compiler import parse_order
from chronologia.extract.model import (Conventions, LangSpec,
                                           TokenizerModes)

LOCALE_DIR = os.path.join(os.path.dirname(__file__), os.pardir, "locale")


def _resolve_dotted(ref: Optional[str]) -> Optional[Callable]:
    if not ref:
        return None
    module, _, attr = ref.partition(":")
    return getattr(import_module(module), attr)


def load_lang_spec(lang: str, locale_dir: str = LOCALE_DIR) -> LangSpec:
    res = LocaleResources(locale_dir)
    lang_dir = os.path.join(locale_dir, lang)

    with open(os.path.join(lang_dir, "lang.json"), encoding="utf-8") as fh:
        cfg = json.load(fh)

    def forms(base):
        return [f.lower() for f in res.load_vocabulary(base, lang)]

    months: Dict[str, int] = {}
    weekdays: Dict[str, int] = {}
    units: Dict[str, str] = {}
    named_days: Dict[str, int] = {}
    directions: Dict[str, int] = {}
    rel_markers: Dict[str, int] = {}
    connectors: Dict[str, frozenset] = {}
    calendar_months: Dict[str, Dict[str, int]] = {}
    cal_surface_owner: Dict[str, str] = {}   # surface -> calendar, collision guard
    clock_fractions: Dict[str, int] = {}
    meridiems: Dict[str, int] = {}
    clock_dirs: Dict[str, int] = {}
    seasons: Dict[str, str] = {}
    scope_units: Dict[str, str] = {}
    ordinal_suffixes: list = []
    day_cycles: Dict[str, str] = {}
    cycle_positions: Dict[str, int] = {}
    regnal_names: Dict[str, tuple] = {}
    roman_anchors: Dict[str, str] = {}
    periods: Dict[str, str] = {}
    scales: Dict[str, int] = {}
    period_parts: Dict[str, str] = {}
    decade_words: Dict[str, int] = {}
    clock_landmarks: Dict[str, int] = {}

    for path in sorted(glob.glob(os.path.join(lang_dir, "*.voc"))):
        base = os.path.basename(path)[:-len(".voc")]
        surfaces = forms(base)
        if base.startswith("month_"):
            rest = base[len("month_"):]
            if rest.isdigit():
                months.update({s: int(rest) for s in surfaces})
            else:                          # month_<calendar>_<n>.voc
                cal_key, _, num = rest.rpartition("_")
                if cal_key not in CALENDARS:
                    raise ValueError(
                        f"{base}.voc names unknown calendar {cal_key!r}; "
                        f"known: {sorted(CALENDARS)}")
                table = calendar_months.setdefault(cal_key, {})
                for s in surfaces:
                    if s in cal_surface_owner and cal_surface_owner[s] != cal_key:
                        raise ValueError(
                            f"surface {s!r} claimed by both calendars "
                            f"{cal_surface_owner[s]!r} and {cal_key!r} in "
                            f"language {lang!r}")
                    cal_surface_owner[s] = cal_key
                    table[s] = int(num)
        elif base.startswith("weekday_"):
            weekdays.update({s: int(base[len("weekday_"):]) for s in surfaces})
        elif base.startswith("unit_"):
            units.update({s: base[len("unit_"):] for s in surfaces})
        elif base.startswith("named_day_"):
            off = int(base[len("named_day_"):])
            named_days.update({s: off for s in surfaces})
        elif base == "marker_past":
            directions.update({s: -1 for s in surfaces})
        elif base == "marker_future":
            directions.update({s: 1 for s in surfaces})
        elif base == "marker_next":
            rel_markers.update({s: 1 for s in surfaces})
        elif base == "marker_last":
            rel_markers.update({s: -1 for s in surfaces})
        elif base == "marker_this":
            rel_markers.update({s: 0 for s in surfaces})
        elif base.startswith("clock_fraction_"):
            n = int(base[len("clock_fraction_"):])
            clock_fractions.update({s: n for s in surfaces})
        elif base == "clock_meridiem_am":
            meridiems.update({s: 0 for s in surfaces})
        elif base == "clock_meridiem_pm":
            meridiems.update({s: 12 for s in surfaces})
        elif base == "clock_dir_past":
            clock_dirs.update({s: 1 for s in surfaces})
        elif base == "clock_dir_to":
            clock_dirs.update({s: -1 for s in surfaces})
        elif base.startswith("season_"):
            name = base[len("season_"):]
            seasons.update({s: name for s in surfaces})
        elif base.startswith("scope_unit_"):
            kind = base[len("scope_unit_"):]
            scope_units.update({s: kind for s in surfaces})
        elif base.startswith("regnal_"):
            # regnal_<seqkey>_<segname>.voc: segment of a regnal sequence
            seqkey, _, segname = base[len("regnal_"):].partition("_")
            for s in surfaces:
                regnal_names[s] = (seqkey, segname)
        elif base.startswith("roman_anchor_"):
            anchor_name = base[len("roman_anchor_"):]
            for s in surfaces:
                roman_anchors[s] = anchor_name
        elif base.startswith("period_part_"):
            part = base[len("period_part_"):]
            for s in surfaces:
                period_parts[s] = part
        elif base.startswith("period_"):
            # period_<chronologia key>.voc  (key may itself contain "_")
            key = base[len("period_"):]
            for s in surfaces:
                periods[s] = key
        elif base.startswith("scale_"):
            factor = int(base[len("scale_"):])
            for s in surfaces:
                scales[s] = factor
        elif base.startswith("decade_word_"):
            tens = int(base[len("decade_word_"):])
            for s in surfaces:
                decade_words[s] = tens
        elif base.startswith("clock_landmark_"):
            mins = int(base[len("clock_landmark_"):])
            for s in surfaces:
                clock_landmarks[s] = mins
        elif base.startswith("cycle_"):
            # cycle_<key>_<n>.voc: day <n> (0-based) of the named day cycle
            key, _, num = base[len("cycle_"):].rpartition("_")
            for s in surfaces:
                day_cycles[s] = key
                cycle_positions[s] = int(num)
        elif base.startswith("marker_"):
            connectors[base[len("marker_"):]] = frozenset(surfaces)

    quantifiers = {s: float(val) for val, forms_ in cfg.get("quantifiers", {}).items()
                   for s in forms_}

    orders = {name: tuple(parse_order(name, raw) for raw in body["orders"])
              for name, body in cfg.get("constructions", {}).items()}
    flags = {name: {k: v for k, v in body.items() if k != "orders"}
             for name, body in cfg.get("constructions", {}).items()}

    conv = cfg.get("conventions", {})
    tok = cfg.get("tokenizer", {})

    return LangSpec(
        lang=lang,
        months=months, weekdays=weekdays, units=units,
        named_days=named_days, directions=directions,
        rel_markers=rel_markers, connectors=connectors,
        calendar_months={k: dict(v) for k, v in calendar_months.items()},
        lemmas=cfg.get("lemmas", {}),
        suffix_strip=tuple(tuple(pair) for pair in cfg.get("suffix_strip", [])),
        orders=orders, construction_flags=flags,
        conventions=Conventions(
            week_start=conv.get("week_start", "monday"),
            dmy=conv.get("dmy", True),
            hemisphere=conv.get("hemisphere"),
            prefer_future=conv.get("prefer_future", True),
            bare_half_to=conv.get("bare_half_to", False)),
        tokenizer=TokenizerModes(
            split_contractions=tok.get("split_contractions", False),
            ordinal_dot=tok.get("ordinal_dot", False)),
        guards=cfg.get("guards", {}),
        hook=_resolve_dotted(cfg.get("hook")),
        clock_fractions=clock_fractions, meridiems=meridiems,
        clock_dirs=clock_dirs, seasons=seasons, scope_units=scope_units,
        ordinal_suffixes=tuple(ordinal_suffixes),
        day_cycles=day_cycles, cycle_positions=cycle_positions,
        day_subdivision=cfg.get("day_subdivision"),
        regnal_names=regnal_names, roman_anchors=roman_anchors,
        periods=periods, scales=scales, period_parts=period_parts,
        decade_words=decade_words, clock_landmarks=clock_landmarks,
        quantifiers=quantifiers)
