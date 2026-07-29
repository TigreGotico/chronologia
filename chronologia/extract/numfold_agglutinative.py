"""Spelled-number folding for the heavy-morphology batch (el, hu, fi, et, eu).

Same job as the English/Slavic folds: collapse a maximal run of spelled
number-words into one digit :class:`~chronologia.extract.model.Token` so a
``NUM``/``HOUR``/``DAY`` slot binds the same whether the writer typed ``5``
or spelled it.  These languages add two wrinkles a nominative word list does
not cover, so the factory below takes them as explicit facts:

* **oblique/declined forms the extractor does not read** -- the Finnish and
  Estonian genitive numerals used in offset slots ("kahden viikon",
  "kolme nädala"), the Greek feminine clock-hour numerals that agree with
  *ώρα* ("τρεις"/"τέσσερις"), and the Basque *-ak* hour forms ("bostak").
  These are given as an explicit ``{surface: value}`` map: run membership is
  gated on the surface and the value is read from the map when the number
  model rejects the form.

* **homographs that must NOT fold** -- the Hungarian *hét* is both "seven"
  and "week"; folding it to ``7`` would erase the ``week`` unit token.  Such
  surfaces are named in ``exclude`` and never treated as numbers.

Each ``fold_<lang>`` is wired as the language ``hook`` in
``locale/<lang>/lang.json`` and is a pure ``tuple[Token] -> tuple[Token]``.
"""
from __future__ import annotations

from dataclasses import replace
from importlib import import_module
from typing import Callable, Dict, FrozenSet, Tuple

from chronologia.extract.model import Token
from chronologia.extract.numfold_engine import NumberGrammar, make_fold, reindex
from chronologia.extract.numfold_ordinals import with_ordinals


def _make_fold(lang: str, extra_values: Dict[str, float] | None = None,
               exclude: FrozenSet[str] = frozenset()
               ) -> Callable[[Tuple[Token, ...]], Tuple[Token, ...]]:
    """A cardinal fold whose word set is derived from the model's own
    pronunciation, augmented by an ``extra`` map of oblique/hour surfaces the
    pronouncer does not emit (also the single-token fallback value source) and
    minus ``exclude`` homographs.  The model import is deferred to first call.
    """
    extra = {k.lower(): v for k, v in (extra_values or {}).items()}
    holder: dict = {}

    def _load():
        mod = import_module("ovos_number_parser.numbers_" + lang)
        pron = getattr(mod, "pronounce_number_" + lang)
        extract = getattr(mod, "extract_number_" + lang)
        words = set()
        for n in range(0, 100):
            try:
                for w in str(pron(n)).lower().replace("-", " ").split():
                    words.add(w)
            except Exception:
                pass
        words |= set(extra)
        words -= exclude

        def value_of(text):
            try:
                return extract(text)
            except Exception:
                return False
        return make_fold(NumberGrammar(
            is_number=lambda tok: tok.is_number or tok.text in words,
            extract=value_of,
            single_fallback=extra.get))

    def fold(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
        f = holder.get("fold")
        if f is None:
            f = holder["fold"] = _load()
        return f(tokens)

    return fold


# -- Greek: feminine clock-hour numerals agree with the elided ώρα ----------
# extract_number_el already reads most; the run-membership gate needs the
# feminine surfaces the *pronounce* side (neuter) does not emit.
_EL_FEM_HOURS = {
    "μία": 1, "τρεις": 3, "τέσσερις": 4,
    "δεκατρείς": 13, "δεκατέσσερις": 14,
}
_el_numfold = _make_fold("el", _EL_FEM_HOURS)

# -- Greek: the written day-of-month is a digit + ordinal ending -------------
# "5η Μαρτίου" (the 5th of March), "της 5ης Μαρτίου" (of the 5th of March).
# A Greek τακτικό αριθμητικό (ordinal) inflects for gender/case; when spelled
# with a digit the ending rides on the numeral ("5η", "5ος", "5ου").  The
# day-of-month agrees with the feminine ημέρα, so "Nη"/"Nης" are the everyday
# forms, but the masculine/neuter/plural endings are the same closed class and
# are folded too so any digit-ordinal binds its numeral.  Source: Νεοελληνική
# Γραμματική (Τριανταφυλλίδης), τακτικά αριθμητικά; Πύλη για την Ελληνική Γλώσσα
# (greek-language.gr) ordinal-ending paradigm.
#
# The tokenizer shears the ending off the digit ("5η" -> "5", "η"), so a number
# immediately followed by a bare ordinal-ending fragment folds back to the
# number and the DAY/NUM slot binds.  The merge is gated on ADJACENCY (no space
# between the two source tokens): "η"/"ο"/"οι" are also the feminine/neuter
# definite articles, and "5 η ώρα" ("5 o'clock", article present) must keep its
# separate article token -- only the glued "5η" is an ordinal.
_EL_ORD_SUFFIX = frozenset({
    "η", "ης", "ην",              # feminine (day agrees with ημέρα): nom/gen/acc
    "ος", "ου", "ο", "ον",       # masculine / neuter
    "οι", "ων", "ους", "ες",     # plural forms
})


def fold_el(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    merged = []
    i = 0
    n = len(tokens)
    while i < n:
        t = tokens[i]
        nxt = tokens[i + 1] if i + 1 < n else None
        if (t.is_number and nxt is not None and not nxt.is_number
                and nxt.text in _EL_ORD_SUFFIX
                and t.char_end is not None and nxt.char_start is not None
                and nxt.char_start == t.char_end):
            merged.append(replace(t, raw=t.raw + nxt.raw,
                                  char_end=nxt.char_end
                                  if nxt.char_end is not None else t.char_end))
            i += 2
            continue
        merged.append(t)
        i += 1
    return _el_numfold(reindex(tuple(merged)))


# -- Hungarian: "hét" is both seven and week; never fold it to a number.
# "két" is the attributive form of 2 (the pronounce side emits "kettő"), so
# it is supplied explicitly for the "két hét múlva" counting slot.
# The clock hour "at N o'clock" glues the temporal case suffix -kor onto the
# cardinal ("háromkor" = at three), which the pronounce back-end does not emit;
# given as one-token surfaces so "délután háromkor" reads a clock hour.  "hétkor"
# (at seven) is a distinct surface from the excluded "hét" (week/seven), so the
# exclude above is unaffected.  Source: Wiktionary, -kor
# (https://en.wiktionary.org/wiki/-kor#Hungarian), temporal case suffix; the
# cardinals are the standard telling-time forms (Magyar helyesírás, Akadémiai).
_HU_KOR_HOURS = {
    "egykor": 1, "kettőkor": 2, "háromkor": 3, "négykor": 4, "ötkor": 5,
    "hatkor": 6, "hétkor": 7, "nyolckor": 8, "kilenckor": 9, "tízkor": 10,
    "tizenegykor": 11, "tizenkettőkor": 12,
}
fold_hu = _make_fold("hu", {"két": 2, **_HU_KOR_HOURS},
                     exclude=frozenset({"hét"}))
# Hungarian spells the day-of-month with a single-token ordinal that the
# cardinal back-end does not read ("tizenötödike április" = the 15th of April);
# ``pronounce_ordinal_hu`` emits every 1..31 as one word (tizenegyedik,
# huszonegyedik ...), so ``with_ordinals`` derives the whole range from the
# model.  "hét" (week/seven) is never an ordinal surface, so the exclude above
# is unaffected.  Magyar helyesírás (Akadémiai): sorszámnevek.
fold_hu = with_ordinals(fold_hu, "hu")


# -- Finnish: genitive numerals used in the "N <unit> kuluttua/sitten" slot -
_FI_GENITIVE = {
    "yhden": 1, "kahden": 2, "kolmen": 3, "neljän": 4, "viiden": 5,
    "kuuden": 6, "seitsemän": 7, "kahdeksan": 8, "yhdeksän": 9,
    "kymmenen": 10, "yhdentoista": 11, "kahdentoista": 12,
    "kolmentoista": 13, "neljäntoista": 14, "viidentoista": 15,
    "kuudentoista": 16, "seitsemäntoista": 17, "kahdeksantoista": 18,
    "yhdeksäntoista": 19, "kahdenkymmenen": 20,
    "puolen": 0.5, "puolentoista": 1.5,
}
# Finnish tells the clock hour with the ablative "-lta/-ltä" ("kello kolmelta"
# = at three o'clock); the ablative numeral is a single word the cardinal
# back-end does not read, so the 1..12 telling-time forms are given explicitly.
# Source: Wiktionary, -lta (https://en.wiktionary.org/wiki/-lta#Finnish),
# ablative case; VISK §1237 (kellonajat) for the telling-time use.
_FI_ABLATIVE_HOURS = {
    "yhdeltä": 1, "kahdelta": 2, "kolmelta": 3, "neljältä": 4, "viideltä": 5,
    "kuudelta": 6, "seitsemältä": 7, "kahdeksalta": 8, "yhdeksältä": 9,
    "kymmeneltä": 10, "yhdeltätoista": 11, "kahdeltatoista": 12,
}
fold_fi = _make_fold("fi", {**_FI_GENITIVE, **_FI_ABLATIVE_HOURS})
# Finnish spells the day-of-month with a single-token ordinal the cardinal
# back-end does not read in date position ("viidestoista huhtikuuta" = the 15th
# of April).  ``pronounce_ordinal_fi`` emits every 1..31 as one compound word
# (ensimmäinen, viidestoista, kahdeskymmenesensimmäinen ...), so ``with_ordinals``
# derives the whole range from the model.  Iso suomen kielioppi (VISK) §770:
# järjestysluvut.
fold_fi = with_ordinals(fold_fi, "fi")


# -- Estonian: genitive numerals used in the "N <unit> pärast/tagasi" slot --
_ET_GENITIVE = {
    "ühe": 1, "kahe": 2, "kolme": 3, "nelja": 4, "viie": 5, "kuue": 6,
    "seitsme": 7, "kaheksa": 8, "üheksa": 9, "kümne": 10,
    "poole": 0.5, "pooleteist": 1.5,
}
fold_et = _make_fold("et", _ET_GENITIVE)
# Estonian spells the day-of-month with an ordinal the cardinal back-end does
# not read ("viieteistkümnes aprill" = the 15th of April).  ``pronounce_ordinal_et``
# emits 1..20 and 30 as one word (esimene, viieteistkümnes, kolmekümnes) but the
# compound tens 21..29/31 as two words ("kahekümne esimene"), which the
# single-token ordinal pre-pass cannot fold; those remain a documented deferral.
# Eesti keele käsiraamat (EKI): järgarvsõnad.
fold_et = with_ordinals(fold_et, "et")


# -- Basque: date words carry the case, not a preposition -------------------
# "ekainaren 5ean" (of-June 5th-in), "2027ko ekaina" (2027-of June).  The
# tokenizer shears the digit from its case suffix ("5ean" -> "5", "ean"); a
# number followed by a bare case-suffix fragment folds back to the number so
# the DAY/YEAR slot binds.  Month/weekday surfaces themselves carry their
# inflections in the *.voc files (many-surface entries), not here.
_EU_HOUR_FORMS = {
    "ordubata": 1, "ordubiak": 2, "hirurak": 3, "laurak": 4, "bostak": 5,
    "seirak": 6, "zazpirak": 7, "zortzirak": 8, "bederatziak": 9,
    "hamarrak": 10, "hamaikak": 11, "hamabiak": 12,
    # inessive "at N o'clock" ("hiruretan" = at three); the plural hour numeral
    # carries the -etan case, so it is one word the cardinal back-end does not
    # read.  1 and 2 are two-word forms ("ordu batean", "ordu bietan") and fold
    # via the case-suffix pre-pass, not here.  Source: Wiktionary, -etan
    # (https://en.wiktionary.org/wiki/-etan#Basque), inessive plural; Euskara
    # batua telling-time forms (Euskaltzaindia, orduak).
    "hiruretan": 3, "lauretan": 4, "bostetan": 5, "seietan": 6,
    "zazpietan": 7, "zortzietan": 8, "bederatzietan": 9, "hamarretan": 10,
    "hamaiketan": 11, "hamabietan": 12,
}
# NB: a bare "k" is deliberately excluded -- it collides with the "k.a."/
# "k.o." era abbreviations the tokenizer shears to a "k" fragment.
_EU_NUM_SUFFIX = frozenset({
    "a", "an", "ean", "n", "ko", "eko", "ren",
    "garren", "garrena", "garrenean",
})
_eu_numfold = _make_fold("eu", _EU_HOUR_FORMS)


def fold_eu(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    merged = []
    i = 0
    n = len(tokens)
    while i < n:
        t = tokens[i]
        nxt = tokens[i + 1] if i + 1 < n else None
        if (t.is_number and nxt is not None and not nxt.is_number
                and nxt.text in _EU_NUM_SUFFIX):
            merged.append(replace(t, raw=t.raw + nxt.raw,
                                   char_end=nxt.char_end if nxt.char_end is not None
                                   else t.char_end))
            i += 2
            continue
        merged.append(t)
        i += 1
    return _eu_numfold(reindex(tuple(merged)))
