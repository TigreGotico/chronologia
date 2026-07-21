"""i18n layer for civil holidays: official native names, display translations
and the :meth:`CivilHoliday.display_name` fallback chain.

Three honestly-distinct layers are exercised here:

1. **Official native names** parsed from the ``.tab`` ``name`` cell — a plain
   single name (backward-compatible) or ``;;``-separated ``lang:``-tagged
   alternates that populate :attr:`CivilHoliday.names`.
2. **Display translations** from ``holiday_data/i18n/translations.tab`` — marked
   ``source: translation`` because they are renderings, not official facts.
3. The **fallback chain**: official name for the language, else translation, else
   the primary name.
"""
import os

import pytest

from chronologia import (CivilHoliday, holidays_for, load_translations,
                         parse_name_cell)
from chronologia.astrodate import AstroDate, DateSpan
from chronologia.civil_holidays import (_DATA_DIR, _TRANSLATIONS_FILE,
                                        load_calendar)


# --------------------------------------------------------------------------
# parse_name_cell — the .tab name-cell grammar
# --------------------------------------------------------------------------
def test_parse_plain_single_name_is_backward_compatible():
    primary, names = parse_name_cell("New Year's Day")
    assert primary == "New Year's Day"
    assert names == {}


def test_parse_lang_tagged_alternates():
    primary, names = parse_name_cell("zh:春节 ;; en:Spring Festival")
    assert primary == "春节"
    assert names == {"zh": "春节", "en": "Spring Festival"}


def test_parse_first_alternate_is_primary_even_when_tagged():
    primary, names = parse_name_cell("ar:عيد الفطر ;; en:Eid al-Fitr")
    assert primary == "عيد الفطر"
    assert names["ar"] == "عيد الفطر"
    assert names["en"] == "Eid al-Fitr"


def test_parse_bcp47_region_subtag_accepted():
    _primary, names = parse_name_cell("pt-BR:Carnaval ;; en:Carnival")
    assert names["pt-BR"] == "Carnaval"


def test_parse_name_with_colon_but_no_lang_tag_stays_plain():
    # A name that merely contains a colon (long left side) is NOT a lang tag.
    primary, names = parse_name_cell("Something: a subtitle")
    assert primary == "Something: a subtitle"
    assert names == {}


def test_parse_empty_cell_rejected():
    with pytest.raises(ValueError):
        parse_name_cell("   ")


# --------------------------------------------------------------------------
# display_name fallback chain
# --------------------------------------------------------------------------
def _holiday(name, names=None, translations=None, juris="XX"):
    d = AstroDate(2024, 1, 1)
    return CivilHoliday(name, DateSpan(d, d, "exact"), juris, None,
                        frozenset({"public"}), "exact",
                        names=names or {}, translations=translations or {})


def test_display_name_prefers_official_over_translation():
    h = _holiday("春节", names={"zh": "春节", "en": "Spring Festival"},
                 translations={"en": "SHOULD-NOT-WIN"})
    assert h.display_name("en") == "Spring Festival"   # official en wins
    assert h.display_name("zh") == "春节"


def test_display_name_falls_back_to_translation():
    h = _holiday("Ano Novo", names={}, translations={"en": "New Year's Day"})
    assert h.display_name("en") == "New Year's Day"


def test_display_name_falls_back_to_primary_name():
    h = _holiday("Ano Novo")
    assert h.display_name("ja") == "Ano Novo"      # no official, no translation


def test_display_name_region_subtag_falls_back_to_base_lang():
    h = _holiday("Carnaval", translations={"en": "Carnival"})
    assert h.display_name("en-GB") == "Carnival"   # en-GB -> en


# --------------------------------------------------------------------------
# translations.tab loader + wiring through holidays_for
# --------------------------------------------------------------------------
def test_load_translations_parses_the_shipped_file():
    table = load_translations()
    assert ("PT", "Ano Novo") in table
    assert table[("PT", "Ano Novo")]["es"] == "Año Nuevo"


def test_load_translations_missing_file_is_empty():
    assert load_translations(os.path.join(_DATA_DIR, "does-not-exist.tab")) == {}


def test_translations_file_marks_itself_as_translation_source():
    text = open(_TRANSLATIONS_FILE, encoding="utf-8").read()
    assert "source: translation" in text


def test_holidays_for_attaches_translations():
    ano_novo = [h for h in holidays_for("PT", 2024) if h.name == "Ano Novo"][0]
    assert ano_novo.display_name("en") == "New Year's Day"
    assert ano_novo.display_name("de") == "Neujahr"
    # Portuguese is the official primary — display_name returns the native name.
    assert ano_novo.display_name("pt") == "Ano Novo"


def test_translations_are_not_official_names():
    # A translation must NOT masquerade as an official name: PT holidays carry no
    # `names` map (single official language), yet display_name still renders en.
    ano_novo = [h for h in holidays_for("PT", 2024) if h.name == "Ano Novo"][0]
    assert dict(ano_novo.names) == {}
    assert "en" in ano_novo.translations


# --------------------------------------------------------------------------
# Serialization round-trips the new fields
# --------------------------------------------------------------------------
def test_to_json_from_json_round_trips_names_and_translations():
    h = _holiday("春节", names={"zh": "春节", "en": "Spring Festival"},
                 translations={"pt": "Ano Novo Chinês"})
    back = CivilHoliday.from_json(h.to_json())
    assert back.name == "春节"
    assert dict(back.names) == {"zh": "春节", "en": "Spring Festival"}
    assert dict(back.translations) == {"pt": "Ano Novo Chinês"}
    assert back.display_name("en") == "Spring Festival"


def test_to_json_omits_empty_i18n_fields():
    env = _holiday("Ano Novo").to_json()
    assert "names" not in env and "translations" not in env


def test_old_envelope_without_i18n_still_loads():
    env = {"type": "CivilHoliday", "name": "Ano Novo",
           "span": _holiday("Ano Novo").span.to_json(),
           "jurisdiction": "PT", "subdiv": None,
           "categories": ["public"], "basis": "exact"}
    back = CivilHoliday.from_json(env)
    assert back.name == "Ano Novo" and dict(back.names) == {}


# --------------------------------------------------------------------------
# .tab format spec: multi-name cells parse, single-name cells unchanged
# --------------------------------------------------------------------------
def test_every_tab_name_cell_parses():
    for fn in sorted(os.listdir(_DATA_DIR)):
        if not fn.endswith(".tab"):
            continue
        cal = load_calendar(os.path.join(_DATA_DIR, fn))
        for rule in cal.rules:
            # every rule has a non-empty primary name; tagged langs, if any, map
            assert rule.name
            for lang, text in rule.names.items():
                assert lang and text
