# -*- coding: utf-8 -*-
"""Spelled-ordinal folding shared across the number-fold families.

The cardinal folds (``numfold``, ``numfold_slavic``, ``numfold_semitic``,
``numfold_agglutinative``) read *cardinal* number-words from
``ovos_number_parser``'s ``extract_number_<lang>`` back-end.  Several
constructions instead take a **spelled ordinal** in their ``ORD`` slot -- the
calendar quarter is the canonical one ("třetí kvartál" = third quarter,
"الربع الثالث" = the third quarter).  Those ordinal surfaces are their own
closed morphological class the cardinal back-end does not read, so this
pre-pass folds a lone ordinal-word token to the digit its ``ORD`` slot binds.

The word->value map is built, where the language exposes it, from
``ovos_number_parser``'s ``pronounce_ordinal_<lang>`` (inverted over a small
range); languages whose model carries no ordinal pronouncer supply an explicit
closed table (a fact of the language, kept tiny).  Only **single-token**
ordinal surfaces are folded -- compound ordinals ("twenty-third") are out of
scope for the quarter/scoped-ordinal constructions that need this.

Each entry is applied as a ``tuple[Token] -> tuple[Token]`` pre-pass wrapped
around the language's existing cardinal fold, so the cardinal fold sees an
already-numeric token and leaves it untouched.
"""
from __future__ import annotations

from functools import lru_cache
from importlib import import_module
from typing import Callable, Dict, Optional, Tuple

from chronologia.extract.model import Token
from chronologia.extract.numfold_engine import reindex as _reindex


@lru_cache(maxsize=None)
def _pron_ordinal_map(lang: str, hi: int = 31) -> Dict[str, int]:
    """Invert ``pronounce_ordinal_<lang>`` over ``1..hi`` into a
    single-word surface -> value map, or ``{}`` when the model has no
    ordinal pronouncer."""
    try:
        mod = import_module(f"ovos_number_parser.numbers_{lang}")
        pron = getattr(mod, f"pronounce_ordinal_{lang}")
    except (ImportError, AttributeError):
        return {}
    out: Dict[str, int] = {}
    for n in range(1, hi + 1):
        try:
            w = str(pron(n)).strip().lower()
        except Exception:
            continue
        if w and " " not in w and w not in out:
            out[w] = n
    return out


def _make_rewrite(omap: Dict[str, int]) -> Callable:
    frozen = dict(omap)

    def rewrite(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
        out = []
        changed = False
        for t in tokens:
            if not t.is_number and t.text in frozen:
                val = frozen[t.text]
                out.append(Token(text=str(val), raw=str(val), index=t.index,
                                 is_number=True, value=val,
                                 char_start=t.char_start,
                                 char_end=t.char_end))
                changed = True
            else:
                out.append(t)
        return _reindex(out) if changed else tokens

    return rewrite


def with_ordinals(fold: Callable, lang: str,
                  extra: Optional[Dict[str, int]] = None,
                  exclude=()) -> Callable:
    """Wrap a cardinal ``fold`` so a lone spelled-ordinal surface folds to its
    digit *before* the cardinal fold runs.

    ``extra`` is an explicit surface->value table merged over (and taking
    precedence for the gender/case forms a construction actually attests) the
    model-derived ``pronounce_ordinal_<lang>`` map.  ``exclude`` drops surfaces
    that are **homographs of a calendar name** the fold must not clobber --
    e.g. the Arabic ordinals الأول / الثاني double as the Levantine month
    components (تشرين الأول, كانون الثاني), so they stay their own token.
    """
    omap = dict(_pron_ordinal_map(lang))
    if extra:
        omap.update(extra)
    for w in exclude:
        omap.pop(w, None)
    if not omap:
        return fold
    rewrite = _make_rewrite(omap)

    def folded(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
        return fold(rewrite(tokens))

    return folded
