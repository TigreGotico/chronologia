# -*- coding: utf-8 -*-
"""Spelled-number folding for Filipino -- two whole numeral systems at once.

Filipino counts with two complete, living numeral vocabularies: the native
Austronesian set (``isa``, ``dalawa``, ``tatlo``, ...) and a Spanish-derived
set (``uno``, ``dos``, ``tres``, ...).  They are not registers of each other
and they are not in free variation; they are split by GRAMMATICAL SLOT, and a
single date or clock reading routinely draws on both.  Nothing else in the
tree needs two etymologically separate tables, so both live here side by side
with their own composition rules, which genuinely differ:

* the native set joins a tens word to its unit with the enclitic ``'t``
  ("dalawampu't dalawa" == 22) and multiplies with ``libo`` / ``daan``
  ("dalawang libo" == 2000);
* the Spanish set joins by juxtaposition below thirty ("beynte uno" == 21)
  and with ``y`` above it ("kuwarenta y singko" == 45, "trenta y otso" == 38).

No surface belongs to both tables, so a run is read by whichever table its
first word is in and the two never have to be told apart by context.

The clock is where the split bites.  The Spanish-lexified construction states
the hour as a bare cardinal after ``alas``/``ala`` and appends Spanish
minutes ("alas diyes trenta y singko ng gabi" == 22:35).  The native
construction states the hour as an ``ika-`` ORDINAL and counts native minutes
toward it in one of two directions -- ``makalipas`` ("after") for the first
half of the hour, ``bago`` ("before") for the second ("limang minuto
makalipas ang ika-anim ng umaga" == 06:05; "labinlimang minuto bago ang
ika-apat ng hapon" == 15:45).  The same ``ika-`` ordinal spells the day of a
date ("ika-24 ng Agosto"), which is why the ordinal pass folds to a bare
integer and lets the surrounding construction decide whether it read an hour
or a day.

Sources: en.wiktionary.org, Category:Tagalog cardinal numbers (each cardinal
and ordinal surface below is an entry there, checked individually); the
en.wiktionary.org ``ika-`` entry, which glosses the prefix both as the
ordinal former and as "used to express o'clock"; and en.wikipedia.org, "Date
and time notation in the Philippines", for the worked clock and date examples
and for the ``makalipas``/``bago`` split.

Deliberately absent, each because no per-word attestation was found rather
than because the value was in doubt: ``sesenta`` (60) and ``nobenta`` (90),
whose Wiktionary entries carry only a money noun and no numeral sense; the
variant spellings ``kwatro``, ``sais``, ``nwebe``, ``dyes``, ``bente`` and
``kwarenta``, which have no Tagalog entry under those spellings while
``kuwatro``, ``seis``, ``nuwebe``, ``diyes``, ``beynte`` and ``kuwarenta``
do; the ordinals ``ikadalawa`` and ``ikatatlo``, the attested second and
third being the suppletive ``ikalawa`` and ``ikatlo``; and ``una``, glossed
as the adjective "first" rather than as a numeral, and far too common a word
to fold to 1 on that basis.
"""
from __future__ import annotations

from typing import Callable, Dict, Optional, Tuple

from chronologia.extract.model import Token
from chronologia.extract.numfold_engine import reindex

_NATIVE: Dict[str, int] = {
    "isa": 1, "dalawa": 2, "tatlo": 3, "apat": 4, "lima": 5, "anim": 6,
    "pito": 7, "walo": 8, "siyam": 9, "sampu": 10,
    "labing-isa": 11, "labindalawa": 12, "labintatlo": 13, "labing-apat": 14,
    "labinlima": 15, "labing-anim": 16, "labimpito": 17, "labingwalo": 18,
    "labinsiyam": 19,
    "dalawampu": 20, "tatlumpu": 30, "apatnapu": 40, "limampu": 50,
    "animnapu": 60, "pitumpu": 70, "walumpu": 80, "siyamnapu": 90,
    "daan": 100, "sandaan": 100, "libo": 1000, "sanlibo": 1000,
}

_SPANISH: Dict[str, int] = {
    "uno": 1, "dos": 2, "tres": 3, "kuwatro": 4, "singko": 5,
    # seis is the Wiktionary spelling; sais is the one the worked clock
    # examples use ("alas sais singko ng umaga" == 06:05).
    "seis": 6, "sais": 6,
    "siyete": 7, "otso": 8, "nuwebe": 9, "diyes": 10, "onse": 11, "dose": 12,
    "trese": 13, "katorse": 14, "kinse": 15, "disiseis": 16,
    "disisiyete": 17, "disiotso": 18, "disinuwebe": 19,
    "beynte": 20, "treynta": 30, "trenta": 30, "kuwarenta": 40,
    "singkuwenta": 50, "setenta": 70, "otsenta": 80,
    "siyento": 100, "mil": 1000,
}

#: the ordinals written solid, exactly as Wiktionary spells them.  Eleventh
#: and fourteenth are absent because their solid spellings carry an internal
#: hyphen (ikalabing-isa, ikalabing-apat) that the tokenizer shears; they are
#: read by :data:`_ORD_TEEN_STEMS` instead.
_ORDINALS: Dict[str, int] = {
    "ikaisa": 1, "ikalawa": 2, "ikatlo": 3, "ikaapat": 4, "ikalima": 5,
    "ikaanim": 6, "ikapito": 7, "ikawalo": 8, "ikasiyam": 9, "ikasampu": 10,
    "ikalabindalawa": 12, "ikalabintatlo": 13, "ikalabinlima": 15,
    "ikadalawampu": 20,
}

#: "ikalabing-" + unit, the sheared half of the two attested hyphenated teen
#: ordinals.
_ORD_TEEN_PREFIX = "ikalabing"
_ORD_TEEN_STEMS: Dict[str, int] = {"isa": 11, "apat": 14}

#: the same shear on the CARDINAL teens: eleven, fourteen and sixteen are
#: spelled with an internal hyphen (labing-isa, labing-apat, labing-anim)
#: where twelve, thirteen, fifteen and seventeen through nineteen are solid,
#: so only these three arrive as two tokens.
_TEEN_PREFIX = "labing"
_TEEN_STEMS: Dict[str, int] = {"isa": 11, "apat": 14, "anim": 16}

#: the bare ``ika`` prefix left standing when the tokenizer shears the hyphen
#: of the separated spelling ("ika-apat" -> "ika", "apat").  Only stems whose
#: solid ordinal is attested are read this way, so "ika dalawa" and "ika
#: tatlo" stay unfolded -- the attested second and third are ikalawa/ikatlo.
_ORD_PREFIX = "ika"
_ORD_STEMS: Dict[str, int] = {
    w: _NATIVE[w] for w in
    ("isa", "apat", "lima", "anim", "pito", "walo", "sampu")
}

#: magnitude classes, shared by both systems: a run descends through them,
#: and only a hundred- or thousand-word may follow something smaller, as its
#: multiplier.  Two words of the same class never compose, which is what
#: keeps "alas seis singko" two tokens (hour six, minute five) instead of
#: one eleven.
_UNIT, _TEN, _HUNDRED, _SCALE = 1, 2, 3, 4


def _magnitude(value: int) -> int:
    if value >= 1000:
        return _SCALE
    if value >= 100:
        return _HUNDRED
    if value >= 20:
        return _TEN
    return _UNIT


def _composes(previous: int, following: int) -> bool:
    prev, nxt = _magnitude(previous), _magnitude(following)
    if nxt > prev:
        return nxt in (_HUNDRED, _SCALE)
    return nxt < prev


#: the enclitic "and" that joins a tens word to its unit in the native system
#: ("dalawampu't dalawa"), written onto the tens word.
_ENCLITIC = ("'t", "'y")


def _native_value(word: str) -> Optional[int]:
    """The native cardinal a surface spells, linker and enclitic included.

    A Filipino word takes the ligature ``-ng`` after a vowel and ``-g`` after
    ``n`` when it modifies what follows ("dalawa" -> "dalawang libo", "daan"
    -> "daang"), and the enclitic ``'t`` when it joins the next numeral
    ("dalawampu" -> "dalawampu't dalawa").  Both are inflections of the same
    cardinal, so both read back to it.
    """
    if word in _NATIVE:
        return _NATIVE[word]
    for clitic in _ENCLITIC:
        if word.endswith(clitic) and word[:-len(clitic)] in _NATIVE:
            return _NATIVE[word[:-len(clitic)]]
    if word.endswith("ng") and word[:-2] in _NATIVE:
        return _NATIVE[word[:-2]]
    if word.endswith("g") and word[:-1] in _NATIVE:
        return _NATIVE[word[:-1]]
    return None


def _numeric(tok: Token, value: int, end: Token = None) -> Token:
    return Token(text=str(value), raw=str(value), index=tok.index,
                 is_number=True, value=value, char_start=tok.char_start,
                 char_end=(end or tok).char_end)


def _ordinal_rewrite(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Fold an ``ika-`` ordinal to the bare integer it ranks.

    Runs before the cardinal passes so the ordinal claims its stem first.
    The result is a plain number because the two slots this construction
    fills -- the day of a date and the hour of a native clock reading -- both
    want an integer, and only the surrounding words tell them apart.
    """
    out, i, n, changed = [], 0, len(tokens), False
    while i < n:
        t = tokens[i]
        nxt = tokens[i + 1] if i + 1 < n else None
        if not t.is_number and t.text in _ORDINALS:
            out.append(_numeric(t, _ORDINALS[t.text]))
            i, changed = i + 1, True
            continue
        if (not t.is_number and t.text == _ORD_TEEN_PREFIX and nxt is not None
                and not nxt.is_number and nxt.text in _ORD_TEEN_STEMS):
            out.append(_numeric(t, _ORD_TEEN_STEMS[nxt.text], nxt))
            i, changed = i + 2, True
            continue
        if (not t.is_number and t.text == _TEEN_PREFIX and nxt is not None
                and not nxt.is_number
                and _strip_teen(nxt.text) in _TEEN_STEMS):
            out.append(_numeric(t, _TEEN_STEMS[_strip_teen(nxt.text)], nxt))
            i, changed = i + 2, True
            continue
        if not t.is_number and t.text == _ORD_PREFIX and nxt is not None:
            value = nxt.value if nxt.is_number else _ORD_STEMS.get(
                _strip_linker(nxt.text))
            if value is not None:
                out.append(_numeric(t, value, nxt))
                i, changed = i + 2, True
                continue
        out.append(t)
        i += 1
    return reindex(out) if changed else tokens


def _strip_teen(word: str) -> str:
    """The bare unit stem of a hyphenated teen's second half.

    Only the last element of a compound carries the ligature, so the stem
    arrives bare in "labing-anim na araw" and linked in "labing-isang araw".
    """
    for stem in _TEEN_STEMS:
        if word == stem or word == stem + "ng" or word == stem + "g":
            return stem
    return word


def _strip_linker(word: str) -> str:
    """The bare stem of a word carrying the modifying ligature.

    Only used to look an ordinal stem up: "ika-isang araw" spells its stem
    "isang", the same cardinal under the ligature.
    """
    if word in _ORD_STEMS:
        return word
    if word.endswith("ng") and word[:-2] in _ORD_STEMS:
        return word[:-2]
    if word.endswith("g") and word[:-1] in _ORD_STEMS:
        return word[:-1]
    return word


def read_native_run(words: Tuple[str, ...]) -> Optional[int]:
    """The value of a run of native cardinal surfaces.

    Additive within a magnitude group, multiplicative on ``daan`` (hundred)
    and ``libo`` (thousand), which closes its group into the total:
    "dalawang libo't dalawampu't dalawa" == 2022.
    """
    total = group = 0
    seen = False
    for word in words:
        value = _native_value(word)
        if value is None:
            return None
        if value == 1000:
            group = (group or 1) * 1000
            total += group
            group = 0
        elif value == 100:
            group = (group or 1) * 100
        else:
            group += value
        seen = True
    return total + group if seen else None


def read_spanish_run(words: Tuple[str, ...]) -> Optional[int]:
    """The value of a run of Spanish-derived cardinal surfaces.

    ``y`` is the joiner above thirty ("kuwarenta y singko" == 45) and is
    simply skipped; below thirty the words are juxtaposed ("beynte uno").
    """
    total = group = 0
    seen = False
    for word in words:
        if word == "y":
            continue
        value = _SPANISH.get(word)
        if value is None:
            return None
        if value == 1000:
            group = (group or 1) * 1000
            total += group
            group = 0
        elif value == 100:
            group = (group or 1) * 100
        else:
            group += value
        seen = True
    return total + group if seen else None


def _run_rewrite(tokens: Tuple[Token, ...], value_of, read_run,
                 joiner: Optional[str]) -> Tuple[Token, ...]:
    """Fold every maximal composing run one numeral table can read."""
    out, i, n, changed = [], 0, len(tokens), False
    while i < n:
        t = tokens[i]
        value = None if t.is_number else value_of(t.text)
        if value is None:
            out.append(t)
            i += 1
            continue
        j, last, words = i + 1, value, [t.text]
        while j < n and not tokens[j].is_number:
            word = tokens[j].text
            if word == joiner:
                # a bare joiner only extends the run if a readable numeral
                # follows it; a dangling "y" is left where it stands.
                after = tokens[j + 1] if j + 1 < n else None
                if (after is None or after.is_number
                        or value_of(after.text) is None
                        or not _composes(last, value_of(after.text))):
                    break
                words.append(word)
                j += 1
                continue
            nxt = value_of(word)
            if nxt is None or not _composes(last, nxt):
                break
            words.append(word)
            last = nxt
            j += 1
        total = read_run(tuple(words))
        if total is None:
            out.append(t)
            i += 1
            continue
        out.append(_numeric(t, total, tokens[j - 1]))
        i, changed = j, True
    return reindex(out) if changed else tokens


def _native_rewrite(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    return _run_rewrite(tokens, _native_value, read_native_run, None)


def _spanish_rewrite(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    return _run_rewrite(tokens, _SPANISH.get, read_spanish_run, "y")


def _compose(*passes: Callable) -> Callable:
    def run(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
        for p in passes:
            tokens = p(tokens)
        return tokens
    return run


#: the ordinal pass leads so an ``ika-`` hour or day claims its stem before a
#: cardinal pass could take that stem for a bare count; the two cardinal
#: tables then run in either order, sharing no surface.
fold_fil = _compose(_ordinal_rewrite, _native_rewrite, _spanish_rewrite)
