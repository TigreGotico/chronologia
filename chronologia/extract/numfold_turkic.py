"""Turkic spelled-number folding (az / tr).

These languages expose a single ``extract_number_<lang>`` reader (no
``NumberVocabulary``), so the Germanic single-extractor fold applies
verbatim, plus a shared locative-case clock-hour strip ("saat üçte" / "saat
üçdə" -> "üç") and, for Turkish, a case-marked spoken-clock hour map and an
"ilk" ordinal.

Split out of ``numfold.py`` verbatim (behaviour-preserving refactor).  The
``_lazy_germanic_fold`` engine primitive stays in ``numfold`` because the
Germanic folds and the base-locale folds (id/kab/ms/fa) share it too --
imported here rather than duplicated.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Tuple

from chronologia.extract.model import Token
from chronologia.extract.numfold import _lazy_germanic_fold
from chronologia.extract.numfold_engine import reindex as _reindex
from chronologia.extract.numfold_ordinals import with_ordinals as _with_ordinals

# ---------------------------------------------------------------------------
# Turkic / isolating spelled-number folding (tr / az / id / ms / kab)
#
# These families expose a single ``extract_number_<lang>`` reader (no
# ``NumberVocabulary``), so the Germanic single-extractor fold applies
# verbatim: a maximal run of number-words is joined and read to one digit
# token, with clock-fraction and scale words withheld so the token that
# distinguishes a construction survives.  ``extract_number_<lang>`` here has
# signature ``(text, short_scale=True, ordinals=False)`` -- the fold's
# ``value_of`` tries ``ordinals=True`` then the cardinal default, which the
# extra ``short_scale`` positional default leaves untouched.
# ---------------------------------------------------------------------------
# Turkish spoken-clock hours carry the case suffix the direction word agrees
# with -- accusative (-ı/-i/-u/-ü) before "geçe" (past), dative (-e/-a) before
# "kala" (to).  ``extract_number_tr`` reads only the bare cardinal, so these
# inflected surfaces (which the pronounce side never emits) are mapped back to
# their hour value here; the accusative/dative distinction is redundant with
# the mandatory geçe/kala word and so is safely collapsed to the digit.
# 1..10 as single tokens ("saat dokuzu beş geçe" = 9:05, "yediye çeyrek kala"
# = 6:45); 11/12 ("on bir"/"on iki") inflect their final word (biri/ikiyi),
# so the "on" + mapped-final-word run folds through the cardinal reader.
_TR_HOURS = {
    "biri": 1, "ikiyi": 2, "üçü": 3, "dördü": 4, "beşi": 5,
    "altıyı": 6, "yediyi": 7, "sekizi": 8, "dokuzu": 9, "onu": 10,
    "bire": 1, "ikiye": 2, "üçe": 3, "dörde": 4, "beşe": 5,
    "altıya": 6, "yediye": 7, "sekize": 8, "dokuza": 9, "ona": 10,
}
_tr_numfold = _lazy_germanic_fold(
    "ovos_number_parser.numbers_tr", "extract_number_tr",
    # "buçuk" (=30, the additive half-past word) and "çeyrek" (=15) are held
    # out of the number run so the FRACTION slot binds them ("üç buçuk" =
    # 3:30) instead of folding to 3.5.
    {"yarım", "çeyrek", "buçuk", "bin", "milyon", "milyar"})


# Turkic locative case marks "at <hour>" on the clock numeral: Turkish "saat
# üçte" (at three), Azerbaijani "saat üçdə".  The suffix harmonises for
# backness and preceding-consonant voicing -- tr -te/-ta/-de/-da, az
# -tə/-ta/-də/-da -- and ``extract_number_<lang>`` does not read the inflected
# surface: it silently mis-reads "üçte"/"üçdə" as the fraction 1/3 (0.333), so
# the HOUR slot never binds and the whole span is dropped.  This mirrors the
# fi ablative ("kello kolmelta"), eu inessive ("hiruretan") and hu temporal
# ("háromkor") clock folds already in the agglutinative batch, and the
# accusative/dative geçe/kala fold just below: fold the case-suffixed hour
# back to its bare cardinal so the ordinary number path binds it.  Sources:
# Wiktionary, -də/-da (Azerbaijani) and -de/-te (Turkish) locative case; the
# suffixed numeral is the everyday telling-time form (TDK Güncel Türkçe
# Sözlük "saat"; Azərbaycan dilinin izahlı lüğəti "saat").
#
# Fired only in the clock frame (a "saat" hour-noun token present) and only
# when the stripped stem reads as a bare 0..23 cardinal, so bare numbers,
# dates and any non-clock word ending in these letters stay byte-identical.
# The strip runs *before* the cardinal run-fold so a compound hour folds
# through it: "on birde" -> "on" + "bir" -> 11, "on ikide" -> 12.
_TR_LOCATIVE_SUFFIXES = ("tə", "də", "te", "ta", "de", "da")


def _strip_locative_hour(tokens, lang):
    if not any(t.text == "saat" for t in tokens):
        return tokens
    import importlib
    extract = getattr(importlib.import_module(
        "ovos_number_parser.numbers_" + lang), "extract_number_" + lang)
    out = []
    for t in tokens:
        if not t.is_number:
            w = t.text
            for suf in _TR_LOCATIVE_SUFFIXES:
                if w.endswith(suf) and len(w) > len(suf):
                    stem = w[:-len(suf)]
                    try:
                        val = extract(stem)
                    except Exception:
                        val = False
                    if (isinstance(val, (int, float))
                            and not isinstance(val, bool)
                            and float(val) == int(val) and 0 <= val <= 23):
                        t = replace(t, text=stem)
                    break
        out.append(t)
    return tuple(out)


def fold_tr(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Turkish fold: strip a locative-case clock hour ("saat üçte" -> "üç"),
    cardinal run fold, then map the case-marked spoken-clock hour to its digit.
    The hour map runs *after* the cardinal fold so the mapped hour does not
    merge with a following bare-minute cardinal: "dokuzu beş geçe" must stay
    [9][5][geçe] (9:05), not fold to one number.
    """
    tokens = _strip_locative_hour(tokens, "tr")
    folded = _tr_numfold(tokens)
    out = [replace(t, text=str(_TR_HOURS[t.text]), is_number=True,
                   value=_TR_HOURS[t.text])
           if (not t.is_number and t.text in _TR_HOURS) else t
           for t in folded]
    return _reindex(tuple(out))
# Turkish ordinals so the ``NUM`` slot of "2020'nin ilk/ikinci yarısı" binds:
# ``pronounce_ordinal_tr`` emits birinci/ikinci ..., and "ilk" -- the ordinary
# word for "first/initial" that the half phrase actually uses -- is added as the
# one surface the pronouncer does not cover.  TDK Güncel Türkçe Sözlük: "ilk" =
# birinci; "ikinci" = sıra sayı sıfatı.  https://sozluk.gov.tr
fold_tr = _with_ordinals(fold_tr, "tr", {"ilk": 1})
_az_numfold = _lazy_germanic_fold(
    "ovos_number_parser.numbers_az", "extract_number_az",
    {"yarım", "min", "milyon", "milyard"})


def fold_az(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Azerbaijani fold: strip the locative-case clock hour ("saat üçdə" ->
    "üç") before the cardinal run-fold, then fold as usual."""
    return _az_numfold(_strip_locative_hour(tokens, "az"))
