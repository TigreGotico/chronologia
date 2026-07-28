"""The shared pre-match token pipeline: text -> the exact tokens the matcher sees.

Both the public :func:`~chronologia.extract.extract_timespan` path and the
:func:`~chronologia.extract.explain` debug window run this identical sequence
so a trace never misrepresents a real parse:

1. tokenize (language tokenizer modes);
2. normalise (temporal-lemma / suffix-strip morphology);
3. the language ``hook`` (English: the spelled-number fold ``numfold``), so a
   written-out number ("the fifth of june") binds the same slot a digit would;
4. multiword-vocab merge -- period surfaces the tokenizer split ("bronze age")
   folded back into one token so a single slot can bind them.

Factored here (rather than duplicated in the engine facade and the explain
window) precisely because a divergence between the two is the bug this module
exists to prevent.
"""
from __future__ import annotations

import re
from dataclasses import replace
from typing import List, Tuple

from chronologia.extract.model import LangSpec, Token
from chronologia.extract.normaliser import TemporalNormaliser
from chronologia.extract.numfold_roman import fold_roman_numerals
from chronologia.extract.tokenizer import Tokenizer

_WS = re.compile(r"\s+")


def require_text(text, caller: str) -> str:
    """The input contract of every public extractor, checked once at the edge.

    An extractor reads text, so anything that is not a ``str`` -- ``None``,
    a number, a ``bytes`` blob -- is a mistake in the calling program, and
    the library says so with a :class:`TypeError` that names the contract
    instead of letting an internal ``AttributeError`` leak out several
    frames later.  Text the library simply cannot read, the empty string
    included, is an ordinary answer of "nothing here" and returns the
    extractor's empty result.

    Checking here, at the one place text enters the pipeline, is what keeps
    the internals free of type tests.
    """
    if not isinstance(text, str):
        raise TypeError(
            f"{caller}() reads text: expected str, got "
            f"{type(text).__name__}; unreadable text returns the empty "
            f"result rather than raising")
    return text


def render_remainder(text: str, tokens) -> str:
    """The leftover text of the *unconsumed* ``tokens``, read from ``text``.

    The single source of a remainder string.  ``tokens`` are the tokens no
    construction claimed, in stream order, each still carrying its character
    extent into the original ``text``.  Every maximal run of index-consecutive
    unconsumed tokens is sliced straight out of ``text`` -- so punctuation and
    spacing *inside* a run survive verbatim, where the older ``" ".join(raw)``
    silently dropped them -- then the runs are joined by a single space and inner
    whitespace is collapsed.  A token with no recorded extent (a fully
    engine-synthesised one) falls back to its ``raw`` surface.
    """
    if not tokens:
        return ""
    runs: List[List[Token]] = []
    for t in tokens:
        if runs and t.index == runs[-1][-1].index + 1:
            runs[-1].append(t)
        else:
            runs.append([t])
    parts = []
    for run in runs:
        s, e = run[0].char_start, run[-1].char_end
        if s is None or e is None:
            parts.append(" ".join(x.raw for x in run))
        else:
            parts.append(text[s:e])
    return _WS.sub(" ", " ".join(parts)).strip()


def multiword_surfaces(spec: LangSpec) -> Tuple[str, ...]:
    """Every multiword vocabulary surface the tokenizer split on whitespace,
    longest first so "late bronze age" wins over "bronze age".

    A period ("bronze age"), a named day ("day after tomorrow" / Arabic
    "بعد غد"), a weekday (Hebrew "יום ראשון"), a clock landmark
    ("gece yarısı" / "منتصف الليل"), a meridiem ("öğleden sonra"), a
    season, a decade phrase (Hebrew "שנות השמונים"), a calendar month
    (Levantine "تشرين الأول") or a weekend ("hafta sonu", "آخر هفته",
    "סוף שבוע" / "نهاية الأسبوع") can all be written as several words; the
    tokenizer breaks them apart and this pass glues each back into the single
    token its slot binds.  Numbers never participate, so a merged surface is
    always a lexical token.

    Multiword *connectors* ("vor christus", "قبل الميلاد", "que vén") are
    excluded on purpose -- the matcher binds those natively via
    ``_connector_span``, so pre-merging them here would double-handle the
    surface."""
    seen = set()
    for table in (spec.periods, spec.named_days, spec.clock_landmarks,
                  spec.meridiems, spec.seasons, spec.units, spec.months,
                  spec.weekdays, spec.rel_markers, spec.directions,
                  spec.scope_units, spec.clock_fractions, spec.clock_dirs,
                  spec.decade_words, spec.weekend_words, spec.holidays,
                  spec.regnal_names, spec.archon_names, spec.dayparts):
        seen.update(s for s in table if " " in s)
    for cal in spec.calendar_months.values():
        seen.update(s for s in cal if " " in s)
    return tuple(sorted(seen, key=lambda s: len(s.split()), reverse=True))


def merge_multiword(tokens: Tuple[Token, ...],
                    surfaces: Tuple[str, ...]) -> Tuple[Token, ...]:
    """Fold runs matching a multiword surface back into one token."""
    if not surfaces:
        return tokens
    phrases = [(s.split(), s) for s in surfaces]
    out: List[Token] = []
    i = 0
    while i < len(tokens):
        for words, surface in phrases:
            n = len(words)
            if [t.text for t in tokens[i:i + n]] == words:
                run = tokens[i:i + n]
                raw = " ".join(t.raw for t in run)
                # the merged token spans the whole surface run: its extent runs
                # from the first constituent's start to the last's end.
                out.append(Token(text=surface, raw=raw, index=len(out),
                                 char_start=run[0].char_start,
                                 char_end=run[-1].char_end, cap=run[0].cap,
                                 prev_cap=run[0].prev_cap))
                i += n
                break
        else:
            out.append(replace(tokens[i], index=len(out)))
            i += 1
    return tuple(out)


def pretokens(text: str, spec: LangSpec) -> Tuple[Token, ...]:
    """The pre-match stream *before* number folding: tokenize + normalise only.

    Range detection reads this stream, not the folded one, because the
    spelled-number fold merges digits across a connector -- "3 and 5" collapses
    to one number -- which would erase the very ``and``/``to`` a range splits on.
    Every token still carries its original character extent, so an endpoint
    sub-slice can be folded on its own afterwards (:func:`fold_tokens`).
    """
    return TemporalNormaliser(spec).normalise(
        Tokenizer(spec.tokenizer).tokenize(text))


def fold_tokens(tokens: Tuple[Token, ...], spec: LangSpec,
                text: str) -> Tuple[Token, ...]:
    """The folding tail of the pipeline applied to a (sub-)stream of pretokens.

    Number fold (the per-language ``hook``), the context-gated Roman-numeral
    fold, and the multiword-vocab merge.  Run on the whole stream for the
    single-span path, or on a lone range endpoint's slice so its numbers fold in
    isolation -- exactly as the old per-substring re-tokenization did, but
    without re-running the tokenizer.
    """
    if spec.hook is not None:
        tokens = spec.hook(tokens)
    # context-gated Roman-numeral ordinals ("século XII", "anno MMXX"): a
    # spec-aware fold (it reads the language's own century/year vocabulary), so
    # it runs here rather than in the per-language hook.
    tokens = fold_roman_numerals(tokens, spec, text)
    return merge_multiword(tokens, multiword_surfaces(spec))


def prematch_tokens(text: str, spec: LangSpec) -> Tuple[Token, ...]:
    """The complete pre-match pipeline for ``text`` under ``spec``."""
    return fold_tokens(pretokens(text, spec), spec, text)
