"""Spelled-number folding pre-pass.

The tokenizer only recognises *digit* runs as numbers; natural speech spells
them ("vijf dagen geleden", "lima hari lagi").  This pass folds a maximal run
of number-words into a single digit :class:`~chronologia.extract.model.Token`
so every ``NUM``/``DAY``/``YEAR``/``ORD`` slot binds the same way whether the
writer typed a digit or a word.

The languages in :data:`~chronologia.extract.numlayer.NUMTAG_LANGS` read
their numbers through numtag (:mod:`chronologia.extract.numlayer`).  This
module holds the ``_make_germanic_fold``/``_lazy_germanic_fold``
single-extractor engine that ``numfold_germanic`` uses.  The Romance family
lives in ``numfold_romance``, the North Germanic family in ``numfold_germanic``;
the Slavic, Baltic and Indo-Aryan folds each have their own sibling module.

Wired as a language ``hook`` in each locale's ``lang.json`` and applied by
:func:`~chronologia.extract.pipeline.fold_tokens` after normalisation.  Every
fold is a pure ``tuple[Token] -> tuple[Token]`` transform, re-indexed so
``Token.index`` stays contiguous.
"""
from __future__ import annotations

from dataclasses import replace

from chronologia.extract.numfold_engine import NumberGrammar, make_fold


# ---------------------------------------------------------------------------
# Continental / North Germanic spelled-number folding
#
# The Germanic languages build numbers as single compound words
# ("einundzwanzig" 21, "vijfentwintig" 25), so a spelled number is usually a
# *single* token rather than English's multi-word run.  ovos-number-parser
# resolves those compounds; the fold owns only which tokens are numbers.
#
# Two surfaces must survive the fold: clock fractions ("halb"/"viertel",
# "halv"/"kvart" -- their own FRACTION slot) and scale words
# ("million"/"milliard" -- the deep-time SCALE slot).  They are excluded by
# an explicit stop-set per language.
# ---------------------------------------------------------------------------

def _make_germanic_fold(extract_fn, stop_words, ord_suffixes=(), word_map=None,
                        join_words=()):
    """Build a ``tuple[Token] -> tuple[Token]`` fold for a Germanic language.

    ``extract_fn`` is the language's ``ovos_number_parser`` extractor; the
    German-family extractors return ordinals only under ``ordinals=True`` and
    cardinals only under the default, so both are tried.  ``stop_words`` are
    surfaces that resolve as numbers but must stay their own token (clock
    fractions and scale words).
    """
    stop = frozenset(stop_words)
    joinset = frozenset(join_words)
    suffixes = frozenset(ord_suffixes)
    wmap = dict(word_map or {})

    def value_of(text):
        v = extract_fn(text, ordinals=True)
        if v is False or v is None:
            v = extract_fn(text)
        return v

    def is_ordinal(tok):
        # an ordinal is the surface the back-end reads only as an ordinal
        cardinal = extract_fn(tok.text)
        return ((cardinal is False or cardinal is None)
                and extract_fn(tok.text, ordinals=True) not in (False, None))

    def is_numword(tok):
        if tok.is_number:
            return True
        if tok.text in stop:
            return False
        # a bare multiplier word that BUILDS a number but has no standalone value
        # (Indonesian/Malay "puluh" ten, "ratus" hundred, "belas" -teen): the
        # per-token value probe below reads it as False, which would sever the
        # run at it ("dua ratus" -> [dua][ratus] -> nothing), so admit it to the
        # run explicitly.  Its value comes from the back-end reading the joined
        # run ("dua ratus" == 200); a stray one folds to nothing (value None) and
        # is left untouched.
        if tok.text in joinset:
            return True
        v = value_of(tok.text)
        return v is not None and v is not False

    def pre(tokens):
        # pass -1: rewrite fixed word->value surfaces to digit tokens.  Used
        # for the Frisian inflected "coming-hour" forms ("fiven" -> 5,
        # "fjouweren" -> 4) that the number parser does not recognise but the
        # clock look-ahead ("healwei fiven" == 04:30) needs as a bare HOUR.
        if wmap:
            tokens = tuple(
                replace(t, text=str(wmap[t.text]), raw=t.raw,
                        is_number=True, value=wmap[t.text])
                if (not t.is_number and t.text in wmap) else t
                for t in tokens)

        # pass 0: merge a digit followed by a lone alphabetic ordinal suffix
        # ("21 e" -> 21, Dutch "21e"; "3 de" -> 3).  Digit-dot ordinals are
        # handled by the tokenizer (ordinal_dot); this covers the alpha form.
        if suffixes:
            merged = []
            i = 0
            while i < len(tokens):
                t = tokens[i]
                nxt = tokens[i + 1] if i + 1 < len(tokens) else None
                if (t.is_number and nxt is not None and not nxt.is_number
                        and nxt.text in suffixes):
                    merged.append(replace(t, raw=t.raw + nxt.raw,
                                          ordinal=True))
                    i += 2
                    continue
                merged.append(t)
                i += 1
            tokens = tuple(merged)
        return tokens

    return make_fold(NumberGrammar(
        is_number=is_numword, extract=value_of, pre=pre, ordinal=is_ordinal))


def _lazy_germanic_fold(module_name, fn_name, stop_words, ord_suffixes=(),
                        word_map=None, join_words=()):
    """Defer the ``ovos_number_parser`` import to first call (keeps locale
    load cheap and import-order-independent)."""
    holder = {}

    def fold(tokens):
        f = holder.get("f")
        if f is None:
            import importlib
            extract_fn = getattr(importlib.import_module(module_name), fn_name)
            f = holder["f"] = _make_germanic_fold(extract_fn, stop_words,
                                                  ord_suffixes, word_map,
                                                  join_words)
        return f(tokens)

    return fold
