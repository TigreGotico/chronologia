"""Schema + linter for the locale grammar (``lang.json`` + ``*.voc``).

Three layers:

* **schema unit tests** -- the derived checker itself catches the defect
  classes it claims to (unknown slot, malformed optional syntax, non-numeric
  quantifier key, unknown group/construction, an unreachable order);
* **every shipped locale validates** -- all 40 locales pass
  :func:`chronologia.extract.schema.validate` (structural + reachability),
  loudly, one parametrised case per locale;
* **the linter** -- deeper data-quality checks reported as per-locale failures:
  duplicate surfaces within a ``.voc``, surfaces that normalise to empty, and
  placeholder-English left in a non-English ``period_part_*`` file (the
  early/mid/late bug class).
"""
import glob
import json
import os
from pathlib import Path

import pytest
from ovos_spec_tools import LocaleResources, expand, read_resource_file

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


def _voc_surfaces(lang, base, vocab_map):
    """Expanded, lower-cased surfaces of ``<lang>/<base>.voc`` (empty if absent)."""
    path = Path(LOCALE_DIR) / lang / (base + ".voc")
    if not path.exists():
        return []
    out = []
    for template in read_resource_file(path):
        for sample in expand(template, vocab_map):
            out.append(sample.lower())
    return out


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
    # declaring an archon order with no archon_*.voc is dead: build such a case
    spec = load_lang_spec("en")
    cfg = {"constructions": {"deep_time": {"orders": ["NUM SCALE year_word ago"]}}}
    from dataclasses import replace
    stripped = replace(spec, scales={})       # remove the SCALE vocabulary
    errs = validate_reachability(stripped, cfg, "en")
    assert any("unreachable" in e and "SCALE" in e for e in errs)


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
    vocab_map = LocaleResources(LOCALE_DIR).vocabularies(lang)
    defects = []
    for path in sorted(glob.glob(os.path.join(LOCALE_DIR, lang, "*.voc"))):
        base = os.path.basename(path)[:-len(".voc")]
        surfaces = _voc_surfaces(lang, base, vocab_map)
        seen, dups = set(), set()
        for s in surfaces:
            (dups if s in seen else seen).add(s)
        if dups:
            defects.append(f"{base}.voc duplicate surface(s): {sorted(dups)}")
        if any(not s.strip() for s in surfaces):
            defects.append(f"{base}.voc has surface(s) normalising to empty")
    assert not defects, "\n".join(defects)


@pytest.mark.parametrize("lang", [l for l in LOCALES if l != REFERENCE])
def test_no_english_placeholder_period_parts(lang):
    # the early/mid/late bug class: a non-English period_part_*.voc left byte-
    # identical to English is almost never a real cognate set (unlike unit
    # abbreviations "min"/"sec", which legitimately coincide across languages,
    # so this heuristic is deliberately scoped to period_part_* only)
    en_vocab = LocaleResources(LOCALE_DIR).vocabularies(REFERENCE)
    vocab_map = LocaleResources(LOCALE_DIR).vocabularies(lang)
    suspects = []
    for path in sorted(glob.glob(os.path.join(LOCALE_DIR, lang, "period_part_*.voc"))):
        base = os.path.basename(path)[:-len(".voc")]
        mine = set(_voc_surfaces(lang, base, vocab_map))
        theirs = set(_voc_surfaces(REFERENCE, base, en_vocab))
        if mine and theirs and mine == theirs:
            suspects.append(f"{base}.voc identical to en: {sorted(mine)}")
    assert not suspects, "\n".join(suspects)


# --------------------------------------------------------------------------- #
# regression probes -- de-duplicating a .voc must never drop its surface
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
    # era_year_ref.voc is read by the eras subsystem, not the span loader, so
    # assert the surface survived the de-duplication at the file level
    surfaces = {ln.strip().lower() for ln in
                (Path(LOCALE_DIR) / "fr" / "era_year_ref.voc")
                .read_text(encoding="utf-8").splitlines() if ln.strip()}
    assert "l'an" in surfaces
