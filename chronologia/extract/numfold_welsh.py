# -*- coding: utf-8 -*-
"""Spelled-number folding pre-pass for Welsh.

The tokenizer only recognises *digit* runs as numbers; Welsh speech spells
them, so a run of spelled number-words is folded into a single digit
:class:`~chronologia.extract.model.Token` and a ``NUM``/``DAY``/``HOUR``/
``ORD`` slot then binds the same whether the writer typed ``3`` or the word.

Three facts make Welsh unlike every fold already here.

**Two numeral systems coexist.**  The traditional *vigesimal* series counts in
twenties -- ``pymtheg`` 15, ``deunaw`` 18, ``ugain`` 20, ``un ar hugain`` 21
("one on twenty"), ``hanner cant`` 50 ("half a hundred"), ``pedwar ugain`` 80
("four twenties") -- and the modern *decimal* series spells the same values as
``TENS deg UNIT`` (``un deg wyth`` 18, ``dau ddeg un`` 21).  Both are read
here, because the vigesimal one is the series a date or an age actually uses:
"the decimal system is widely used, but is rather uncommon for dates and ages"
(en.wikipedia.org, "Welsh numerals").  A decimal-only fold would miss the
temporal domain precisely.

**Two, three and four agree in gender with the noun they count** -- ``dau``/
``dwy``, ``tri``/``tair``, ``pedwar``/``pedair`` -- so both members of each
pair spell the same value, and :func:`counted_phrase` picks the one the unit
noun's gender demands.  Five and above never inflect; ``pump``/``chwech``/
``cant`` have a shortened form (``pum``, ``chwe``, ``can``) used *before a
noun*.

**Initial consonants mutate.**  A preceding word can change the FIRST letter
of the numeral: ``am dri o'r gloch`` (at three o'clock) and ``chwarter i
bedwar`` (quarter to four) show ``tri`` -> ``dri`` and ``pedwar`` -> ``bedwar``
after the soft-mutation triggers ``am`` and ``i``.  Every cardinal and ordinal
surface is therefore registered in its radical form *and* in the soft-mutated
form the regular table below derives, so the matcher sees one value whichever
surface the sentence carries.  Mutation of the *unit nouns* is a vocabulary
question and is answered in the ``.voc`` files, not here.

One further vigesimal shape has to be undone rather than read: above twenty
the numeral WRAPS the noun -- ``pum munud ar hugain`` is "twenty-five minutes",
five...on-twenty with ``munud`` sitting inside the numeral.
:func:`_split_vigesimal_rewrite` recognises that frame around a time-unit noun
and rebuilds the whole number in front of it.

Sources.  Cardinals and ordinals 0..100, both systems, with the masculine /
feminine pairs and the before-a-noun short forms: en.wiktionary.org,
"Appendix:Welsh numbers" (the language's own numeral table), corroborated by
en.wikipedia.org, "Welsh numerals" (vigesimal tens, the domain preference).
The soft-mutation table: en.wikipedia.org, "Welsh mutation".  The split
vigesimal and the mutated hour: en.wikibooks.org, "Welsh/Mynediad/Lesson 8"
(a full five-minute clock table).  Nothing is delegated to an external number
back-end.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Callable, Dict, Optional, Tuple

from chronologia.extract.model import Token
from chronologia.extract.numfold_engine import reindex

#: the two genders a Welsh numeral agrees in.
MASCULINE, FEMININE = "m", "f"
GENDERS = (MASCULINE, FEMININE)

# ---------------------------------------------------------------------------
# Soft mutation (treiglad meddal).  The radical -> soft column of the mutation
# table; the digraphs ch, dd, ff, ng, th are single Welsh letters that do not
# soft-mutate, so they must be tested BEFORE the single-letter rules or the
# "c" of "chwech" would be read as a mutable c.  Nasal and aspirate mutation
# are not applied to numerals: no numeral surface in a temporal construction
# was attested under either.
# Source: en.wikipedia.org, "Welsh mutation".
# ---------------------------------------------------------------------------
_SOFT_DIGRAPHS: Dict[str, str] = {"ll": "l", "rh": "r"}
_SOFT_INERT_DIGRAPHS = frozenset({"ch", "dd", "ff", "ng", "th"})
_SOFT_LETTERS: Dict[str, str] = {
    "p": "b", "t": "d", "c": "g", "b": "f", "d": "dd", "g": "", "m": "f"}


def soft_mutate(word: str) -> str:
    """The soft-mutated surface of ``word``, or ``word`` when it cannot mutate.

    Only the initial consonant changes; ``g`` disappears entirely
    (``gorffennaf`` -> ``orffennaf``) and a word opening on a vowel or on an
    inert digraph is returned unchanged.
    """
    head = word[:2]
    if head in _SOFT_DIGRAPHS:
        return _SOFT_DIGRAPHS[head] + word[2:]
    if head in _SOFT_INERT_DIGRAPHS:
        return word
    return _SOFT_LETTERS.get(word[:1], word[:1]) + word[1:]


def _mutate_phrase(phrase: str) -> str:
    """Soft-mutate a phrase, which touches its FIRST word only."""
    head, _, tail = phrase.partition(" ")
    return (soft_mutate(head) + " " + tail).strip() if tail else soft_mutate(head)


# ---------------------------------------------------------------------------
# The cardinal series.  ``UNIT_FORMS`` holds every surface of 0..10; the
# gendered pairs of 2..4 and the before-a-noun short forms of 5, 6 and 10 all
# spell the same value, so they live in one list per value.
# ---------------------------------------------------------------------------
#: value -> the surfaces of 0..10, radical.
_UNITS: Dict[int, Tuple[str, ...]] = {
    0: ("sero",),
    1: ("un",),
    2: ("dau", "dwy"),
    3: ("tri", "tair"),
    4: ("pedwar", "pedair"),
    5: ("pump", "pum"),
    6: ("chwech", "chwe"),
    7: ("saith",),
    8: ("wyth",),
    9: ("naw",),
    10: ("deg", "deng"),
}

#: the numeral form that agrees with a masculine / feminine counted noun.
#: Only 2, 3 and 4 have a pair; every other value is invariant.
GENDERED: Dict[int, Dict[str, str]] = {
    2: {MASCULINE: "dau", FEMININE: "dwy"},
    3: {MASCULINE: "tri", FEMININE: "tair"},
    4: {MASCULINE: "pedwar", FEMININE: "pedair"},
}

#: the shortened form each of these takes immediately BEFORE a noun
#: ("pum munud", "chwe mis"); the long form is the citation one.
BEFORE_NOUN: Dict[int, str] = {5: "pum", 6: "chwe", 10: "deng", 100: "can"}

#: the vigesimal words that are single lexemes rather than compounds.
_VIGESIMAL_WORDS: Dict[int, Tuple[str, ...]] = {
    12: ("deuddeg", "deuddeng"),
    15: ("pymtheg",),
    18: ("deunaw",),
    20: ("ugain",),
    40: ("deugain",),
    50: ("hanner cant",),
    60: ("trigain",),
    70: ("deg a thrigain",),
    80: ("pedwar ugain",),
    90: ("deg a phedwar ugain",),
    100: ("cant", "can"),
}

#: the vigesimal compounds built on "ar ddeg" (+10), "ar bymtheg" (+15) and
#: "ar hugain" (+20).  Transcribed row by row from the numeral appendix rather
#: than generated, because the series is not regular: 16 and 17 count onto
#: FIFTEEN, 18 is the lexical "deunaw" beside a feminine "tair ar bymtheg",
#: and 31 stacks both frames ("un ar ddeg ar hugain", one-on-ten-on-twenty).
_VIGESIMAL_COMPOUNDS: Dict[int, Tuple[str, ...]] = {
    11: ("un ar ddeg",),
    13: ("tri ar ddeg", "tair ar ddeg"),
    14: ("pedwar ar ddeg", "pedair ar ddeg"),
    16: ("un ar bymtheg",),
    17: ("dau ar bymtheg", "dwy ar bymtheg"),
    18: ("tair ar bymtheg",),
    19: ("pedwar ar bymtheg", "pedair ar bymtheg"),
    21: ("un ar hugain",),
    22: ("dau ar hugain", "dwy ar hugain"),
    23: ("tri ar hugain", "tair ar hugain"),
    24: ("pedwar ar hugain", "pedair ar hugain"),
    25: ("pump ar hugain", "pum ar hugain"),
    26: ("chwech ar hugain", "chwe ar hugain"),
    27: ("saith ar hugain",),
    28: ("wyth ar hugain",),
    29: ("naw ar hugain",),
    30: ("deg ar hugain",),
    31: ("un ar ddeg ar hugain",),
    32: ("deuddeg ar hugain", "deuddeng ar hugain"),
    33: ("tri ar ddeg ar hugain", "tair ar ddeg ar hugain"),
    34: ("pedwar ar ddeg ar hugain", "pedair ar ddeg ar hugain"),
    35: ("pymtheg ar hugain",),
    36: ("un ar bymtheg ar hugain",),
    37: ("dau ar bymtheg ar hugain", "dwy ar bymtheg ar hugain"),
    38: ("deunaw ar hugain",),
    39: ("pedwar ar bymtheg ar hugain", "pedair ar bymtheg ar hugain"),
}

#: the decimal tens, each "UNIT deg" with the ten soft-mutated after a
#: mutating unit ("dau ddeg" 20, "tri deg" 30).  The unit words are the
#: masculine ones; the appendix gives no feminine tens.
_DECIMAL_TENS: Dict[int, str] = {
    20: "dau ddeg", 30: "tri deg", 40: "pedwar deg", 50: "pum deg",
    60: "chwe deg", 70: "saith deg", 80: "wyth deg", 90: "naw deg"}

#: the vigesimal series above 39 is shipped only at the ROUND tens.  The
#: appendix's 41..99 compounds join their parts with "ac" before a consonant
#: ("deugain ac dau"), which the coordinator's own attested alternation
#: ("a" before a consonant, "ac" before a vowel) contradicts; rather than pick
#: a side, those compounds are omitted and only the decimal spelling of
#: 41..99 is read.  ``test_cy_omitted_surfaces`` pins the refusal.


def _cardinal_phrases() -> Dict[str, int]:
    """Every spelled cardinal surface 0..100 -> value, radical and mutated."""
    out: Dict[str, int] = {}

    def put(phrase: str, value: int) -> None:
        out.setdefault(phrase, value)
        out.setdefault(_mutate_phrase(phrase), value)

    for value, words in _UNITS.items():
        for w in words:
            put(w, value)
    for value, words in _VIGESIMAL_WORDS.items():
        for w in words:
            put(w, value)
    for value, words in _VIGESIMAL_COMPOUNDS.items():
        for w in words:
            put(w, value)
    # the decimal series: "un deg un" 11 .. "naw deg naw" 99, the tens bare
    for tens, head in _DECIMAL_TENS.items():
        put(head, tens)
        for rest in range(1, 10):
            for w in _UNITS[rest]:
                put(f"{head} {w}", tens + rest)
    for rest in range(1, 10):
        for w in _UNITS[rest]:
            put(f"un deg {w}", 10 + rest)
    return out


#: spelled cardinal surface (space-joined) -> value.
CARDINALS: Dict[str, int] = _cardinal_phrases()

# ---------------------------------------------------------------------------
# Ordinals.  1st is suppletive ("cyntaf", bearing no resemblance to "un"), 3rd
# and 4th carry the same masculine / feminine pair the cardinals do, and above
# ten the series compounds on the vigesimal frames exactly as the cardinals do
# ("unfed ar ddeg" 11th, "unfed ar ddeg ar hugain" 31st).  A day-of-month never
# exceeds 31, so the table stops there.
# Source: en.wiktionary.org, "Appendix:Welsh numbers", ordinal column.
# ---------------------------------------------------------------------------
_ORDINAL_FORMS: Dict[int, Tuple[str, ...]] = {
    1: ("cyntaf",),
    2: ("ail", "eilfed"),
    3: ("trydydd", "trydedd"),
    4: ("pedwerydd", "pedwaredd"),
    5: ("pumed",),
    6: ("chweched",),
    7: ("seithfed",),
    8: ("wythfed",),
    9: ("nawfed",),
    10: ("degfed",),
    11: ("unfed ar ddeg",),
    12: ("deuddegfed",),
    13: ("trydydd ar ddeg", "trydedd ar ddeg"),
    14: ("pedwerydd ar ddeg", "pedwaredd ar ddeg"),
    15: ("pymthegfed",),
    16: ("unfed ar bymtheg",),
    17: ("ail ar bymtheg", "eilfed ar bymtheg"),
    18: ("deunawfed",),
    19: ("pedwerydd ar bymtheg", "pedwaredd ar bymtheg"),
    20: ("ugeinfed",),
    21: ("unfed ar hugain",),
    22: ("ail ar hugain",),
    23: ("trydydd ar hugain", "trydedd ar hugain"),
    24: ("pedwerydd ar hugain", "pedwaredd ar hugain"),
    25: ("pumed ar hugain",),
    26: ("chweched ar hugain",),
    27: ("seithfed ar hugain",),
    28: ("wythfed ar hugain",),
    29: ("nawfed ar hugain",),
    30: ("degfed ar hugain",),
    31: ("unfed ar ddeg ar hugain",),
}

#: spelled ordinal surface (space-joined) -> value, radical and mutated.
ORDINALS: Dict[str, int] = {}
for _v, _forms in _ORDINAL_FORMS.items():
    for _f in _forms:
        ORDINALS.setdefault(_f, _v)
        ORDINALS.setdefault(_mutate_phrase(_f), _v)

#: the ordinal suffix a DIGIT day-of-month carries ("y 3ydd o Orffennaf", "yr
#: 11eg o Fai").  The tokenizer shears the digit from the letters, leaving a
#: fragment no other vocabulary claims; it is glued back onto the digit rather
#: than folded to a distinct value, since a numeric slot reads a plain digit
#: either way.  Source: en.wiktionary.org, "Appendix:Welsh numbers", the
#: "Ordinal abbreviation" column (1af, 2il, 3ydd, 4ydd, 5ed, 7fed, 11eg, 21ain).
_DIGIT_ORD_SUFFIX = frozenset({"af", "il", "ydd", "edd", "ed", "fed", "eg",
                               "ain"})

# ---------------------------------------------------------------------------
# Unit nouns.  ``gender`` drives the numeral's agreement; ``counted`` is the
# form used directly after a numeral, which for the year is the dedicated
# count form "blynedd" rather than either the singular "blwyddyn" or the plural
# "blynyddoedd".  Every form is the en.wiktionary.org headword line of the noun
# named beside it.
# ---------------------------------------------------------------------------
UNIT_FORMS: Dict[str, Dict[str, str]] = {
    # eiliad (masculine/feminine), plural eiliadau
    "second": {"gender": MASCULINE, "singular": "eiliad", "counted": "eiliad"},
    # munud (masculine/feminine), plural munudau
    "minute": {"gender": MASCULINE, "singular": "munud", "counted": "munud"},
    # awr (feminine), plural oriau
    "hour": {"gender": FEMININE, "singular": "awr", "counted": "awr"},
    # diwrnod (masculine), plural diwrnodau -- the COUNTABLE day, the one a
    # numeral takes; "dydd" is the uncountable daytime and the weekday head.
    "day": {"gender": MASCULINE, "singular": "diwrnod",
            "counted": "diwrnod"},
    # wythnos (feminine), plural wythnosau
    "week": {"gender": FEMININE, "singular": "wythnos", "counted": "wythnos"},
    # mis (masculine), plural misoedd
    "month": {"gender": MASCULINE, "singular": "mis", "counted": "mis"},
    # blwyddyn (feminine), plural blynyddoedd, count form blynedd
    "year": {"gender": FEMININE, "singular": "blwyddyn",
             "counted": "blynedd"},
    # degawd (masculine/feminine), plural degawdau
    "decade": {"gender": MASCULINE, "singular": "degawd", "counted": "degawd"},
    # canrif (feminine), plural canrifoedd
    "century": {"gender": FEMININE, "singular": "canrif", "counted": "canrif"},
}

#: the counted noun's initial mutates after some numerals and not others.  Two
#: is a soft-mutation trigger ("dwy flynedd", "dau fis"); five, seven, eight,
#: nine, ten, twelve and a hundred take the NASAL mutation on this one noun
#: ("pum mlynedd"), which is why the year has three surfaces.  Only the
#: numerals whose effect on a time-unit noun was attested in running text are
#: listed; everything else leaves the noun radical.
#: Sources: en.wiktionary.org "blwyddyn" ("dwy flynedd", "pum mlynedd");
#: cy.wikipedia.org running text ("dau fis", "tri diwrnod", "tair blynedd").
_SOFT_AFTER = frozenset({2})
_NASAL_YEAR_AFTER = frozenset({5, 7, 8, 9, 10, 12, 100})
#: b -> m is the nasal-mutation cell the year's count form lands in.
_NASAL_YEAR = {"blynedd": "mlynedd"}


def numeral_surface(n: int, gender: str = MASCULINE,
                    before_noun: bool = False) -> str:
    """The spelled surface of ``n``, agreeing in ``gender``.

    Agreement reaches 2, 3 and 4 only; every other value is invariant, so the
    gender argument is inert for them.  ``before_noun`` selects the shortened
    form five, six, ten and a hundred take immediately before a noun.

    Defined over the vigesimal series the numeral appendix attests: 0..39, the
    round tens to 90 and 100.  A value with no attested vigesimal spelling is
    refused rather than composed from the appendix's "ac"-joined compounds.
    """
    if gender not in GENDERS:
        raise ValueError(f"unknown gender {gender!r}")
    n = int(n)
    if before_noun and n in BEFORE_NOUN:
        return BEFORE_NOUN[n]
    if n in GENDERED:
        return GENDERED[n][gender]
    if n in _UNITS:
        return _UNITS[n][0]
    if n in _VIGESIMAL_COMPOUNDS:
        forms = _VIGESIMAL_COMPOUNDS[n]
        return forms[1] if gender == FEMININE and len(forms) > 1 else forms[0]
    if n in _VIGESIMAL_WORDS:
        return _VIGESIMAL_WORDS[n][0]
    raise ValueError(f"no attested Welsh vigesimal surface for {n}")


def decimal_surface(n: int, gender: str = MASCULINE) -> str:
    """The modern decimal spelling of ``n`` (0..99).

    The decimal series has no gendered tens, so agreement reaches only a
    trailing 2, 3 or 4 ("dau ddeg dwy" 22 feminine).
    """
    if gender not in GENDERS:
        raise ValueError(f"unknown gender {gender!r}")
    n = int(n)
    if n < 0 or n > 99:
        raise ValueError(f"no decimal Welsh surface for {n}")
    if n <= 10:
        return GENDERED[n][gender] if n in GENDERED else _UNITS[n][0]
    tens, rest = divmod(n, 10)
    head = "un deg" if tens == 1 else _DECIMAL_TENS[tens * 10]
    if rest == 0:
        return head
    tail = GENDERED[rest][gender] if rest in GENDERED else _UNITS[rest][0]
    return f"{head} {tail}"


def unit_surface(n: int, kind: str) -> str:
    """The surface of unit ``kind`` counted by ``n``.

    A Welsh numeral is followed by the SINGULAR (or, for the year, its
    dedicated count form), never a plural, and the numeral may mutate that
    noun's initial: soft after two, nasal after the numerals the year's count
    form was attested under.
    """
    forms = UNIT_FORMS[kind]
    word = forms["counted"] if n != 1 else forms["singular"]
    n = abs(int(n))
    if n in _SOFT_AFTER:
        return soft_mutate(word)
    if kind == "year" and n in _NASAL_YEAR_AFTER:
        return _NASAL_YEAR[word]
    return word


def counted_phrase(n: int, kind: str) -> str:
    """``n`` spelled vigesimally and agreeing with unit ``kind``."""
    gender = UNIT_FORMS[kind]["gender"]
    return f"{numeral_surface(n, gender, before_noun=True)} " \
           f"{unit_surface(n, kind)}"


# ---------------------------------------------------------------------------
# The rewriting passes
# ---------------------------------------------------------------------------
def _numeric(tok: Token, value: int, end: Token = None) -> Token:
    return Token(text=str(value), raw=str(value), index=tok.index,
                 is_number=True, value=value, char_start=tok.char_start,
                 char_end=(end or tok).char_end)


#: the longest spelled surface, in tokens, either table holds.
_MAX_SPAN = max(len(p.split()) for p in (*CARDINALS, *ORDINALS))


def _phrase_rewrite(tokens: Tuple[Token, ...],
                    table: Dict[str, int]) -> Tuple[Token, ...]:
    """Fold the LONGEST spelled surface in ``table`` starting at each token.

    Longest-first is what keeps a compound whole: "deg ar hugain" is thirty,
    not ten followed by a stranded "ar hugain", and "un deg wyth" is eighteen
    rather than one and eight.
    """
    out, i, n, changed = [], 0, len(tokens), False
    while i < n:
        if tokens[i].is_number:
            out.append(tokens[i])
            i += 1
            continue
        for span in range(min(_MAX_SPAN, n - i), 0, -1):
            window = tokens[i:i + span]
            if any(t.is_number for t in window):
                continue
            value = table.get(" ".join(t.text for t in window))
            if value is not None:
                out.append(_numeric(window[0], value, window[-1]))
                i, changed = i + span, True
                break
        else:
            out.append(tokens[i])
            i += 1
    return reindex(out) if changed else tokens


def _cardinal_rewrite(tokens):
    return _phrase_rewrite(tokens, CARDINALS)


def _ordinal_rewrite(tokens):
    return _phrase_rewrite(tokens, ORDINALS)


def _digit_ordinal_rewrite(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Glue a digit back to its ordinal-suffix fragment ("3ydd", "11eg").

    Gated on the two being written SOLID -- no gap at all between the digit
    and the letters -- so an ordinary word that happens to spell a suffix is
    never swallowed off a neighbouring number.
    """
    out, i, n, changed = [], 0, len(tokens), False
    while i < n:
        t = tokens[i]
        nxt = tokens[i + 1] if i + 1 < n else None
        if (t.is_number and nxt is not None and not nxt.is_number
                and nxt.text in _DIGIT_ORD_SUFFIX
                and t.char_end is not None and nxt.char_start is not None
                and nxt.char_start == t.char_end):
            out.append(replace(t, raw=t.raw + nxt.raw, char_end=nxt.char_end))
            i, changed = i + 2, True
            continue
        out.append(t)
        i += 1
    return reindex(tuple(out)) if changed else tokens


#: the time-unit nouns a split vigesimal may wrap.  Kept to this closed set --
#: rather than any word at all -- so the frame is only undone where the result
#: is certainly a counted time expression.
_SPLIT_NOUNS = frozenset(
    {"eiliad", "eiliadau", "munud", "funud", "munudau", "awr", "oriau",
     "diwrnod", "ddiwrnod", "dydd", "ddydd", "wythnos", "mis", "fis",
     "blwyddyn", "flwyddyn", "blynedd", "flynedd", "mlynedd"})

#: the "ar TENS" tail of a split vigesimal and the value it adds.
_SPLIT_TAIL: Dict[str, int] = {"hugain": 20, "ddeg": 10, "bymtheg": 15}


def _split_vigesimal_rewrite(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Rebuild a vigesimal numeral that WRAPS its noun.

    Welsh counts above twenty by putting the noun inside the numeral: "pum
    munud ar hugain" is twenty-five minutes, not five minutes with a trailing
    "on twenty".  The tail is folded back into the leading count so the number
    reaches the matcher whole and the noun keeps its slot.
    """
    out, i, n, changed = [], 0, len(tokens), False
    while i < n:
        t = tokens[i]
        if (t.is_number and i + 3 < n and tokens[i + 1].text in _SPLIT_NOUNS
                and tokens[i + 2].text == "ar"
                and tokens[i + 3].text in _SPLIT_TAIL):
            out.append(_numeric(t, t.value + _SPLIT_TAIL[tokens[i + 3].text],
                                tokens[i + 3]))
            out.append(replace(tokens[i + 1], index=tokens[i + 1].index))
            i, changed = i + 4, True
            continue
        out.append(t)
        i += 1
    return reindex(out) if changed else tokens


def _compose(*passes: Callable) -> Callable:
    def run(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
        for p in passes:
            tokens = p(tokens)
        return tokens
    return run


#: the digit-ordinal glue runs first so "3ydd" is one token before anything
#: else could read the bare "3"; the spelled ordinals then lead the cardinals
#: (their compounds share the "ar ddeg" / "ar hugain" frames, and only the
#: ordinal table should claim "unfed ar ddeg"); the split-vigesimal pass runs
#: last because it needs the leading count already folded to a digit.
fold_cy = _compose(_digit_ordinal_rewrite, _ordinal_rewrite,
                   _cardinal_rewrite, _split_vigesimal_rewrite)
