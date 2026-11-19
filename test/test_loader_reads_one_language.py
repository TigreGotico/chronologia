"""load_lang_spec reads the language it loads, and only that one.

A process answers in one language or two, but the locale tree holds every
language the package ships. Reading the others costs a first query their
whole tree: in a browser (Pyodide) that was most of the seconds before the
first date-bearing answer.
"""
import os
from pathlib import Path

import pytest
from ovos_spec_tools import LocaleResources

from chronologia.extract import loader

LOCALE = Path(loader.LOCALE_DIR).resolve()
LANGS = sorted(p.name for p in LOCALE.iterdir() if (p / "lang.json").is_file())


def test_reads_only_files_of_the_language_it_loads(monkeypatch):
    import ovos_spec_tools.resources as resources
    read = []

    def counted(reader):
        def wrapped(path, *args, **kwargs):
            read.append(Path(path).resolve())
            return reader(path, *args, **kwargs)
        return wrapped

    monkeypatch.setattr(resources, "read_resource_file", counted(resources.read_resource_file))
    monkeypatch.setattr(loader, "read_resource_file", counted(loader.read_resource_file))
    loader.load_lang_spec("en")
    assert read
    elsewhere = {p.relative_to(LOCALE).parts[0] for p in read
                 if not p.is_relative_to(LOCALE / "en")}
    assert elsewhere == set()


@pytest.mark.parametrize("lang", LANGS)
def test_vocabulary_map_is_what_locale_resources_gives(lang):
    # the map ``<name>`` references are expanded against, as
    # ovos_spec_tools.LocaleResources computes it for this one language
    expected = LocaleResources(str(LOCALE)).vocabularies(lang)
    assert loader._vocabularies(os.path.join(str(LOCALE), lang)) == expected


@pytest.mark.parametrize("lang, expected", [
    ("pt", "pt"), ("pt-PT", "pt"), ("pt-BR", "pt"), ("en-US", "en"),
    ("da-DK", "da"), ("nb-NO", "nb"), ("EN-us", "en"),
])
def test_language_is_matched_as_locale_resources_matches_it(lang, expected):
    # what LocaleResources.vocabularies() would have read for this request
    assert Path(loader._lang_dir(lang, str(LOCALE))).name == expected
    assert (LocaleResources(str(LOCALE)).vocabularies(lang)
            == loader._vocabularies(os.path.join(str(LOCALE), expected)))


def test_a_region_loads_its_language_s_words():
    # the words come from pt/; what depends on the tag asked for (the tag
    # itself, holidays by region) stays as it was
    import dataclasses
    regional, plain = loader.load_lang_spec("pt-BR"), loader.load_lang_spec("pt")
    assert regional.lang == "pt-BR"
    tag_bound = {"lang", "holidays", "holiday_sources"}
    for field in dataclasses.fields(plain):
        if field.name not in tag_bound:
            assert getattr(regional, field.name) == getattr(plain, field.name), field.name


def test_no_close_language_is_an_error():
    with pytest.raises(FileNotFoundError):
        loader.load_lang_spec("zz")
