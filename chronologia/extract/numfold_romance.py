"""Romance-language spelled-number folding (an/ast/ca/es/fr/gl/it/mwl/oc/pt/ro).

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

from ovos_number_parser.numbers_fr import extract_number_fr

from chronologia.extract.model import Token
from chronologia.extract.numfold_engine import (NumberGrammar, make_fold,
                                                    reindex as _reindex)
from chronologia.extract.numfold_ordinals import with_ordinals as _with_ordinals


# ---------------------------------------------------------------------------
# Romance spelled-number folding (pt / es / gl / ca)
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
    "it": frozenset({"il", "lo", "la", "i", "gli", "le", "l"}),
    "es": frozenset({"el", "la", "los", "las"}),
    "ca": frozenset({"el", "la", "els", "les", "l"}),
    "gl": frozenset({"o", "a", "os", "as"}),
    "pt": frozenset({"o", "a", "os", "as"}),
    "fr": frozenset({"le", "la", "les", "l"}),
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
        out[i] = replace(t, is_number=True, value=tens_map[t.text])
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
                       char_end=t.char_end)
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
                       extra_ordinals=None):
    """``extra_ordinals`` -- a closed surface->value table for spelled
    ordinals a language's ``NumberVocabulary`` does not carry at all (rather
    than carrying under a different, homograph-colliding spelling): Spanish
    fuses its 11th-19th/21st-29th/31st ordinals into a single word
    ("decimotercero", "vigesimoprimero") the vocabulary's ORDINAL_TENS/
    ORDINAL_UNITS tables do not list (they list only the two-word compound's
    components, "décimo"/"tercero", which already compose through the
    back-end).  Entries are added to both the run-membership word set and
    the single-token fallback map, exactly like the vocabulary-derived
    ordinals above."""
    from ovos_number_parser.util import RomanceNumberExtractor
    numbers_mod = import_module("ovos_number_parser.numbers_" + lang_code)
    vocab = next(v for v in vars(numbers_mod).values()
                 if type(v).__name__ == "NumberVocabulary")
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

    # the a.c./d.c. glue runs first, then the shared engine: run membership
    # from the vocab-derived word set, the language's JOIN_WORD as the internal
    # connector (kept in the back-end text), and the feminine-ordinal map as the
    # single-token fallback the back-end rejects.
    base = make_fold(NumberGrammar(
        is_number=lambda tok: tok.is_number or tok.text in numwords,
        extract=lambda text: extract_fn(text, ordinals=True),
        joiner=lambda tok: tok.text in joins,
        single_fallback=ordinal_value.get,
        pre=_glue,
        bridge_ok=_romance_additive_join))
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
    vocab = next(v for v in vars(numbers_mod).values()
                 if type(v).__name__ == "NumberVocabulary")
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


# pt: feminine ordinals "segunda/quarta/quinta/sexta" are weekday names
_fold_pt_base = _make_romance_fold("pt", {"segunda", "quarta", "quinta", "sexta",
                                          "terca", "terça"})


def _license_weekday_ordinal(tokens, mapping, units):
    """Read a weekday-homograph ordinal as its digit before a period noun.

    The feminine ordinals a Romance language blacklists from the number fold
    are blacklisted because each is also the name of a weekday -- Portuguese
    "segunda" is at once the ordinal "second" and Monday (segunda-feira).  The
    blacklist protects the weekday reading everywhere, but directly before the
    week noun the weekday reading is not available: "a segunda semana de março"
    is the second week of March, never Monday, because a weekday name does not
    take a following "semana".  In that one position the homograph is licensed
    to its digit so the "nth week of a month" composition can bind it, the same
    positional licensing that lets the plural weekday surface be read only in
    the syntactic slot that disambiguates it.
    """
    out = []
    n = len(tokens)
    for i, tok in enumerate(tokens):
        nxt = tokens[i + 1] if i + 1 < n else None
        if (not tok.is_number and tok.text in mapping
                and nxt is not None and nxt.text in units):
            value = mapping[tok.text]
            out.append(Token(text=str(value), raw=tok.raw, index=0,
                             is_number=True, value=value))
        else:
            out.append(tok)
    return _reindex(tuple(out))


#: The week nouns of Portuguese, the position that licenses the ordinal
#: reading of a weekday-homograph ordinal.
_PT_WEEK_UNITS = frozenset({"semana", "semanas"})
#: weekday-homograph feminine ordinal -> its value.  "terça" (Tuesday) is not
#: listed: the third ordinal is "terceira", no homograph, and it already folds.
_PT_ORDINAL_BEFORE_WEEK = {"segunda": 2, "quarta": 4, "quinta": 5, "sexta": 6}

# Portuguese writes the clock quarter with an explicit article -- "quatro e um
# quarto" == 4:15, "duas menos um quarto" == 1:45 -- where the "um"/"uma" is the
# article of "um quarto" (a quarter), not a number.  The spelled-number fold
# would otherwise read "quatro e um" as 5 (the JOIN_WORD "e") or fold the lone
# "um" to the digit 1, both of which lose the article the clock grammar needs.
# Unlike Italian/French (which blacklist "un" outright), Portuguese still spells
# "vinte e um" == 21 with a standalone "um", so the article cannot be removed
# from the number vocabulary wholesale -- it is protected only in the one place
# it is unambiguously an article: directly before the "quarto" fraction word.
# The stream is folded around such an "um", leaving "vinte e um dias" == 21
# untouched.  Source: Ciberdúvidas da Língua Portuguesa, "as horas".
_PT_QUARTER_SURFACES = frozenset({"quarto", "quartos"})


def fold_pt(tokens):
    # Portuguese writes the digital clock exactly like French/Occitan --
    # "15h", "15h30", "9h" -- so the same "Nh[MM]" literal is folded to an
    # ``HH:MM`` CLOCK token here (see :func:`_collapse_h_clock`).  Without
    # this the grammar reads the digits as HOUR and strands the bare "h" as
    # unmatched remainder, since no pt clock_time order consumes it.
    tokens = _collapse_h_clock(tokens)
    tokens = _license_weekday_ordinal(tokens, _PT_ORDINAL_BEFORE_WEEK,
                                      _PT_WEEK_UNITS)
    protected = {
        i for i, t in enumerate(tokens)
        if t.text in ("um", "uma") and i + 1 < len(tokens)
        and tokens[i + 1].text in _PT_QUARTER_SURFACES
    }
    if not protected:
        return _fold_pt_base(tokens)
    out = []
    segment = []
    for i, t in enumerate(tokens):
        if i in protected:
            if segment:
                out.extend(_fold_pt_base(tuple(segment)))
                segment = []
            out.append(t)
        else:
            segment.append(t)
    if segment:
        out.extend(_fold_pt_base(tuple(segment)))
    return _reindex(tuple(out))


# Portuguese marks a *recurring set* with the plural throughout: "todas as
# terceiras quintas-feiras do mes" (every third thursday of the month) carries
# a plural article, a plural ordinal and a plural weekday, where the singular
# would name one particular occasion.  The plural feminine ordinal is the same
# closed morphological class as its singular, so it is derived from the number
# vocabulary (feminine form + "s") rather than listed by hand.
#
# Both genders are folded, because the weekday the ordinal agrees with picks
# the gender: "as terceiras quintas-feiras" (feminine, a weekday in -feira)
# against "os primeiros sabados" (masculine, saturday/sunday).
#
# Two classes of surface are held back.  The weekday homographs are skipped in
# the plural for exactly the reason they are blacklisted in the singular --
# "quintas" is Thursday, never five -- which also leaves "segundas" alone so
# "todas as segundas-feiras" stays a weekday.  And the masculine plurals that
# are ordinary nouns the fold must not eat are excluded by name: "segundos" is
# seconds and "quartos" is the clock quarter, both of which other constructions
# in this engine bind as words.
_PT_WEEKDAY_ORDINALS = frozenset({"segunda", "terca", "terça", "quarta",
                                  "quinta", "sexta"})
#: masculine plural ordinals that are homographs of a noun this engine reads.
_PT_ORDINAL_NOUN_HOMOGRAPHS = frozenset({"segundos", "quartos"})
#: plural feminine ordinals that are homographs of a Roman-calendar anchor.
#: "nonas" is at once the ninth-plural ordinal and the vernacular Nones; it is
#: held back from the plural-ordinal fold and licensed to the digit 9 by
#: :func:`_license_pt_nonas` everywhere except the anchor frame ("as nonas de
#: julho"), where it must survive as the word so ``roman_date`` binds it.
_PT_ANCHOR_ORDINAL_HOMOGRAPHS = frozenset({"nonas"})
#: pt "of" prepositions (plain and article-fused) that introduce the month in
#: the Roman-anchor frame -- the position that licenses the Nones reading.
_PT_OF_PREP = frozenset({"de", "do", "da", "dos", "das", "d"})


def _license_pt_nonas(tokens):
    """Positionally read the homograph "nonas".

    Portuguese "nonas" is at once the feminine plural ordinal "ninth" and the
    vernacular name of the Roman *Nones*.  The two readings split by position:
    the anchor is followed by an "of" preposition introducing the month ("as
    nonas **de** julho"), the ordinal is not ("as nonas semanas").  "nonas" is
    withheld from the plural-ordinal fold (see :data:`_PT_ANCHOR_ORDINAL_HOMOGRAPHS`)
    and licensed back to the digit 9 here in every position that is **not** the
    anchor frame, so ``roman_date`` binds the Nones while the plain ordinal
    still folds.
    """
    out = list(tokens)
    n = len(out)
    for i, t in enumerate(out):
        if t.is_number or t.text != "nonas":
            continue
        nxt = out[i + 1] if i + 1 < n else None
        if nxt is not None and nxt.text in _PT_OF_PREP:
            continue
        out[i] = Token(text="9", raw=t.raw, index=0, is_number=True,
                       value=9, char_start=t.char_start, char_end=t.char_end)
    return _reindex(tuple(out))


def _pt_plural_ordinals():
    from ovos_number_parser import numbers_pt
    vocab = next(v for v in vars(numbers_pt).values()
                 if type(v).__name__ == "NumberVocabulary")
    out = {}
    for val, surf in vocab.ORDINAL_UNITS.items():
        if not surf:
            continue
        for form in _fem_forms(surf) | {surf.lower()}:
            if form in _PT_WEEKDAY_ORDINALS:
                continue
            plural = form + "s"
            if plural in _PT_ORDINAL_NOUN_HOMOGRAPHS:
                continue
            if plural in _PT_ANCHOR_ORDINAL_HOMOGRAPHS:
                continue
            out[plural] = val
    return out


def _pt_ordinal_fold(fold):
    """Wrap ``fold`` so *only* the plural ordinals above are pre-folded.

    ``with_ordinals`` merges the model-derived ``pronounce_ordinal_pt`` map by
    default, whose **singular** entries are homographs this engine binds as
    words -- "quarto" is the clock quarter ("as tres e quarto", "um quarto de
    hora") and "segundo" is a second.  Folding those to digits would take the
    clock fraction and duration constructions apart, so every model-derived
    surface is excluded and the plural table is the whole contribution.
    """
    plurals = _pt_plural_ordinals()
    from chronologia.extract.numfold_ordinals import _pron_ordinal_map
    exclude = set(_pron_ordinal_map("pt")) - set(plurals)
    return _with_ordinals(fold, "pt", plurals, exclude=exclude)


fold_pt = _pt_ordinal_fold(fold_pt)
_fold_pt_ordinal = fold_pt


def fold_pt(tokens):  # noqa: F811 -- final wrap adds Nones licensing
    return _license_pt_nonas(_fold_pt_ordinal(tokens))


# deep-time SCALE-frame licensing: "um bilião"/"mil milhões de anos"
fold_pt = _with_scale_frame(fold_pt, "pt", frozenset({"um", "uma"}),
                            million_extra=frozenset({"milhões", "milhoes",
                                                     "milhão", "milhao"}))


# Spanish fuses its 11th-19th/21st-29th/31st ordinals into a single word --
# "decimotercero" (13th), "vigesimoprimero" (21st) -- rather than the
# two-word compound ("décimo tercero") the NumberVocabulary's ORDINAL_TENS/
# ORDINAL_UNITS tables already compose through the back-end.  The fused
# spelling is the one RAE prescribes as primary and the one native text
# overwhelmingly uses; without it "el decimotercer mes de 2026" silently
# degraded to a bare year_ref match on "2026" instead of refusing (no 13th
# month exists) the way "el 13.º mes de 2026" and English "the thirteenth
# month of 2026" already do (R81, PR #640).
#
# Source: Real Academia Española, Diccionario panhispánico de dudas (2005),
# s.v. "numerales, 2.2" -- the fused spelling loses the tens-word's own
# written accent ("décimo"->"decimo-", "vigésimo"->"vigesimo-") while the
# unit component keeps its own ("séptimo" -> "decimoséptimo"); "undécimo"/
# "duodécimo" are the classical alternatives for 11th/12th, "decimonoveno"/
# "decimonono" both attested for 19th.  Apocopated forms ("decimotercer",
# "vigesimoprimer") are the form used directly before a masculine singular
# noun ("el decimotercer mes"), mirroring "tercer"/"primer" themselves.
_ES_TENS_PREFIX = {10: "decimo", 20: "vigesimo", 30: "trigesimo"}
#: masculine unit-ordinal suffix fused onto the tens prefix above.
_ES_UNIT_SUFFIX_MASC = {1: "primero", 2: "segundo", 3: "tercero", 4: "cuarto",
                        5: "quinto", 6: "sexto", 7: "séptimo", 8: "octavo",
                        9: "noveno"}
#: apocopated masculine forms (before a masculine singular noun) -- only
#: 1st and 3rd apocopate in Spanish.
_ES_UNIT_SUFFIX_APOC = {1: "primer", 3: "tercer"}
#: classical alternative spellings RAE lists alongside the productive fused
#: form, keyed by value.
_ES_ORDINAL_ALT = {11: ("undécimo",), 12: ("duodécimo",),
                   19: ("decimonono",)}


def _es_fuse(prefix, suffix):
    """Fuse a tens prefix onto a unit suffix, eliding the tens prefix's
    trailing "o" before the unit's own leading "o" ("decimo" + "octavo" ->
    "decimoctavo", never the double-vowel "decimooctavo") -- the one unit
    (8th, "octavo") that starts with the vowel the prefix ends in."""
    if prefix.endswith("o") and suffix.startswith("o"):
        return prefix[:-1] + suffix
    return prefix + suffix


def _es_compound_ordinals():
    out = {}
    for tens_val, prefix in _ES_TENS_PREFIX.items():
        for unit_val, suffix in _ES_UNIT_SUFFIX_MASC.items():
            val = tens_val + unit_val
            masc = _es_fuse(prefix, suffix)
            out[masc] = val
            out[masc[:-1] + "a"] = val  # feminine: -o -> -a
            apoc_suffix = _ES_UNIT_SUFFIX_APOC.get(unit_val)
            if apoc_suffix:
                out[prefix + apoc_suffix] = val
            for alt in _ES_ORDINAL_ALT.get(val, ()):
                out[alt] = val
                out[alt[:-1] + "a"] = val
    return out


fold_es = _make_romance_fold("es", set(), extra_ordinals=_es_compound_ordinals())
fold_gl = _make_romance_fold("gl", set())
fold_ca = _make_romance_fold("ca", set())
# deep-time SCALE-frame licensing (article-one + multiword "mil <million>")
fold_es = _with_scale_frame(fold_es, "es", frozenset({"un", "una"}),
                            million_extra=frozenset({"millones", "millon",
                                                     "millón"}))
fold_gl = _with_scale_frame(fold_gl, "gl", frozenset({"un", "unha"}),
                            million_extra=frozenset({"millóns", "millons",
                                                     "millón", "millon"}))
fold_ca = _with_scale_frame(fold_ca, "ca", frozenset({"un", "una"}),
                            million_extra=frozenset({"milions", "milió"}))
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
# fr / it / ro / oc / ast: language-specific pre-passes layered on the shared
# Romance fold factory.
#
# ``_make_romance_fold`` already owns spelled-number folding (compound
# numbers, JOIN_WORD bridging, feminine ordinals, and the a.c./d.c. glue).
# These five locales need small token-surgery pre-passes it does not provide:
# elided proclitics split so a bare year-word binds ("d'annees" -> d annees),
# fixed idiom phrases collapse to one connector ("il y a", "avanti cristo"),
# French/Occitan "NhMM" clock notation folds to an HH:MM literal, and a digit
# followed by an ordinal-suffix word merges ("1er" -> 1, "20-lea" -> 20).
# "un/una" are blacklisted from folding so the clock fraction "meno un
# quarto" keeps its article token.
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


#: "jour(s)" -- the one unit "N jours après/avant demain/hier" ("N days
#: after/before tomorrow/yesterday") is spelled with, checked by
#: :func:`_num_unit_before` to decide whether "après demain"/"avant hier"
#: are the fixed +-2-day idiom or the DIRECTIONAL MARKER of a genuine
#: numeral-scaled offset (see ``_FR_GUARDED_PHRASES``).
_FR_DAY_UNIT_WORDS = frozenset({"jour", "jours"})


def _num_unit_before(tokens, i, unit_words):
    """True when a ``[NUM] UNIT`` pre-amble ends immediately at index ``i``
    ("**deux jours** " before "après demain") -- read from the still
    UN-folded stream (spelled numbers have not folded to digits yet at this
    point in the pipeline), so a spelled numeral is recognised through
    :func:`extract_number_fr` rather than ``Token.is_number``."""
    if i < 2:
        return False
    unit_tok, num_tok = tokens[i - 1], tokens[i - 2]
    if unit_tok.text not in unit_words:
        return False
    if num_tok.is_number:
        return True
    value = extract_number_fr(num_tok.text, ordinals=False)
    return value is not False and value is not None


#: fused French idiom surfaces whose collapse must be HELD BACK when a
#: numeral quantity heads them ("deux jours après demain" = demain+2, an
#: ordinary numeral-scaled offset with "après" as its marker, R147) --
#: unlike a bare "après demain"/"avant hier", which is always the fixed
#: +-2-day idiom.  Every other ``_FR_PHRASES`` entry (the BC/AD markers,
#: "il y a", "week end") has no such competing numeral-offset reading, so it
#: collapses unconditionally.
_FR_GUARDED_PHRASES = frozenset({"apresdemain", "avanthier"})


def _collapse_phrase(tokens, words, surface):
    """Collapse a fixed multiword sequence ("il y a") to one token.

    A guarded surface (see ``_FR_GUARDED_PHRASES``) is left un-collapsed
    when a ``[NUM] UNIT`` pre-amble ("deux jours") immediately precedes it,
    so the directional marker word stays a separate token for the offset
    grammar (or the generic anchored-offset composition pass) to bind.
    """
    n = len(words)
    guarded = surface in _FR_GUARDED_PHRASES
    out = []
    i = 0
    while i < len(tokens):
        if ([t.text for t in tokens[i:i + n]] == words
                and not (guarded
                        and _num_unit_before(tokens, i, _FR_DAY_UNIT_WORDS))):
            raw = " ".join(t.raw for t in tokens[i:i + n])
            out.append(Token(text=surface, raw=raw, index=0))
            i += n
        else:
            out.append(tokens[i])
            i += 1
    return _reindex(out)


def _collapse_h_clock(tokens):
    """Fold French/Occitan "20h30"/"20h" into one ``HH:MM`` clock literal."""
    out = []
    i = 0
    n = len(tokens)
    while i < n:
        t = tokens[i]
        nxt = tokens[i + 1] if i + 1 < n else None
        nn = tokens[i + 2] if i + 2 < n else None
        if (t.is_number and t.value is not None and 0 <= t.value <= 24
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
            out.append(t)
            i += 2
            continue
        out.append(t)
        i += 1
    return _reindex(out)


def _romance_prepass_fold(lang_code, blacklist, proclitics=frozenset(),
                          phrases=(), h_clock=False, ord_suffixes=frozenset(),
                          fem_ord=None, reader=None,
                          extra_numwords=frozenset(), extra_homograph=None,
                          extra_ordinals=None):
    base = _make_romance_fold(lang_code, blacklist, reader=reader,
                              extra_numwords=extra_numwords,
                              extra_homograph=extra_homograph,
                              extra_ordinals=extra_ordinals)
    fem_ord = fem_ord or {}

    def fold(tokens):
        if proclitics:
            tokens = _elision_split(tokens, proclitics)
        for seq, surface in phrases:
            tokens = _collapse_phrase(tokens, seq, surface)
        if h_clock:
            tokens = _collapse_h_clock(tokens)
        if ord_suffixes:
            tokens = _merge_digit_ordinal(tokens, ord_suffixes)
        if fem_ord:
            # feminine ordinals the number back-end rejects ("a doua",
            # "la segunda") -- map the surface straight to its digit.
            tokens = _reindex(tuple(
                Token(text=str(fem_ord[t.text]), raw=t.raw, index=0,
                      is_number=True, value=fem_ord[t.text])
                if (not t.is_number and t.text in fem_ord) else t
                for t in tokens))
        return base(tokens)

    return fold


# -- French -----------------------------------------------------------------
_FR_PHRASES = [
    (["avant", "jésus", "christ"], "avjc"), (["avant", "jesus", "christ"], "avjc"),
    (["avant", "notre", "ère"], "avjc"), (["avant", "notre", "ere"], "avjc"),
    (["av", "j", "c"], "avjc"), (["av", "jc"], "avjc"),
    (["après", "jésus", "christ"], "apjc"), (["apres", "jesus", "christ"], "apjc"),
    (["de", "notre", "ère"], "apjc"), (["de", "notre", "ere"], "apjc"),
    (["ap", "j", "c"], "apjc"), (["ap", "jc"], "apjc"),
    (["il", "y", "a"], "ilya"),
    (["avant", "hier"], "avanthier"),
    (["apres", "demain"], "apresdemain"), (["après", "demain"], "apresdemain"),
    (["week", "end"], "weekend"),
]
#: the oclock surfaces that turn a preceding "un"/"une" into the hour 1.
_FR_HEURE = frozenset({"heure", "heures"})

#: the coordinator that joins the unit "un" to a French tens word in 21..71
#: ("vingt **et** un", "soixante **et** onze") -- the one connector that can
#: sit between the tens number and the licensed cardinal tail.
_FR_ET = frozenset({"et"})


def _fr_is_number_word(tok):
    """Is ``tok`` a spelled/parsed French number to the left of a "un" tail?

    A left neighbour that already carries a numeric reading (a folded digit
    run, "quatre-vingt" pre-folded to 80) or whose surface the French number
    back-end reads as a cardinal ("vingt", "cent", "mille", "deux") -- read
    with ``ordinals=False`` so an ordinal homograph ("premier") never counts.
    """
    if tok is None:
        return False
    if tok.is_number:
        return True
    value = extract_number_fr(tok.text, ordinals=False)
    return value is not False and value is not None


def _license_fr_un_compound(tokens):
    """Read "un"/"une" as the cardinal 1 when it is the *tail of a numeric
    compound*, the inverse of the blacklist that keeps it an article.

    French drops "un"/"une" from the spelled-number vocabulary so the everyday
    indefinite article and the clock-fraction article survive the fold ("un
    jour" = a day, "un quart d'heure" = a quarter hour, "une semaine" = a
    week).  That same blacklist silently truncates every compound number that
    *ends* in one -- "vingt et un" (21), "cent un" (101), "quatre-vingt-un"
    (81), "deux cent un" (201), "mille un" (1001) -- because the run-builder
    cannot extend across the missing "un".  The two readings are separable by
    position exactly as Portuguese separates its "um" article (see
    :func:`fold_pt`): the cardinal is the "un"/"une" whose left neighbour is a
    number, either directly ("cent un", "quatre-vingt-un") or across the
    coordinator "et" whose own left neighbour is a number ("vingt et un",
    "cent vingt et un").  In that position -- and only there -- the surface is
    marked a number so the shared extractor composes it additively (cent + 1 =
    101, vingt et 1 = 21) and the following unit binds; everywhere else the
    article stays byte-identical.  The *word* surface is kept (only
    ``is_number``/``value`` are set), because the shared run-folder re-reads
    the run's joined text through the number back-end, which composes "cent un"
    but not the digit-mixed "cent 1".
    """
    out = list(tokens)
    n = len(out)
    changed = False
    for i, t in enumerate(out):
        if t.is_number or t.text not in ("un", "une"):
            continue
        prev = out[i - 1] if i - 1 >= 0 else None
        if prev is not None and prev.text in _FR_ET:
            left = out[i - 2] if i - 2 >= 0 else None
        else:
            left = prev
        if _fr_is_number_word(left):
            out[i] = replace(t, is_number=True, value=1)
            changed = True
    return _reindex(tuple(out)) if changed else tokens


def _license_fr_une_heure(tokens):
    """Read "un"/"une" as the hour 1 directly before "heure(s)".

    French "une" is at once the feminine indefinite article ("une semaine" =
    a week) and the feminine cardinal one, and the shared number back-end
    leaves both "un" and "une" unfolded so the article reading survives
    ("il y a une semaine").  On the clock, though, the hour name is spoken
    exactly like the article -- "une heure" is one o'clock, and every
    fraction/meridiem/subtractive frame built on it ("une heure et quart",
    "une heure moins le quart", "une heure du matin") needs the 1 to bind the
    HOUR slot the way "deux heures" already does.  The two readings are
    distinguishable by position: the cardinal is the "un"/"une" immediately
    before the oclock word "heure(s)", and the article everywhere else.  Only
    that position is licensed to the digit 1, so "une semaine" and every other
    article use stays byte-identical.
    """
    out = list(tokens)
    n = len(out)
    for i, t in enumerate(out):
        if t.is_number or t.text not in ("un", "une"):
            continue
        nxt = out[i + 1] if i + 1 < n else None
        if nxt is not None and nxt.text in _FR_HEURE:
            out[i] = replace(t, text="1", is_number=True, value=1)
    return _reindex(tuple(out))


#: spelled ordinals 11th-31st that ``extract_number_fr`` does not recognise
#: as ordinals at all -- it reads every "ième" suffix as a *fraction* marker
#: instead ("onzième" -> 1/11, "vingt-deuxième" -> 22 by accident but
#: "vingt et unième" -> 20, dropping the "un" tail), a wrong value the shared
#: run-extraction machinery would confidently fold or silently truncate
#: rather than refuse.  These are stamped straight to their digit *before*
#: that machinery ever sees them (see :func:`_stamp_fr_compound_ordinals`),
#: bypassing ``extract_number_fr`` for this closed set entirely.
#: 11th-16th are irregular fused single words; 17th-19th and 21st-29th
#: prefix the ten across a hyphen the tokenizer splits ("dix-septième" ->
#: "dix","septième"); the X1 forms insert the coordinator "et" before
#: "unième" ("vingt et unième") rather than hyphenating, exactly as the
#: cardinals themselves do ("vingt et un").
#: Source: Larousse / Académie française, "Les adjectifs numéraux ordinaux".
_FR_SINGLE_ORDINALS = {
    "onzième": 11, "douzième": 12, "treizième": 13, "quatorzième": 14,
    "quinzième": 15, "seizième": 16, "vingtième": 20, "trentième": 30,
}
#: multiword compounds, longest surface first so "vingt et unième" is
#: matched before any shorter prefix could apply.
_FR_MULTIWORD_ORDINALS = [
    (["vingt", "et", "unième"], 21), (["trente", "et", "unième"], 31),
    (["dix", "septième"], 17), (["dix", "huitième"], 18),
    (["dix", "neuvième"], 19), (["vingt", "deuxième"], 22),
    (["vingt", "troisième"], 23), (["vingt", "quatrième"], 24),
    (["vingt", "cinquième"], 25), (["vingt", "sixième"], 26),
    (["vingt", "septième"], 27), (["vingt", "huitième"], 28),
    (["vingt", "neuvième"], 29),
]


def _stamp_fr_compound_ordinals(tokens):
    """Stamp French spelled ordinals 11th-31st straight to their digit,
    ahead of the general cardinal fold.

    ``extract_number_fr`` reads the "ième" suffix as a *fraction* marker for
    every one of these ("onzième" -> 1/11), not the ordinal it actually
    spells, so letting them flow into the normal run-extraction would fold a
    wrong value with high confidence (or, for the "et"-joined X1 forms,
    silently drop the "un" tail: "vingt et unième" -> 20) instead of
    resolving to the right month/day or refusing an impossible one.  Stamping
    the digit here, before the run scan, makes the shared machinery treat
    each compound exactly like any other already-folded number.
    """
    out = list(tokens)
    for words, val in _FR_MULTIWORD_ORDINALS:
        m = len(words)
        result = []
        i = 0
        n = len(out)
        while i < n:
            if (not out[i].is_number
                    and [t.text for t in out[i:i + m]] == words):
                first, last = out[i], out[i + m - 1]
                raw = "".join(t.raw for t in out[i:i + m])
                result.append(Token(text=str(val), raw=raw, index=0,
                                    is_number=True, value=val,
                                    char_start=first.char_start,
                                    char_end=last.char_end))
                i += m
            else:
                result.append(out[i])
                i += 1
        out = result
    out = [
        Token(text=str(_FR_SINGLE_ORDINALS[t.text]), raw=t.raw, index=0,
              is_number=True, value=_FR_SINGLE_ORDINALS[t.text],
              char_start=t.char_start, char_end=t.char_end)
        if (not t.is_number and t.text in _FR_SINGLE_ORDINALS) else t
        for t in out
    ]
    return _reindex(tuple(out))


# French composes its tens above sixty rather than naming them: eighty is
# four twenties ("quatre-vingts") and ninety is eighty plus ten
# ("quatre-vingt-dix"), a vigesimal reading the shared Romance extractor does
# not perform -- it adds the components instead and returns 24 and 34.  The
# French wrapper is the one that carries the vigesimal collapse, so French
# reads its numbers through the wrapper.  Without it every French phrase built
# on 80 or 90 -- "les années quatre-vingt", "quatre-vingts ans" -- parsed as a
# different number or not at all.  Source: Académie française, "quatre-vingts"
# (9e éd.), https://www.dictionnaire-academie.fr/article/A9Q0152
_fold_fr_ordinals_base = _romance_prepass_fold(
    "fr", {"un", "une"},
    reader=lambda text, ordinals=True: extract_number_fr(
        text, ordinals=ordinals),
    # "vingt" and "cent" take the plural -s exactly when they close a round
    # number -- "quatre-vingts", "deux cents", but "quatre-vingt-un" and "deux
    # cent un" -- and the shared vocabulary lists only the singular, so the
    # prescribed spelling of 80 and 200 fell out of the run and left the
    # leading "quatre"/"deux" behind as the whole number.
    extra_numwords=frozenset({"vingts", "cents"}),
    proclitics=frozenset({"d", "l", "j", "n", "s", "c", "m", "t", "qu"}),
    # feminine ordinals the number back-end rejects but that agree with a
    # feminine noun the constructions bind ("la premiere/première moitié",
    # "la seconde moitié").  "seconde" is unambiguous in French date text --
    # French has no time-unit "seconde" vocabulary here -- so it maps straight to
    # 2 like the Spanish/Romanian feminine tables above.
    fem_ord={"première": 1, "premiere": 1, "seconde": 2},
    phrases=_FR_PHRASES, h_clock=True,
    ord_suffixes=frozenset({"er", "ere", "ère", "e", "eme", "ème",
                            "nd", "nde", "d", "re", "es", "emes", "èmes"}))


def fold_fr(tokens):
    # spelled 11th-31st ordinals stamped straight to their digit before the
    # general cardinal fold, which would otherwise misread every one of them
    # as a fraction -- see :func:`_stamp_fr_compound_ordinals`.
    return _fold_fr_ordinals_base(_stamp_fr_compound_ordinals(tokens))


# deep-time SCALE-frame licensing: "un milliard/un billion d'années"
fold_fr = _with_scale_frame(fold_fr, "fr", frozenset({"un", "une"}))
# clock-frame licensing: "une heure" (one o'clock) and every fraction/meridiem/
# subtractive frame built on it -- "un"/"une" reads as the hour 1 before
# "heure(s)", the article everywhere else.
_fold_fr_scaled = fold_fr


def fold_fr(tokens):  # noqa: F811 -- final wrap adds une-heure + un-compound
    return _fold_fr_scaled(
        _license_fr_une_heure(_license_fr_un_compound(tokens)))


# -- Italian ----------------------------------------------------------------
_IT_PHRASES = [
    (["avanti", "cristo"], "ac"), (["dopo", "cristo"], "dc"),
    (["avanti", "l", "era", "volgare"], "ac"), (["era", "volgare"], "dc"),
    (["altro", "ieri"], "altroieri"), (["avanti", "ieri"], "avantieri"),
    (["dopo", "domani"], "dopodomani"),
    (["fine", "settimana"], "finesettimana"),
]
#: the di-family prepositions (plain and article-fused) that introduce the
#: reference date after the before-marker "prima" -- "prima di gennaio",
#: "prima del 5 aprile".  "d"/"dell" are the elision-split heads of "d'"/
#: "dell'".
_IT_OFFSET_PREP = frozenset({"di", "del", "dello", "della", "dell", "dei",
                             "degli", "delle", "d"})


def _license_it_prima(tokens):
    """Positionally read the homograph "prima".

    Italian "prima" is at once the feminine ordinal "first" and the
    directional marker "before"; a blanket number-fold would erase the
    marker, a blanket blacklist would erase the ordinal.  The two readings
    are distinguishable by position, so "prima" is blacklisted from the
    general fold (see :func:`fold_it`) and licensed to the digit 1 *only*
    where it is the ordinal -- i.e. everywhere it is **not** in the offset
    frame.  It is the before-marker when it either

    * is immediately followed by a di-family preposition introducing the
      reference date ("prima **di** gennaio", "prima **del** 5 aprile"), or
    * closes a ``[NUM] UNIT`` duration ("3 giorni **prima** del ...",
      "tre giorni **prima** ...") -- the token before it a (non-number) unit
      word, the one before that a number;

    and the ordinal "first" otherwise ("**prima** settimana", "la **prima**
    domenica", "**prima** quindicina"), where it folds to 1 so the ordinal
    constructions bind it.  The rule keys off the preposition and the
    NUM+UNIT shape, never a hard-coded month or unit list, so it generalises.
    """
    out = list(tokens)
    n = len(out)
    for i, t in enumerate(out):
        if t.is_number or t.text != "prima":
            continue
        nxt = out[i + 1] if i + 1 < n else None
        prev = out[i - 1] if i - 1 >= 0 else None
        prev2 = out[i - 2] if i - 2 >= 0 else None
        is_before_marker = (
            (nxt is not None and nxt.text in _IT_OFFSET_PREP)
            or (prev is not None and not prev.is_number
                and prev2 is not None and prev2.is_number))
        if not is_before_marker:
            out[i] = Token(text="1", raw=t.raw, index=0, is_number=True,
                           value=1, char_start=t.char_start,
                           char_end=t.char_end)
    return _reindex(tuple(out))


# Italian spells its 11th-19th ordinals identically to the FRACTION
# denominator of the same value -- "tredicesimo" is at once "thirteenth" and
# "a-thirteenth" (vocab.FRACTION[13] == vocab.ORDINAL_TENS would list it too,
# but ORDINAL_TENS only carries the round-ten entries 10/20/../90, so this
# homograph collision is invisible to the shared TENS mechanism and must be
# named explicitly).  Without licensing, "undicesimo".."diciannovesimo" are
# simply absent from the number-fold's word set (silently dropped as
# fractions), so a phrase built on one -- "il tredicesimo mese del 2026" --
# never tokenizes an ordinal at all and falls through to a bare year_ref
# match, same failure mode as the Spanish/Catalan compound gap this change
# closes.  Licensed positionally (after a definite article / before the
# quarter noun) exactly like the 1st-9th homographs above -- each is a
# complete single-word ordinal with no further composition, so (unlike the
# décimo/tretzè TENS-prefix case) stamping straight to its digit is correct.
# Source: standard Italian ordinal-numeral formation (Treccani, "numerali
# ordinali"): 11th-19th borrow the cardinal's stem + "-esimo" and are
# genuinely homographic with the same-value fraction.
_IT_TEEN_HOMOGRAPH = {
    "undicesimo": 11, "dodicesimo": 12, "tredicesimo": 13,
    "quattordicesimo": 14, "quindicesimo": 15, "sedicesimo": 16,
    "diciassettesimo": 17, "diciottesimo": 18, "diciannovesimo": 19,
}
# Italian composes 21st-31st (and every higher non-round ordinal) by fusing
# the cardinal's stem onto "-esimo": ventuno -> ventunesimo (21st, unlike
# "ventunesimo" any FRACTION collision -- Italian's FRACTION table stops at
# 20).  The two-word compound "ventesimo primo" already composes through the
# back-end, but the fused spelling is the one Italian actually writes.
# Source: Treccani / Accademia della Crusca, "numerali ordinali" -- the
# fused compound elides the cardinal's final vowel before "-esimo" except
# where the cardinal itself ends in an accented vowel (23rd "ventitré" keeps
# its final "e": "ventitreesimo").
_IT_COMPOUND_ORDINALS = {
    "ventunesimo": 21, "ventiduesimo": 22, "ventitreesimo": 23,
    "ventiquattresimo": 24, "venticinquesimo": 25, "ventiseiesimo": 26,
    "ventisettesimo": 27, "ventottesimo": 28, "ventinovesimo": 29,
    "trentunesimo": 31,
}
# "prima" is the feminine ordinal "first" *and* the directional marker
# "before"; it is blacklisted from the general number fold (so the offset
# composition can read the marker) and positionally licensed back to the digit
# 1 in ordinal position by ``_license_it_prima``.  The unambiguous masculine
# "primo" still folds to 1 in the general pass.
_fold_it_base = _romance_prepass_fold(
    "it", {"un", "uno", "una", "milioni", "miliardi", "mila", "prima"},
    proclitics=frozenset({"l", "un", "d", "dell", "all", "nell", "dall",
                          "sull", "quest", "quell", "c"}),
    phrases=_IT_PHRASES,
    extra_homograph=_IT_TEEN_HOMOGRAPH,
    extra_ordinals=_IT_COMPOUND_ORDINALS)


def _split_it_fused_mila(tokens):
    """Split Italian's fused round-thousand spelling ("duemila", "diecimila")
    into the multiplier and the scale particle ("due"/"dieci", "mila"), so the
    existing ``[NUM] mila`` composition in ``nseries._read_scale`` binds it
    exactly as it already binds the space-separated "due mila".  The prefix is
    validated through ``extract_number_it`` itself -- not a hand-listed table --
    so it generalises to every multiplier the backend understands and cannot
    mis-split an unrelated word (the only Italian surface ending in "mila" is
    the bare scale word "mila", excluded here)."""
    from ovos_number_parser.numbers_it import extract_number_it
    out = []
    changed = False
    for t in tokens:
        if not t.is_number and t.text.endswith("mila") and t.text != "mila":
            prefix = t.text[:-4]
            val = extract_number_it(prefix, ordinals=False) if prefix else False
            if isinstance(val, (int, float)) and val:
                cs, ce = t.char_start, t.char_end
                p_end = cs + len(prefix) if cs is not None else None
                m_start = ce - 4 if ce is not None else None
                out.append(Token(text=prefix, raw=prefix, index=0,
                                 char_start=cs, char_end=p_end))
                out.append(Token(text="mila", raw="mila", index=0,
                                 char_start=m_start, char_end=ce))
                changed = True
                continue
        out.append(t)
    return _reindex(tuple(out)) if changed else tokens


def fold_it(tokens):
    return _license_it_prima(_fold_it_base(_split_it_fused_mila(tokens)))


# deep-time SCALE-frame licensing: "un miliardo/un bilione di anni fa"
fold_it = _with_scale_frame(fold_it, "it", frozenset({"un", "uno", "una"}))


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
    fem_ord={"doua": 2, "două": 2, "treia": 3, "patra": 4, "cincea": 5,
             "șasea": 6, "sasea": 6, "șaptea": 7, "saptea": 7, "opta": 8,
             "noua": 9, "zecea": 10})
# deep-time SCALE-frame licensing: "un miliard/un bilion de ani în urmă"
fold_ro = _with_scale_frame(fold_ro, "ro", frozenset({"un", "unu", "una", "o"}))


# -- Occitan ----------------------------------------------------------------
_OC_PHRASES = [
    (["abans", "jèsus", "crist"], "acn"), (["abans", "jesus", "crist"], "acn"),
    (["aprèp", "jèsus", "crist"], "apc"), (["aprep", "jesus", "crist"], "apc"),
    (["abans", "ièr"], "abansièr"), (["abans", "ier"], "abansièr"),
    (["passat", "deman"], "passatdeman"), (["delà", "deman"], "passatdeman"),
    (["que", "ven"], "queven"),
    (["week", "end"], "weekend"),
]
fold_oc = _romance_prepass_fold(
    "oc", {"un", "una"},
    proclitics=frozenset({"l", "d", "un", "qu", "n", "s"}),
    phrases=_OC_PHRASES, h_clock=True,
    ord_suffixes=frozenset({"èr", "er", "n", "nd", "en", "ena", "a", "d"}))


# -- Asturian ---------------------------------------------------------------
_AST_PHRASES = [
    (["enantes", "de", "cristu"], "adc"), (["antes", "de", "cristu"], "adc"),
    (["dempués", "de", "cristu"], "ddc"), (["despues", "de", "cristu"], "ddc"),
    (["pasáu", "mañana"], "trasmañana"), (["pasao", "mañana"], "trasmañana"),
    (["que", "vien"], "quevien"),
    (["fin", "de", "selmana"], "findeselmana"),
]
fold_ast = _romance_prepass_fold(
    "ast", {"un", "una"},
    proclitics=frozenset({"l", "d", "un", "n"}),
    phrases=_AST_PHRASES,
    fem_ord={"primera": 1, "segunda": 2, "tercera": 3, "cuarta": 4,
             "quinta": 5, "sexta": 6, "séptima": 7, "septima": 7,
             "octava": 8, "novena": 9, "décima": 10, "decima": 10})
