"""A locale fold hook that replaces a run of tokens keeps the character extent.

The fold hooks of fr, pt, es and the other Romance locales build one token from
a run ("20h", "après demain", "ce week-end").  The new token takes the first
token's start and the last token's end, so a mention read through a hook has a
``char_span`` and its ``text`` is the slice of the utterance.
"""
import ast
import glob
import os
from datetime import datetime

import pytest

from chronologia import extract_timespans

ANCHOR = datetime(2017, 6, 27, 13, 4)
HERE = os.path.dirname(__file__)
LANGS = sorted(os.path.basename(p)[len("nl_corpus_"):]
               for p in glob.glob(os.path.join(HERE, "nl_corpus_*")))


def _utterances(lang):
    found = set()
    for path in sorted(glob.glob(os.path.join(HERE, f"nl_corpus_{lang}", "*.py"))):
        with open(path, encoding="utf-8") as fh:
            tree = ast.parse(fh.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                value = node.value.strip()
                if (2 <= len(value) <= 160 and "\n" not in value
                        and any(c.isalnum() for c in value)):
                    found.add(value)
    return sorted(found)


@pytest.mark.parametrize("lang", LANGS)
def test_every_corpus_mention_has_its_slice_of_the_utterance(lang):
    bad = []
    for utterance in _utterances(lang):
        try:
            mentions = extract_timespans(utterance, lang, ANCHOR)
        except Exception:
            continue
        for m in mentions:
            if (m.char_span is None
                    or m.text != utterance[m.char_span[0]:m.char_span[1]]):
                bad.append((utterance, m.text, m.char_span))
    assert not bad, bad[:5]


@pytest.mark.parametrize("text,lang,mention_text,span", [
    ("demain 20h", "fr", "demain 20h", (0, 10)),
    ("20h", "fr", "20h", (0, 3)),
    ("ce week-end", "fr", "ce week-end", (0, 11)),
    ("après demain", "fr", "après demain", (0, 12)),
    ("amanhã às 20h", "pt", "amanhã às 20h", (0, 13)),
    ("1492 d.c.", "es", "1492 d.c", (0, 8)),
    ("20h ce soir", "fr", "20h ce soir", (0, 11)),
    ("du 10h au 12h", "fr", "du 10h au 12h", (0, 13)),
])
def test_a_mention_read_through_a_hook_is_the_utterance_slice(
        text, lang, mention_text, span):
    found = extract_timespans(text, lang, ANCHOR)
    assert [(m.text, m.char_span) for m in found] == [(mention_text, span)]


def test_a_compound_phrase_keeps_each_extent():
    text = "demain 20h après demain"
    found = extract_timespans(text, "fr", ANCHOR)
    assert found
    for m in found:
        assert m.char_span is not None
        assert text[m.char_span[0]:m.char_span[1]] == m.text
