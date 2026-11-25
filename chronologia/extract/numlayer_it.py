"""Italian date words over the numtag number layer."""
from __future__ import annotations

from typing import Tuple

from chronologia.extract.model import Token
from chronologia.extract.numlayer import (collapse_marked_h_clock,
                                          collapse_phrase, elision_split,
                                          glue_abbreviations)
from chronologia.extract.numlayer_romance import (Claims, DateWords,
                                                  count_words, fold,
                                                  locale_words)

_WORDS = DateWords(
    lang="it",
    fractions=locale_words("it", "clock_fraction_") | {"quarti"},
    definite=frozenset({"il", "lo", "la", "i", "gli", "le", "l"}),
    quarter_articles=frozenset({"un"}),
    articles_are_words=True,
    clock_prepositions=frozenset({"alle", "all"}),
    unit_nouns=frozenset({"secondi"}),
    unit_ordinals=frozenset({"secondo"}),
    counts=count_words("it", locale_words("it", "marker_since")))

#: The proclitics that elide before a vowel: "l'undici", "dell'anno".
_PROCLITICS = frozenset({"l", "un", "d", "dell", "all", "nell", "dall",
                         "sull", "quest", "quell", "c"})
#: The markers before which the hour-letter clock folds: "alle 21h30".
_CLOCK_MARKERS = frozenset({"alle", "all", "alla", "a", "ad", "ore", "ora"})
_PHRASES = [
    (["avanti", "cristo"], "ac"), (["dopo", "cristo"], "dc"),
    (["avanti", "l", "era", "volgare"], "ac"), (["era", "volgare"], "dc"),
    # the dotted abbreviations "a.e.v."/"e.v." of the areligious era formula
    # (https://it.wikipedia.org/wiki/Era_volgare) have no rows.  The tokenizer
    # shatters them on their dots and this table matches on token text alone,
    # so a row would equally match the same letters written apart: "a", "e"
    # and "v" are an ordinary preposition, the conjunction "and" and a Roman
    # numeral, and "1500 a e V" or "il 3 e V maggio" would read as a dated era
    # marker -- a sign flip on ordinary Italian.  The spelled-out
    # "(avanti l') era volgare" above carries the same meaning unambiguously.
    (["altro", "ieri"], "altroieri"), (["avanti", "ieri"], "avantieri"),
    (["dopo", "domani"], "dopodomani"),
    (["fine", "settimana"], "finesettimana"),
]
#: The di-family prepositions that introduce the date after "prima":
#: "prima di gennaio", "prima del 5 aprile".
_OFFSET_PREP = frozenset({"di", "del", "dello", "della", "dell", "dei",
                          "degli", "delle", "d"})


def split_elisions(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """The Italian ``pre_hook``: split an elided proclitic from its word
    ("l'undici" gives "l" and "undici"), so the number layer finds the
    number in the word."""
    return elision_split(tokens, _PROCLITICS)


def _prima(tokens: Tuple[Token, ...]) -> Claims:
    """Claim "prima" where it is the marker "before", not the ordinal.

    "prima" is the feminine ordinal "first" and the marker "before".  It is
    the marker before a di-family preposition ("prima di gennaio"), before a
    written year ("prima 2030"), and after a count and its unit ("tre giorni
    prima del 5 aprile").  Everywhere else it is the ordinal: "la prima
    settimana".
    """
    claimed = set()
    for i, t in enumerate(tokens):
        if t.text != "prima" or t.mention is None:
            continue
        nxt = tokens[i + 1] if i + 1 < len(tokens) else None
        prev = tokens[i - 1] if i > 0 else None
        prev2 = tokens[i - 2] if i > 1 else None
        if ((nxt is not None and nxt.text in _OFFSET_PREP)
                or (nxt is not None and nxt.is_number and nxt.raw is not None
                    and len(nxt.raw) == 4 and nxt.raw.isdigit())
                or (prev is not None and prev.mention is None
                    and not prev.is_number and prev2 is not None
                    and (prev2.is_number or prev2.mention is not None))):
            claimed.add(i)
    return claimed, set(), {}


def fold_it(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """The Italian number fold."""
    tokens = split_elisions(collapse_marked_h_clock(tokens, _CLOCK_MARKERS))
    for words, surface in _PHRASES:
        tokens = collapse_phrase(tokens, words, surface)
    return fold(glue_abbreviations(tokens), _WORDS, _prima)
