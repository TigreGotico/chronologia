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

from typing import List, Tuple

from chronologia.extract.model import LangSpec, Token
from chronologia.extract.normaliser import TemporalNormaliser
from chronologia.extract.tokenizer import Tokenizer


def multiword_surfaces(spec: LangSpec) -> Tuple[str, ...]:
    """Multiword period surfaces ("bronze age") the tokenizer splits, longest
    first so "late bronze age" wins over "bronze age"."""
    return tuple(sorted((s for s in spec.periods if " " in s),
                        key=lambda s: len(s.split()), reverse=True))


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
                raw = " ".join(t.raw for t in tokens[i:i + n])
                out.append(Token(text=surface, raw=raw, index=len(out)))
                i += n
                break
        else:
            out.append(Token(tokens[i].text, tokens[i].raw, len(out),
                             tokens[i].is_number, tokens[i].value))
            i += 1
    return tuple(out)


def prematch_tokens(text: str, spec: LangSpec) -> Tuple[Token, ...]:
    """The complete pre-match pipeline for ``text`` under ``spec``."""
    tokens = TemporalNormaliser(spec).normalise(
        Tokenizer(spec.tokenizer).tokenize(text))
    if spec.hook is not None:
        tokens = spec.hook(tokens)
    return merge_multiword(tokens, multiword_surfaces(spec))
