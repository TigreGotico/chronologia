"""French date words over the numtag number layer."""
from __future__ import annotations

from dataclasses import replace
from typing import Tuple

from chronologia.extract.model import LangSpec, Token
from chronologia.extract.numfold_engine import reindex, run_extent
from chronologia.extract.numfold_romance import (_collapse_h_clock,
                                                 _collapse_phrase,
                                                 _elision_split, _glue,
                                                 _merge_digit_ordinal)
from chronologia.extract.numlayer_romance import (Claims, DateWords,
                                                  count_words, fold,
                                                  locale_words)

_WORDS = DateWords(
    lang="fr",
    fractions=locale_words("fr", "clock_fraction_") | {"quarts"},
    definite=frozenset({"le", "la", "les", "l"}),
    quarter_articles=frozenset({"un"}),
    unit_nouns=frozenset({"secondes"}),
    unit_ordinals=frozenset({"seconde"}),
    counts=count_words("fr", locale_words("fr", "marker_since")),
    articles_are_words=True)

#: The proclitics that elide before a vowel: "d'onze", "l'an", "qu'un".
_PROCLITICS = frozenset({"d", "l", "j", "n", "s", "c", "m", "t", "qu"})
_PHRASES = [
    (["avant", "jésus", "christ"], "avjc"),
    (["avant", "jesus", "christ"], "avjc"),
    (["avant", "notre", "ère"], "avjc"), (["avant", "notre", "ere"], "avjc"),
    (["av", "j", "c"], "avjc"), (["av", "jc"], "avjc"),
    (["après", "jésus", "christ"], "apjc"),
    (["apres", "jesus", "christ"], "apjc"),
    (["de", "notre", "ère"], "apjc"), (["de", "notre", "ere"], "apjc"),
    (["ap", "j", "c"], "apjc"), (["ap", "jc"], "apjc"),
    (["il", "y", "a"], "ilya"),
    (["week", "end"], "weekend"),
]
#: "avant hier" and "après demain" are the fixed day before yesterday and
#: day after tomorrow, except after a count of days: in "deux jours après
#: demain" the word "après" is the marker of an offset from tomorrow.
_DAY_PHRASES = [
    (["avant", "hier"], "avanthier"),
    (["apres", "demain"], "apresdemain"), (["après", "demain"], "apresdemain"),
]
_DAY_UNITS = frozenset({"jour", "jours"})
_HOURS = frozenset({"heure", "heures"})
_ET = frozenset({"et"})
#: The suffixes of a digit ordinal that the tokenizer splits: "1 er".
_ORDINAL_SUFFIXES = frozenset({"er", "ere", "ère", "e", "eme", "ème", "nd",
                               "nde", "d", "re", "es", "emes", "èmes"})


def split_elisions(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """The French ``pre_hook``: split an elided proclitic from its word
    ("d'onze" gives "d" and "onze"), so the number layer finds the number in
    the word.  A lexical apostrophe stays: "aujourd'hui"."""
    return _elision_split(tokens, _PROCLITICS)


def _day_phrases(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    out = list(tokens)
    for words, surface in _DAY_PHRASES:
        n = len(words)
        i = 0
        while i + n <= len(out):
            counted = (i >= 2 and out[i - 1].text in _DAY_UNITS
                       and (out[i - 2].is_number
                            or out[i - 2].mention is not None))
            if [t.text for t in out[i:i + n]] == words and not counted:
                raw = " ".join(t.raw for t in out[i:i + n])
                cs, ce = run_extent(out[i:i + n])
                out[i:i + n] = [Token(text=surface, raw=raw, index=0,
                                      char_start=cs, char_end=ce)]
            i += 1
    return reindex(tuple(out))


def _une_heure(tokens: Tuple[Token, ...]) -> Claims:
    """Keep "un" and "une" before "heure" as the hour 1: "une heure et
    quart".  Everywhere else the article stays a word: "une semaine"."""
    kept = {i for i, t in enumerate(tokens[:-1])
            if t.text in ("un", "une") and tokens[i + 1].text in _HOURS}
    return set(), kept, {}


def fold_fr(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """The French number fold.

    "h" is the symbol of "heure" (OQLF, Banque de dépannage linguistique,
    "Écriture des nombres exprimant une durée": "2 heures 28 minutes (ou :
    2 h 28 min)"), so after the counted-offset words "dans" and "il y a" it
    is the hour unit, and before the clock directions "et" and "moins" it is
    the hour word.  Everywhere else "20h30" is a clock time.
    """
    tokens = split_elisions(tokens)
    for words, surface in _PHRASES:
        tokens = _collapse_phrase(tokens, words, surface)
    tokens = _day_phrases(tokens)
    tokens = _collapse_h_clock(tokens, frozenset({"dans", "ilya"}),
                               frozenset({"et", "moins"}))
    tokens = _merge_digit_ordinal(tokens, _ORDINAL_SUFFIXES)
    return fold(_glue(tokens), _WORDS, _une_heure)


def _governed_hour_length(tokens, spec, governors, fractions, minus,
                          minus_articles, second_symbols):
    """Spell a counted length of hours as "N h et M minutes et S secondes".

    After a counted-offset word ("dans", "il y a") the hour and the count
    that follows it are one length: "dans 2h30", "dans 2 h 30", "dans 2
    heures et demie", "dans 2 h 10 s".  The grammar reads that length only in
    its full form ("dans 2 heures et 30 minutes"), so the short forms are
    rewritten to it.  The unit word after the count names its unit: none or
    a minute word is minutes, a second word or one of ``second_symbols`` is
    seconds, and any other unit ("dans 2 heures 10 jours") is not part of
    the length, so the phrase is left as written.  ``fractions`` maps the
    fraction words after "et" to their minutes.  After a ``minus`` word the
    count is taken away from the hours, with an optional article before a
    fraction: "dans 2 h moins le quart" is the length 1 h 45 min, "dans 2 h
    moins 10" is 1 h 50 min, "dans 2 h moins 10 secondes" is 1 h 59 min 50 s.

    It runs as the language ``post_hook``: the pipeline holds a counted
    second word out of the number fold, and only the whole stream shows the
    unit after the count.
    """
    def count(tok):
        return (tok is not None and tok.is_number and tok.value is not None
                and 0 < tok.value < 60 and float(tok.value).is_integer())

    def unit_of(k):
        if k >= n:
            return None
        if tokens[k].text in second_symbols:
            return "second"
        return spec.units.get(tokens[k].text)

    def number(value):
        return Token(text=str(value), raw=str(value), index=0,
                     is_number=True, value=value)

    def word(text):
        return Token(text=text, raw=text, index=0)

    out = []
    i = 0
    n = len(tokens)
    while i < n:
        t = tokens[i]
        hour = tokens[i + 1] if i + 1 < n else None
        if not (out and out[-1].text in governors and t.is_number
                and hour is not None and spec.units.get(hour.text) == "hour"):
            out.append(t)
            i += 1
            continue
        nxt = tokens[i + 2] if i + 2 < n else None
        nn = tokens[i + 3] if i + 3 < n else None
        hours = t
        minutes = seconds = None
        if count(nxt):
            unit = unit_of(i + 3)
            if unit is None:
                minutes, used = int(nxt.value), 3
            elif unit == "minute":
                minutes, used = int(nxt.value), 4
            elif unit == "second":
                seconds, used = int(nxt.value), 4
        elif (nxt is not None and nxt.text in _ET and nn is not None
                and nn.text in fractions):
            minutes, used = fractions[nn.text], 4
        elif (nxt is not None and nxt.text in minus
                and t.value is not None and float(t.value).is_integer()):
            j = i + 3
            if nn is not None and nn.text in minus_articles:
                j += 1
            taken_tok = tokens[j] if j < n else None
            taken = None  # seconds
            if taken_tok is not None and taken_tok.text in fractions:
                taken, used = fractions[taken_tok.text] * 60, j + 1 - i
            elif j == i + 3 and count(taken_tok):
                unit = unit_of(i + 4)
                if unit is None:
                    taken, used = int(taken_tok.value) * 60, 4
                elif unit == "minute":
                    taken, used = int(taken_tok.value) * 60, 5
                elif unit == "second":
                    taken, used = int(taken_tok.value), 5
            if taken is not None and int(t.value) * 3600 > taken:
                whole, rest = divmod(int(t.value) * 3600 - taken, 3600)
                hours = number(whole)
                minutes, seconds = divmod(rest, 60)
                seconds = seconds or None
        if minutes is None and seconds is None:
            out.append(t)
            i += 1
            continue
        # the rewritten length keeps the extent of what was written, so a
        # remainder or a mention reads the user's own words
        first, last = tokens[i + 2], tokens[i + used - 1]
        tail = []
        if minutes is not None:
            tail += [word("et"), number(minutes), word("minutes")]
        if seconds is not None:
            tail += [word("et"), number(seconds), word("secondes")]
        tail = [replace(x, char_start=first.char_start, char_end=last.char_end)
                for x in tail]
        out.extend([replace(hours, raw=t.raw, char_start=t.char_start,
                            char_end=t.char_end), hour] + tail)
        i += used
    return reindex(tuple(out))


def fold_fr_hour_length(tokens: Tuple[Token, ...],
                        spec: LangSpec) -> Tuple[Token, ...]:
    """The French ``post_hook``: a counted length of hours after "dans" or
    "il y a" (:func:`_governed_hour_length`).

    A count of hours and minutes after those offset words is one length
    (OQLF, Banque de dépannage linguistique, "Écriture des nombres exprimant
    une durée": "L'expérience a duré exactement 2 heures 28 minutes. (ou :
    2 h 28 min)"), and so is a count of seconds after it: "La championne a
    couru l'épreuve en 10 min 35 s 7/100." (same page).  "sec" is also a
    symbol of the second: "Symbole de la seconde. Note : Le symbole du
    Système international est s." (Wiktionnaire, s.v. "sec", Conventions
    internationales, 3, labelled "Non standard").  "et demie" and "et quart" after a count of hours
    are its half and its quarter: "Qui a la valeur d'une moitié s'ajoutant à
    la quantité exprimée par le substantif. Il a deux ans et demi" (TLFi,
    s.v. "demi", I.A); "Quart d'heure" : "Une des quatre parties égales
    d'une heure, quinze minutes." (TLFi, s.v. "quart", B.1.a).  "moins"
    before a count takes it away from the hours: "Pour indiquer une
    soustraction" (TLFi, s.v. "moins", II.A), and "moins le quart est plus
    fréq. que moins un quart" (TLFi, s.v. "quart", B.1.a).
    """
    return _governed_hour_length(
        tokens, spec, governors=frozenset({"dans", "ilya"}),
        fractions={"demie": 30, "demi": 30, "quart": 15},
        minus=frozenset({"moins"}),
        minus_articles=frozenset({"le", "la", "un"}),
        second_symbols=frozenset({"s", "sec"}))
