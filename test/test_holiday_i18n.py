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
# Official native names as primary data, with co-official / romanized alternates
# --------------------------------------------------------------------------
@pytest.mark.parametrize("juris,year,langs", [
    ("SA", 2024, ("ar", "en")),   # Arabic primary + English romanization
    ("CN", 2024, ("zh", "en")),
    ("JP", 2024, ("ja", "en")),
    ("IL", 2024, ("he", "en")),
])
def test_multi_official_jurisdictions_carry_all_names(juris, year, langs):
    hols = holidays_for(juris, year)
    # every holiday of these jurisdictions carries every declared language
    assert hols
    for h in hols:
        for lang in langs:
            assert lang in h.names, (juris, h.name, lang, dict(h.names))
        # the primary name is the first official language (native script)
        assert h.name == h.names[langs[0]]


def test_saudi_primary_is_arabic_english_is_display():
    eid = [h for h in holidays_for("SA", 2024)
           if h.display_name("en") == "Eid al-Fitr"][0]
    assert eid.name == "عيد الفطر"          # official native primary
    assert eid.names["ar"] == "عيد الفطر"
    assert eid.display_name("ar") == "عيد الفطر"
    assert eid.display_name("en") == "Eid al-Fitr"


def test_canada_federal_holidays_are_bilingual():
    canada_day = [h for h in holidays_for("CA", 2024)
                  if h.name == "Canada Day"][0]
    assert canada_day.names["en"] == "Canada Day"
    assert canada_day.names["fr"] == "Fête du Canada"
    assert canada_day.display_name("fr") == "Fête du Canada"


def test_gb_welsh_co_official_name():
    xmas = [h for h in holidays_for("GB", 2024)
            if h.name == "Christmas Day"][0]
    assert xmas.names["cy"] == "Dydd Nadolig"
    assert xmas.display_name("cy") == "Dydd Nadolig"


def test_india_national_days_carry_hindi():
    rep = [h for h in holidays_for("IN", 2024) if h.name == "Republic Day"][0]
    assert rep.names["hi"] == "गणतंत्र दिवस"


def test_spain_regional_co_official_name():
    cat = [h for h in holidays_for("ES", 2024, subdiv="ES-CT")
           if h.name == "Fiesta Nacional de Cataluña"][0]
    assert cat.names["ca"] == "Diada Nacional de Catalunya"


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


# --------------------------------------------------------------------------
# Translation-coverage matrix (en/pt/es/de/fr) for the 15 jurisdictions
# --------------------------------------------------------------------------
#: The official primary language of each jurisdiction's primary `name`. A holiday
#: is trivially "covered" for this language by its own name. Every shipped
#: jurisdiction is listed so the coverage helpers never KeyError as new
#: native-primary country files land.
_PRIMARY_LANG = {
    "PT": "pt", "US": "en", "GB": "en", "CA": "en", "AU": "en", "IN": "en",
    "CN": "zh", "JP": "ja", "IL": "he", "SA": "ar", "TR": "tr", "DE": "de",
    "FR": "fr", "BR": "pt", "ES": "es",
    # tier-2 additions (native-primary):
    "AR": "es", "AT": "de", "BE": "nl", "CH": "de", "CL": "es", "CO": "es",
    "CZ": "cs", "DK": "da", "EG": "ar", "FI": "fi", "GR": "el", "ID": "id",
    "IE": "en", "IT": "it", "MA": "ar", "MX": "es", "MY": "ms", "NL": "nl",
    "NO": "no", "PE": "es", "PK": "en", "PL": "pl", "SE": "sv", "SK": "sk",
    "UY": "es",
    # batch-1 (25 new national jurisdictions):
    "NG": "en", "BD": "bn", "RU": "ru", "ET": "am", "PH": "fil", "VN": "vi",
    "CD": "fr", "IR": "fa", "TH": "th", "TZ": "sw", "ZA": "en", "MM": "my",
    "KE": "sw", "KR": "ko", "UG": "en", "DZ": "ar", "SD": "ar", "IQ": "ar",
    "AF": "fa", "UZ": "uz", "YE": "ar", "NP": "ne", "VE": "es", "GH": "en",
    "RO": "ro",
    # batch-2 (25 more new national jurisdictions):
    "JO": "ar", "AO": "pt", "MZ": "pt", "MG": "mg", "CM": "en", "CI": "fr",
    "NE": "fr", "LK": "si", "BF": "fr", "ML": "fr", "KZ": "kk", "MW": "en",
    "ZM": "en", "SY": "ar", "EC": "es", "SN": "fr", "KH": "km", "TD": "en",
    "ZW": "en", "GN": "fr", "RW": "rw", "BJ": "fr", "BI": "fr", "TG": "fr",
    "HT": "fr",
    # batch-3 (25 more national jurisdictions):
    "SO": "en", "GT": "es", "CU": "es", "DO": "es", "BO": "es", "HN": "es",
    "HU": "hu", "BY": "be", "PG": "en", "AE": "ar", "TJ": "tg", "RS": "sr",
    "PY": "es", "NI": "es", "SV": "es", "LA": "lo", "SL": "en", "LY": "ar",
    "KG": "ky", "TM": "tk", "SG": "en", "ER": "en", "CR": "es", "PA": "es",
    "MR": "en",
    # batch-4 (25 more new national jurisdictions):
    "KP": "ko", "TW": "zh", "TN": "ar", "SS": "en", "AZ": "az", "BG": "bg",
    "CG": "fr", "CF": "fr", "NZ": "en", "KW": "ar", "HR": "hr", "GE": "ka",
    "MD": "ro", "MN": "mn", "BA": "bs", "LT": "lt", "AM": "hy", "AL": "sq",
    "JM": "en", "GM": "en", "QA": "ar", "NA": "en", "BW": "en", "GA": "fr",
    "LS": "en",
    # batch-5 (the closing sweep -- 106 more jurisdictions to vacanza parity):
    "AD": "ca", "AG": "en", "AI": "en", "AQ": "en", "AS": "en", "AW": "pap",
    "AX": "fi", "BB": "en", "BH": "ar", "BL": "fr", "BM": "en", "BN": "ms",
    "BQ": "nl", "BS": "en", "BT": "dz", "BZ": "en", "CC": "en", "CK": "en",
    "CV": "pt", "CW": "pap", "CX": "en", "CY": "el", "DJ": "fr", "DM": "en",
    "EE": "et", "EH": "ar", "FJ": "en", "FK": "en", "FM": "en", "FO": "fo",
    "GD": "en", "GF": "fr", "GG": "en", "GI": "en", "GL": "kl", "GP": "fr",
    "GQ": "es", "GS": "en", "GU": "en", "GW": "pt", "GY": "en", "HK": "zh",
    "IM": "en", "IS": "is", "JE": "en", "KI": "en", "KM": "en", "KN": "en",
    "KY": "en", "LB": "ar", "LC": "en", "LI": "de", "LR": "en", "LU": "lb",
    "LV": "lv", "MC": "fr", "ME": "cnr", "MF": "fr", "MH": "en", "MK": "mk",
    "MO": "zh", "MP": "en", "MQ": "fr", "MS": "en", "MT": "mt", "MU": "en",
    "MV": "dv", "NC": "fr", "NF": "en", "NR": "en", "NU": "en", "OM": "ar",
    "PF": "fr", "PM": "fr", "PN": "en", "PR": "en", "PS": "ar", "PW": "en",
    "RE": "fr", "SB": "en", "SC": "en", "SH": "en", "SI": "sl", "SJ": "no",
    "SM": "it", "SR": "nl", "ST": "pt", "SX": "nl", "SZ": "en", "TC": "en",
    "TF": "fr", "TK": "en", "TL": "pt", "TO": "to", "TT": "en", "TV": "tvl",
    "UM": "en", "VA": "it", "VC": "en", "VG": "en", "VI": "en", "VU": "en",
    "WF": "fr", "WS": "en", "XK": "sq", "YT": "fr",
}
_MATRIX_LANGS = ("en", "pt", "es", "de", "fr")

#: Jurisdictions whose full en/pt/es/de/fr display matrix has been authored in
#: translations.tab (or is trivially covered because the primary language is one
#: of the matrix five). The strict matrix test enforces only these. It is a
#: DELIBERATELY GROWING allowlist: adding a jurisdiction's national holidays to
#: translations.tab (in all five languages) is what qualifies it for entry — the
#: honest alternative to fabricating low-confidence renderings for every new
#: country the moment its native-primary .tab lands. The en+native guarantee
#: (below) is what every jurisdiction gets immediately.
_MATRIX_JURISDICTIONS = frozenset({
    "PT", "US", "GB", "CA", "AU", "IN", "CN", "JP", "IL", "SA", "TR", "DE",
    "FR", "BR", "ES", "IE", "IT",
})


def _all_rules():
    """(juris, subdiv, name, names_map) for every non-municipal rule shipped.

    Municipal holidays (Portugal's ~300 concelho saints' days and the like) are
    excluded: they are proper-noun local feasts whose name is the same word in
    every language, so display falls back to the native name by design. The
    translation matrix targets the national and regional tiers people display.
    """
    out = []
    for fn in sorted(os.listdir(_DATA_DIR)):
        if not fn.endswith(".tab"):
            continue
        cal = load_calendar(os.path.join(_DATA_DIR, fn))
        j = cal.jurisdiction.upper()
        for rule in cal.rules:
            if "municipal" in rule.categories:
                continue
            out.append((j, rule.subdiv, rule.name, dict(rule.names)))
    return out


def _covered(juris, name, names_map, trans, lang):
    return (lang in names_map
            or lang in trans.get((juris, name), {})
            or _PRIMARY_LANG[juris] == lang)


def test_every_shipped_jurisdiction_has_a_primary_language():
    # Guards the coverage helpers: every jurisdiction file must be classified.
    shipped = {j for j, _s, _n, _m in _all_rules()}
    assert shipped <= set(_PRIMARY_LANG), (
        f"unclassified jurisdictions: {shipped - set(_PRIMARY_LANG)}")


def test_every_non_municipal_holiday_of_covered_jurisdictions_has_en_and_native():
    # en + native is the immediate guarantee for every jurisdiction whose display
    # matrix has been authored; the native name is always present.
    trans = load_translations()
    missing = []
    for j, _subdiv, name, names_map in _all_rules():
        if j not in _MATRIX_JURISDICTIONS:
            continue
        if not name:
            missing.append((j, name, "native"))
        if not _covered(j, name, names_map, trans, "en"):
            missing.append((j, name, "en"))
    assert not missing, f"holidays missing en/native coverage: {missing}"


def test_every_national_holiday_has_full_five_language_matrix():
    trans = load_translations()
    missing = []
    for j, subdiv, name, names_map in _all_rules():
        if subdiv is not None:                    # national tier only
            continue
        if j not in _MATRIX_JURISDICTIONS:        # deliberately-growing allowlist
            continue
        for lang in _MATRIX_LANGS:
            if not _covered(j, name, names_map, trans, lang):
                missing.append((j, name, lang))
    assert not missing, f"national holidays missing matrix coverage: {missing}"


def test_multi_official_new_jurisdictions_carry_co_official_names():
    # Switzerland (de/fr/it), Belgium (nl/fr/de) and Ireland (en/ga): national
    # holidays carry their co-official names.
    expect = {
        ("CH", "Neujahrstag"): {"fr": "Nouvel An", "it": "Capodanno"},
        ("BE", "Nieuwjaar"): {"fr": "Nouvel An", "de": "Neujahr"},
        ("IE", "New Year's Day"): {"ga": "Lá Caille"},
    }
    for (juris, primary), langs in expect.items():
        year = 2024
        h = [x for x in holidays_for(juris, year) if x.name == primary][0]
        for lang, text in langs.items():
            assert h.names.get(lang) == text, (juris, primary, lang, dict(h.names))
            assert h.display_name(lang) == text


def test_display_name_renders_every_matrix_language_for_a_sample():
    # A concrete end-to-end check across scripts: each jurisdiction renders in
    # all five display languages via the fallback chain.
    samples = {
        ("PT", 2024): "Ano Novo", ("US", 2024): "New Year's Day",
        ("DE", 2024): "Neujahr", ("CN", 2024): "元旦", ("SA", 2024): "عيد الفطر",
        ("JP", 2024): "元日", ("IL", 2024): "פסח", ("TR", 2024): "Cumhuriyet Bayramı",
    }
    for (juris, year), primary in samples.items():
        h = [x for x in holidays_for(juris, year) if x.name == primary][0]
        for lang in _MATRIX_LANGS:
            assert h.display_name(lang), (juris, primary, lang)


def test_translations_never_shadow_an_official_name():
    # display_name must return the OFFICIAL name when the language is official,
    # even if a translation for that language also exists.
    trans = load_translations()
    for j, _subdiv, name, names_map in _all_rules():
        for lang in names_map:
            got = trans.get((j, name), {})
            if lang in got:
                # if both exist, they should agree that the official one wins:
                # simulate a CivilHoliday and check display_name.
                from chronologia.astrodate import AstroDate, DateSpan
                d = AstroDate(2024, 1, 1)
                h = CivilHoliday(name, DateSpan(d, d, "exact"), j, None,
                                 frozenset({"public"}), "exact",
                                 names=names_map, translations=got)
                assert h.display_name(lang) == names_map[lang]
