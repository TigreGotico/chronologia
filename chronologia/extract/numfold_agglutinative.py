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
        # Pronounce through 999, not just 100: the single-token hundred words
        # 200..900 ("kétszáz", "kaksisataa", "kakssada", "διακόσια", "berrehun")
        # only appear when a number >= 200 is pronounced, so a run set built from
        # 0..100 alone silently dropped every spelled hundred and returned None
        # for "kétszáz nap" (two hundred days).  The 100..999 sweep adds only
        # those hundred words (tens/units are already covered by 0..99), so the
        # set stays a closed class of genuine number-words.
        for n in range(0, 1000):
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


def _with_fused_thousands(fold: Callable[[Tuple[Token, ...]], Tuple[Token, ...]],
                          lang: str, suffix: str
                          ) -> Callable[[Tuple[Token, ...]], Tuple[Token, ...]]:
    """Wrap ``fold`` so a Hungarian/Finnish fused round-thousand word folds
    with its trailing sub-thousand chunk instead of dropping it.

    Hungarian and Finnish glue the thousands multiplier straight onto the scale
    word in one token -- hu "kétezer" (két + ezer = 2000), "háromezer" (3000);
    fi "kaksituhatta" (2000), "kolmetuhatta" (3000) -- and then attach the
    trailing sub-thousand part as a hyphenated or spaced word ("kétezer-huszonnégy"
    = 2024, "kaksituhatta neljä" = 2004).  The model-derived run set is built by
    pronouncing only 0..999, so the fused word is never a run member; the scan
    skips it and the sub-thousand chunk folds in isolation, so the duration reader
    saw only "huszonnégy" = 24 and dropped the 2000.  The ``<multiplier>ezer`` /
    ``<multiplier>tuhatta`` back-ends themselves cannot compose the two either
    (``extract_number_hu("kétezer huszonnégy")`` returns 2000, silently dropping
    the 24), so the value is composed here: multiplier*1000 + the sub-thousand
    remainder, as one synthetic number token spanning the whole run.

    The multiplier prefix is validated through the language's own
    ``extract_number_<lang>`` -- not a hand-listed table -- so it generalises to
    every multiplier the back-end reads ("tizennégyezer" = 14000) and cannot
    mis-split an unrelated word.  The bare scale word (hu "ezer", fi "tuhat" /
    "tuhatta" = 1000) has an empty prefix and is left untouched, so that path is
    not regressed.
    """
    holder: dict = {}

    def _num():
        ext = holder.get("ext")
        if ext is None:
            m = import_module("ovos_number_parser.numbers_" + lang)
            ext = holder["ext"] = getattr(m, "extract_number_" + lang)
        return ext

    def _value(text):
        try:
            v = _num()(text)
        except Exception:
            return None
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            return None
        return v

    def _fuse(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
        out = []
        i = 0
        n = len(tokens)
        changed = False
        while i < n:
            t = tokens[i]
            thousands = None
            if (not t.is_number and t.text.endswith(suffix)
                    and len(t.text) > len(suffix)):
                prefix = t.text[:-len(suffix)]
                mult = _value(prefix)
                if mult is not None and mult > 0 and float(mult).is_integer():
                    thousands = int(mult) * 1000
            if thousands is None:
                out.append(t)
                i += 1
                continue
            # Absorb a trailing run of spelled sub-thousand number-words
            # (hyphen already sheared by the tokenizer, or spaced).  Each must
            # read as an integer in 1..999; a following unit word, another
            # thousands word (>= 1000) or a bare digit stops the run.
            j = i + 1
            rest = []
            while j < n:
                nt = tokens[j]
                if nt.is_number:
                    break
                rv = _value(nt.text)
                if rv is not None and 0 < rv < 1000 and float(rv).is_integer():
                    rest.append(nt)
                    j += 1
                else:
                    break
            rest_val = 0
            if rest:
                joined = _value(" ".join(x.text for x in rest))
                if joined is not None and 0 < joined < 1000 and float(joined).is_integer():
                    rest_val = int(joined)
                else:
                    rest_val = sum(int(_value(x.text)) for x in rest)
            total = thousands + rest_val
            last = rest[-1] if rest else t
            out.append(Token(text=str(total), raw=str(total), index=0,
                             is_number=True, value=total,
                             char_start=t.char_start, char_end=last.char_end))
            changed = True
            i = j
        return reindex(tuple(out)) if changed else tokens

    def wrapped(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
        return fold(_fuse(tokens))

    return wrapped


def _with_bare_case_hour(fold: Callable[[Tuple[Token, ...]], Tuple[Token, ...]],
                         hours: Dict[str, float], at_surface: str,
                         skip_before: FrozenSet[str] = frozenset()
                         ) -> Callable[[Tuple[Token, ...]], Tuple[Token, ...]]:
    """Wrap a ``fold`` so a bare CASE-SUFFIXED clock hour binds its HOUR.

    The colloquial telling-time numeral drops the "o'clock" word and glues the
    temporal/ablative/inessive case suffix straight onto the cardinal -- hu
    "háromkor" (at three), fi "kolmelta", eu "hiruretan".  The cardinal back-end
    does not read the glued form, and folding it to a bare number would leave the
    clock frame no cue at all: standalone the digit binds nothing (returns None),
    and after a daypart lead the numeral is stranded and only the band comes back.

    The one glued token is split into a synthetic ``at`` marker followed by the
    hour number, so the universal "at HOUR" clock order (present in every locale)
    binds it -- standalone and after a daypart/meridiem lead ("MERIDIEM at? HOUR").
    The marker carries an empty ``raw`` and a zero-width extent, so it never
    reaches the remainder text.  It is suppressed when the hour already trails an
    explicit clock marker (Finnish "kello kolmelta"), keeping that frame's parse
    byte-identical.  ``at_surface`` must be a surface in the locale's
    ``marker_at.voc``; ``hours`` is the ``{glued surface: value}`` telling-time map.
    """
    def pre(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
        out = []
        for i, t in enumerate(tokens):
            value = None if t.is_number else hours.get(t.text)
            if value is None:
                out.append(t)
                continue
            num = int(value) if float(value).is_integer() else float(value)
            led = i > 0 and tokens[i - 1].text in skip_before
            if not led:
                out.append(Token(text=at_surface, raw="", index=0,
                                 char_start=t.char_start,
                                 char_end=t.char_start))
            out.append(replace(t, text=str(num), raw=t.raw,
                               is_number=True, value=num))
        return fold(reindex(tuple(out)))

    return pre


# -- Greek: feminine clock-hour numerals agree with the elided ώρα ----------
# extract_number_el already reads most; the run-membership gate needs the
# feminine surfaces the *pronounce* side (neuter) does not emit.
_EL_FEM_HOURS = {
    "μία": 1, "τρεις": 3, "τέσσερις": 4,
    "δεκατρείς": 13, "δεκατέσσερις": 14,
}
# Greek hundreds inflect for gender; ``pronounce_number_el`` emits only the
# NEUTER form (διακόσια), so the FEMININE hundreds that agree with feminine unit
# nouns ("διακόσιες μέρες" -- 200 days, μέρα being feminine) and the MASCULINE
# hundreds ("διακόσιοι μήνες") never entered the model-derived run set and folded
# to None.  ``extract_number_el`` reads every gender correctly, so the surfaces
# only need to be present in the run set; the neuter forms already arrive via
# the 0..999 pronunciation sweep.
_EL_HUNDREDS = {
    "διακόσιες": 200, "τριακόσιες": 300, "τετρακόσιες": 400,
    "πεντακόσιες": 500, "εξακόσιες": 600, "εφτακόσιες": 700,
    "επτακόσιες": 700, "οχτακόσιες": 800, "οκτακόσιες": 800,
    "εννιακόσιες": 900,
    "διακόσιοι": 200, "τριακόσιοι": 300, "τετρακόσιοι": 400,
    "πεντακόσιοι": 500, "εξακόσιοι": 600, "επτακόσιοι": 700,
    "οκτακόσιοι": 800, "εννιακόσιοι": 900,
}
_el_numfold = _make_fold("el", {**_EL_FEM_HOURS, **_EL_HUNDREDS})

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
fold_hu = _make_fold("hu", {"két": 2},
                     exclude=frozenset({"hét"}))
# Hungarian spells the day-of-month with a single-token ordinal that the
# cardinal back-end does not read ("tizenötödike április" = the 15th of April);
# ``pronounce_ordinal_hu`` emits every 1..31 as one word (tizenegyedik,
# huszonegyedik ...), so ``with_ordinals`` derives the whole range from the
# model.  "hét" (week/seven) is never an ordinal surface, so the exclude above
# is unaffected.  Magyar helyesírás (Akadémiai): sorszámnevek.
def _hu_day_ord_extra() -> Dict[str, int]:
    """The possessive day-of-month ordinal ("május tizenötödike" / "-én" = the
    15th) that the bare ordinal map misses: ``pronounce_ordinal_hu`` emits only
    the bare "-dik" form, so append the possessive -e/-én (front vowel harmony)
    or -a/-án (back), read straight off the ordinal's own "-Vdik" vowel -- the
    harmony the pronouncer already chose, so mixed-vowel stems (huszonegyedike,
    front) come out right.  n=1 is suppletive (elseje/elsején, not elsőe)."""
    pron = getattr(import_module("ovos_number_parser.numbers_hu"),
                   "pronounce_ordinal_hu")
    out: Dict[str, int] = {}
    for n in range(1, 32):
        try:
            bare = str(pron(n)).strip().lower()
        except Exception:
            continue
        if not bare.endswith("dik"):        # első
            out["elseje"] = out["elsején"] = n
            continue
        front = bare[-4] in "eéiíöőüű"
        out[bare + ("e" if front else "a")] = n
        out[bare + ("én" if front else "án")] = n
    return out


fold_hu = with_ordinals(fold_hu, "hu", extra=_hu_day_ord_extra())
# The bare "-kor" telling-time forms (háromkor, nyolckor, ...) drop "óra" and
# glue -kor onto the numeral; split them so "at HOUR" binds ("kor" is the hu
# marker_at surface).  "N órakor" keeps its own "órakor" oclock token and is
# untouched here.
fold_hu = _with_bare_case_hour(fold_hu, _HU_KOR_HOURS, "kor")
# Fold the fused round-thousand spelling ("kétezer-huszonnégy" = 2024) instead
# of dropping the thousands and reading only the trailing chunk.  Outermost so
# it rewrites the raw surface tokens before the cardinal/ordinal/clock folds.
fold_hu = _with_fused_thousands(fold_hu, "hu", "ezer")


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
fold_fi = _make_fold("fi", {**_FI_GENITIVE})
# Finnish spells the day-of-month with a single-token ordinal the cardinal
# back-end does not read in date position ("viidestoista huhtikuuta" = the 15th
# of April).  ``pronounce_ordinal_fi`` emits every 1..31 as one compound word
# (ensimmäinen, viidestoista, kahdeskymmenesensimmäinen ...), so ``with_ordinals``
# derives the whole range from the model.  Iso suomen kielioppi (VISK) §770:
# järjestysluvut.
fold_fi = with_ordinals(fold_fi, "fi")
# The bare ablative telling-time forms (kolmelta, yhdeksältä, ...) drop "kello"
# and carry -lta/-ltä alone; split them so "at HOUR" binds ("kello" is the fi
# marker_at surface).  When "kello" is already spoken ("kello kolmelta") the
# synthetic marker is suppressed so that frame stays byte-identical.
fold_fi = _with_bare_case_hour(fold_fi, _FI_ABLATIVE_HOURS, "kello",
                               skip_before=frozenset({"kello", "klo"}))
# Fold the fused round-thousand spelling ("kaksituhatta neljä" = 2004) instead
# of dropping the thousands.  The scale word here is the partitive "tuhatta"
# ("kaksituhatta"); the bare "tuhat"/"tuhatta" = 1000 has an empty prefix and is
# left untouched.
fold_fi = _with_fused_thousands(fold_fi, "fi", "tuhatta")


# -- Estonian: genitive numerals used in the "N <unit> pärast/tagasi" slot --
_ET_GENITIVE = {
    "ühe": 1, "kahe": 2, "kolme": 3, "nelja": 4, "viie": 5, "kuue": 6,
    "seitsme": 7, "kaheksa": 8, "üheksa": 9, "kümne": 10,
    "poole": 0.5, "pooleteist": 1.5,
}
fold_et = _make_fold("et", _ET_GENITIVE)
# Estonian spells the day-of-month with an ordinal the cardinal back-end does
# not read ("viieteistkümnes aprill" = the 15th of April).  ``pronounce_ordinal_et``
# emits 1..20 and 30 as one word (esimene, viieteistkümnes, kolmekümnes) and the
# compound tens 21..29/31 as two words ("kahekümne esimene").  A tens-prefix
# pre-pass (the same one the Slavic family uses) merges "TENS UNIT" into one day
# token before the single-token ordinal fold runs; a bare unit ("esimene
# aprill") is left alone because the rewrite only fires when a tens word leads.
# Eesti keele käsiraamat (EKI): järgarvsõnad.
from chronologia.extract.numfold_ordinals import _pron_ordinal_map as _pom
from chronologia.extract.numfold_slavic import (_compose as _sl_compose,
                                                _day_rewrite as _sl_day_rewrite)
_ET_TENS_ORD = {"kahekümne": 20, "kolmekümne": 30}
fold_et = _sl_compose(
    _sl_day_rewrite(dict(_pom("et")), _ET_TENS_ORD),
    with_ordinals(fold_et, "et"))


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
}
# inessive "at N o'clock" ("hiruretan" = at three); the plural hour numeral
# carries the -etan case, so it is one word the cardinal back-end does not read
# AND, with the "o'clock" word dropped, it leaves the clock frame no cue.  Split
# to a synthetic "at" ("etan" is the eu marker_at surface) + the hour digit so
# "at HOUR" / "MERIDIEM at? HOUR" binds it standalone and after a daypart lead.
# 1 and 2 are two-word forms ("ordu batean", "ordu bietan") and fold via the
# case-suffix pre-pass, not here.  Source: Wiktionary, -etan
# (https://en.wiktionary.org/wiki/-etan#Basque), inessive plural; Euskara batua
# telling-time forms (Euskaltzaindia, orduak).
_EU_INESSIVE_HOURS = {
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
# Basque spells its compound hundreds with the conjunction "eta" ("ehun eta
# hogei" = 120), so pronouncing 100..999 pulls the bare connector "eta" into the
# derived word set.  But "eta" is ALSO the hour<->fraction connector of the
# spoken clock ("bostak eta erdi" = half past five); left in the number set it
# lets the fold swallow the clock's "eta" and the whole clock stops resolving.
# Exclude it: single-token hundreds ("berrehun" = 200) still fold, and a spaced
# "eta"-joined compound >= 101 never folded before this file taught the sweep to
# reach past 100, so nothing is lost.
_eu_numfold = _make_fold("eu", _EU_HOUR_FORMS, exclude=frozenset({"eta"}))


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


# Basque spells the ordinal-weekday-of-month selector with a spelled ordinal the
# cardinal back-end does not read ("martxoaren hirugarren astelehena" = the third
# Monday of March).  ``pronounce_ordinal_eu`` emits the ``-garren`` series
# (bigarren, hirugarren, laugarren ...) and ``lehenengo`` for 1; the short first
# ordinal ``lehen`` is the attested idiom the pronouncer omits, so it is supplied
# explicitly.  Source: Euskaltzaindia, zenbaki ordinalak (lehen(engo), bigarren,
# hirugarren ...).
fold_eu = with_ordinals(fold_eu, "eu", {"lehen": 1, "lehenengo": 1})
# Bind the bare inessive telling-time hour ("hiruretan" = at three) the same way
# hu/fi bind their glued clock hours: split to a synthetic "at" + the hour digit
# so "at HOUR" (and "MERIDIEM at? HOUR" after "goizeko"/"arratsaldeko") binds it.
fold_eu = _with_bare_case_hour(fold_eu, _EU_INESSIVE_HOURS, "etan")
