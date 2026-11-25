"""Schema + linter for the locale grammar (``lang.json`` + ``vocab.json``).

Three layers:

* **schema unit tests** -- the derived checker itself catches the defect
  classes it claims to (unknown slot, malformed optional syntax, non-numeric
  quantifier key, unknown group/construction, an unreachable order);
* **every shipped locale validates** -- all 40 locales pass
  :func:`chronologia.extract.schema.validate` (structural + reachability),
  loudly, one parametrised case per locale;
* **the linter** -- deeper data-quality checks reported as per-locale failures:
  duplicate surfaces within a vocabulary, surfaces that normalise to empty, and
  placeholder-English left in a non-English ``period_part_*`` file (the
  early/mid/late bug class);
* **the vocabulary schema** -- every ``vocab.json`` validates against
  ``locale/vocab.schema.json``.
"""
import glob
import json
import os

import jsonschema
import pytest

from chronologia.extract.loader import LOCALE_DIR, load_lang_spec
from chronologia.extract.schema import (KNOWN_GROUPS, SLOT_ALPHABET,
                                        LocaleSchemaError, validate,
                                        validate_config, validate_reachability)

LOCALES = sorted(os.path.basename(os.path.dirname(f))
                 for f in glob.glob(os.path.join(LOCALE_DIR, "*", "lang.json")))
REFERENCE = "en"


def _cfg(lang):
    with open(os.path.join(LOCALE_DIR, lang, "lang.json"), encoding="utf-8") as fh:
        return json.load(fh)


def _words(lang):
    """``vocab.json`` of ``lang``: base name -> surfaces."""
    with open(os.path.join(LOCALE_DIR, lang, "vocab.json"), encoding="utf-8") as fh:
        return json.load(fh)["words"]


def _voc_surfaces(lang, base):
    """Lower-cased surfaces of the vocabulary ``base`` of ``lang`` (empty if absent)."""
    return [s.lower() for s in _words(lang).get(base, [])]


# --------------------------------------------------------------------------- #
# schema unit tests -- the checker catches what it claims to
# --------------------------------------------------------------------------- #

def test_slot_alphabet_derived_from_matcher():
    # a non-trivial alphabet, read live from matcher._bind, covering a spread
    # of slot families so a matcher rename can never silently shrink it
    assert len(SLOT_ALPHABET) >= 40
    for slot in ("MONTH", "NUM", "SEASON", "ERANAME", "PERIOD", "ANCHOR_DAY"):
        assert slot in SLOT_ALPHABET


def test_unknown_slot_is_flagged():
    cfg = {"constructions": {"named_day": {"orders": ["BOGUS_SLOT"]}}}
    errs = validate_config(cfg, "xx")
    assert any("unknown slot 'BOGUS_SLOT'" in e for e in errs)


def test_malformed_optional_suffix_is_flagged():
    cfg = {"constructions": {"named_day": {"orders": ["MO?NTH DAY"]}}}
    errs = validate_config(cfg, "xx")
    assert any("malformed optional suffix" in e for e in errs)


def test_non_numeric_quantifier_key_is_flagged():
    cfg = {"quantifiers": {"lots": ["many"]}}
    errs = validate_config(cfg, "xx")
    assert any("not a numeric string" in e for e in errs)


def test_unknown_construction_group_is_flagged():
    cfg = {"constructions": {"named_day": {"orders": ["DAY_WORD"],
                                           "group": "made_up"}}}
    errs = validate_config(cfg, "xx")
    assert any("unknown construction group" in e for e in errs)


def test_unknown_construction_name_is_flagged():
    cfg = {"constructions": {"not_a_construction": {"orders": ["NUM"]}}}
    errs = validate_config(cfg, "xx")
    assert any("unknown construction name" in e for e in errs)


def test_unknown_top_level_key_is_flagged():
    assert any("unknown top-level key 'wat'" in e
               for e in validate_config({"wat": 1}, "xx"))


def test_reachability_flags_missing_vocabulary():
    # en genuinely has no archon vocabulary competitor problem, but a locale
    # declaring an archon order with no archon_* vocabulary is dead: build such a case
    spec = load_lang_spec("en")
    cfg = {"constructions": {"deep_time": {"orders": ["NUM SCALE year_word ago"]}}}
    from dataclasses import replace
    stripped = replace(spec, scales={})       # remove the SCALE vocabulary
    errs = validate_reachability(stripped, cfg, "en")
    assert any("unreachable" in e and "SCALE" in e for e in errs)


def test_reachability_flags_optional_connector_without_vocabulary():
    spec = load_lang_spec("en")
    cfg = {"constructions": {"clock_time": {"orders": ["at? ofd? HOUR"]}}}
    errs = validate_reachability(spec, cfg, "en")
    assert any("unreachable" in e and "ofd" in e for e in errs)


def test_optional_shared_connector_may_lack_vocabulary():
    # "article?" is a base-grammar connector; a language without articles
    # shares the order and ships no article vocabulary
    from dataclasses import replace
    spec = load_lang_spec("en")
    stripped = replace(spec, connectors={k: v for k, v in spec.connectors.items()
                                         if k != "article"})
    cfg = {"constructions": {"weekend_ref": {"orders": ["article? WEEKEND"]}}}
    assert validate_reachability(stripped, cfg, "en") == []


@pytest.mark.parametrize("section", ["override", "extend"])
def test_base_grammar_orders_are_checked(section):
    spec = load_lang_spec("en")
    for order, expected in (("REL_MARKER WEEKDAYY", "unknown slot 'WEEKDAYY'"),
                            ("ofd WEEKDAY", "no vocabulary for ofd"),
                            ("ofd? WEEKDAY", "no vocabulary for ofd")):
        cfg = {"base_grammar": {section: {"weekday_ref": [order]}}}
        errs = validate_config(cfg, "en") + validate_reachability(spec, cfg, "en")
        assert any(expected in e and section in e for e in errs), (order, errs)


def test_positions_unknown_role_is_flagged():
    errs = validate_config({"positions": {"nope": "post"}}, "xx")
    assert any("unknown marker role 'nope'" in e for e in errs)


def test_positions_unknown_position_is_flagged():
    errs = validate_config({"positions": {"until": "sideways"}}, "xx")
    assert any("unknown position 'sideways'" in e for e in errs)


def test_positions_reachability_flags_missing_marker_vocab():
    # declaring until=affix without any marker_until surface is dead data
    spec = load_lang_spec("en")
    from dataclasses import replace
    stripped = replace(spec, connectors={k: v for k, v in spec.connectors.items()
                                          if k != "until"})
    errs = validate_reachability(stripped, {"positions": {"until": "affix"}}, "en")
    assert any("positions['until']" in e and "unreachable" in e for e in errs)


def test_hu_declares_affix_and_post_positions():
    # the flipped Hungarian exceptions: -ig is an affix until, óta a postposed
    # since, both first-class facts on the loaded spec
    spec = load_lang_spec("hu")
    assert spec.positions.get("until") == "affix"
    assert spec.positions.get("since") == "post"


def test_validate_raises_loudly_with_context():
    with pytest.raises(LocaleSchemaError) as exc:
        validate({"constructions": {"named_day": {"orders": ["NOPE"]}}}, "xx")
    assert exc.value.lang == "xx" and exc.value.errors


# --------------------------------------------------------------------------- #
# every shipped locale validates (structural + reachability), loudly
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("lang", LOCALES)
def test_locale_validates(lang):
    # load_lang_spec itself runs validate(); calling it here surfaces the exact
    # findings in the assertion message rather than a bare load traceback
    spec = load_lang_spec(lang)
    errors = validate_config(_cfg(lang), lang)
    errors += validate_reachability(spec, _cfg(lang), lang)
    assert not errors, "\n".join(errors)


# --------------------------------------------------------------------------- #
# linter -- data-quality defects reported per locale
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("lang", LOCALES)
def test_no_duplicate_or_empty_surfaces(lang):
    defects = []
    for base in _words(lang):
        surfaces = _voc_surfaces(lang, base)
        seen, dups = set(), set()
        for s in surfaces:
            (dups if s in seen else seen).add(s)
        if dups:
            defects.append(f"{base} duplicate surface(s): {sorted(dups)}")
        if any(not s.strip() for s in surfaces):
            defects.append(f"{base} has surface(s) normalising to empty")
    assert not defects, "\n".join(defects)


@pytest.mark.parametrize("lang", [l for l in LOCALES if l != REFERENCE])
def test_no_english_placeholder_period_parts(lang):
    # the early/mid/late bug class: a non-English period_part_* vocabulary left byte-
    # identical to English is almost never a real cognate set (unlike unit
    # abbreviations "min"/"sec", which legitimately coincide across languages,
    # so this heuristic is deliberately scoped to period_part_* only)
    suspects = []
    for base in _words(lang):
        if not base.startswith("period_part_"):
            continue
        mine = set(_voc_surfaces(lang, base))
        theirs = set(_voc_surfaces(REFERENCE, base))
        if mine and theirs and mine == theirs:
            suspects.append(f"{base} identical to en: {sorted(mine)}")
    assert not suspects, "\n".join(suspects)


# --------------------------------------------------------------------------- #
# regression probes -- de-duplicating a vocabulary must never drop its surface
# (locks the surfaces whose files had duplicate lines removed)
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("lang,attr,surface", [
    ("ro", "seasons", "toamna"),        # autumn (also the diacritic "toamnă")
    ("ro", "seasons", "vara"),          # summer
    ("ro", "seasons", "iarna"),         # winter
    ("sk", "units", "hodín"),           # hour (genitive plural)
    ("an", "scales", "millons"),        # million (Aragonese)
    ("bg", "rel_markers", "тази"),      # "this" (feminine)
    ("oc", "rel_markers", "aqueste"),   # "this" (Occitan)
])
def test_deduped_surface_still_binds(lang, attr, surface):
    assert surface in getattr(load_lang_spec(lang), attr)


def test_deduped_connectors_still_bind():
    assert "olympiads" in load_lang_spec("en").connectors.get("olympiad")


def test_deduped_era_year_ref_surface_retained():
    # era_year_ref is read by the eras subsystem, not the span loader, so
    # assert the surface survived the de-duplication in the vocabulary itself
    assert "l'an" in _voc_surfaces("fr", "era_year_ref")


# --------------------------------------------------------------------------- #
# vocab.json -- every locale validates against locale/vocab.schema.json
# --------------------------------------------------------------------------- #

with open(os.path.join(LOCALE_DIR, "vocab.schema.json"), encoding="utf-8") as _fh:
    VOCAB_SCHEMA = json.load(_fh)


@pytest.mark.parametrize("lang", LOCALES)
def test_vocab_json_matches_schema(lang):
    with open(os.path.join(LOCALE_DIR, lang, "vocab.json"), encoding="utf-8") as fh:
        jsonschema.validate(json.load(fh), VOCAB_SCHEMA)


@pytest.mark.parametrize("lang", LOCALES)
def test_vocab_json_is_sorted_and_deduplicated(lang):
    words = _words(lang)
    assert list(words) == sorted(words)
    unsorted = [base for base, surfaces in words.items()
                if surfaces != sorted(set(surfaces))]
    assert not unsorted, f"not sorted or not unique: {unsorted}"


@pytest.mark.parametrize("lang", LOCALES)
def test_vocab_sources_name_vocabularies(lang):
    with open(os.path.join(LOCALE_DIR, lang, "vocab.json"), encoding="utf-8") as fh:
        document = json.load(fh)
    assert set(document.get("sources", {})) <= set(document["words"])


def test_vocab_schema_rejects_malformed_documents():
    bad_version = {"format_version": 2, "words": {}}
    empty_list = {"format_version": 1, "words": {"unit_day": []}}
    duplicate = {"format_version": 1, "words": {"unit_day": ["day", "day"]}}
    empty_source = {"format_version": 1, "words": {"unit_day": ["day"]},
                    "sources": {"unit_day": []}}
    for doc in (bad_version, empty_list, duplicate, empty_source):
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(doc, VOCAB_SCHEMA)
