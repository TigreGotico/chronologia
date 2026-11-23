"""Estonian, Finnish, Hungarian and Basque date words over the numtag number
layer.

numtag reads the numbers of these languages, the case forms too: Finnish
"kahden viikon" and "kolmelta", Estonian "kahe nädala" and "viiendal",
Hungarian "háromkor" and "kétezer-huszonnégy", Basque "hirugarren".  The
shared rules of :mod:`chronologia.extract.numlayer_germanic` claim the clock
fractions, the deep-time scale words and the counts of things.  This module
adds the passes that the clock and the date of each language need around
that fold: the bare case-suffixed clock hour, the case suffix written after
a digit, and the words that numtag does not read.
"""
from __future__ import annotations

import re
from dataclasses import replace
from typing import Callable, Dict, FrozenSet, Optional, Tuple

from numtag import Kind, tag_numbers

from chronologia.extract.model import Token
from chronologia.extract.numfold_engine import reindex
from chronologia.extract.numlayer_germanic import (DateWords, count_words, fold,
                                                   locale_words)

Fold = Callable[[Tuple[Token, ...]], Tuple[Token, ...]]


def _words(lang: str) -> DateWords:
    return DateWords(lang=lang,
                     fractions=locale_words(lang, "clock_fraction_"),
                     counts=count_words(lang))


def _with_bare_case_hour(fold: Fold, hours: Dict[str, float], at_surface: str,
                         skip_before: FrozenSet[str] = frozenset(),
                         digit_suffix: Optional[str] = None,
                         no_digit_suffix_after: FrozenSet[str] = frozenset()
                         ) -> Fold:
    """Wrap a ``fold`` so a bare CASE-SUFFIXED clock hour binds its HOUR.

    The colloquial telling-time numeral drops the "o'clock" word and glues the
    temporal/ablative/inessive case suffix straight onto the cardinal -- hu
    "háromkor" (at three), fi "kolmelta", eu "hiruretan".  Folded to a bare
    number, it would leave the clock frame no cue at all: standalone the digit
    binds nothing (returns None), and after a daypart lead the numeral is
    stranded and only the band comes back.

    The one glued token is split into a synthetic ``at`` marker followed by the
    hour number, so the universal "at HOUR" clock order (present in every locale)
    binds it -- standalone and after a daypart/meridiem lead ("MERIDIEM at? HOUR").
    The marker carries an empty ``raw`` and a zero-width extent, so it never
    reaches the remainder text.  It is suppressed when the hour already trails an
    explicit clock marker (Finnish "kello kolmelta"), keeping that frame's parse
    byte-identical.  ``at_surface`` must be a surface in the locale's
    ``marker_at.voc``; ``hours`` is the ``{glued surface: value}`` telling-time map.

    ``digit_suffix`` names the same suffix written after an hour in DIGITS,
    where the orthography separates it with a hyphen the tokenizer drops:
    Hungarian writes "reggel 9-kor" and "delutan 2-kor" beside the spelled
    "kilenckor".  The suffix then arrives as its own token behind the number,
    and the pair is read exactly like the glued form.  Only a locale whose
    spelling rules actually hyphenate the suffix onto a numeral passes it, and
    ``no_digit_suffix_after`` names the surfaces that must not license it: a
    clock fraction in a count-toward-the-hour language, where binding the hour
    alone would answer a whole hour late with the fraction stranded.
    """
    def pre(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
        out = []
        skip = False
        for i, t in enumerate(tokens):
            if skip:
                skip = False
                continue
            nxt = tokens[i + 1] if i + 1 < len(tokens) else None
            if (digit_suffix is not None and t.is_number and t.value is not None
                    and 0 <= t.value <= 24 and float(t.value).is_integer()
                    and nxt is not None and nxt.text == digit_suffix
                    and not (i > 0
                             and tokens[i - 1].text in no_digit_suffix_after)):
                value, skip = t.value, True
            else:
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


# -- Estonian ---------------------------------------------------------------
_ET_WORDS = _words("et")


def fold_et(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """The Estonian number fold."""
    return fold(tokens, _ET_WORDS)


# -- Finnish ----------------------------------------------------------------
# Finnish tells the clock hour with the ablative "-lta/-ltä" ("kello kolmelta"
# = at three o'clock).  With "kello" dropped, the ablative alone marks the
# clock.  Source: Wiktionary, -lta (https://en.wiktionary.org/wiki/-lta#Finnish),
# ablative case; VISK §1237 (kellonajat) for the telling-time use.
_FI_ABLATIVE_HOURS = {
    "yhdeltä": 1, "kahdelta": 2, "kolmelta": 3, "neljältä": 4, "viideltä": 5,
    "kuudelta": 6, "seitsemältä": 7, "kahdeksalta": 8, "yhdeksältä": 9,
    "kymmeneltä": 10, "yhdeltätoista": 11, "kahdeltatoista": 12,
}
_FI_WORDS = _words("fi")


def _fold_fi(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    return fold(tokens, _FI_WORDS)


# The bare ablative telling-time forms (kolmelta, yhdeksältä, ...) drop "kello"
# and carry -lta/-ltä alone; split them so "at HOUR" binds ("kello" is the fi
# marker_at surface).  When "kello" is already spoken ("kello kolmelta") the
# synthetic marker is suppressed so that frame stays byte-identical.
fold_fi = _with_bare_case_hour(_fold_fi, _FI_ABLATIVE_HOURS, "kello",
                               skip_before=frozenset({"kello", "klo"}))


# -- Hungarian --------------------------------------------------------------
# The clock hour "at N o'clock" glues the temporal case suffix -kor onto the
# cardinal ("háromkor" = at three).  Source: Wiktionary, -kor
# (https://en.wiktionary.org/wiki/-kor#Hungarian), temporal case suffix; the
# cardinals are the standard telling-time forms (Magyar helyesírás, Akadémiai).
_HU_KOR_HOURS = {
    "egykor": 1, "kettőkor": 2, "háromkor": 3, "négykor": 4, "ötkor": 5,
    "hatkor": 6, "hétkor": 7, "nyolckor": 8, "kilenckor": 9, "tízkor": 10,
    "tizenegykor": 11, "tizenkettőkor": 12,
}
_HU_WORDS = _words("hu")
_HU_CLOCK_NOUNS = locale_words("hu", "marker_oclock")
_HU_WEEK = locale_words("hu", "unit_week")


def _hu_week_and_counted_fraction(tokens: Tuple[Token, ...]):
    """Claim "hét" when it names the week, and keep a counted fraction.

    "hét" is both seven and week, and so are its case forms ("hetet",
    "héttel", "hétig").  It is seven only before a unit of time or a clock
    noun: "hét nap" (seven days), "hét óra" (seven o'clock).  Alone or after
    any other word it is the week: "jövő héten", "két héttel ezelőtt".

    A clock fraction after "és" ends a count: "két és fél óra" is 2.5
    hours, "két és negyed óra" 2.25 hours.  The shared rules claim the
    fraction as the clock word, which is right in "fél nyolc" (7:30), so the
    count keeps it.
    """
    claimed, kept = set(), set()
    for i, t in enumerate(tokens):
        if t.mention is None:
            continue
        if t.text in _HU_WEEK and t.mention.text.lower() == t.text:
            nxt = tokens[i + 1].text if i + 1 < len(tokens) else None
            if nxt not in _HU_WORDS.counts.units and nxt not in _HU_CLOCK_NOUNS:
                claimed.add(i)
        elif (t.text in _HU_WORDS.fractions and i > 0
              and tokens[i - 1].text == "és"
              and tokens[i - 1].mention is t.mention):
            kept.add(i)
    return claimed, kept, {}


#: The possessive day of the month: "május tizenötödike" (the 15th of May),
#: "tizenötödikén" (on the 15th).  The suffix follows the vowel of the
#: ordinal: -e/-én after a front vowel, -a/-án after a back vowel.  The first
#: day is suppletive: "elseje", "elsején".  Magyar helyesírás (Akadémiai):
#: sorszámnevek; en.wiktionary s.v. elseje.
_HU_DAY_POSSESSIVE = re.compile(r"(.+dik)(?:e|a|én|án)")
_HU_FIRST_DAY = frozenset({"elseje", "elsején"})


def _hu_day_ordinal(word: str) -> Optional[int]:
    """The day of a possessive day ordinal, or None.  numtag reads the bare
    ordinal stem ("tizenötödik")."""
    if word in _HU_FIRST_DAY:
        return 1
    m = _HU_DAY_POSSESSIVE.fullmatch(word)
    if m is None:
        return None
    found = tag_numbers(m.group(1), "hu")
    if (len(found) == 1 and found[0].kind is Kind.ORDINAL
            and found[0].text == m.group(1)):
        day = int(found[0].value)
        if 1 <= day <= 31:
            return day
    return None


def _hu_day_ordinals(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    out = []
    for t in tokens:
        day = (None if t.is_number or t.mention is not None
               else _hu_day_ordinal(t.text))
        out.append(t if day is None else replace(
            t, text=str(day), is_number=True, value=day, ordinal=True))
    return reindex(tuple(out))


def _fold_hu(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    return fold(_hu_day_ordinals(tokens), _HU_WORDS, extra=_hu_week_and_counted_fraction)


# The bare "-kor" telling-time forms (háromkor, nyolckor, ...) drop "óra" and
# glue -kor onto the numeral; split them so "at HOUR" binds ("kor" is the hu
# marker_at surface).  "N órakor" keeps its own "órakor" oclock token and is
# untouched here.
# The suffix is also written after an hour in DIGITS, hyphenated: hu.wikipedia
# prose has "reggel 9-kor", "delutan 2-kor" and "ejjel 11-kor".  A leading
# clock fraction is held back, because Hungarian counts TOWARD the hour: "fel
# 8-kor" is 07:30, so binding the hour alone would answer 08:00 with "fel"
# stranded, a wrong time where refusing is right.
_HU_CLOCK_FRACTIONS = frozenset({"negyed", "fél", "fel", "háromnegyed",
                                 "haromnegyed"})
fold_hu = _with_bare_case_hour(_fold_hu, _HU_KOR_HOURS, "kor",
                               digit_suffix="kor",
                               no_digit_suffix_after=_HU_CLOCK_FRACTIONS)
# A day number or a digit clock takes its case suffix after a hyphen: AkH. 12,
# rule 298, "1848. márc. 15-én", "2014. febr. 28-a", "1-je", "1-jén"; rule
# 300, "10:35-kor".  The tokenizer drops the hyphen and leaves the suffix as a
# word of its own, so a suffix that follows a hyphen folds back into the
# number or clock it is written on.  The sublative "-ra"/"-re" names the same
# point as a target ("ébressz fel 7-re", wake me for 7).  "-ig" (until) is not
# folded: it carries a meaning of its own.  The tokenizer splits the dotted
# clock "10.35" at its dot, so the two halves join back into "10:35" when a
# clock suffix follows.  An hour after a clock fraction ("fél 8-kor", 7:30)
# keeps its suffix too, because the fraction blocks the "at HOUR" reading of
# the bare-suffix fold below.
_HU_DAY_SUFFIX = frozenset({"a", "e", "án", "én", "je", "jén", "ra", "re"})
_HU_CLOCK_SUFFIX = frozenset({"kor", "ra", "re"})
_HU_CLOCK = re.compile(r"\d{1,2}[:.]\d{2}")


def _hu_dotted_clock(tokens: Tuple[Token, ...], i: int) -> Optional[Token]:
    """The clock "HH:MM" that tokens ``i`` and ``i + 1`` spell as "HH.MM"
    when a hyphenated clock suffix follows, else None."""
    if i + 2 >= len(tokens):
        return None
    hour, minute = tokens[i], tokens[i + 1]
    if not (hour.trailing_dot and re.fullmatch(r"\d{1,2}", hour.text)
            and re.fullmatch(r"\d{2}", minute.text)
            and minute.char_start is not None and hour.char_end is not None
            and minute.char_start == hour.char_end + 1
            and minute.trailing_hyphen
            and tokens[i + 2].text in _HU_CLOCK_SUFFIX
            and int(hour.text) <= 23 and int(minute.text) <= 59):
        return None
    return replace(hour, text=f"{hour.text}:{minute.text}",
                   raw=f"{hour.raw}.{minute.raw}", char_end=minute.char_end,
                   is_number=False, value=None, trailing_dot=False,
                   trailing_hyphen=True)


def _with_hu_hyphen_suffix(fold):
    def pre(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
        out, i, n = [], 0, len(tokens)
        while i < n:
            clock = _hu_dotted_clock(tokens, i)
            if clock is not None:
                tokens = tokens[:i] + (clock,) + tokens[i + 2:]
                n -= 1
            t = tokens[i]
            nxt = tokens[i + 1] if i + 1 < n else None
            after_fraction = i > 0 and tokens[i - 1].text in _HU_CLOCK_FRACTIONS
            if nxt is not None and t.trailing_hyphen and (
                    (t.is_number and t.value is not None
                     and 1 <= t.value <= 31 and nxt.text in _HU_DAY_SUFFIX)
                    or (t.is_number and t.value is not None and after_fraction
                        and 0 <= t.value <= 24 and nxt.text in _HU_CLOCK_SUFFIX)
                    or (_HU_CLOCK.fullmatch(t.text)
                        and nxt.text in _HU_CLOCK_SUFFIX)):
                out.append(replace(t, raw=t.raw + nxt.raw,
                                   char_end=nxt.char_end or t.char_end,
                                   trailing_hyphen=False))
                i += 2
                continue
            out.append(t)
            i += 1
        return fold(reindex(tuple(out)))

    return pre


fold_hu = _with_hu_hyphen_suffix(fold_hu)
# A count with a half: "két és fél" (two and a half) and "másfél" (one and a
# half, en.wiktionary s.v. másfél) are one number.  Without the fold the
# offset reads only "fél óra" and strands the whole part.  A number after
# "fél" keeps it a clock ("kettő és fél három", 2 and 2:30).
_HU_ONE_AND_A_HALF = frozenset({"másfél", "masfel"})
_HU_HALF = frozenset({"fél", "fel"})


def _with_hu_half_count(fold):
    def post(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
        tokens = fold(tokens)
        out, i, n = [], 0, len(tokens)
        while i < n:
            t = tokens[i]
            if (i + 3 < n and t.is_number and t.value is not None
                    and float(t.value).is_integer()
                    and tokens[i + 1].text == "és"
                    and tokens[i + 2].text in _HU_HALF
                    and not tokens[i + 3].is_number):
                value, last, step = t.value + 0.5, tokens[i + 2], 3
            elif (t.text in _HU_ONE_AND_A_HALF and i + 1 < n
                  and not tokens[i + 1].is_number):
                value, last, step = 1.5, t, 1
            else:
                out.append(t)
                i += 1
                continue
            # the raw shows the decimal, so the token never binds a clock
            # HOUR: "két és fél óra" is a length of 2.5 hours, and the clock
            # says half past two as "fél három"
            out.append(replace(t, text=str(value), raw=str(value),
                               is_number=True, value=value,
                               char_end=last.char_end))
            i += step
        return reindex(tuple(out))

    return post


fold_hu = _with_hu_half_count(fold_hu)


# -- Basque -----------------------------------------------------------------
# The clock hour takes the article and the plural: "bostak" (five o'clock),
# "ordu bata" (one o'clock).  numtag reads no hour form, so the table gives
# each one its value.  Araua 35, "Orduak nola esan", section 1, p. 182:
# "Aski da dagokion zenbatzaileari artikulua eta plural marka eranstea ...
# Hirurak dira".
_EU_HOUR_FORMS = {
    "ordubata": (1, False), "ordubiak": (2, False), "hirurak": (3, False),
    "laurak": (4, False), "bostak": (5, False), "seirak": (6, False),
    "zazpirak": (7, False), "zortzirak": (8, False),
    "bederatziak": (9, False), "hamarrak": (10, False),
    "hamaikak": (11, False), "hamabiak": (12, False),
}
# inessive "at N o'clock" ("hiruretan" = at three); the plural hour numeral
# carries the -etan case, and with the "o'clock" word dropped it leaves the
# clock frame no cue.  Split to a synthetic "at" ("etan" is the eu marker_at
# surface) + the hour digit so "at HOUR" / "MERIDIEM at? HOUR" binds it
# standalone and after a daypart lead.  1 and 2 are two-word forms ("ordu
# batean", "ordu bietan") and fold via the case-suffix pre-pass, not here.
# Source: Wiktionary, -etan (https://en.wiktionary.org/wiki/-etan#Basque),
# inessive plural; Euskara batua telling-time forms (Euskaltzaindia, orduak).
_EU_INESSIVE_HOURS = {
    "hiruretan": 3, "lauretan": 4, "bostetan": 5, "seietan": 6,
    "zazpietan": 7, "zortzietan": 8, "bederatzietan": 9, "hamarretan": 10,
    "hamaiketan": 11, "hamabietan": 12,
}
# "ekainaren 5ean" (of-June 5th-in), "2027ko ekaina" (2027-of June).  The
# tokenizer shears the digit from its case suffix ("5ean" -> "5", "ean"); a
# number followed by a bare case-suffix fragment folds back to the number so
# the DAY/YEAR slot binds.  A bare "k" is left out: it collides with the
# "k.a."/"k.o." era abbreviations the tokenizer shears to a "k" fragment.
# "ak" is the absolutive plural a digit hour carries like the spelled
# "bostak": Araua 35, "Orduak nola esan", section 1, p. 182 ("Aski da
# dagokion zenbatzaileari artikulua eta plural marka eranstea ... Hirurak
# dira") and decision 6, p. 185 ("arratsaldeko 3etatik gaueko 12ak arte").
_EU_NUM_SUFFIX = frozenset({
    "a", "ak", "an", "ean", "n", "ko", "eko", "ren",
    "garren", "garrena", "garrenean",
})
_EU_WORDS = _words("eu")


def _eu_digit_suffix(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    merged = []
    i = 0
    n = len(tokens)
    while i < n:
        t = tokens[i]
        nxt = tokens[i + 1] if i + 1 < n else None
        if (t.is_number and nxt is not None and not nxt.is_number
                and nxt.text == "etan"):
            # the digit hour with the inessive glued on ("3etan" = at three;
            # Araua 37 writes case suffixes onto digits, "1995eko", "7an"):
            # the same synthetic "at" + hour the spelled "hiruretan" gets
            merged.append(Token(text="etan", raw="", index=t.index,
                                char_start=t.char_start, char_end=t.char_start))
            merged.append(replace(t, raw=t.raw + nxt.raw,
                                  char_end=nxt.char_end if nxt.char_end is not None
                                  else t.char_end))
            i += 2
            continue
        if (t.is_number and nxt is not None and not nxt.is_number
                and nxt.text in _EU_NUM_SUFFIX):
            merged.append(replace(t, raw=t.raw + nxt.raw,
                                  char_end=nxt.char_end if nxt.char_end is not None
                                  else t.char_end))
            i += 2
            continue
        merged.append(t)
        i += 1
    return reindex(tuple(merged))


def _fold_eu(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    return fold(_eu_digit_suffix(tokens), _EU_WORDS, table=_EU_HOUR_FORMS)


fold_eu = _with_bare_case_hour(_fold_eu, _EU_INESSIVE_HOURS, "etan")
