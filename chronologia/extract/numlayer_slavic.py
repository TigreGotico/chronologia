"""Date words over the numtag number layer, shared by the Slavic folds.

numtag reads the numbers of Bulgarian, Croatian, Czech, Polish, Russian,
Slovak, Slovene and Ukrainian in every case form: "двадцать третьего",
"dwudziestego trzeciego", "pěti", "petimi".  The count, scale and year rules
are those of :mod:`chronologia.extract.numlayer_germanic`.  This module adds
the date words of the Slavic grammars:

- a clock or period fraction that numtag reads as a fraction stays a word:
  "půl deváté" is 8:30, "pierwsza połowa 2020" is the first half of 2020, and
  "осем и половина" is 8:30;
- a decade word stays a word: "девяностые" names the 1990s, not the number 90;
- an ordinal or a count of millions before a word that no date rule reads
  ranks or counts things, so it stays words: "ve druhém patře" is the second
  floor, not two o'clock, and "milion důvodů" keeps its word in an event
  summary;
- an ordinal word from 1 to 31 can name a day of the month ("двадцатого
  числа"), so its number token carries :attr:`Token.day_ordinal`.

The folds of the eight languages close the module.  Each one names the
words that numtag does not read yet, through a spelling that it reads.
"""
from __future__ import annotations

from dataclasses import replace
from fractions import Fraction
from typing import Callable, List, Optional, Set, Tuple

from numtag import Form, Kind, NumberMention, Role

from chronologia.extract.model import Token
from chronologia.extract.numfold_engine import reindex
from chronologia.extract.numlayer import reread
from chronologia.extract.numlayer_germanic import (Claims, DateWords,
                                                   count_words, ends_mention,
                                                   fold, locale_words,
                                                   mention_end)

Fold = Callable[[Tuple[Token, ...]], Tuple[Token, ...]]


def _names_things(mention: NumberMention) -> bool:
    """Whether ``mention`` can rank or count things: an ordinal, or a count
    that ends in a scale word of a million or more ("milion", "два
    миллиона").  A thousand is left out, because a year ends in one: "v roce
    dva tisíce"."""
    if mention.kind is Kind.ORDINAL:
        return True
    return (mention.kind is Kind.CARDINAL and bool(mention.parts)
            and mention.parts[-1].role is Role.SCALE
            and Fraction(mention.value) >= 10 ** 6)


def _date_words(lang: str) -> Callable[[Tuple[Token, ...]], Claims]:
    fractions = locale_words(lang, "clock_fraction_", "marker_half",
                             "period_part_")
    decades = locale_words(lang, "decade_word_")
    vocabulary = locale_words(lang, "")

    def claims(tokens: Tuple[Token, ...]) -> Claims:
        claimed: Set[int] = set()
        n = len(tokens)
        for i, tok in enumerate(tokens):
            m = tok.mention
            if m is None or tok.is_number:
                continue
            if tok.text in fractions:
                if ends_mention(tok) and m.kind is Kind.FRACTION:
                    claimed.add(i)
            elif tok.text in decades:
                claimed.add(i)
            elif ends_mention(tok) and _names_things(m):
                end = mention_end(tokens, i)
                nxt = tokens[end] if end < n else None
                if (nxt is not None and not nxt.is_number
                        and nxt.mention is None and not nxt.break_before
                        and nxt.text.isalpha()
                        and nxt.text not in vocabulary):
                    k = i
                    while k >= 0 and tokens[k].mention is m:
                        claimed.add(k)
                        k -= 1
        return claimed, set(), {}

    return claims


def _day_ordinals(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    return tuple(replace(t, day_ordinal=True)
                 if (t.is_number and t.ordinal and t.mention is not None
                     and t.mention.form is Form.WORDS
                     and 1 <= (t.value or 0) <= 31) else t
                 for t in tokens)


def _read(run: Tuple[Token, ...], lang: str) -> Optional[Token]:
    """The one number token numtag reads over all of ``run``, or ``None``."""
    read = reread(run, lang)
    return read[0] if len(read) == 1 and read[0].is_number else None


def _number_before(out: List[Token], t: Token) -> int:
    """The index in ``out`` where the mention before ``t`` starts, through
    one joiner word ("dvadeset i trećega"), or ``len(out)``."""
    k = len(out)
    if t.break_before or not k:
        return k
    joiner = out[k - 1]
    if (k > 1 and joiner.mention is None and not joiner.is_number
            and not joiner.break_before):
        k -= 1
    m = out[k - 1].mention
    if m is None:
        return len(out)
    while k and out[k - 1].mention is m:
        k -= 1
    return k


def read_unread(tokens: Tuple[Token, ...], lang: str,
                spelling: Callable[[str], str]) -> Tuple[Token, ...]:
    """Read each word that numtag does not read through the spelling that
    it does read.  ``spelling`` maps a word to that spelling, or to the word
    itself.  The word is read with the mention before it when the two name
    one number ("dvadeset trećega" is 23), else alone."""
    out = []
    changed = False
    for t in tokens:
        twin = t.text if t.is_number or t.mention else spelling(t.text)
        if twin == t.text:
            out.append(t)
            continue
        word = replace(t, raw=twin)
        start = _number_before(out, t)
        read = (_read(tuple(out[start:]) + (word,), lang)
                if start < len(out) else None)
        if read is None:
            start = len(out)
            read = _read((word,), lang)
        if read is None:
            out.append(t)
            continue
        run = out[start:] + [t]
        del out[start:]
        out.append(replace(read, raw=" ".join(x.raw for x in run),
                           char_start=run[0].char_start, char_end=t.char_end,
                           before=run[0].before, after=run[0].after))
        changed = True
    return reindex(tuple(out)) if changed else tokens


def make_fold(lang: str, pre: Optional[Fold] = None,
              spelling: Optional[Callable[[str], str]] = None) -> Fold:
    """The number fold of the Slavic locale ``lang``.  ``pre`` runs on the
    tokens before the fold, and ``spelling`` names the spelling numtag reads
    for a word it does not read (:func:`read_unread`)."""
    words = DateWords(lang=lang, fractions=frozenset(),
                      counts=count_words(lang))
    extra = _date_words(lang)

    def run(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
        if pre is not None:
            tokens = pre(tokens)
        if spelling is not None:
            tokens = read_unread(tokens, lang, spelling)
        return _day_ordinals(fold(tokens, words, extra=extra))

    return run


# -- Russian ---------------------------------------------------------------
# The genitive units that "пол" (half) joins into one word: "полчаса" is half
# an hour, "полминуты", "полдня", "полнедели" (unit_hour.voc, unit_minute.voc,
# unit_day.voc, unit_week.voc).  The split gives the two words of the spaced
# spelling "пол часа", which the grammar reads.
_RU_HALF_UNITS = frozenset({"часа", "минуты", "дня", "недели"})


def _ru_hour(t: Token) -> Optional[Token]:
    """The ordinal clock hour 1..12 that numtag reads in ``t``, or ``None``."""
    hour = _read((t,), "ru")
    if hour is None or not hour.ordinal or not 1 <= (hour.value or 0) <= 12:
        return None
    return hour


def _split_ru_half(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Split the Russian "пол" compounds.

    "полчаса" becomes "пол" and "часа".  "полдевятого" is half toward the
    ninth hour, 8:30: it becomes the clock fraction "половина" and the
    ordinal hour, which numtag reads.  "полдень" and "полночь" stay whole,
    because no number follows "пол" in them.

    A "пол" word before an ordinal hour is the clock fraction too.  The
    dictionary writes "пол-одиннадцатого" with a hyphen, because the hour
    starts with a vowel, and "полвосьмого" solid (Русский орфографический
    словарь РАН, ред. В. В. Лопатин, О. Е. Иванова: "полвосьмо́го"); writers
    and speech recognisers also give the spaced "пол восьмого".
    """
    out = []
    changed = False
    for i, t in enumerate(tokens):
        nxt = tokens[i + 1] if i + 1 < len(tokens) else None
        if (t.text == "пол" and nxt is not None and not nxt.is_number
                and not nxt.break_before and _ru_hour(nxt) is not None):
            out.append(Token(text="половина", raw=t.raw, index=t.index,
                             char_start=t.char_start, char_end=t.char_end,
                             cap=t.cap, prev_cap=t.prev_cap,
                             break_before=t.break_before))
            changed = True
            continue
        tail = t.text[3:] if t.text.startswith("пол") and not t.is_number else ""
        if tail in _RU_HALF_UNITS:
            half_text, rest = "пол", None
        elif tail:
            rest = _ru_hour(replace(t, raw=tail))
            if rest is None:
                out.append(t)
                continue
            half_text = "половина"
        else:
            out.append(t)
            continue
        mid = t.char_start + 3 if t.char_start is not None else None
        out.append(Token(text=half_text, raw=half_text, index=t.index,
                         char_start=t.char_start, char_end=mid))
        out.append(replace(rest, index=t.index, char_start=mid,
                           char_end=t.char_end) if rest is not None else
                   Token(text=tail, raw=tail, index=t.index,
                         char_start=mid, char_end=t.char_end))
        changed = True
    return reindex(tuple(out)) if changed else tokens


# -- Czech -----------------------------------------------------------------
def _glue_cs_three_quarters(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Join the spaced "tři čtvrtě" into the solid "třičtvrtě" of the clock
    fractions.  Internetová jazyková příručka (ÚJČ AV ČR), "Vyjadřování
    času", writes the example spaced: "tři čtvrtě na sedm" is 6:45."""
    out = []
    i = 0
    n = len(tokens)
    while i < n:
        t = tokens[i]
        nxt = tokens[i + 1] if i + 1 < n else None
        if (nxt is not None and not t.is_number and t.text == "tři"
                and nxt.text == "čtvrtě"):
            out.append(Token(text="třičtvrtě", raw=t.raw + " " + nxt.raw,
                             index=t.index, char_start=t.char_start,
                             char_end=nxt.char_end, cap=t.cap,
                             prev_cap=t.prev_cap))
            i += 2
            continue
        out.append(t)
        i += 1
    return reindex(tuple(out)) if len(out) != n else tokens


# The bookish day ordinal "prvého" beside "prvního" (Slovník spisovného jazyka
# českého: "prvý", the bookish form of "první").
_CS_SPELLINGS = {"prvého": "prvního"}


# -- Polish ----------------------------------------------------------------
def glue_pl_half(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Join the spaced "w pół do" before an ordinal hour into the clock
    fraction "wpół do": "w pół do ósmej" is 7:30.  The dictionary writes it
    solid (Słownik języka polskiego PWN, "wpół": "wpół do dziewiątej");
    writers and speech recognisers also give the spaced form.

    It is the ``pre_hook`` of the Polish locale, so the range reader sees
    "wpół" and does not read "do" as "until"."""
    out = []
    i = 0
    n = len(tokens)
    while i < n:
        t = tokens[i]
        if (i + 3 < n and t.text == "w" and tokens[i + 1].text == "pół"
                and tokens[i + 2].text == "do"
                and not any(x.break_before for x in tokens[i + 1:i + 4])):
            hour = _read((tokens[i + 3],), "pl")
            if (hour is not None and hour.ordinal
                    and 1 <= (hour.value or 0) <= 12):
                half = tokens[i + 1]
                out.append(Token(text="wpół", raw=t.raw + " " + half.raw,
                                 index=t.index, char_start=t.char_start,
                                 char_end=half.char_end, cap=t.cap,
                                 prev_cap=t.prev_cap,
                                 break_before=t.break_before))
                i += 2
                continue
        out.append(t)
        i += 1
    return reindex(tuple(out)) if len(out) != n else tokens


# -- Croatian --------------------------------------------------------------
def _hr_spelling(word: str) -> str:
    """The short form of a Croatian ordinal with the movable "a" (navezak):
    "trećega" is "trećeg", "prvoga" is "prvog" (Hrvatski jezični portal:
    sklonidba rednih brojeva, "-og(a)", "-eg(a)")."""
    return word[:-1] if word.endswith(("oga", "ega")) else word


# -- Bulgarian -------------------------------------------------------------
# The teens and the tens 20 and 30 have a long and a contracted spelling:
# "единадесети" and "единайсети", "двадесети" and "двайсети".  en.wiktionary
# lists each contracted form as an alternative form of the long one.
_BG_CONTRACTIONS = (("надесет", "найсет"), ("двадесет", "двайсет"),
                    ("тридесет", "трийсет"))


def _bg_spelling(word: str) -> str:
    for long, short in _BG_CONTRACTIONS:
        if long in word:
            return word.replace(long, short)
    return word


# -- Slovene ---------------------------------------------------------------
# The hour one in the genitive plural of the clock: "ob enih" is at one, "pol
# enih" is 12:30 (Fran, SSKJ2: "en").
_SL_SPELLINGS = {"enih": "ena"}


fold_bg = make_fold("bg", spelling=_bg_spelling)
fold_cs = make_fold("cs", pre=_glue_cs_three_quarters,
                    spelling=lambda w: _CS_SPELLINGS.get(w, w))
fold_hr = make_fold("hr", spelling=_hr_spelling)
fold_pl = make_fold("pl")
fold_ru = make_fold("ru", pre=_split_ru_half)
fold_sk = make_fold("sk")
fold_sl = make_fold("sl", spelling=lambda w: _SL_SPELLINGS.get(w, w))
fold_uk = make_fold("uk")
