"""Turkish and Azerbaijani date words over the numtag number layer.

numtag reads the case forms of the Turkic clock hour: the locative "saat
üçte" and "saat üçdə" (at three), the accusative "dokuzu beş geçe" (9:05) and
the dative "yediye çeyrek kala" (6:45).  The shared rules of
:mod:`chronologia.extract.numlayer` claim the clock fractions, the
deep-time scale words and the counts of things.  This module adds the case
suffix written after a digit hour and the words numtag does not read.
"""
from __future__ import annotations

from typing import Tuple

from chronologia.extract.model import Token
from chronologia.extract.numlayer import (DateWords, count_words, fold,
                                          locale_words)
from chronologia.extract.numfold_engine import reindex

# Turkic locative case marks "at <hour>" on the clock numeral: Turkish "saat
# üçte" (at three), Azerbaijani "saat üçdə".  The suffix harmonises for
# backness and preceding-consonant voicing -- tr -te/-ta/-de/-da, az
# -tə/-ta/-də/-da.  Sources: Wiktionary, -də/-da (Azerbaijani) and -de/-te
# (Turkish) locative case; the suffixed numeral is the everyday telling-time
# form (TDK Güncel Türkçe Sözlük "saat"; Azərbaycan dilinin izahlı lüğəti
# "saat").
_LOCATIVE_SUFFIXES = frozenset({"tə", "də", "te", "ta", "de", "da"})


def _drop_digit_locative(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Drop the locative suffix of a digit clock hour: "saat 9'da".

    The tokenizer splits the apostrophe, so "9'da" arrives as "9" and "da".
    In the clock frame (a "saat" token present) a suffix one apostrophe after
    a digit is the "at <hour>" mark, and the clock grammar reads the bare
    hour.  Unrelated "-da/-de" words ("orada", "burada") never stand one
    apostrophe after a digit, so they stay.
    """
    if not any(t.text == "saat" for t in tokens):
        return tokens
    out = []
    for i, t in enumerate(tokens):
        prev = tokens[i - 1] if i else None
        if (prev is not None and prev.is_number and not t.is_number
                and t.text in _LOCATIVE_SUFFIXES
                and prev.char_end is not None
                and t.char_start == prev.char_end + 1):
            continue
        out.append(t)
    return reindex(tuple(out))


def _words(lang: str) -> DateWords:
    return DateWords(lang=lang,
                     fractions=locale_words(lang, "clock_fraction_"),
                     counts=count_words(lang))


_TR_WORDS = _words("tr")
_AZ_WORDS = _words("az")
# "ilk" is the ordinary word for "first" in "2020'nin ilk yarısı" (the first
# half of 2020).  TDK Güncel Türkçe Sözlük (https://sozluk.gov.tr), "ilk",
# sense 1: "Zaman, sıra, yer ve önem bakımından ötekilerden önce gelen".
_TR_TABLE = {"ilk": (1, True)}


def fold_tr(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """The Turkish number fold."""
    return fold(_drop_digit_locative(tokens), _TR_WORDS, table=_TR_TABLE)


def _az_other_day(tokens: Tuple[Token, ...]):
    """Claim "biri" in "o biri gün" (the day after tomorrow): the phrase is a
    named day, not the count one (``locale/az/named_day_2.voc``)."""
    claimed = {i for i, t in enumerate(tokens)
               if t.text == "biri" and t.mention is not None
               and i > 0 and tokens[i - 1].text == "o"}
    return claimed, set(), {}


def fold_az(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """The Azerbaijani number fold."""
    return fold(_drop_digit_locative(tokens), _AZ_WORDS, extra=_az_other_day)
