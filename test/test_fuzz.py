"""Crash-freeness fuzz suite.

The public extraction edges (:func:`~chronologia.extract.extract_timespan`,
:func:`~chronologia.extract.nseries.extract_duration`,
:func:`~chronologia.extract.nseries.extract_recurrence`,
:func:`~chronologia.extract.nseries.extract_timespans`) must never raise on
*any* string input -- untrusted natural-language text is exactly the input
this library exists to eat, so a crash on garbage input is always a bug,
never an acceptable "user error". Each function's contract is: return
``None``/``[]`` (no match) or a valid result -- never propagate an
exception.

Every property here is seeded/deterministic (Hypothesis runs with
``derandomize=True``; the plain-Python generators use a fixed
``random.Random`` seed) so this suite is reproducible in CI with no
wall-clock dependency, and stays within a roughly 30s budget across all 40
locale languages.

Any crash found during authoring was either fixed (if a trivial input
guard) or is recorded below as a minimized ``xfail`` with its repro -- see
the "known crashes" section at the bottom of this file.
"""
from __future__ import annotations

import os
import random
import string

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from chronologia.extract import extract_timespan
from chronologia.extract.nseries import (extract_duration, extract_recurrence,
                                         extract_timespans)

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_LOCALE_DIR = os.path.join(_REPO_ROOT, "chronologia", "locale")
_TEST_DIR = os.path.dirname(os.path.abspath(__file__))

#: every language chronologia ships locale data for -- discovered, never
#: hardcoded, so a new locale package is covered automatically.
LANGS = sorted(
    d for d in os.listdir(_LOCALE_DIR)
    if os.path.isdir(os.path.join(_LOCALE_DIR, d)))

FUNCS = (
    ("extract_timespan", lambda t, l: extract_timespan(t, l)),
    ("extract_duration", lambda t, l: extract_duration(t, l)),
    ("extract_recurrence", lambda t, l: extract_recurrence(t, l)),
    ("extract_timespans", lambda t, l: extract_timespans(t, l)),
)

_FAST = settings(
    max_examples=3, derandomize=True, deadline=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large,
                          HealthCheck.function_scoped_fixture],
)


def _assert_never_raises(text, lang):
    for name, fn in FUNCS:
        try:
            fn(text, lang)
        except Exception as exc:  # pragma: no cover - failure path
            pytest.fail(
                f"{name}({text!r}, lang={lang!r}) raised "
                f"{type(exc).__name__}: {exc}")


# --------------------------------------------------------------------------
# 1. Random unicode strings, per language.
# --------------------------------------------------------------------------

#: known-crashing inputs excluded from the generic property below and
#: recorded explicitly further down (see "known crashes"), so this property
#: documents the gap instead of going red on every run.
_KNOWN_CRASH_INPUTS = {
    "da": {"¹"}, "nb": {"¹"}, "nn": {"¹"},
}


@pytest.mark.parametrize("lang", LANGS)
@given(text=st.text(min_size=0, max_size=200))
@_FAST
def test_random_unicode_never_crashes(lang, text):
    if text in _KNOWN_CRASH_INPUTS.get(lang, ()):
        pytest.skip("known crash, see test_known_crash_superscript_digit_nb_da_nn")
    _assert_never_raises(text, lang)


# --------------------------------------------------------------------------
# 2. Mixed-script garbage (Latin + CJK + Arabic + emoji + combining marks).
# --------------------------------------------------------------------------

_MIXED_SCRIPT_ALPHABET = st.sampled_from(
    "abcXYZ0123456789 \t\n"
    "中文测试"       # CJK
    "العربية"  # Arabic
    "\U0001F600\U0001F4C5\U0001F553"  # emoji incl. calendar/clock
    "́̈"                    # combining acute/diaeresis
    "​‎‮"              # zero-width / bidi control
)


@pytest.mark.parametrize("lang", LANGS)
@given(text=st.text(alphabet=_MIXED_SCRIPT_ALPHABET, min_size=0, max_size=100))
@_FAST
def test_mixed_script_garbage_never_crashes(lang, text):
    _assert_never_raises(text, lang)


# --------------------------------------------------------------------------
# 3. Real corpus sentences: random truncations and concatenations.
# --------------------------------------------------------------------------

def _corpus_sentences():
    """A pool of real natural-language sentences pulled from every corpus.

    Reuses the benchmark adapter's own gold-case collector so this stays in
    sync with the corpora without re-implementing pytest collection here.
    """
    import sys
    sys.path.insert(0, _REPO_ROOT)
    from benchmark.adapter import collect_gold_cases

    return [c.text for c in collect_gold_cases()]


_CORPUS_SENTENCES = _corpus_sentences()
_RNG = random.Random(1234)


def _truncations_and_concats(n):
    """``n`` deterministic truncations/concatenations of real sentences."""
    out = []
    if not _CORPUS_SENTENCES:
        return out
    for _ in range(n):
        a = _RNG.choice(_CORPUS_SENTENCES)
        if _RNG.random() < 0.5:
            # truncate at a random character boundary (may split mid-word,
            # mid-token, or even mid multi-byte grapheme cluster).
            cut = _RNG.randint(0, len(a))
            out.append(a[:cut] if _RNG.random() < 0.5 else a[cut:])
        else:
            b = _RNG.choice(_CORPUS_SENTENCES)
            sep = _RNG.choice([" ", "", "; ", "\n", " and "])
            out.append(a + sep + b)
    return out


@pytest.mark.parametrize("lang", LANGS)
def test_corpus_truncations_and_concats_never_crash(lang):
    for text in _truncations_and_concats(6):
        _assert_never_raises(text, lang)


# --------------------------------------------------------------------------
# 4. Huge inputs (10k chars).
# --------------------------------------------------------------------------

#: tokenizing+resolving a 10k-char string costs ~0.2-1.2s per call in this
#: engine (real, measured cost -- not a hang: every shape below completes
#: well under a couple of seconds on every one of the 40 languages). Running
#: all three shapes through all four extract_* functions on all 40
#: languages would alone burn well over a minute, blowing the ~30s budget
#: for no extra crash-finding power beyond a couple of languages -- a
#: single repeated character (no token boundaries at all) is checked on
#: every language with the cheapest function; the fuller sweep (a repeated
#: real phrase, a 10k CJK run, all four functions) runs on a small but
#: script-diverse subset.
_HUGE_SWEEP_LANGS = [l for l in ("en", "de", "ar", "he", "tr") if l in LANGS]


@pytest.mark.parametrize("lang", LANGS)
def test_huge_repeated_char_never_crashes(lang):
    try:
        extract_timespan("x" * 10_000, lang)
    except Exception as exc:  # pragma: no cover - failure path
        pytest.fail(
            f"extract_timespan('x'*10000, lang={lang!r}) raised "
            f"{type(exc).__name__}: {exc}")


@pytest.mark.parametrize("lang", _HUGE_SWEEP_LANGS)
def test_huge_input_full_sweep_never_crashes(lang):
    huge_repeat = ("in three weeks from tomorrow at 5pm on june the 3rd, "
                  "1998 next monday ")
    huge = (huge_repeat * (10_000 // len(huge_repeat) + 1))[:10_000]
    assert len(huge) == 10_000
    _assert_never_raises(huge, lang)
    _assert_never_raises("中" * 10_000, lang)


# --------------------------------------------------------------------------
# 5. Null-ish / degenerate edge cases.
# --------------------------------------------------------------------------

_NULLISH = (
    "", " ", "\t", "\n", "\r\n", "   \n\t  ",
    "\x00", "\x00\x00\x00", "﻿", "​",
    ".", ",", "...", "???", "!!!",
    "0", "-1", "999999999999999999999999999999",
    string.punctuation,
)


@pytest.mark.parametrize("lang", LANGS)
def test_nullish_edge_cases_never_crash(lang):
    for text in _NULLISH:
        _assert_never_raises(text, lang)


# --------------------------------------------------------------------------
# 6. extract_timespans: non-overlapping, in-order mentions.
# --------------------------------------------------------------------------

def _mentions_are_ordered_and_non_overlapping(mentions):
    prev_end = None
    for m in mentions:
        span = m.char_span or m.token_span
        assert span[0] <= span[1], f"inverted extent {span!r} in {m!r}"
        if prev_end is not None:
            assert span[0] >= prev_end, (
                f"mention {m!r} starts before the previous one ends "
                f"(prev_end={prev_end})")
        prev_end = span[1]


@pytest.mark.parametrize("lang", LANGS)
def test_extract_timespans_never_overlap_and_stay_ordered(lang):
    texts = _truncations_and_concats(4) + [
        "meet friday at 3 or monday at noon",
        "in three weeks and also next tuesday",
    ]
    for text in texts:
        try:
            mentions = extract_timespans(text, lang)
        except Exception as exc:  # pragma: no cover - failure path
            pytest.fail(
                f"extract_timespans({text!r}, lang={lang!r}) raised "
                f"{type(exc).__name__}: {exc}")
        assert isinstance(mentions, list)
        _mentions_are_ordered_and_non_overlapping(mentions)


# --------------------------------------------------------------------------
# Known crashes (minimized repro).
#
# Found by ``test_random_unicode_never_crashes`` during authoring of this
# suite: ``extract_timespan("¹", lang)`` (a bare superscript "1", U+00B9)
# raises an uncaught ``ValueError`` for the "da"/"nb"/"nn" locales.
#
# Root cause lives *outside* chronologia, in the shared
# ``ovos-number-parser`` dependency: ``numbers_nb.py``'s
# ``_expand_compound_numbers`` -> ``_int_value`` helper checks
# ``w.isdigit()`` (which Python considers ``True`` for Unicode superscript
# digits such as "¹") and then calls the builtin ``int(w)`` on it, which
# rejects the same string ("invalid literal for int() with base 10: '¹'")
# -- an ``isdigit()``/``int()`` mismatch on a non-ASCII digit character, not
# a chronologia bug. chronologia's own ``numfold.py`` propagates whatever
# ``ovos-number-parser`` raises without a guard.
#
# This benchmark/fuzz task's scope is explicitly "do NOT touch the extract
# engine" (chronologia/extract/*), and the fix belongs even further
# upstream in ovos-number-parser, not in this repo at all -- so it is
# recorded here as a documented, minimized xfail rather than patched.
# --------------------------------------------------------------------------

@pytest.mark.parametrize("lang", ["da", "nb", "nn"])
@pytest.mark.xfail(
    strict=True, raises=ValueError,
    reason="ovos-number-parser numbers_nb.py: isdigit()/int() mismatch on "
           "U+00B9 superscript '1' -- upstream bug, not in chronologia's "
           "extract engine or in this repo's scope; see comment above.")
def test_known_crash_superscript_digit_nb_da_nn(lang):
    extract_timespan("¹", lang)
