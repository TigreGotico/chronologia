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
optional dotted bindings (``numbers``, ``hook``).
"""
from __future__ import annotations

import glob
import json
import os
from importlib import import_module
from pathlib import Path
from typing import Callable, Dict, Optional, Set

from ovos_spec_tools import LocaleResources, expand, read_resource_file

from dataclasses import replace

from chronologia.calendars import CALENDARS
from chronologia.civil_holidays import well_known_source, well_known_surfaces
from chronologia.extract.base_grammar import merge_orders
from chronologia.extract.compiler import parse_order
from chronologia.extract.model import (Conventions, LangSpec,
                                           TokenizerModes)
from chronologia.extract.normaliser import TemporalNormaliser
from chronologia.extract.schema import validate as validate_locale
from chronologia.extract.tokenizer import Tokenizer

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

    # Expand every ``.voc`` against the language's vocabulary map computed
    # ONCE.  ``LocaleResources.load_vocabulary`` recomputes ``vocabularies()``
    # -- an rglob over the whole locale tree plus a re-read of every file --
    # on *each* call; with ~220 vocabulary files per locale that is quadratic
    # (the tree is re-scanned once per file loaded).  We do the byte-identical
    # expansion (``ovos_spec_tools.expand`` over the same name->templates map)
    # but read the tree a single time, turning first-call locale loading from
    # O(files^2) into O(files).
    vocab_map = res.vocabularies(lang)

    # The tokenizer emits letter runs and DISCARDS punctuation, so a shipped
    # surface written with internal punctuation ("μ.μ.", "π. χ.", "ap. j.-c.",
    # "week-end") can never equal a token's text -- it is dead vocabulary by
    # construction, and the slot it feeds silently falls into the remainder.
    # The hyphen is as fatal as the dot and less obvious about it: English
    # "week-end" split into "week" and "end", the unit noun "week" claimed the
    # first half and the second was stranded, so "this week-end" quietly read
    # as the whole week.  Every surface is
    # therefore ALSO registered in its token-canonical form: the surface run
    # through this language's own tokenizer, tokens space-joined -- exactly the
    # canonicalisation the holiday surfaces below already use.  Multi-token
    # canonical forms ("μ μ") are glued back by ``pipeline.merge_multiword``,
    # the same pass that binds "bronze age" or "öğleden sonra"; multiword
    # connectors are bound natively by the matcher's ``_connector_span``.  The
    # original dotted surface is kept as well, so nothing that matched before
    # stops matching.
    surface_tokenizer = Tokenizer(TokenizerModes(
        split_contractions=cfg.get("tokenizer", {}).get("split_contractions", False),
        ordinal_dot=cfg.get("tokenizer", {}).get("ordinal_dot", False)))

    def _canonical(surface: str) -> str:
        return " ".join(t.text for t in surface_tokenizer.tokenize(surface))

    def forms(base):
        samples: list = []
        for template in read_resource_file(Path(lang_dir) / (base + ".voc")):
            for sample in expand(template, vocab_map):
                if sample not in samples:
                    samples.append(sample)
        out = [f.lower() for f in samples]
        for f in list(out):
            canon = _canonical(f)
            if canon and canon not in out:
                out.append(canon)
        return out

    months: Dict[str, int] = {}
    weekdays: Dict[str, int] = {}
    weekday_full: Dict[str, int] = {}
    units: Dict[str, str] = {}
    singular_units: Dict[str, str] = {}
    named_days: Dict[str, int] = {}
    directions: Dict[str, int] = {}
    rel_markers: Dict[str, int] = {}
    connectors: Dict[str, frozenset] = {}
    calendar_months: Dict[str, Dict[str, int]] = {}
    cal_surface_owner: Dict[str, str] = {}   # surface -> calendar, collision guard
    clock_fractions: Dict[str, int] = {}
    clock_fractions_prev: Dict[str, int] = {}
    clock_dir_minutes: Dict[str, int] = {}
    meridiems: Dict[str, int] = {}
    night_meridiems: Set[str] = set()
    clock_dirs: Dict[str, int] = {}
    seasons: Dict[str, str] = {}
    solar_events: Dict[str, str] = {}
    solar_quals: Dict[str, str] = {}
    scope_units: Dict[str, str] = {}
    dual_units: Dict[str, str] = {}
    ordinal_suffixes: list = []
    day_cycles: Dict[str, str] = {}
    cycle_positions: Dict[str, int] = {}
    regnal_names: Dict[str, tuple] = {}
    roman_anchors: Dict[str, str] = {}
    archon_names: Dict[str, str] = {}
    periods: Dict[str, str] = {}
    scales: Dict[str, int] = {}
    scales_by_mode: Dict[str, Dict[str, int]] = {"short": {}, "long": {}}
    period_parts: Dict[str, str] = {}
    decade_words: Dict[str, int] = {}
    clock_landmarks: Dict[str, int] = {}
    dayparts: Dict[str, str] = {}
    daypart_deictics: Dict[str, str] = {}
    daypart_today_words: Set[str] = set()
    clock_zones: Dict[str, int] = {}
    weekend_words: Set[str] = set()
    exclusion_triggers: Set[str] = set()
    exclusion_bound_guards: Set[str] = set()
    exclusion_coord: Set[str] = set()
    exclusion_scope: Set[str] = set()
    exclusion_filler: Set[str] = set()
    jurisdictions: Dict[str, str] = {}

    for path in sorted(glob.glob(os.path.join(lang_dir, "*.voc"))):
        base = os.path.basename(path)[:-len(".voc")]
        surfaces = forms(base)
        if base.startswith("month_"):
            rest = base[len("month_"):]
            if rest.isdigit():
                n = int(rest)
                if not 1 <= n <= 12:
                    raise ValueError(
                        f"{base}.voc: Gregorian month number {n} out of "
                        f"range 1..12")
                months.update({s: n for s in surfaces})
            else:                          # month_<calendar>_<n>.voc
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
                table = calendar_months.setdefault(cal_key, {})
                for s in surfaces:
                    if s in cal_surface_owner and cal_surface_owner[s] != cal_key:
                        raise ValueError(
                            f"surface {s!r} claimed by both calendars "
                            f"{cal_surface_owner[s]!r} and {cal_key!r} in "
                            f"language {lang!r}")
                    cal_surface_owner[s] = cal_key
                    table[s] = int(num)
        elif base.startswith("weekday_abbr_"):
            # abbreviations bind the WEEKDAY slot (marker-ed orders) but NOT
            # the bare-weekday order, so short forms that are also common words
            # never resolve to a weekday on their own
            idx = int(base[len("weekday_abbr_"):])
            if not 0 <= idx <= 6:
                raise ValueError(
                    f"{base}.voc: weekday index {idx} out of range 0..6")
            weekdays.update({s: idx for s in surfaces})
        elif base.startswith("weekday_"):
            idx = int(base[len("weekday_"):])
            if not 0 <= idx <= 6:
                raise ValueError(
                    f"{base}.voc: weekday index {idx} out of range 0..6")
            weekdays.update({s: idx for s in surfaces})
            weekday_full.update({s: idx for s in surfaces})
        elif base.startswith("unit1_"):
            singular_units.update({s: base[len("unit1_"):] for s in surfaces})
        elif base.startswith("unit_dual_"):
            # dual-noun unit surface (Semitic ساعتان / שעתיים == "two hours");
            # read as (2 x unit) by the duration engine, kept out of ``units``.
            dual_units.update({s: base[len("unit_dual_"):] for s in surfaces})
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
        elif base == "marker_dayparttoday":
            # a bare daypart surface lexically fused with TODAY ("tonight",
            # "vanavond") -- carries no REL_MARKER of its own, but anchors
            # exactly as "this <daypart>" does.
            daypart_today_words.update(surfaces)
        elif base == "marker_daypart_past":
            # deictic daypart selector picking the NEAREST PAST occurrence of a
            # time-of-day band (Indonesian "tadi" -- "tadi pagi" = this (past)
            # morning, "tadi malam" = last night); the day it lands on is not a
            # fixed offset but depends on whether today's band has begun.
            daypart_deictics.update({s: "past" for s in surfaces})
        elif base == "marker_daypart_future":
            # deictic daypart selector picking the NEAREST FUTURE occurrence of a
            # time-of-day band (Indonesian "nanti" -- "nanti malam" = tonight,
            # "nanti pagi" = tomorrow morning).
            daypart_deictics.update({s: "future" for s in surfaces})
        elif base.startswith("clock_fraction_prev_"):
            # a bare fraction naming a position in the hour BEFORE the one
            # spoken ("पौने दस" == 09:45).  Unioned into clock_fractions too, so
            # the FRACTION slot binds it exactly as any other fraction word.
            n = int(base[len("clock_fraction_prev_"):])
            clock_fractions_prev.update({s: n for s in surfaces})
            clock_fractions.update({s: n for s in surfaces})
        elif base.startswith("clock_fraction_"):
            n = int(base[len("clock_fraction_"):])
            clock_fractions.update({s: n for s in surfaces})
        elif base.startswith("clock_dir_minute_"):
            n = int(base[len("clock_dir_minute_"):])
            clock_dir_minutes.update({s: n for s in surfaces})
        elif base == "clock_meridiem_am":
            meridiems.update({s: 0 for s in surfaces})
        elif base == "clock_meridiem_pm":
            meridiems.update({s: 12 for s in surfaces})
        elif base == "clock_meridiem_night":
            # The NIGHT daypart is a BAND crossing midnight, not a uniform +12
            # PM shift: "the one at night" is 01:00, not 13:00.  Surfaces are
            # unioned into ``meridiems`` (value unused) so the MERIDIEM slot
            # binds them, and tracked in ``night_meridiems`` so the resolver
            # applies the midnight-crossing band-split instead of a flat offset.
            meridiems.update({s: 12 for s in surfaces})
            night_meridiems.update(surfaces)
        elif base == "clock_dir_past":
            clock_dirs.update({s: 1 for s in surfaces})
        elif base == "clock_dir_to":
            clock_dirs.update({s: -1 for s in surfaces})
        elif base.startswith("season_"):
            name = base[len("season_"):]
            seasons.update({s: name for s in surfaces})
        elif base.startswith("solar_event_"):
            # solar_event_<kind>.voc: the astronomical-event word, kind is
            # "solstice" or "equinox" (chronologia.equinoxes, Meeus ch.27)
            kind = base[len("solar_event_"):]
            solar_events.update({s: kind for s in surfaces})
        elif base.startswith("solar_qual_"):
            # solar_qual_<season>.voc: a formal equinox qualifier that is NOT a
            # plain season word (vernal -> spring, autumnal -> autumn), so it
            # binds only the solar_event construction and never season_ref
            name = base[len("solar_qual_"):]
            solar_quals.update({s: name for s in surfaces})
        elif base.startswith("scope_unit_"):
            kind = base[len("scope_unit_"):]
            scope_units.update({s: kind for s in surfaces})
        elif base.startswith("jurisdiction_"):
            # jurisdiction_<code>.voc: country/region-name surfaces resolving
            # to the civil-holidays engine's jurisdiction code ("every holiday
            # in Portugal" -> "pt" -> "PT"). Per-locale opt-in vocab, like
            # every other surface table here -- never a shared cross-locale
            # list. An unmapped country name simply has no surface anywhere
            # and the "every holiday in <X>" finder declines to match it.
            code = base[len("jurisdiction_"):].upper()
            jurisdictions.update({s: code for s in surfaces})
        elif base.startswith("regnal_"):
            # regnal_<seqkey>_<segname>.voc: segment of a regnal sequence.  The
            # sequence key may itself contain underscores ("egyptian_low"), so
            # match it against the registered keys greedily (longest prefix)
            # rather than splitting on the first underscore.
            from chronologia.regnal import REGNAL_SEQUENCES
            rest = base[len("regnal_"):]
            seqkey = max((k for k in REGNAL_SEQUENCES
                          if rest == k or rest.startswith(k + "_")),
                         key=len, default=rest.partition("_")[0])
            segname = rest[len(seqkey) + 1:] if rest != seqkey else rest
            for s in surfaces:
                regnal_names[s] = (seqkey, segname)
        elif base.startswith("roman_anchor_"):
            anchor_name = base[len("roman_anchor_"):]
            for s in surfaces:
                roman_anchors[s] = anchor_name
        elif base.startswith("archon_"):
            # archon_<key>.voc: eponymous archon of Athens (key indexes
            # chronologia.archons.ARCHONS)
            archon_key = base[len("archon_"):]
            for s in surfaces:
                archon_names[s] = archon_key
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
            # ``scale_<value>.voc``       -> mode-independent surface (base)
            # ``scale_<value>.short.voc`` -> surface valid under the SHORT scale
            # ``scale_<value>.long.voc``  -> surface valid under the LONG scale
            # The dialect-ambiguous billion-cognate ships in BOTH a short file
            # (10^9) and a long file (10^12); the resolver reads the active
            # mode's table first, falling back to the base ``scales`` map.  Every
            # surface -- base or mode-tagged -- is unioned into ``scales`` so the
            # SCALE slot binds it whatever the mode.
            rest = base[len("scale_"):]
            mode = None
            for suffix in ("short", "long"):
                if rest.endswith("." + suffix):
                    mode = suffix
                    rest = rest[: -len("." + suffix)]
                    break
            factor = int(rest)
            for s in surfaces:
                if mode is None:
                    scales[s] = factor
                else:
                    scales_by_mode[mode][s] = factor
                    scales.setdefault(s, factor)
        elif base.startswith("decade_word_"):
            tens = int(base[len("decade_word_"):])
            for s in surfaces:
                decade_words[s] = tens
        elif base.startswith("clock_landmark_"):
            mins = int(base[len("clock_landmark_"):])
            for s in surfaces:
                clock_landmarks[s] = mins
        elif base.startswith("daypart_"):
            # daypart_<name>.voc: surfaces naming the time-of-day band <name>
            # (band boundaries live in chronologia.dayparts, CLDR-cited)
            name = base[len("daypart_"):]
            for s in surfaces:
                dayparts[s] = name
        elif base.startswith("clock_zone_"):
            mins = int(base[len("clock_zone_"):])
            for s in surfaces:
                clock_zones[s] = mins
        elif base == "special_weekend":
            weekend_words.update(surfaces)
        elif base == "marker_exclusion":
            exclusion_triggers.update(s.lower() for s in surfaces)
        elif base == "marker_exclusion_bound":
            exclusion_bound_guards.update(s.lower() for s in surfaces)
        elif base == "marker_exclusion_coord":
            exclusion_coord.update(s.lower() for s in surfaces)
        elif base == "marker_exclusion_scope":
            exclusion_scope.update(s.lower() for s in surfaces)
        elif base == "marker_exclusion_filler":
            exclusion_filler.update(s.lower() for s in surfaces)
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

    # Merge the shared BASE GRAMMAR (a construction's default orders, inherited
    # by every locale) onto this locale's inline ``constructions`` orders,
    # honouring its ``base_grammar`` block (disable / override / extend).  The
    # merge is an ADDITIVE SUPERSET: a base order is only ever appended, so a
    # locale can never lose an inline order it already declared.
    inline_orders = {name: list(body["orders"])
                     for name, body in cfg.get("constructions", {}).items()}
    merged_orders = merge_orders(cfg, inline_orders)
    orders = {name: tuple(parse_order(name, raw) for raw in raws)
              for name, raws in merged_orders.items()}
    flags = {name: {k: v for k, v in body.items() if k != "orders"}
             for name, body in cfg.get("constructions", {}).items()}

    conv = cfg.get("conventions", {})
    tok = cfg.get("tokenizer", {})

    # ``plural_units`` collects every unit surface that is NOT a singular unit
    # word, so the scoped-ordinal resolver can veto "the two <unit>s of June" (a
    # bare COUNT) while still resolving "the second <unit> of June" (a true
    # ordinal).  Both ``units`` and ``scope_units`` feed the check so a plural
    # SEL_UNIT is caught too.
    #
    # Preferred derivation -- correct by construction: when a locale ships
    # explicit ``unit1_<kind>.voc`` singular vocab (``singular_units``), a
    # surface is plural iff it is a real unit surface that is NOT one of those
    # listed singulars.  This covers non-``-s`` plurals -- Italian giorno/giorni,
    # Dutch dag/dagen, Russian case-based день/дня -- and never mis-flags the
    # German genitive-singular jahres/monats, because a locale's own listed
    # singulars decide the split.
    #
    # Fallback -- ``-s``/``-es``/``-ies`` morphology: for a locale WITHOUT
    # ``unit1_`` files (en/es/fr/de/pt), a unit surface is plural when another
    # same-kind surface plus an ``-s``/``-es`` ending spells it (day+s ->
    # days, fortnight+s -> fortnights), or a same-kind ``y``-ending surface
    # with ``y`` swapped for ``ies`` spells it (century -> centuries). The
    # relation IS the plural, so it never mis-flags a singular; a non-``-s``
    # language with no ``unit1_`` files produces an empty set and its scoped
    # readings are left untouched.
    _all_units = {**units, **scope_units}
    if singular_units:
        plural_units = frozenset(
            s for s in _all_units if s not in singular_units)
    else:
        plural_units = frozenset(
            s for s, kind in _all_units.items()
            if (s.endswith("s")
                and ((s[:-1] in _all_units and _all_units[s[:-1]] == kind)
                     or (s.endswith("es") and s[:-2] in _all_units
                         and _all_units[s[:-2]] == kind)
                     or (s.endswith("ies") and s[:-3] + "y" in _all_units
                         and _all_units[s[:-3] + "y"] == kind))))

    spec = LangSpec(
        lang=lang,
        months=months, weekdays=weekdays, units=units,
        singular_units=singular_units,
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
            weekend_start=conv.get("weekend_start", 5),
            offset_clock_composes=conv.get(
                "offset_clock_composes", False)),
        tokenizer=TokenizerModes(
            split_contractions=tok.get("split_contractions", False),
            ordinal_dot=tok.get("ordinal_dot", False),
            ordinal_dot_max_digits=tok.get("ordinal_dot_max_digits"),
            dotted_date=tok.get("dotted_date", False),
            decimal_comma=tok.get("decimal_comma", False),
            dotted_clock=tok.get("dotted_clock", False)),
        guards=cfg.get("guards", {}),
        hook=_resolve_dotted(cfg.get("hook")),
        pre_hook=_resolve_dotted(cfg.get("pre_hook")),
        clock_fractions=clock_fractions,
        clock_fractions_prev=clock_fractions_prev,
        clock_dir_minutes=clock_dir_minutes,
        meridiems=meridiems,
        night_meridiems=frozenset(night_meridiems),
        clock_dirs=clock_dirs, seasons=seasons,
        solar_events=solar_events, solar_quals=solar_quals,
        scope_units=scope_units,
        dual_units=dual_units,
        plural_units=plural_units,
        ordinal_suffixes=tuple(ordinal_suffixes),
        day_cycles=day_cycles, cycle_positions=cycle_positions,
        day_subdivision=cfg.get("day_subdivision"),
        regnal_names=regnal_names, roman_anchors=roman_anchors,
        archon_names=archon_names,
        periods=periods, scales=scales,
        scales_by_mode={m: dict(t) for m, t in scales_by_mode.items()},
        period_parts=period_parts,
        decade_words=decade_words, clock_landmarks=clock_landmarks,
        dayparts=dayparts,
        daypart_deictics=daypart_deictics,
        daypart_today_words=frozenset(daypart_today_words),
        clock_zones=clock_zones,
        jurisdictions=jurisdictions,
        weekend_words=frozenset(weekend_words),
        exclusion_triggers=frozenset(exclusion_triggers),
        exclusion_bound_guards=frozenset(exclusion_bound_guards),
        exclusion_coord=frozenset(exclusion_coord),
        exclusion_scope=frozenset(exclusion_scope),
        exclusion_filler=frozenset(exclusion_filler),
        weekday_full=weekday_full,
        quantifiers=quantifiers,
        positions=cfg.get("positions", {}))

    # LOUD schema validation on load (behind the lazy per-language path): the
    # parsed config must be structurally sound AND every construction order must
    # be reachable given the vocabulary this locale actually ships.  Bad locale
    # data raises here with locale+field context rather than silently disabling
    # a construction.
    validate_locale(cfg, lang, spec)

    # Holiday surfaces are FACTS harvested from the holidays engine's i18n
    # tables, then folded through the *same* tokenizer + normaliser the matcher
    # uses so a multi-word or inflected surface ("domingo de pascoa", "corpo de
    # deus") is stored exactly as the token stream will present it.  The keys of
    # the resulting map are canonical, space-joined normalised surfaces; the
    # multiword-merge pass glues the multi-word ones back into one token.
    holidays: Dict[str, str] = {}
    holiday_sources: Dict[str, str] = {}
    tokenizer = Tokenizer(spec.tokenizer)
    normaliser = TemporalNormaliser(spec)
    for surface, key in well_known_surfaces(lang).items():
        toks = normaliser.normalise(tokenizer.tokenize(surface))
        if spec.hook is not None:
            # apply the same language hook (e.g. French elision split) the real
            # pre-match pipeline runs, so a stored surface matches token-for-token
            toks = spec.hook(toks)
        if not toks:
            continue
        canon = " ".join(t.text for t in toks)
        holidays[canon] = key
        holiday_sources[key] = well_known_source(key, lang)
    return replace(spec, holidays=holidays, holiday_sources=holiday_sources)
