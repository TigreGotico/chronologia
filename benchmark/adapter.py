"""Gold-case adapter: walk the repo's own NL corpora for benchmark cases.

The corpora under ``test/nl_corpus_<lang>/`` are hand-derived natural
language test cases -- a sentence in, an exact expected ``date``/``datetime``
out -- built independently of every engine under test here (see each
corpus's ``_corpus.py`` docstring).  Re-using them as the differential gold
set means the benchmark never grades an engine against another engine's own
output.

This module discovers those gold cases *generically*, with no hardcoded
per-language logic: it collects every parametrized pytest case shaped
``(text, expected)`` where ``expected`` is a ``date``/``datetime`` instance
(the ``text,expected`` convention used across ~40 corpora for span-native
assertions -- as opposed to ``extract_duration`` cases, whose ``expected``
is a ``timedelta`` and is naturally excluded by the type check below).
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from datetime import date, datetime
from typing import Dict, List, Optional

import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_HERE)
_TEST_DIR = os.path.join(_REPO_ROOT, "test")


@dataclass(frozen=True)
class GoldCase:
    """One hand-derived (text -> date) gold case from a corpus package."""

    lang: str          # e.g. "de" -- the chronologia locale code
    text: str          # the natural-language sentence
    expected: date     # the hand-derived expected date (time-of-day dropped)
    anchor: datetime   # the corpus's "now" (module-level ANCHOR)
    source: str        # "<corpus package>/<test file>::<test function>"


def _corpus_packages() -> Dict[str, str]:
    """Discover ``nl_corpus_<code>`` packages -> {lang_code: dir_path}."""
    out = {}
    for name in sorted(os.listdir(_TEST_DIR)):
        path = os.path.join(_TEST_DIR, name)
        if (name.startswith("nl_corpus_") and os.path.isdir(path)
                and os.path.exists(os.path.join(path, "__init__.py"))):
            out[name[len("nl_corpus_"):]] = path
    return out


class _CollectItemsPlugin:
    def __init__(self):
        self.items = []

    def pytest_collection_modifyitems(self, items):
        self.items.extend(items)


def _collect_lang_gold(lang: str, path: str) -> List[GoldCase]:
    plugin = _CollectItemsPlugin()
    devnull = open(os.devnull, "w")
    stdout, sys.stdout = sys.stdout, devnull
    try:
        pytest.main(
            ["--collect-only", "-q", "-p", "no:cacheprovider", path],
            plugins=[plugin],
        )
    finally:
        sys.stdout = stdout
        devnull.close()

    out = []
    for item in plugin.items:
        # Business-day golds are computed with the ``jurisdiction=`` kwarg
        # (and, in the composition tests, module anchors the collector cannot
        # recover per-case). The adapter cannot reproduce those calls -- and
        # the competitor engines have no jurisdiction concept at all -- so
        # the comparison would be scoring different questions. Excluded, not
        # hidden: the scoreboard documents this.
        if "test_nl_business_days" in item.nodeid:
            continue
        callspec = getattr(item, "callspec", None)
        if callspec is None:
            continue
        params = callspec.params
        if "text" not in params or "expected" not in params:
            continue
        text = params["text"]
        expected = params["expected"]
        if not isinstance(text, str) or not isinstance(expected, (date, datetime)):
            continue
        module = item.module
        anchor = getattr(module, "ANCHOR", datetime(2017, 6, 27, 13, 4))
        exp_date = expected.date() if isinstance(expected, datetime) else expected
        out.append(GoldCase(
            lang=lang, text=text, expected=exp_date, anchor=anchor,
            source=f"{os.path.basename(path)}/{item.nodeid}",
        ))
    return out


def collect_gold_cases(langs: Optional[List[str]] = None) -> List[GoldCase]:
    """Collect every (text -> date) gold case across corpus packages.

    ``langs`` restricts collection to a subset (by chronologia locale code);
    ``None`` collects every discovered corpus package.
    """
    packages = _corpus_packages()
    if langs is not None:
        packages = {k: v for k, v in packages.items() if k in langs}
    cases = []
    for lang, path in packages.items():
        cases.extend(_collect_lang_gold(lang, path))
    return cases


def all_langs() -> List[str]:
    return sorted(_corpus_packages())
