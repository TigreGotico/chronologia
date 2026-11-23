"""Kabyle date words over the numtag number layer."""
from __future__ import annotations

from typing import Tuple

from chronologia.extract.model import Token
from chronologia.extract.numlayer_germanic import (DateWords, count_words, fold,
                                                   locale_words)

# Kabyle tells the time with Arabic-borrowed hour NOUNS carrying the definite
# article ("ɣef lxemsa n tmeddit" = at five in the evening), not with the bare
# Berber cardinals.  numtag reads the bare borrowings ("tlata") but none of
# the article-bearing hour forms (https://github.com/TigreGotico/numtag/issues/149),
# so the table gives each one its value and the HOUR slot binds.  Every
# surface below is written as an hour on kab.wikipedia:
# "ɣef lweḥda n tṣ̣ebḥit", "ɣef tizi n jjuj d wezgen n tmeddit", "ɣef tlata n
# tmeddit", "ɣef ṛṛebɛa d wezgen n tmeddit", "ɣef lxemsa n tmeddit", "ɣef
# tmanya n tmeddit", "ɣef ttesɛa n tṣ̣ebḥit", "Lɛecṛa n tṣ̣ebḥit", "ɣef leḥdac
# d wezgen n tṣ̣ebḥit", "ɣef ttnac n yiḍ" (Tafsut n Yimaziɣen, Bgayet).
# The remaining hour nouns come from the Kabyle sentences on Tatoeba, each
# with the English it is paired with:
#   "Ha-tt-an d ssaɛtin ɣiṛ ṛṛbeɛ."      -- "It's quarter to two."
#   "Ha-tt-an d zzuǧ ɣiṛ ṛṛbeɛ."         -- "It's quarter to two."
#   "Ad d-uɣaleɣ ɣef ssetta d wezgen."   -- "I will be back at half past six."
#   "Ha-tt-an d ssebɛ u ṛṛbeɛ."          -- a seven-o'clock quarter reading.
#   "Ha-tt-an d ttmanya ɣiṛ ṛṛbeɛ."      -- "It's a quarter to eight."
#   "Attan d lεacra d wezgen."           -- "It is ten-thirty."
#   "Ha-tt-an d leḥḍac u ṛṛbeɛ."         -- "It's a quarter past eleven."
# Two and seven take their standard forms from @athmanemokraoui, a native
# Kabyle speaker, on
# https://github.com/TigreGotico/chronologia/pull/846#issuecomment-5573978767:
#   "Six is 'ssetta', but seven is 'ssebɛa' (always with the final -a)."
#   "For the clock hour write 'ssaɛtin' (d ssaɛtin = it's two o'clock).  For
#    the cardinal number 2 itself, use 'jjuǧ' depending on regional
#    phonetics."
# "ssebɛa" and "jjuǧ" rest on that comment alone.  The apocopated "ssebɛ" of
# the Tatoeba sentence above keeps parsing beside "ssebɛa", as do "jjuj" and
# "zzuǧ" beside "jjuǧ" -- a parser accepts every attested variation.
_KAB_HOUR_NOUNS = {
    "lweḥda": (1, False), "jjuj": (2, False), "jjuǧ": (2, False), "zzuǧ": (2, False), "ssaɛtin": (2, False), "ṛṛebɛa": (4, False),
    "lxemsa": (5, False), "ssetta": (6, False), "ssebɛa": (7, False), "ssebɛ": (7, False), "ttmanya": (8, False),
    "ttesɛa": (9, False),
    "lɛecṛa": (10, False), "lɛacra": (10, False), "leḥdac": (11, False), "leḥḍac": (11, False), "ttnac": (12, False),
}
_WORDS = DateWords(
    lang="kab",
    fractions=locale_words("kab", "clock_fraction_"),
    counts=count_words("kab"))


def fold_kab(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """The Kabyle number fold."""
    return fold(tokens, _WORDS, table=_KAB_HOUR_NOUNS)
