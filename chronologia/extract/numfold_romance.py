"""Romance-language spelled-number folding (an/ast/mwl/oc/ro).

Catalan, French, Galician, Italian, Portuguese and Spanish read their numbers
through numtag (``numlayer_ca`` and its siblings).

Shared mechanism: the number-word set is read from ovos_number_parser's
``NumberVocabulary`` for the language, and a maximal run of those words
(joined by the language's "and" word) is folded to a single digit token via
``extract_number_<lang>`` (ordinals included).  Per-language wrappers add the
token-surgery a locale needs on top (elision splits, clock-notation folds,
fixed-idiom collapses, ordinal-fraction homograph licensing, and the
deep-time SCALE-frame licensing shared by every Romance locale).

Split out of ``numfold.py`` verbatim (behaviour-preserving refactor); shared
primitives (``NumberGrammar``/``make_fold``/``reindex``) come from
``numfold_engine``, and ordinal-pronouncer wrapping from ``numfold_ordinals``.
"""
from __future__ import annotations

import os
from dataclasses import replace
from importlib import import_module

from ovos_number_parser.util import NumberVocabulary

from chronologia.extract.model import Token
from chronologia.extract.numfold_engine import (NumberGrammar, make_fold,
                                                with_marked_h_clock,
                                                    reindex as _reindex)
from chronologia.extract.numfold_ordinals import with_ordinals as _with_ordinals


# ---------------------------------------------------------------------------
# Romance spelled-number folding
# ---------------------------------------------------------------------------
#
# The English fold above carries its own closed-class word list.  The Romance
# languages share one mechanism: the number-word set is read straight from
# ``ovos_number_parser``'s ``NumberVocabulary`` for the language, and a
# maximal run of those words (joined by the language's "and" word) is folded
# to a single digit token via ``extract_number_<lang>`` (ordinals included).
#
# Two classes of word are deliberately *withheld* from the run so the token
# that distinguishes a construction survives intact:
#
#   * clock fractions (``meia`` / ``media`` / ``mig`` ...) -- their own
#     ``FRACTION`` slot ("as tres e meia");
#   * multiplier scale words (``mil`` / ``milhao`` / ``bilhao`` ...) -- the
#     ``SCALE`` slot of deep time ("66 milhoes de anos atras").
#
# A per-language weekday blacklist keeps a feminine-ordinal surface that
# doubles as a weekday name (pt "segunda"/"quarta"/"quinta"/"sexta") from
# ever being read as a number.
from importlib import import_module


def _number_vocabulary(numbers_mod):
    """The language's ``NumberVocabulary`` instance; a language may subclass it
    (ovos-number-parser's Occitan ``OccitanVocabulary``)."""
    return next(v for v in vars(numbers_mod).values()
                if isinstance(v, NumberVocabulary))


def _fem_forms(surf):
    """Feminine ordinal surfaces of a masculine ordinal: ``o``->``a``
    (primeiro->primeira) and a bare ``+a`` (tercer->tercera, segon->segona)
    cover pt/es/gl and ca respectively.  Spurious candidates are harmless --
    they never occur in real text."""
    s = surf.lower()
    forms = {s + "a"}
    if s.endswith("o"):
        forms.add(s[:-1] + "a")
    return forms


def _romance_numwords(vocab, blacklist):
    """The closed set of spelled number-words the fold may absorb, built from
    a ``NumberVocabulary``.  Cardinals, tens, hundreds and ordinals are in;
    fractions, multiplier scales and the language's hundred particle stay in
    but only when they are not scale words; blacklisted weekday-homographs
    are removed."""
    words = set()
    for table in (vocab.UNITS, vocab.TENS, vocab.HUNDREDS,
                  vocab.ORDINAL_UNITS, vocab.ORDINAL_TENS,
                  vocab.ORDINAL_HUNDREDS):
        words.update(v.lower() for v in table.values() if v)
    # Feminine hundreds ("duzentas", "quinhentas", "quinientas") -- the vocab's
    # HUNDREDS are masculine-only and GENDERED_SPELLINGS covers just 1/2, but
    # 200-900 in pt/es/gl regularly agree -os -> -as with a feminine unit
    # ("quinhentas horas").  The backend already parses the feminine surface;
    # this is a pure surface-set gap.  "cem"/"cien"/"cen" (100) is invariable
    # and does not end in "-os", so it is untouched; other Romance hundreds
    # (ca "dos-cents", it "cento", ro "sute", fr "cent") do not end in "-os".
    for v in vocab.HUNDREDS.values():
        s = (v or "").lower()
        if s.endswith("os"):
            words.add(s[:-2] + "as")
    words.update(k.lower() for k in vocab.ALT_SPELLINGS)
    for gmap in vocab.GENDERED_SPELLINGS.values():
        words.update(v.lower() for v in gmap.values() if v)
    # feminine ordinals ("primeira", "terceira") -- generated o->a, then the
    # weekday-homograph blacklist is applied below
    for v in list(vocab.ORDINAL_UNITS.values()):
        if v:
            words.update(_fem_forms(v))
    if vocab.HUNDRED_PARTICLE:
        words.add(vocab.HUNDRED_PARTICLE.lower())
    # withhold multiplier scale words (mil/milhao/bilhao...) and clock
    # fractions so deep-time SCALE and clock FRACTION tokens survive
    scales = set()
    for table in (vocab.SHORT_SCALE, vocab.LONG_SCALE):
        scales.update(v.lower() for v in table.values() if v)
    fractions = set()
    for table in (vocab.FRACTION, vocab.FRACTION_FEMALE):
        fractions.update(v.lower() for v in table.values() if v)
    words -= scales
    words -= fractions
    words -= {w.lower() for w in blacklist}
    return frozenset(words)


#: definite articles (incl. elided "l") *per locale* -- the position that
#: licenses the *ordinal* reading of an ordinal-fraction homograph.  The scoped
#: ordinal is always "il/el/o/la <ordinal> <weekday|unit>"; the clock fraction
#: is "un/e <quarto>", never introduced by a definite article, so keying the
#: fold off a preceding definite article leaves every clock fraction byte-
#: identical.  Kept per-locale on purpose: a surface that is a definite article
#: in one Romance language ("i" = Italian masculine plural article) is the
#: coordinator "and" in another (Catalan "les tres **i** quart"), so a merged
#: set would mis-license a clock fraction.  A fact of the languages, kept tiny.
_ROMANCE_DEFINITE = {
    "oc": frozenset({"lo", "la", "los", "las", "les", "l"}),
    "an": frozenset({"o", "a", "os", "as", "lo", "la", "los", "las", "l"}),
    "ast": frozenset({"el", "la", "lo", "los", "les", "l"}),
    "mwl": frozenset({"l", "la", "lo", "ls", "las", "los"}),
    "ro": frozenset(),
}


def _homograph_ordinal_map(vocab, blacklist):
    """Surface -> value for the *ordinal* reading of every ordinal-unit
    surface that is also a *fraction* word ("terzo"/"quarto"/"cuarto" =
    third/fourth *and* a-third/a-quarter).  These are dropped from the
    number-fold's word set (see :func:`_romance_numwords`) so the clock
    FRACTION slot keeps them, which silently disabled the ``scoped_ordinal``
    ("il quarto giovedì di novembre") reading for every ordinal a language
    happens to spell like its fraction.  A blacklisted weekday-homograph
    (Portuguese feminine "quarta" = Wednesday) is excluded -- its ordinal /
    weekday ambiguity is a separate, positionally-licensed concern."""
    fractions = set()
    for table in (vocab.FRACTION, vocab.FRACTION_FEMALE):
        fractions.update(v.lower() for v in table.values() if v)
    black = {w.lower() for w in blacklist}
    out = {}
    for val, surf in vocab.ORDINAL_UNITS.items():
        if not surf:
            continue
        for s in {surf.lower()} | _fem_forms(surf):
            if s in fractions and s not in black:
                out[s] = val
    return out


def _homograph_tens_map(vocab, blacklist):
    """Surface -> value for the *ordinal* reading of every ORDINAL_TENS
    surface that is also a *fraction* word (pt/es/gl "décimo" = tenth *and*
    a-tenth; Catalan spells every ordinal 11-19 the same as its fraction --
    "tretzè"/"dotzè" = 13th/12th *and* a-thirteenth/a-twelfth).  Held out of
    the number-fold's word set for the same reason as the unit homographs
    (see :func:`_homograph_ordinal_map`), and licensed back positionally by
    :func:`_license_tens_homograph` -- but *keeping the original surface*
    rather than stamping straight to a digit, because a tens word is not
    always the whole ordinal on its own: "décimo segundo" (twelfth) and
    "décimo terceiro" (thirteenth) are TWO-token compounds the number
    back-end composes from the spelled tens word plus a following spelled
    unit, and stamping the tens word to its own bare digit (as the unit
    homograph fold does, correctly, for a single-word ordinal) would feed
    the back-end "10 segundo" and silently truncate the compound to 10."""
    fractions = set()
    for table in (vocab.FRACTION, vocab.FRACTION_FEMALE):
        fractions.update(v.lower() for v in table.values() if v)
    black = {w.lower() for w in blacklist}
    out = {}
    for val, surf in vocab.ORDINAL_TENS.items():
        if not surf:
            continue
        for s in {surf.lower()} | _fem_forms(surf):
            if s in fractions and s not in black:
                out[s] = val
    return out


def _license_tens_homograph(tokens, tens_map, definite, quarter_words=frozenset()):
    """Positionally read a tens ordinal/fraction homograph ("décimo"/"tretzè").

    Same positional rule as :func:`_license_ordinal_fraction` -- licensed
    after a definite article or before the quarter noun, left alone (the
    fraction reading) everywhere else -- but the token keeps its ORIGINAL
    surface, only ``is_number``/``value`` are stamped, so a following
    spelled unit word still composes through the shared back-end ("décimo
    segundo" -> 12, "décimo terceiro" -> 13) instead of being handed a
    pre-stamped digit the back-end cannot recombine with the next word.
    """
    if not tens_map or (not definite and not quarter_words):
        return tokens
    out = list(tokens)
    changed = False
    n = len(out)
    for i, t in enumerate(out):
        if t.is_number or t.text not in tens_map:
            continue
        prev = out[i - 1] if i - 1 >= 0 else None
        nxt = out[i + 1] if i + 1 < n else None
        after_article = prev is not None and prev.text in definite
        before_quarter = nxt is not None and nxt.text in quarter_words
        if not after_article and not before_quarter:
            continue  # not an ordinal frame -- leave for FRACTION
        out[i] = replace(t, is_number=True, value=tens_map[t.text],
                         ordinal=True)
        changed = True
    return _reindex(tuple(out)) if changed else tokens


#: locale root, for reading a language's ``marker_quarter_word.voc`` (the
#: calendar-quarter noun -- "trimestre") at fold-build time.
_LOCALE_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "locale")


def _quarter_word_surfaces(lang_code):
    """The calendar-quarter noun surfaces ("trimestre"/"trimestres") of a
    language, read from ``locale/<lang>/marker_quarter_word.voc``.

    This is the *second* position (besides a preceding definite article) that
    licenses the ordinal reading of an ordinal-fraction homograph: an ordinal
    number-word directly before the quarter noun is the quarter selector
    ("cuarto **trimestre**" = fourth quarter), never the clock/duration
    fraction, which is never followed by "trimestre".  Read from the same
    vocabulary the ``quarter_ref`` construction binds so the two never drift."""
    path = os.path.join(_LOCALE_ROOT, lang_code, "marker_quarter_word.voc")
    if not os.path.exists(path):
        return frozenset()
    out = set()
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            surf = line.strip()
            if surf and not surf.startswith("#"):
                out.add(surf.lower())
    return frozenset(out)


def _license_ordinal_fraction(tokens, homomap, definite, quarter_words=frozenset()):
    """Positionally read an ordinal-fraction homograph ("quarto"/"cuarto").

    The surface is the scoped ordinal ("**il quarto** giovedì", "**la cuarta**
    semana") directly after a definite article, the quarter selector ("**cuarto
    trimestre** de 2040" = fourth quarter) directly before the calendar-quarter
    noun, and the clock quarter ("tre **e quarto**", "un **quarto** d'ora")
    everywhere else.  Only the two ordinal frames -- a preceding definite
    article, or a following quarter noun -- fold to the digit so
    ``scoped_ordinal`` / ``quarter_ref`` bind it; every clock-fraction frame
    keeps the bare word for the FRACTION slot, so the fold is byte-identical
    there (a fraction word is never followed by "trimestre" nor, in the
    duration frame "un quarto de hora", introduced by a definite article).  The
    positive licence also survives a fold that segments the stream around a
    protected article (Portuguese "um quarto"): a segment stripped of its
    article no longer sees the definite article and correctly stays the
    fraction word."""
    if not homomap or (not definite and not quarter_words):
        return tokens
    out = list(tokens)
    changed = False
    n = len(out)
    for i, t in enumerate(out):
        if t.is_number or t.text not in homomap:
            continue
        prev = out[i - 1] if i - 1 >= 0 else None
        nxt = out[i + 1] if i + 1 < n else None
        after_article = prev is not None and prev.text in definite
        before_quarter = nxt is not None and nxt.text in quarter_words
        if not after_article and not before_quarter:
            continue  # not an ordinal frame -- leave for FRACTION
        val = homomap[t.text]
        out[i] = Token(text=str(val), raw=t.raw, index=0, is_number=True,
                       value=val, char_start=t.char_start,
                       char_end=t.char_end, ordinal=True)
        changed = True
    return _reindex(tuple(out)) if changed else tokens


# abbreviations the tokenizer shatters on their dots/hyphens ("a.c." -> a,c;
# "meio-dia" -> meio,dia).  The fold glues the fragments back into the single
# token a marker/landmark slot binds.  Keyed by the fragment tuple, longest
# match first; shared across the Romance locales (surfaces are the same).
_ROMANCE_GLUE = {
    ("a", "e", "c"): "aec", ("a", "c"): "ac", ("d", "c"): "dc",
    ("e", "c"): "ec", ("a", "p"): "ap",
    ("meio", "dia"): "meiodia", ("meia", "noite"): "meianoite",
    ("migdia",): "migdia",
}


def _glue(tokens):
    seqs = sorted(_ROMANCE_GLUE, key=len, reverse=True)
    out = []
    i = 0
    n = len(tokens)
    while i < n:
        for seq in seqs:
            k = len(seq)
            if tuple(t.text for t in tokens[i:i + k]) == seq:
                raw = "".join(t.raw for t in tokens[i:i + k])
                out.append(Token(text=_ROMANCE_GLUE[seq], raw=raw, index=0))
                i += k
                break
        else:
            out.append(tokens[i])
            i += 1
    return tuple(out)


def _romance_additive_join(left, right):
    """Is ``left e right`` a genuine additive continuation of one Romance
    numeral (``vinte e cinco`` == 25), rather than two separate numbers the
    ``e`` merely stands between (``sete e vinte`` == seven, *e* twenty)?

    The connective ``e`` fills the next place of a *round* base: a tens word
    from twenty up ("vinte e cinco"), or a hundred/thousand ("cento e vinte",
    "mil e quinhentos").  The rule, in place-value terms: the running value is
    a multiple of ten of at least twenty, and the joined atom is smaller than
    the base's lowest occupied place -- so a unit (< 10) may follow a ten, a
    two-digit remainder (< 100) may follow a hundred, and so on.  Teen bases
    (``dez e cinco``) and unit bases (``sete e vinte``) are excluded, which is
    exactly what leaves a spoken clock minute for the MINUTE slot.
    """
    if left < 20 or left % 10 != 0 or right <= 0:
        return False
    place = 10
    while left % (place * 10) == 0:
        place *= 10
    return right < place


def _make_romance_fold(lang_code, blacklist, reader=None,
                       extra_numwords=frozenset(), extra_homograph=None,
                       extra_ordinals=None, word_map=None):
    """``extra_ordinals`` -- a closed surface->value table for spelled
    ordinals a language's ``NumberVocabulary`` does not carry at all (rather
    than carrying under a different, homograph-colliding spelling): Spanish
    fuses its 11th-19th/21st-29th/31st ordinals into a single word
    ("decimotercero", "vigesimoprimero") the vocabulary's ORDINAL_TENS/
    ORDINAL_UNITS tables do not list (they list only the two-word compound's
    components, "décimo"/"tercero", which already compose through the
    back-end).  Entries are added to both the run-membership word set and
    the single-token fallback map, exactly like the vocabulary-derived
    ordinals above.

    ``word_map`` -- a closed surface->value table for spelled cardinals
    ``extract_number_<lang>`` does not read under an attested spelling
    variant (mirrors the Germanic ASCII-twin ``word_map`` in
    :func:`chronologia.extract.numfold.make_germanic_fold`): the surface is
    rewritten to a digit token in a pre-pass, before the vocabulary-driven
    extractor ever sees it, so no change to ``ovos_number_parser`` is
    needed."""
    from ovos_number_parser.util import RomanceNumberExtractor
    numbers_mod = import_module("ovos_number_parser.numbers_" + lang_code)
    vocab = _number_vocabulary(numbers_mod)
    # the shared spoken-number reader; for most Romance languages
    # ``extract_number_<lang>`` is a thin wrapper over exactly this, and a
    # language whose wrapper adds a real hook passes that wrapper as ``reader``.
    extractor = RomanceNumberExtractor(vocab)

    def extract_fn(text, ordinals=True):
        if reader is not None:
            return reader(text, ordinals=ordinals)
        return extractor.extract_number(text, ordinals=ordinals)
    extra_ordinals = {k.lower(): v for k, v in (extra_ordinals or {}).items()}
    numwords = (_romance_numwords(vocab, blacklist) | frozenset(extra_numwords)
               | frozenset(extra_ordinals))
    joins = frozenset(j.lower() for j in vocab.JOIN_WORD)
    # some ``extract_number_<lang>`` back-ends do not recognise the feminine
    # ordinal surface ("tercera", "segona"); a direct surface->value map,
    # built from the masculine ordinals plus their generated feminine forms,
    # is the fallback for a single-token run the back-end rejects.
    ordinal_value = {}
    for table in (vocab.ORDINAL_UNITS, vocab.ORDINAL_TENS):
        for val, surf in table.items():
            if surf:
                ordinal_value[surf.lower()] = val
                for fem in _fem_forms(surf):
                    ordinal_value[fem] = val
    ordinal_value = {k: v for k, v in ordinal_value.items()
                     if k in numwords}
    ordinal_value.update(extra_ordinals)

    wmap = dict(word_map or {})

    def _pre(tokens):
        if wmap:
            tokens = tuple(
                replace(t, text=str(wmap[t.text]), raw=t.raw,
                        is_number=True, value=wmap[t.text])
                if (not t.is_number and t.text in wmap) else t
                for t in tokens)
        return _glue(tokens)

    # the word-map rewrite (if any) runs first so a spelling variant becomes
    # a plain digit token before the a.c./d.c. glue and the shared engine see
    # it; run membership from the vocab-derived word set, the language's
    # JOIN_WORD as the internal connector (kept in the back-end text), and
    # the feminine-ordinal map as the single-token fallback the back-end
    # rejects.
    base = make_fold(NumberGrammar(
        is_number=lambda tok: tok.is_number or tok.text in numwords,
        extract=lambda text: extract_fn(text, ordinals=True),
        joiner=lambda tok: tok.text in joins,
        single_fallback=ordinal_value.get,
        pre=_pre,
        bridge_ok=_romance_additive_join,
        ordinal=lambda tok: tok.text in ordinal_value))
    # ordinal-fraction homographs ("quarto" = fourth *and* a-quarter) are held
    # out of ``numwords`` above so the clock FRACTION slot keeps them; license
    # the ordinal reading back positionally (outside the "un quarto" fraction
    # frame) so the scoped_ordinal construction can bind higher ordinals.
    homomap = dict(_homograph_ordinal_map(vocab, blacklist))
    # some languages spell the quarter ordinal with a surface their own number
    # vocabulary does not list as an ordinal ("quarto" in Aragonese, whose
    # ordinal-4 is "cuatreno" and whose fraction-4 is "cuarto"); an explicit
    # homograph entry licenses that surface in the ordinal frames only.
    if extra_homograph:
        homomap.update(extra_homograph)
    # ORDINAL_TENS surfaces that are also fraction words ("décimo", the
    # Catalan 11th-19th series) need the same positional licensing, but
    # composing rather than digit-stamped -- see :func:`_homograph_tens_map`.
    tens_homomap = _homograph_tens_map(vocab, blacklist)
    definite = _ROMANCE_DEFINITE.get(lang_code, frozenset())
    quarter_words = _quarter_word_surfaces(lang_code)
    if (not homomap and not tens_homomap) or (not definite and not quarter_words):
        return base

    def folded(tokens):
        tokens = _license_tens_homograph(tokens, tens_homomap, definite,
                                         quarter_words)
        return base(_license_ordinal_fraction(tokens, homomap, definite,
                                              quarter_words))
    return folded


# ---------------------------------------------------------------------------
# deep-time SCALE-frame licensing for the Romance folds
# ---------------------------------------------------------------------------
#
# Two surfaces the general Romance fold deliberately leaves alone must become
# numbers in the one frame that precedes a deep-time SCALE word:
#
#   * the INDEFINITE ARTICLE ("un"/"une"/"um") -- blacklisted from the fold
#     because it is the everyday article ("un jour", "um dia"); directly before
#     a scale word it is the number one ("un milliard", "un billón d'anos"), the
#     same positional licensing English does in ``_fold_article_magnitude``;
#   * the THOUSAND word ("mil") directly before a MILLION word -- the long-scale
#     languages spell 10^9 as a multiword "mil millones"/"mil milhões"; folding
#     "mil" to the numeral 1000 lets the deep-time order read it as NUM=1000
#     SCALE=million (1000 Ma = 10^9), reusing the numeral machinery whole.
#
# Both fire ONLY in the scale frame (the very next token is a scale word), so
# every other "un"/"mil" reading is untouched.
def _romance_scale_frame(lang_code, article_ones,
                         million_extra=frozenset(), scale_extra=frozenset()):
    """Wrap a Romance fold with the deep-time SCALE-frame number licensing.

    ``article_ones`` are the language's indefinite-article surfaces (the
    number one before a scale word).  The thousand/million/scale word sets are
    read from the language's ``NumberVocabulary`` (short + long scale); the
    vocabulary lists only singular scale words, so ``million_extra`` supplies
    the plural million surfaces the multiword 10^9 ("mil millones", "mil
    milhões") actually uses, and ``scale_extra`` any further billion-cognate
    surfaces the article-one frame must recognise.
    """
    numbers_mod = import_module("ovos_number_parser.numbers_" + lang_code)
    vocab = _number_vocabulary(numbers_mod)
    thousand, million, scale_all = set(), set(million_extra), set(scale_extra)
    scale_all |= set(million_extra)
    for table in (vocab.SHORT_SCALE, vocab.LONG_SCALE):
        for factor, surf in table.items():
            if not surf:
                continue
            s = surf.lower()
            scale_all.add(s)
            if factor == 1_000:
                thousand.add(s)
            elif factor == 1_000_000:
                million.add(s)

    def prepass(tokens):
        out = []
        n = len(tokens)
        i = 0
        while i < n:
            t = tokens[i]
            nxt = tokens[i + 1] if i + 1 < n else None
            nxt_txt = nxt.text if nxt is not None else None
            if (not t.is_number and nxt is not None and not nxt.is_number
                    and t.text in article_ones and nxt_txt in scale_all):
                out.append(_scale_num_token(1, t))
                i += 1
                continue
            if (not t.is_number and nxt is not None and not nxt.is_number
                    and t.text in thousand and nxt_txt in million):
                out.append(_scale_num_token(1_000, t))
                i += 1
                continue
            out.append(t)
            i += 1
        return _reindex(tuple(out))

    return prepass


def _scale_num_token(value, like):
    """A numeral token of ``value`` carrying ``like``'s character extent."""
    return Token(text=str(value), raw=like.raw, index=0, is_number=True,
                 value=value, char_start=like.char_start,
                 char_end=like.char_end)


def _with_scale_frame(fold, lang_code, article_ones,
                      million_extra=frozenset(), scale_extra=frozenset()):
    prepass = _romance_scale_frame(lang_code, article_ones,
                                   million_extra, scale_extra)
    return lambda tokens: fold(prepass(tokens))


# an: "martes" (Tuesday) must never be read as a number; the Romance factory
# folds via numbers_an's NumberVocabulary and the shared a.c./d.c. glue.
# an: "quarto" (the qu- spelling) is the idiomatic masculine ordinal 4th before
# "trimestre", but numbers_an lists ordinal-4 only as "cuatreno" and fraction-4
# as "cuarto", so "quarto" is unknown to the vocabulary; an explicit homograph
# entry licenses it to the digit 4 in the ordinal frames (definite article /
# before the quarter noun) only, leaving the "cuarto" quarter-hour fraction
# ("un cuarto de hora") untouched.
fold_an = _make_romance_fold("an", {"martes"}, extra_homograph={"quarto": 4})
# Aragonese apocopated ordinals ("primer", "tercer") the NumberVocabulary lists
# only in their full form ("primero", "tercero"); the apocope is the surface a
# noun phrase attests ("o tercer trimestre").  numbers_an carries no ordinal
# pronouncer, so this is an explicit closed table.
fold_an = _with_ordinals(fold_an, "an", {"primer": 1, "tercer": 3})
# mwl (Mirandese): the feminine ordinals segunda/terça/quarta/quinta/sesta
# are weekday names (segunda-feira ...) and sábado is Saturday -- none may be
# read as a number.
fold_mwl = _make_romance_fold(
    "mwl", {"segunda", "terça", "terca", "quarta", "quinta", "sesta",
            "sabado", "sábado"})


# ---------------------------------------------------------------------------
# ro / oc / ast: language-specific pre-passes layered on the shared Romance
# fold factory.
#
# ``_make_romance_fold`` already owns spelled-number folding (compound
# numbers, JOIN_WORD bridging, feminine ordinals, and the a.c./d.c. glue).
# These locales need small token-surgery pre-passes it does not provide:
# elided proclitics split so a bare year-word binds ("d'annadas" -> d
# annadas), fixed idiom phrases collapse to one connector ("înainte de
# hristos"), the Occitan "NhMM" clock notation folds to an HH:MM literal, and
# a digit followed by an ordinal-suffix word merges ("20-lea" -> 20).  The
# numtag folds of French and Italian share these pre-passes.
# ---------------------------------------------------------------------------

def _elision_split(tokens, proclitics):
    """Split a leading elided proclitic ("d'annees" -> "d", "annees").

    Only the closed proclitic set splits, so a lexical apostrophe inside a
    word ("aujourd'hui") stays whole."""
    out = []
    for t in tokens:
        head, sep, tail = t.text.partition("'")
        if not sep:
            head, sep, tail = t.text.partition("’")
        if sep and head in proclitics and tail:
            # keep each half's character extent into the original utterance --
            # the proclitic occupies the head chars, the elided word the tail
            # chars past the apostrophe -- so a mention built on the split word
            # ("d'abril") still recovers a char span instead of ``None``.
            cs, ce = t.char_start, t.char_end
            if cs is None or ce is None:
                h_start = h_end = w_start = None
            else:
                h_start, h_end, w_start = cs, cs + len(head), ce - len(tail)
            out.append(Token(text=head, raw=head, index=0,
                             char_start=h_start, char_end=h_end))
            out.append(Token(text=tail, raw=tail, index=0,
                             char_start=w_start, char_end=ce if cs is not None
                             else None))
        else:
            out.append(t)
    return _reindex(out)



def _collapse_phrase(tokens, words, surface):
    """Collapse a fixed multiword sequence ("il y a") to one token."""
    n = len(words)
    out = []
    i = 0
    while i < len(tokens):
        if [t.text for t in tokens[i:i + n]] == words:
            raw = " ".join(t.raw for t in tokens[i:i + n])
            out.append(Token(text=surface, raw=raw, index=0))
            i += n
        else:
            out.append(tokens[i])
            i += 1
    return _reindex(out)


def _collapse_h_clock(tokens, governors=frozenset(), followers=frozenset()):
    """Fold French/Occitan "20h30"/"20h" into one ``HH:MM`` clock literal.

    ``governors`` and ``followers`` keep "h" a word: after a counted-offset
    preposition ("dans 2 h") it is the unit of a length, and before a clock
    direction ("9 h et quart") it is the hour word the direction counts from.
    Both readings come from "h" being the symbol of "heure", so the grammar
    reads them as it reads "dans 2 heures" and "9 heures et quart".
    """
    out = []
    i = 0
    n = len(tokens)
    while i < n:
        t = tokens[i]
        nxt = tokens[i + 1] if i + 1 < n else None
        nn = tokens[i + 2] if i + 2 < n else None
        spared = ((out and out[-1].text in governors)
                  or (nn is not None and nn.text in followers))
        if (not spared
                and t.is_number and t.value is not None and 0 <= t.value <= 24
                and float(t.value).is_integer() and nxt is not None
                and nxt.text == "h"):
            if (nn is not None and nn.is_number and nn.value is not None
                    and 0 <= nn.value <= 59 and float(nn.value).is_integer()):
                lit = "%d:%02d" % (int(t.value), int(nn.value))
                out.append(Token(text=lit, raw=lit, index=0))
                i += 3
                continue
            lit = "%d:00" % int(t.value)
            out.append(Token(text=lit, raw=lit, index=0))
            i += 2
            continue
        out.append(t)
        i += 1
    return _reindex(out)


def _merge_digit_ordinal(tokens, suffixes):
    """Drop a lone ordinal-suffix word after a digit ("1 er" -> 1)."""
    out = []
    i = 0
    n = len(tokens)
    while i < n:
        t = tokens[i]
        nxt = tokens[i + 1] if i + 1 < n else None
        if (t.is_number and nxt is not None and not nxt.is_number
                and nxt.text in suffixes):
            out.append(replace(t, ordinal=True))
            i += 2
            continue
        out.append(t)
        i += 1
    return _reindex(out)


def _romance_prepass_fold(lang_code, blacklist, proclitics=frozenset(),
                          phrases=(), h_clock=False, h_spared=((), ()),
                          ord_suffixes=frozenset(),
                          fem_ord=None, reader=None,
                          extra_numwords=frozenset(), extra_homograph=None,
                          extra_ordinals=None, word_map=None,
                          ord_article=frozenset()):
    base = _make_romance_fold(lang_code, blacklist, reader=reader,
                              extra_numwords=extra_numwords,
                              extra_homograph=extra_homograph,
                              extra_ordinals=extra_ordinals,
                              word_map=word_map)
    fem_ord = fem_ord or {}

    def fold(tokens):
        if proclitics:
            tokens = _elision_split(tokens, proclitics)
        for seq, surface in phrases:
            tokens = _collapse_phrase(tokens, seq, surface)
        if h_clock:
            tokens = _collapse_h_clock(tokens, frozenset(h_spared[0]),
                                       frozenset(h_spared[1]))
        if ord_suffixes:
            tokens = _merge_digit_ordinal(tokens, ord_suffixes)
        if fem_ord:
            # feminine ordinals the number back-end rejects ("a doua",
            # "la segunda") -- map the surface straight to its digit.  With
            # ``ord_article`` the surface is an ordinal only after that
            # article: Romanian "doua" alone is the cardinal two.
            tokens = _reindex(tuple(
                Token(text=str(fem_ord[t.text]), raw=t.raw, index=0,
                      is_number=True, value=fem_ord[t.text],
                      ordinal=(not ord_article
                               or (i > 0 and tokens[i - 1].text in ord_article)))
                if (not t.is_number and t.text in fem_ord) else t
                for i, t in enumerate(tokens)))
        return base(tokens)

    return fold


# -- Romanian ---------------------------------------------------------------
_RO_PHRASES = [
    (["înainte", "de", "hristos"], "ihr"), (["inainte", "de", "hristos"], "ihr"),
    (["după", "hristos"], "dhr"), (["dupa", "hristos"], "dhr"),
    (["î", "hr"], "ihr"), (["i", "hr"], "ihr"), (["d", "hr"], "dhr"),
    (["miezul", "nopții"], "miezulnoptii"), (["miezul", "noptii"], "miezulnoptii"),
    (["week", "end"], "weekend"),
]
fold_ro = _romance_prepass_fold(
    "ro", {"un", "unu", "una", "o"},
    phrases=_RO_PHRASES,
    ord_suffixes=frozenset({"lea", "a", "ea", "le"}),
    fem_ord={"doua": 2, "treia": 3, "patra": 4, "cincea": 5,
             "șasea": 6, "sasea": 6, "șaptea": 7, "saptea": 7, "opta": 8,
             "noua": 9, "zecea": 10},
    # The ordinal is "a doua" and the cardinal is "două" (DOOM 3, "doilea"
    # and "doi").  "doua" and "noua" are also the cardinals written without
    # diacritics, so the ordinal takes the article.  "două" is not in the
    # table: after "a" it is the genitive cardinal ("mamă a două fete",
    # C. Stan, Revue roumaine de linguistique LV (3), 2010, p. 243)
    ord_article=frozenset({"a"}))
# deep-time SCALE-frame licensing: "un miliard/un bilion de ani în urmă"
fold_ro = _with_scale_frame(fold_ro, "ro", frozenset({"un", "unu", "una", "o"}))


def _ro_tens_and_one(tokens):
    """Join "douăzeci și unu / una" (21) after the cardinal fold.

    "unu" and "una" are held out of the run set because they are the article
    and the scale-frame count ("un miliard de ani"), so the fold stops at
    "și" and the compound 21, 31 ... 91 never folds ("douăzeci și doi" folds
    because "doi" is an ordinary number word).  Wiktionary: douăzeci și unu
    "twenty-one".  Joined only after a tens count 20..90 and the joiner."""
    out = []
    i = 0
    n = len(tokens)
    while i < n:
        t = tokens[i]
        if (t.is_number and t.value in (20, 30, 40, 50, 60, 70, 80, 90)
                and i + 2 < n and tokens[i + 1].text == "și"
                and tokens[i + 2].text in ("unu", "una")):
            last = tokens[i + 2]
            out.append(Token(text=str(int(t.value) + 1),
                             raw=" ".join(x.raw for x in tokens[i:i + 3]),
                             index=t.index, is_number=True,
                             value=int(t.value) + 1,
                             char_start=t.char_start, char_end=last.char_end))
            i += 3
            continue
        out.append(t)
        i += 1
    return _reindex(tuple(out))


_fold_ro_base = fold_ro


def fold_ro(tokens):
    return _ro_tens_and_one(_fold_ro_base(tokens))


# -- Occitan ----------------------------------------------------------------
_OC_PHRASES = [
    (["abans", "jèsus", "crist"], "acn"), (["abans", "jesus", "crist"], "acn"),
    (["abans", "nòstra", "èra"], "acn"), (["abans", "nostra", "era"], "acn"),
    (["aprèp", "jèsus", "crist"], "apc"), (["aprep", "jesus", "crist"], "apc"),
    (["de", "nòstra", "èra"], "apc"), (["de", "nostra", "era"], "apc"),
    (["abans", "ièr"], "abansièr"), (["abans", "ier"], "abansièr"),
    (["passat", "deman"], "passatdeman"), (["delà", "deman"], "passatdeman"),
    (["que", "ven"], "queven"),
    (["week", "end"], "weekend"),
    # the future-offset marker survives the elision split as one token, the
    # way "dins" does, so the offset grammar binds it ("d'aquí un moment",
    # oc.wiktionary s.v. "lèu").
    (["d", "aquí"], "d'aquí"), (["d", "aicí"], "d'aicí"),
]
# "uèch" (8) is the only spelling ovos_number_parser.numbers_oc reads;
# "uèit"/"uòch" are attested variants it does not (source: native-speaker
# review, https://github.com/OpenVoiceOS/ovos-date-parser/issues/300).
fold_oc = _romance_prepass_fold(
    "oc", {"un", "una"},
    proclitics=frozenset({"l", "d", "un", "qu", "n", "s"}),
    phrases=_OC_PHRASES, h_clock=True,
    ord_suffixes=frozenset({"èr", "er", "n", "nd", "en", "ena", "a", "d"}),
    word_map={"uèit": 8, "uòch": 8})


# -- Asturian ---------------------------------------------------------------
_AST_PHRASES = [
    (["enantes", "de", "cristu"], "adc"), (["antes", "de", "cristu"], "adc"),
    (["dempués", "de", "cristu"], "ddc"), (["despues", "de", "cristu"], "ddc"),
    # the areligious era wording: "cuartu mileniu enantes de la nuesa era"
    # (https://ast.wikipedia.org/wiki/Espada), "l'añu 28 de la nuesa era"
    # (https://ast.wikipedia.org/wiki/Xuan_Bautista).
    (["enantes", "de", "la", "nuesa", "era"], "adc"),
    (["de", "la", "nuesa", "era"], "ddc"),
    (["pasáu", "mañana"], "trasmañana"), (["pasao", "mañana"], "trasmañana"),
    (["que", "vien"], "quevien"),
    (["fin", "de", "selmana"], "findeselmana"),
]
fold_ast = _romance_prepass_fold(
    "ast", set(),
    proclitics=frozenset({"l", "d", "un", "n"}),
    phrases=_AST_PHRASES,
    fem_ord={"primera": 1, "segunda": 2, "tercera": 3, "cuarta": 4,
             "quinta": 5, "sexta": 6, "séptima": 7, "septima": 7,
             "octava": 8, "novena": 9, "décima": 10, "decima": 10})
# Asturian counts the article-one like its Iberian siblings: "una" is the
# numeral wherever a count is expected ("a la una" -- one o'clock, attested in
# running prose on ast.wikipedia: "a la una de la madrugada"), and the article
# only where it heads a scale frame ("hai un millón d'anos").  The blanket
# blacklist read it as the article everywhere, so the feminine hour never
# folded.
fold_ast = _with_scale_frame(fold_ast, "ast", frozenset({"un", "una"}),
                             million_extra=frozenset({"millones", "millon",
                                                      "millón"}))


# The hour-letter clock is written in both of these languages, but only
# where a clock marker already announces one: "la ora 21h30", "a les 21h30".  Each marker set is that locale's own
# marker_at and marker_oclock surfaces, so the notation folds exactly where
# the grammar already reads a clock; a bare "21h30" stays unread, and the
# phrase returns nothing rather than the hour alone with "h30" stranded.
fold_ro = with_marked_h_clock(fold_ro, {"la", "ora", "ore"})
fold_ast = with_marked_h_clock(fold_ast, {"a", "les", "la", "hores", "hora"})
