"""Spelled-number folding pre-pass.

The tokenizer only recognises *digit* runs as numbers; natural speech spells
them ("vijf dagen geleden", "lima hari lagi").  This pass folds a maximal run
of number-words into a single digit :class:`~chronologia.extract.model.Token`
so every ``NUM``/``DAY``/``YEAR``/``ORD`` slot binds the same way whether the
writer typed a digit or a word.

The languages in :data:`~chronologia.extract.numlayer.NUMTAG_LANGS` read
their numbers through numtag (:mod:`chronologia.extract.numlayer`).  This
module holds every locale whose fold does not share a family engine with
another language (``fa``, ``id``, ``kab``, ``ms``), and the
``_make_germanic_fold``/``_lazy_germanic_fold`` single-extractor engine that
``numfold_germanic`` also uses.  The Romance family lives in
``numfold_romance``, the North Germanic family in ``numfold_germanic``; the
Slavic, Semitic, Baltic, Indo-Aryan and Greek folds each have their own
sibling module.

Wired as a language ``hook`` in each locale's ``lang.json`` and applied by
:func:`~chronologia.extract.pipeline.fold_tokens` after normalisation.  Every
fold is a pure ``tuple[Token] -> tuple[Token]`` transform, re-indexed so
``Token.index`` stays contiguous.
"""
from __future__ import annotations

from dataclasses import replace

from chronologia.extract.numfold_engine import (NumberGrammar, make_fold,
                                                    reindex as _reindex)
from chronologia.extract.numfold_ordinals import with_ordinals as _with_ordinals




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

fold_id = _lazy_germanic_fold(
    "ovos_number_parser.numbers_id", "extract_number_id",
    {"setengah", "seperempat", "suku", "ribu", "juta", "miliar", "milyar"},
    join_words={"puluh", "ratus", "belas"})
# Indonesian spelled ordinals ("ketiga" third) fold to their digit so the
# scoped_ordinal ``ORD`` slot binds ("Senin ketiga Maret" = the third Monday of
# March); from the model's ``pronounce_ordinal_id`` (ke- prefix), plus the
# alternative first-ordinal surface "kesatu" the pronouncer spells "pertama".
fold_id = _with_ordinals(fold_id, "id", {"kesatu": 1})
fold_ms = _lazy_germanic_fold(
    "ovos_number_parser.numbers_id", "extract_number_ms",
    {"setengah", "separuh", "suku", "ribu", "juta", "bilion", "miliar"},
    join_words={"puluh", "ratus", "belas"})
# Kabyle tells the time with Arabic-borrowed hour NOUNS carrying the definite
# article ("ɣef lxemsa n tmeddit" = at five in the evening), not with the bare
# Berber cardinals.  ovos-number-parser knows the bare borrowings (tlata,
# setta, sebɛa, tmanya) but none of the article-bearing hour forms, so they
# reach the matcher as plain words and no clock order can bind them.  Map them
# to their value the way the Frisian coming-hour forms are mapped, so the HOUR
# slot binds.  Every surface below is written as an hour on kab.wikipedia:
# "ɣef lweḥda n tṣ̣ebḥit", "ɣef tizi n jjuj d wezgen n tmeddit", "ɣef tlata n
# tmeddit", "ɣef ṛṛebɛa d wezgen n tmeddit", "ɣef lxemsa n tmeddit", "ɣef
# tmanya n tmeddit", "ɣef ttesɛa n tṣ̣ebḥit", "Lɛecṛa n tṣ̣ebḥit", "ɣef leḥdac
# d wezgen n tṣ̣ebḥit", "ɣef ttnac n yiḍ" (Tafsut n Yimaziɣen, Bgayet).
# The remaining hour nouns come from the Kabyle sentences on Tatoeba, each
# with the English it is paired with:
#   "Ha-tt-an d ssaɛtin ɣiṛ ṛṛbeɛ."      -- "It's quarter to two."
#   "Ha-tt-an d zzuǧ ɣiṛ ṛṛbeɛ."         -- "It's quarter to two."
#   "Ad d-uɣaleɣ ɣef ssetta d wezgen."   -- "I will be back at half past six."
#   "Ha-tt-an d ssebɛ u ṛṛbeɛ."          -- a seven-o'clock quarter reading.
#   "Ha-tt-an d ttmanya ɣiṛ ṛṛbeɛ."      -- "It's a quarter to eight."
#   "Attan d lεacra d wezgen."           -- "It is ten-thirty."
#   "Ha-tt-an d leḥḍac u ṛṛbeɛ."         -- "It's a quarter past eleven."
# Two and seven take their standard forms from @athmanemokraoui, a native
# Kabyle speaker, on
# https://github.com/TigreGotico/chronologia/pull/846#issuecomment-5573978767:
#   "Six is 'ssetta', but seven is 'ssebɛa' (always with the final -a)."
#   "For the clock hour write 'ssaɛtin' (d ssaɛtin = it's two o'clock).  For
#    the cardinal number 2 itself, use 'jjuǧ' depending on regional
#    phonetics."
# "ssebɛa" and "jjuǧ" rest on that comment alone.  The apocopated "ssebɛ" of
# the Tatoeba sentence above keeps parsing beside "ssebɛa", as do "jjuj" and
# "zzuǧ" beside "jjuǧ" -- a parser accepts every attested variation.
_KAB_HOUR_NOUNS = {
    "lweḥda": 1, "jjuj": 2, "jjuǧ": 2, "zzuǧ": 2, "ssaɛtin": 2, "ṛṛebɛa": 4,
    "lxemsa": 5, "ssetta": 6, "ssebɛa": 7, "ssebɛ": 7, "ttmanya": 8,
    "ttesɛa": 9,
    "lɛecṛa": 10, "lɛacra": 10, "leḥdac": 11, "leḥḍac": 11, "ttnac": 12,
}
fold_kab = _lazy_germanic_fold(
    "ovos_number_parser.numbers_kab", "extract_number_kab",
    {"azgen", "wezgen", "agim", "amelyun"}, word_map=_KAB_HOUR_NOUNS)
# fa (Persian): single extractor extract_number_fa(text, ordinals=False);
# withhold the half/quarter clock words and the scale words.
fold_fa = _lazy_germanic_fold(
    "ovos_number_parser.numbers_fa", "extract_number_fa",
    {"نیم", "ربع", "چارک", "هزار", "میلیون", "میلیارد"})
# Persian spelled ordinals ("سوم" third) fold to their digit so the quarter's
# ``ORD`` slot binds; from the model's ``pronounce_ordinal_fa``.
fold_fa = _with_ordinals(fold_fa, "fa")

#: the Persian length nouns, from ``locale/fa/unit_*.voc``.  A half word
#: directly before one of these closes a length ("نیم ساعت" half an hour,
#: "نیم قرن" half a century); anywhere else "نیم" keeps the clock FRACTION
#: slot it is withheld from the fold for ("سه و نیم" is half past three).
_FA_UNITS = frozenset({"ساعت", "دقیقه", "ثانیه", "روز", "هفته", "ماه",
                       "سال", "دهه", "قرن"})
_FA_HALF = "نیم"


def _fa_half_before_unit(fold):
    """Fold the Persian half word to 0.5 when a length noun closes it.

    Persian counts an offset with a number and a unit ("دو ساعت دیگه" in two
    hours), and the half word is not a number the extractor reads, so the
    half-length frame had no count at all and the phrase resolved to nothing
    while its duration read correctly.  English and German fold their half
    word in the same position and for the same reason.
    """
    def pre(tokens):
        out = []
        for i, t in enumerate(tokens):
            nxt = tokens[i + 1] if i + 1 < len(tokens) else None
            if (t.text == _FA_HALF and nxt is not None
                    and nxt.text in _FA_UNITS):
                out.append(replace(t, text="0.5", is_number=True, value=0.5))
                continue
            out.append(t)
        return fold(_reindex(tuple(out)))

    return pre


fold_fa = _fa_half_before_unit(fold_fa)



