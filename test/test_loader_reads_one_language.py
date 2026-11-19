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
