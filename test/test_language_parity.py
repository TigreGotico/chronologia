"""The natural-language corpus contract, enforced across languages.

Every language that opts into span-native extraction ships a **corpus
package** ``test/nl_corpus_<code>/`` -- a directory of parametrised
``test_nl_*.py`` modules, each a real sentence a human would say asserting
the exact span, with expected values derived by hand (never pinned from the
engine).  This module is the structural guard over that convention:

* a corpus package is discovered by its directory name -- there is no
  hardcoded language list, so a new language family lands its package and is
  validated automatically, with zero edits here (parallel branches never
  conflict on this file);
* every discovered corpus collects **at least 100 test cases**;
* every non-reference corpus exposes a **semantic-parity block** -- a set of
  meaning-equivalent phrases (tomorrow, in two weeks, June 5th 2027, half
  past nine, 44 BC, ...) asserting the *same* spans the English reference
  corpus asserts.  That block is the cross-language contract: the same
  meaning resolves to the same span in every language.

The reference language (``en``) is exempt from the parity-block requirement
-- it *is* the reference the others are measured against.  Languages whose
locale predates this contract (no corpus package) are simply not discovered;
adding their package opts them in.
"""
import importlib.util
import os
import sys

import pytest

_TEST_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_TEST_DIR)
_LOCALE_DIR = os.path.join(_REPO_ROOT, "chronologia", "locale")

#: the reference language; the parity blocks of every other corpus assert
#: the same spans this language's corpus does.
REFERENCE_LANG = "en"

#: minimum collected cases every corpus package must reach.
MIN_CASES = 100

#: minimum size of the shared semantic-parity block per non-reference corpus.
MIN_PARITY = 25


def _corpus_packages():
    """Discover ``nl_corpus_<code>`` packages under ``test/`` -> {code: path}."""
    out = {}
    for name in sorted(os.listdir(_TEST_DIR)):
        path = os.path.join(_TEST_DIR, name)
        if (name.startswith("nl_corpus_") and os.path.isdir(path)
                and os.path.exists(os.path.join(path, "__init__.py"))):
            out[name[len("nl_corpus_"):]] = path
    return out


_PACKAGES = _corpus_packages()
_LANGS = sorted(_PACKAGES)


class _CollectItemsPlugin:
    """Records every item pytest collects, for later per-package bucketing."""

    def __init__(self):
        self.items = []

    def pytest_collection_modifyitems(self, items):
        self.items.extend(items)


def _collect_all_counts(packages=None):
    """Collect corpus package(s) **once** and bucket item counts by lang.

    This replaces spawning one ``pytest --collect-only`` subprocess per
    language (O(langs) process starts, each paying full pytest import/
    interpreter-startup cost) with a single in-process collection pass over
    every corpus package at once, using pytest's own collection API
    (``pytest.main(..., plugins=[...])`` with a
    ``pytest_collection_modifyitems`` hook) -- the same collector the old
    subprocess invoked, just run once instead of N times.

    ``packages`` defaults to the module-level discovered packages; a caller
    may pass an explicit ``{lang: path}`` dict to exercise this function in
    isolation (e.g. to prove the guard itself catches an empty corpus).
    """
    packages = _PACKAGES if packages is None else packages
    if not packages:
        return {}
    plugin = _CollectItemsPlugin()
    devnull = open(os.devnull, "w")
    stdout, sys.stdout = sys.stdout, devnull
    try:
        pytest.main(
            ["--collect-only", "-q", "-p", "no:cacheprovider",
             *packages.values()],
            plugins=[plugin],
        )
    finally:
        sys.stdout = stdout
        devnull.close()
    counts = {lang: 0 for lang in packages}
    by_path = sorted(packages.items(), key=lambda kv: len(kv[1]), reverse=True)
    for item in plugin.items:
        item_path = str(getattr(item, "path", None) or item.fspath)
        for lang, pkg_path in by_path:
            if item_path == pkg_path or item_path.startswith(pkg_path + os.sep):
                counts[lang] += 1
                break
    return counts


_COUNTS_CACHE = None


def _collect_count(lang):
    global _COUNTS_CACHE
    if _COUNTS_CACHE is None:
        _COUNTS_CACHE = _collect_all_counts()
    return _COUNTS_CACHE[lang]


def test_at_least_one_corpus_exists():
    # the reference corpus must always be present; without it there is no
    # contract to hold the others to.
    assert REFERENCE_LANG in _PACKAGES, \
        "the reference nl_corpus_en package is missing"


@pytest.mark.parametrize("lang", _LANGS)
def test_corpus_backs_a_real_locale(lang):
    assert os.path.exists(os.path.join(_LOCALE_DIR, lang, "lang.json")), \
        f"nl_corpus_{lang} has no matching locale/{lang}/lang.json"


@pytest.mark.parametrize("lang", _LANGS)
def test_corpus_has_enough_cases(lang):
    n = _collect_count(lang)
    assert n >= MIN_CASES, \
        f"nl_corpus_{lang} collects only {n} cases (need >= {MIN_CASES})"


@pytest.mark.parametrize(
    "lang", [l for l in _LANGS if l != REFERENCE_LANG])
def test_non_reference_corpus_has_parity_block(lang):
    parity_file = os.path.join(_PACKAGES[lang], "parity.py")
    assert os.path.exists(parity_file), \
        f"nl_corpus_{lang} has no parity.py semantic-parity block"
    spec = importlib.util.spec_from_file_location(
        f"_parity_{lang}", parity_file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    parity = getattr(mod, "PARITY")
    assert len(parity) >= MIN_PARITY, \
        (f"nl_corpus_{lang}.parity.PARITY has {len(parity)} cases "
         f"(need >= {MIN_PARITY})")


def test_guard_flags_an_empty_corpus(tmp_path):
    """Adversarial test of the guard mechanism itself.

    A corpus package with no ``test_nl_*`` modules must collect zero cases
    and therefore trip the ``MIN_CASES`` threshold -- proving the in-process
    single-pass collector (``_collect_all_counts``) still catches a corpus
    that regresses to empty, exactly as the old per-language subprocess did.
    """
    fake_pkg = tmp_path / "nl_corpus_fake"
    fake_pkg.mkdir()
    (fake_pkg / "__init__.py").write_text("")
    # deliberately no test_nl_*.py files inside -- this is the broken fixture

    counts = _collect_all_counts({"fake": str(fake_pkg)})

    assert counts["fake"] == 0
    assert counts["fake"] < MIN_CASES
