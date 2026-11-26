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
``jurisdiction_<code>.voc``  country/region-name surface -> jurisdiction code ``code``
``named_day_<off>.voc`` named day at day-offset ``off`` (signed)
``daypart_<name>.voc`` surfaces naming the time-of-day band ``name``
``marker_past.voc``     direction marker, sign -1
``marker_future.voc``   direction marker, sign +1
``marker_next.voc``     relative marker, +1 week
``marker_last.voc``     relative marker, -1 week
``marker_this.voc``     relative marker, current week
``marker_<x>.voc``      connector vocab named ``x`` (e.g. ``of``)
======================  ===========================================

``lang.json`` states facts only: tokenizer switches, construction orders
and per-construction flags, conventions, lemma/suffix tables, guards, and
optional dotted bindings (``numbers``, ``hook``) and the ``number_fold``
knobs of the generic number layer.
"""
from __future__ import annotations

import glob
import json
import os
from functools import lru_cache
from importlib import import_module
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from ovos_spec_tools import LocaleResources, expand, read_resource_file

from dataclasses import replace

from chronologia.calendars import CALENDARS
from chronologia.civil_holidays import well_known_source, well_known_surfaces
from chronologia.extract.base_grammar import merge_orders
from chronologia.extract.compiler import parse_order
from chronologia.extract.model import (Conventions, LangSpec,
                                           TokenizerModes)
from chronologia.extract.normaliser import TemporalNormaliser
from chronologia.extract.numlayer import attach, number_fold
from chronologia.extract.schema import validate as validate_locale
from chronologia.extract.tokenizer import Tokenizer

LOCALE_DIR = os.path.join(os.path.dirname(__file__), os.pardir, "locale")

# LocaleResources reads every language of a tree at construction, and an
# installed tree does not change while the process runs: one instance per
# tree serves every language.
_locale_resources = lru_cache(maxsize=None)(LocaleResources)


# Marks a vocabulary file whose surfaces fill a set instead of a surface -> value map.
_SET = object()

# Files that name a single table: ``marker_<x>.voc`` -> ((table, value), ...).
_EXACT = {
    "marker_past": (("directions", -1),),
    "marker_future": (("directions", 1),),
    "marker_next": (("rel_markers", 1),),
    "marker_last": (("rel_markers", -1),),
    "marker_this": (("rel_markers", 0),),
    "marker_dayparttoday": (("daypart_today_words", _SET),),
    "marker_daypart_past": (("daypart_deictics", "past"),),
    "marker_daypart_future": (("daypart_deictics", "future"),),
    "clock_meridiem_am": (("meridiems", 0),),
    "clock_meridiem_pm": (("meridiems", 12),),
    "clock_meridiem_pm_band": (("meridiems", 12), ("band_meridiems", _SET)),
    "clock_meridiem_late": (("late_meridiems", _SET),),
    "clock_meridiem_am_night": (("meridiems", 0), ("am_night_meridiems", _SET)),
    "clock_meridiem_night": (("meridiems", 12), ("night_meridiems", _SET)),
    "clock_dir_past": (("clock_dirs", 1),),
    "clock_dir_to": (("clock_dirs", -1),),
    "special_weekend": (("weekend_words", _SET),),
    "marker_exclusion": (("exclusion_triggers", _SET),),
    "marker_exclusion_bound": (("exclusion_bound_guards", _SET),),
    "marker_exclusion_coord": (("exclusion_coord", _SET),),
    "marker_exclusion_scope": (("exclusion_scope", _SET),),
    "marker_exclusion_filler": (("exclusion_filler", _SET),),
    "marker_at_counts": (("at_counts", _SET),),
    "marker_counted_noun": (("counted_noun", _SET),),
    "marker_upcoming": (("upcoming", _SET),),
    "marker_alarm_joiner": (("alarm_joiners", _SET),),
}

# ``<prefix><rest>.voc``: every surface maps to ``convert(rest)`` in each
# listed table.  The first matching prefix wins, so a longer prefix precedes
# the shorter one it extends.
_PREFIXED: List[Tuple[str, Tuple[str, ...], Callable[[str], Any]]] = [
    ("unit1_", ("singular_units",), str),
    ("unit_dual_", ("dual_units",), str),
    ("unit_", ("units",), str),
    ("named_day_", ("named_days",), int),
    ("clock_fraction_prev_", ("clock_fractions_prev", "clock_fractions"), int),
    ("clock_fraction_", ("clock_fractions",), int),
    ("clock_dir_minute_", ("clock_dir_minutes",), int),
    ("season_", ("seasons",), str),
    ("solar_event_", ("solar_events",), str),
    ("solar_qual_", ("solar_quals",), str),
    ("scope_unit_", ("scope_units",), str),
    ("jurisdiction_", ("jurisdictions",), str.upper),
    ("roman_anchor_", ("roman_anchors",), str),
    ("archon_", ("archon_names",), str),
    ("period_part_", ("period_parts",), str),
    ("period_", ("periods",), str),
    ("decade_word_", ("decade_words",), int),
    ("clock_landmark_", ("clock_landmarks",), int),
    ("daypart_", ("dayparts",), str),
    ("clock_zone_", ("clock_zones",), int),
]


def _resolve_dotted(ref: Optional[str]) -> Optional[Callable]:
    if not ref:
        return None
    module, _, attr = ref.partition(":")
    return getattr(import_module(module), attr)


def _read_surfaces(lang: str, lang_dir: str, cfg: dict, res) -> Dict[str, List[str]]:
    """Expand every ``.voc`` of the language: file base name -> surfaces.

    The tokenizer drops punctuation, so a surface with internal punctuation
    ("μ.μ.", "week-end") can never equal a token's text.  Each surface is
    therefore also registered in its token-canonical form, and the original is
    kept.
    """
    vocab_map = res.vocabularies(lang)
    tok = cfg.get("tokenizer", {})
    tokenizer = Tokenizer(TokenizerModes(
        split_contractions=tok.get("split_contractions", False),
        ordinal_dot=tok.get("ordinal_dot", False)))
    surfaces = {}
    for path in sorted(glob.glob(os.path.join(lang_dir, "*.voc"))):
        templates = read_resource_file(Path(path))
        samples = dict.fromkeys(
            s for template in templates for s in expand(template, vocab_map))
        out = [s.lower() for s in samples]
        seen = set(out)
        for surface in list(out):
            canon = " ".join(t.text for t in tokenizer.tokenize(surface))
            if canon and canon not in seen:
                seen.add(canon)
                out.append(canon)
        surfaces[os.path.basename(path)[:-len(".voc")]] = out
    return surfaces


def _add_month(tables: dict, lang: str, base: str, surfaces: List[str]) -> None:
    rest = base[len("month_"):]
    if rest.isdigit():
        n = int(rest)
        if not 1 <= n <= 12:
            raise ValueError(
                f"{base}.voc: Gregorian month number {n} out of range 1..12")
        tables["months"].update(dict.fromkeys(surfaces, n))
        return
    # month_<calendar>_<n>.voc
    cal_key, _, num = rest.rpartition("_")
    if cal_key not in CALENDARS:
        raise ValueError(
            f"{base}.voc names unknown calendar {cal_key!r}; "
            f"known: {sorted(CALENDARS)}")
    month_count = CALENDARS[cal_key].month_count
    if not num.isdigit() or not 1 <= int(num) <= month_count:
        raise ValueError(
            f"{base}.voc: month number {num!r} out of range "
            f"1..{month_count} for calendar {cal_key!r}")
    calendars = tables["calendar_months"]
    for other, table in calendars.items():
        for s in surfaces:
            if other != cal_key and s in table:
                raise ValueError(
                    f"surface {s!r} claimed by both calendars "
                    f"{other!r} and {cal_key!r} in language {lang!r}")
    calendars.setdefault(cal_key, {}).update(dict.fromkeys(surfaces, int(num)))


def _add_weekday(tables: dict, lang: str, base: str, surfaces: List[str]) -> None:
    # An abbreviation binds the WEEKDAY slot of the marker-ed orders but not
    # the bare-weekday order, so a short form that is also a common word never
    # resolves to a weekday on its own.
    abbreviated = base.startswith("weekday_abbr_")
    idx = int(base[len("weekday_abbr_" if abbreviated else "weekday_"):])
    if not 0 <= idx <= 6:
        raise ValueError(f"{base}.voc: weekday index {idx} out of range 0..6")
    tables["weekdays"].update(dict.fromkeys(surfaces, idx))
    if not abbreviated:
        tables.setdefault("weekday_full", {}).update(dict.fromkeys(surfaces, idx))


def _add_regnal(tables: dict, lang: str, base: str, surfaces: List[str]) -> None:
    # regnal_<seqkey>_<segname>.voc; the sequence key may contain underscores
    # ("egyptian_low"), so it is the longest registered key that prefixes the name.
    from chronologia.regnal import REGNAL_SEQUENCES
    rest = base[len("regnal_"):]
    seqkey = max((k for k in REGNAL_SEQUENCES
                  if rest == k or rest.startswith(k + "_")),
                 key=len, default=rest.partition("_")[0])
    segname = rest[len(seqkey) + 1:] if rest != seqkey else rest
    tables.setdefault("regnal_names", {}).update(
        dict.fromkeys(surfaces, (seqkey, segname)))


def _add_scale(tables: dict, lang: str, base: str, surfaces: List[str]) -> None:
    # scale_<value>.voc holds mode-independent surfaces; scale_<value>.short.voc
    # and .long.voc hold the surfaces of one dialect scale.  Every surface also
    # lands in ``scales`` so the SCALE slot binds it whatever the mode.
    stem, dot, mode = base[len("scale_"):].rpartition(".")
    if not dot or mode not in ("short", "long"):
        stem, mode = base[len("scale_"):], None
    factor = int(stem)
    scales = tables.setdefault("scales", {})
    if mode is None:
        scales.update(dict.fromkeys(surfaces, factor))
        return
    tables["scales_by_mode"][mode].update(dict.fromkeys(surfaces, factor))
    for s in surfaces:
        scales.setdefault(s, factor)


def _add_cycle(tables: dict, lang: str, base: str, surfaces: List[str]) -> None:
    # cycle_<key>_<n>.voc: day <n> (0-based) of the named day cycle
    key, _, num = base[len("cycle_"):].rpartition("_")
    tables.setdefault("day_cycles", {}).update(dict.fromkeys(surfaces, key))
    tables.setdefault("cycle_positions", {}).update(
        dict.fromkeys(surfaces, int(num)))


_SPECIAL = (
    ("month_", _add_month),
    ("weekday_", _add_weekday),
    ("regnal_", _add_regnal),
    ("scale_", _add_scale),
    ("cycle_", _add_cycle),
)


def _fill(tables: dict, table: str, surfaces: List[str], value: Any) -> None:
    if value is _SET:
        tables.setdefault(table, set()).update(surfaces)
    else:
        tables.setdefault(table, {}).update(dict.fromkeys(surfaces, value))


def _load_vocabulary(lang: str, surfaces_by_file: Dict[str, List[str]]) -> dict:
    """Fill the LangSpec vocabulary tables from the ``.voc`` file names."""
    tables: Dict[str, Any] = {name: {} for name in (
        "months", "weekdays", "units", "named_days", "directions",
        "rel_markers", "connectors", "calendar_months")}
    tables["scales_by_mode"] = {"short": {}, "long": {}}
    for base, surfaces in surfaces_by_file.items():
        for prefix, add in _SPECIAL:
            if base.startswith(prefix):
                add(tables, lang, base, surfaces)
                break
        else:
            if base in _EXACT:
                for table, value in _EXACT[base]:
                    _fill(tables, table, surfaces, value)
                continue
            for prefix, targets, convert in _PREFIXED:
                if base.startswith(prefix):
                    value = convert(base[len(prefix):])
                    for table in targets:
                        _fill(tables, table, surfaces, value)
                    break
            else:
                if base.startswith("marker_"):
                    tables["connectors"][base[len("marker_"):]] = frozenset(surfaces)
    return {name: frozenset(t) if isinstance(t, set) else t
            for name, t in tables.items()}


def _plural_units(units: dict, scope_units: dict, singular_units: dict) -> frozenset:
    """Unit surfaces that are the plural of a unit word.

    The scoped-ordinal reading is vetoed for them: "the two <unit>s of June"
    is a count, "the second <unit> of June" an ordinal.  A locale that ships
    ``unit1_<kind>.voc`` states its singulars, and every other unit surface is
    plural.  Without them a surface is plural when another same-kind surface
    plus ``s``/``es`` (or ``y`` -> ``ies``) spells it.
    """
    all_units = {**units, **scope_units}
    if singular_units:
        return frozenset(s for s in all_units if s not in singular_units)
    return frozenset(
        s for s, kind in all_units.items()
        if (s.endswith("s")
            and ((s[:-1] in all_units and all_units[s[:-1]] == kind)
                 or (s.endswith("es") and s[:-2] in all_units
                     and all_units[s[:-2]] == kind)
                 or (s.endswith("ies") and s[:-3] + "y" in all_units
                     and all_units[s[:-3] + "y"] == kind))))


def _load_constructions(cfg: dict) -> Tuple[dict, dict]:
    """Merge the shared base grammar onto the locale's inline orders.

    A base order is only ever appended, so a locale never loses an inline order.
    """
    constructions = cfg.get("constructions", {})
    inline_orders = {name: list(body["orders"])
                     for name, body in constructions.items()}
    orders = {name: tuple(parse_order(name, raw) for raw in raws)
              for name, raws in merge_orders(cfg, inline_orders).items()}
    flags = {name: {k: v for k, v in body.items() if k != "orders"}
             for name, body in constructions.items()}
    return orders, flags


def _conventions(conv: dict) -> Conventions:
    return Conventions(
        week_start=conv.get("week_start", "monday"),
        dmy=conv.get("dmy", True),
        hemisphere=conv.get("hemisphere"),
        prefer_future=conv.get("prefer_future", True),
        bare_half_to=conv.get("bare_half_to", False),
        bare_quarter_to=conv.get("bare_quarter_to", False),
        toward_hour_12h=conv.get("toward_hour_12h", False),
        bare_half_past=conv.get("bare_half_past", False),
        bare_quarter_past=conv.get("bare_quarter_past", False),
        since_directional=conv.get("since_directional", False),
        duration_count_follows_unit=conv.get(
            "duration_count_follows_unit", False),
        daypart_proper_noun_guard=conv.get(
            "daypart_proper_noun_guard", False),
        bare_at_markers=frozenset(conv.get("bare_at_markers", ())),
        clock_of_recurrence=conv.get("clock_of_recurrence", False),
        weekend_start=conv.get("weekend_start", 5))


def _tokenizer_modes(tok: dict) -> TokenizerModes:
    return TokenizerModes(
        split_contractions=tok.get("split_contractions", False),
        ordinal_dot=tok.get("ordinal_dot", False),
        ordinal_dot_max_digits=tok.get("ordinal_dot_max_digits"),
        dotted_date=tok.get("dotted_date", False),
        decimal_comma=tok.get("decimal_comma", False),
        dotted_clock=tok.get("dotted_clock", False))


def _load_holidays(spec: LangSpec) -> Tuple[Dict[str, str], Dict[str, str]]:
    """Holiday surfaces from the holidays engine, in the matcher's token form.

    Each surface runs through the same tokenizer, normaliser and hook as the
    matcher, so a multi-word or inflected surface ("corpo de deus") is keyed
    exactly as the token stream presents it.
    """
    holidays: Dict[str, str] = {}
    sources: Dict[str, str] = {}
    tokenizer = Tokenizer(spec.tokenizer)
    normaliser = TemporalNormaliser(spec)
    for surface, key in well_known_surfaces(spec.lang).items():
        toks = attach(normaliser.normalise(tokenizer.tokenize(surface)),
                      surface, spec.lang)
        if spec.hook is not None:
            toks = spec.hook(toks)
        if not toks:
            continue
        holidays[" ".join(t.text for t in toks)] = key
        sources[key] = well_known_source(key, spec.lang)
    return holidays, sources


def _load_zone_cities(lang_dir: str, cfg: dict) -> Dict[str, str]:
    """``zone_cities.json``: every pattern x city-name surface -> IANA zone.

    Each surface is stored in its token-canonical form, so a merged token
    ("new york time") equals it whatever the punctuation ("New York-tid")."""
    path = os.path.join(lang_dir, "zone_cities.json")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    tokenizer = Tokenizer(_tokenizer_modes(cfg.get("tokenizer", {})))
    out = {}
    for zone, names in data["cities"].items():
        for name in names:
            for pattern in data["patterns"]:
                surface = pattern.format(city=name).lower()
                out[" ".join(t.text for t in tokenizer.tokenize(surface))] = zone
    return out


def load_lang_spec(lang: str, locale_dir: str = LOCALE_DIR) -> LangSpec:
    lang_dir = os.path.join(locale_dir, lang)
    with open(os.path.join(lang_dir, "lang.json"), encoding="utf-8") as fh:
        cfg = json.load(fh)

    vocabulary = _load_vocabulary(lang, _read_surfaces(
        lang, lang_dir, cfg, _locale_resources(locale_dir)))
    orders, flags = _load_constructions(cfg)
    if "number_fold" in cfg:
        hook, pre_hook = number_fold(lang, cfg["number_fold"])
    else:
        hook = _resolve_dotted(cfg.get("hook"))
        pre_hook = _resolve_dotted(cfg.get("pre_hook"))

    spec = LangSpec(
        lang=lang,
        **vocabulary,
        plural_units=_plural_units(vocabulary["units"],
                                   vocabulary.get("scope_units", {}),
                                   vocabulary.get("singular_units", {})),
        lemmas=cfg.get("lemmas", {}),
        suffix_strip=tuple(tuple(pair) for pair in cfg.get("suffix_strip", [])),
        orders=orders, construction_flags=flags,
        conventions=_conventions(cfg.get("conventions", {})),
        tokenizer=_tokenizer_modes(cfg.get("tokenizer", {})),
        guards=cfg.get("guards", {}),
        hook=hook,
        pre_hook=pre_hook,
        post_hook=_resolve_dotted(cfg.get("post_hook")),
        day_subdivision=cfg.get("day_subdivision"),
        quantifiers={s: float(val)
                     for val, forms in cfg.get("quantifiers", {}).items()
                     for s in forms},
        positions=cfg.get("positions", {}),
        zone_cities=_load_zone_cities(lang_dir, cfg))

    # Bad locale data raises here, with locale and field context, instead of
    # silently disabling a construction.
    validate_locale(cfg, lang, spec)

    holidays, holiday_sources = _load_holidays(spec)
    return replace(spec, holidays=holidays, holiday_sources=holiday_sources)
