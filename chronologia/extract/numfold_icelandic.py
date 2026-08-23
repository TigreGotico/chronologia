# -*- coding: utf-8 -*-
"""Spelled-number folding pre-pass for Icelandic.

The tokenizer only recognises *digit* runs as numbers; Icelandic speech
spells them, so a maximal run of spelled number-words is folded into a
single digit :class:`~chronologia.extract.model.Token` and a ``NUM``/
``DAY``/``HOUR``/``ORD`` slot then binds the same whether the writer typed
``3`` or the word.

Icelandic numerals are not governed by the counting rules the Baltic and
Slavic folds implement.  **Only 1 to 4 inflect**, and they inflect as
ordinary strong adjectives -- agreeing in case, gender and number with the
noun they count, exactly as any attributive modifier would: "tveir dagar"
(masculine), "tvaer vikur" (feminine), "tvo ar" (neuter), "fyrir tveimur
arum" (dative).  Five and above never inflect at all.  :data:`NUMERAL_FORMS`
is that agreement table and :func:`numeral_surface` applies it; there is no
last-digit switch and no paucal.

A compound 21..99 is ``TENS og UNIT`` ("tuttugu og einn"), 101..999
``hundrad og ...`` -- the tens and the hundred never inflect, and only the
final element does, so :func:`inflecting_element` reads the agreement off
the last digit while a teen (11..19, a single invariant word) has none.

Sources.  Cardinals 0..999 and ordinals 1st..99th: en.wiktionary.org,
"Appendix:Icelandic numerals" (the language's own numeral table), corroborated
per word by the individual en.wiktionary.org entries in Category:Icelandic
cardinal numbers / Category:Icelandic ordinal numbers.  Declension tables of
einn, tveir, thrir, fjorir and of every unit noun: the en.wiktionary.org
declension table on each headword.  Nothing is delegated to an external
number back-end.
"""
from __future__ import annotations

from typing import Callable, Dict, Optional, Tuple

from chronologia.extract.model import Token
from chronologia.extract.numfold_engine import reindex

#: the four cases Icelandic inflects for.
NOMINATIVE, ACCUSATIVE, DATIVE, GENITIVE = "nom", "acc", "dat", "gen"
#: the three genders a numeral and its counted noun agree in.
MASCULINE, FEMININE, NEUTER = "m", "f", "n"

CASES = (NOMINATIVE, ACCUSATIVE, DATIVE, GENITIVE)
GENDERS = (MASCULINE, FEMININE, NEUTER)


def _paradigm(nom, acc, dat, gen) -> Dict[Tuple[str, str], str]:
    """Build a (case, gender) -> surface map from four gender triples."""
    return {(case, gender): row[i]
            for case, row in zip(CASES, (nom, acc, dat, gen))
            for i, gender in enumerate(GENDERS)}


#: The numerals that inflect, as (case, gender) -> surface.  "einn" is a
#: singular paradigm (it counts one thing); "tveir", "thrir" and "fjorir" are
#: plural-only.  Each row is masculine, feminine, neuter.
#: Source: the en.wiktionary.org declension table on einn, tveir, thrir,
#: fjorir (strong/indefinite, numeral sense).
NUMERAL_FORMS: Dict[int, Dict[Tuple[str, str], str]] = {
    1: _paradigm(("einn", "ein", "eitt"),
                 ("einn", "eina", "eitt"),
                 ("einum", "einni", "einu"),
                 ("eins", "einnar", "eins")),
    2: _paradigm(("tveir", "tvær", "tvö"),
                 ("tvo", "tvær", "tvö"),
                 ("tveimur", "tveimur", "tveimur"),
                 ("tveggja", "tveggja", "tveggja")),
    3: _paradigm(("þrír", "þrjár", "þrjú"),
                 ("þrjá", "þrjár", "þrjú"),
                 ("þremur", "þremur", "þremur"),
                 ("þriggja", "þriggja", "þriggja")),
    4: _paradigm(("fjórir", "fjórar", "fjögur"),
                 ("fjóra", "fjórar", "fjögur"),
                 ("fjórum", "fjórum", "fjórum"),
                 ("fjögurra", "fjögurra", "fjögurra")),
}

#: alternative datives the same tables list beside the primary form.
_DATIVE_VARIANTS = {2: "tveim", 3: "þrem"}
#: the colloquial genitive of four the same table lists.
_GENITIVE_VARIANTS = {4: "fjögra"}

#: the invariant cardinals -- everything from five up, plus zero.
_INVARIANT: Dict[int, str] = {
    0: "núll", 5: "fimm", 6: "sex", 7: "sjö", 8: "átta", 9: "níu", 10: "tíu",
    11: "ellefu", 12: "tólf", 13: "þrettán", 14: "fjórtán", 15: "fimmtán",
    16: "sextán", 17: "sautján", 18: "átján", 19: "nítján",
}
#: the seventeen variant of the same table, listed there beside "sautjan".
_INVARIANT_VARIANTS = {17: "seytján"}

#: the tens, none of which inflect.
TENS: Dict[int, str] = {
    20: "tuttugu", 30: "þrjátíu", 40: "fjörutíu", 50: "fimmtíu", 60: "sextíu",
    70: "sjötíu", 80: "áttatíu", 90: "níutíu",
}

#: "hundrad" is a neuter noun and takes the neuter numeral as its multiplier
#: ("tvo hundrud"); its own plural is "hundrud".
_HUNDRED = {"hundrað", "hundruð"}
#: "thusund" likewise ("eitt thusund", "thusund").
_SCALE = {"þúsund": 1000}
#: the coordinator that joins a compound numeral ("tuttugu og einn").
_AND = "og"


# ---------------------------------------------------------------------------
# Unit nouns.  The noun's own case is imposed by the construction ("fyrir" +
# dative for an offset back, "eftir" + accusative for one forward); its number
# is singular for a count of one and plural otherwise.  Every form below is
# the indefinite column of the en.wiktionary.org declension table on the
# headword named beside it.
# ---------------------------------------------------------------------------
def _noun(gender, sg, pl) -> Dict[str, str]:
    forms = {case: sg[i] for i, case in enumerate(CASES)}
    forms.update({case + "_pl": pl[i] for i, case in enumerate(CASES)})
    forms["gender"] = gender
    return forms


UNIT_FORMS: Dict[str, Dict[str, str]] = {
    # sekunda (feminine)
    "second": _noun(FEMININE,
                    ("sekúnda", "sekúndu", "sekúndu", "sekúndu"),
                    ("sekúndur", "sekúndur", "sekúndum", "sekúndna")),
    # minuta (feminine)
    "minute": _noun(FEMININE,
                    ("mínúta", "mínútu", "mínútu", "mínútu"),
                    ("mínútur", "mínútur", "mínútum", "mínútna")),
    # klukkustund (feminine)
    "hour": _noun(FEMININE,
                  ("klukkustund", "klukkustund", "klukkustund", "klukkustundar"),
                  ("klukkustundir", "klukkustundir", "klukkustundum",
                   "klukkustunda")),
    # dagur (masculine), with the u-umlaut dative plural "dogum"
    "day": _noun(MASCULINE,
                 ("dagur", "dag", "degi", "dags"),
                 ("dagar", "daga", "dögum", "daga")),
    # vika (feminine)
    "week": _noun(FEMININE,
                  ("vika", "viku", "viku", "viku"),
                  ("vikur", "vikur", "vikum", "vikna")),
    # manudur (masculine), genitive singular on the broken stem "manadar"
    "month": _noun(MASCULINE,
                   ("mánuður", "mánuð", "mánuði", "mánaðar"),
                   ("mánuðir", "mánuði", "mánuðum", "mánaða")),
    # ar (neuter), nominative and accusative alike in both numbers
    "year": _noun(NEUTER,
                  ("ár", "ár", "ári", "árs"),
                  ("ár", "ár", "árum", "ára")),
    # aratugur (masculine)
    "decade": _noun(MASCULINE,
                    ("áratugur", "áratug", "áratug", "áratugar"),
                    ("áratugir", "áratugi", "áratugum", "áratuga")),
    # old (feminine), whose plural stem loses the u-umlaut: "aldir", "aldar"
    "century": _noun(FEMININE,
                     ("öld", "öld", "öld", "aldar"),
                     ("aldir", "aldir", "öldum", "alda")),
    # arthusund (neuter)
    "millennium": _noun(NEUTER,
                        ("árþúsund", "árþúsund", "árþúsundi", "árþúsunds"),
                        ("árþúsund", "árþúsund", "árþúsundum", "árþúsunda")),
}


def inflecting_element(n: int) -> Optional[int]:
    """The final element of ``n`` when it inflects, else ``None``.

    Only 1..4 inflect, and only as the LAST element of a compound, so 21 and
    104 inflect on their one while 11..19 -- each a single invariant word --
    inflect not at all.
    """
    n = abs(int(n))
    if 11 <= n % 100 <= 19:
        return None
    last = n % 10
    return last if 1 <= last <= 4 else None


def numeral_surface(n: int, gender: str = NEUTER,
                    case: str = NOMINATIVE) -> str:
    """The spelled surface of ``n`` agreeing in ``gender`` and ``case``.

    Agreement reaches only the final 1..4 of the numeral; everything else is
    invariant, so the gender and case arguments are inert for 5..10, the
    teens, the tens and the hundreds.

    Defined over exactly the shapes the numeral table attests: 0..99, the
    round hundreds ("tvö hundruð"), and 101..199 ("hundrað og einn").  A
    numeral that would need two coordinators ("tvö hundruð og fjörutíu og
    sjö") is refused rather than composed, because no source consulted shows
    one.
    """
    if gender not in GENDERS:
        raise ValueError(f"unknown gender {gender!r}")
    if case not in CASES:
        raise ValueError(f"unknown case {case!r}")
    n = int(n)
    if n == 100:
        return "hundrað"
    if 100 < n < 200:
        return f"hundrað {_AND} {numeral_surface(n - 100, gender, case)}"
    if 200 <= n <= 900 and n % 100 == 0:
        return numeral_surface(n // 100, NEUTER) + " hundruð"
    if not 0 <= n <= 99:
        raise ValueError(f"no attested Icelandic surface for {n}")
    if n >= 20:
        tens, rest = divmod(n, 10)
        head = TENS[tens * 10]
        if rest == 0:
            return head
        return f"{head} {_AND} {numeral_surface(rest, gender, case)}"
    if n in NUMERAL_FORMS:
        return NUMERAL_FORMS[n][(case, gender)]
    return _INVARIANT[n]


def unit_surface(n: int, kind: str, case: str = NOMINATIVE) -> str:
    """The surface of unit ``kind`` counted by ``n``, in ``case``.

    A count of one takes the singular, anything else the plural.  A compound
    ending in one ("tuttugu og einn dagur") is refused: no source consulted
    attests whether the noun stays singular there, and guessing it would put
    an unattested surface into a test's gold.
    """
    if case not in CASES:
        raise ValueError(f"unknown case {case!r}")
    forms = UNIT_FORMS[kind]
    n = abs(int(n))
    if n == 1:
        return forms[case]
    if inflecting_element(n) == 1:
        raise ValueError(
            f"the number of a noun counted by {n} is not attested; only a "
            f"bare 1 takes the singular here")
    return forms[case + "_pl"]


def counted_phrase(n: int, kind: str, case: str = NOMINATIVE) -> str:
    """``n`` spelled out and agreeing with unit ``kind`` in ``case``."""
    gender = UNIT_FORMS[kind]["gender"]
    return f"{numeral_surface(n, gender, case)} {unit_surface(n, kind, case)}"


# ---------------------------------------------------------------------------
# Ordinals.  Every ordinal but "annar" (2nd) is a weak adjective whose three
# distinct endings are -i (masculine nominative), -a (masculine and neuter
# oblique, feminine nominative) and -u (feminine oblique, plural).  A date
# names an elided masculine "dagur", so the two masculine forms are the ones
# a day-of-month reads.  A compound inflects its LAST element only
# ("tuttugasti og fyrsti").
#
# "annar" is deliberately absent: it is the ordinary Icelandic word for
# "another"/"the other", so claiming every "annar" as the digit 2 would
# rewrite plain prose into a number.
# ---------------------------------------------------------------------------
_ORDINAL_LEMMAS: Dict[int, str] = {
    1: "fyrsti", 3: "þriðji", 4: "fjórði", 5: "fimmti", 6: "sjötti",
    7: "sjöundi", 8: "áttundi", 9: "níundi", 10: "tíundi", 11: "ellefti",
    12: "tólfti", 13: "þrettándi", 14: "fjórtándi", 15: "fimmtándi",
    16: "sextándi", 17: "sautjándi", 18: "átjándi", 19: "nítjándi",
}
#: the tens ordinals, which open a compound day ("thritugasti og fyrsti")
_ORDINAL_TENS: Dict[int, str] = {20: "tuttugasti", 30: "þrítugasti"}

#: weak masculine ordinal surface -> value, nominative and oblique alike
ORDINALS: Dict[str, int] = {}
for _v, _lemma in {**_ORDINAL_LEMMAS, **_ORDINAL_TENS}.items():
    ORDINALS[_lemma] = _v
    ORDINALS[_lemma[:-1] + "a"] = _v

#: the tens element of a compound ordinal, keyed by both its weak forms
_ORDINAL_TENS_SURFACES: Dict[str, int] = {
    form: value
    for value, lemma in _ORDINAL_TENS.items()
    for form in (lemma, lemma[:-1] + "a")}
#: the unit element a compound ordinal may close on (1, 3..9)
_ORDINAL_UNITS: Dict[str, int] = {
    form: value
    for value, lemma in _ORDINAL_LEMMAS.items() if value <= 9
    for form in (lemma, lemma[:-1] + "a")}


# ---------------------------------------------------------------------------
# The run reader
# ---------------------------------------------------------------------------
CARDINALS: Dict[str, int] = {}
for _v, _w in _INVARIANT.items():
    CARDINALS[_w] = _v
for _v, _w in _INVARIANT_VARIANTS.items():
    CARDINALS[_w] = _v
for _v, _forms in NUMERAL_FORMS.items():
    for _w in _forms.values():
        CARDINALS[_w] = _v
for _v, _w in _DATIVE_VARIANTS.items():
    CARDINALS[_w] = _v
for _v, _w in _GENITIVE_VARIANTS.items():
    CARDINALS[_w] = _v
for _v, _w in TENS.items():
    CARDINALS[_w] = _v
for _w in _HUNDRED:
    CARDINALS[_w] = 100
CARDINALS.update(_SCALE)


def read_run(text: str) -> Optional[int]:
    """Read the value of a joined run of Icelandic number-word surfaces.

    Additive over units, teens and tens; "hundrad" multiplies the group
    accumulated so far and "thusund" multiplies it and closes it into the
    running total.  The coordinator "og" joins the elements of a compound and
    contributes nothing.  Returns ``None`` when a word is not a number-word,
    so the fold leaves the run alone rather than committing a partial reading.
    """
    total = 0
    group = 0
    seen = False
    for word in text.split():
        if word == _AND:
            continue
        if word.isdigit():
            group += int(word)
            seen = True
            continue
        if word in _SCALE:
            group = (group or 1) * _SCALE[word]
            total += group
            group = 0
            seen = True
            continue
        if word in _HUNDRED:
            group = (group or 1) * 100
            seen = True
            continue
        value = CARDINALS.get(word)
        if value is None:
            return None
        group += value
        seen = True
    return total + group if seen else None


def _numeric(tok: Token, value: int, end: Token = None) -> Token:
    return Token(text=str(value), raw=str(value), index=tok.index,
                 is_number=True, value=value, char_start=tok.char_start,
                 char_end=(end or tok).char_end)


#: the magnitude class of a cardinal surface, which is what licenses one
#: number-word to continue the run another opened.  A composed Icelandic
#: numeral descends through the classes -- a lower class may follow a higher
#: one ("tuttugu og einn", "hundrad og fimm") and a HUNDRED or SCALE word may
#: follow a lower one as its multiplier ("fimm hundrud", "eitt thusund").  Two
#: words of the SAME class never compose, which is what keeps the clock's
#: "fimm minutur i thrju" from collapsing into one number once the unit noun
#: between them is out of the way.
_UNIT_CLASS, _TEN_CLASS, _HUNDRED_CLASS, _SCALE_CLASS = 1, 2, 3, 4


_TENS_SURFACES = frozenset(TENS.values())


def _magnitude(word: str) -> int:
    if word in _SCALE:
        return _SCALE_CLASS
    if word in _HUNDRED:
        return _HUNDRED_CLASS
    if word in _TENS_SURFACES:
        return _TEN_CLASS
    return _UNIT_CLASS


def _composes(previous: str, following: str) -> bool:
    prev, nxt = _magnitude(previous), _magnitude(following)
    if nxt > prev:
        return nxt in (_HUNDRED_CLASS, _SCALE_CLASS)
    return nxt < prev


def _cardinal_rewrite(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Fold a well-formed run of spelled cardinals into one digit token."""
    out, i, n, changed = [], 0, len(tokens), False
    while i < n:
        t = tokens[i]
        if t.is_number or t.text not in CARDINALS:
            out.append(t)
            i += 1
            continue
        j, previous = i + 1, t.text
        while j < n:
            # "og" only continues the run when a composing number-word follows
            k = j + 1 if tokens[j].text == _AND else j
            if (k >= n or tokens[k].is_number
                    or tokens[k].text not in CARDINALS
                    or not _composes(previous, tokens[k].text)):
                break
            previous, j = tokens[k].text, k + 1
        value = read_run(" ".join(tok.text for tok in tokens[i:j]))
        if value is None:
            out.append(t)
            i += 1
            continue
        out.append(_numeric(t, value, tokens[j - 1]))
        i, changed = j, True
    return reindex(out) if changed else tokens


def _ordinal_rewrite(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Fold a spelled ordinal, its "TENS og UNIT" compound included."""
    out, i, n, changed = [], 0, len(tokens), False
    while i < n:
        t = tokens[i]
        if not t.is_number and t.text in _ORDINAL_TENS_SURFACES and i + 2 < n:
            unit = _ORDINAL_UNITS.get(tokens[i + 2].text)
            if tokens[i + 1].text == _AND and unit is not None:
                out.append(_numeric(t, _ORDINAL_TENS_SURFACES[t.text] + unit,
                                    tokens[i + 2]))
                i, changed = i + 3, True
                continue
        if not t.is_number and t.text in ORDINALS:
            out.append(_numeric(t, ORDINALS[t.text]))
            i, changed = i + 1, True
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


fold_is = _compose(_ordinal_rewrite, _cardinal_rewrite)
