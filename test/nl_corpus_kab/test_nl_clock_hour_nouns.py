# -*- coding: utf-8 -*-
"""Kabyle spoken clock: the Arabic-borrowed hour nouns, fractions and "minus".

Kabyle names the hour with a noun ("lxemsa" five, "lɛecṛa" ten), not with the
bare Berber cardinal, and hangs the daypart on it through the genitive "n"
("n tmeddit" of the evening).  The minutes hang off the hour with "u" (and)
or "ɣiṛ" (minus).  Every sentence below is running Kabyle: the hour-noun set
comes from kab.wikipedia, named beside each line, and the fraction and
"minus" set from the Kabyle sentences on Tatoeba, quoted with their English
pairs.

Anchor 2017-06-27 13:04, prefer_future.  Expected instants are worked out from
the anchor, not read back from the parser: an hour that has already gone by
today lands on 06-28, one still ahead lands on 06-27.
"""
from datetime import datetime

import pytest

from ._corpus import nomatch, parse

A = datetime(2017, 6, 27, 13, 4)

# text, expected (Y, M, D, h, m), attesting article
_CLOCKS = [
    # "ɣef lweḥda n tṣ̣ebḥit : tebda-d temhelt n Mizrana"  -- 01:00, gone by
    ("ɣef lweḥda n tṣ̣ebḥit", (2017, 6, 28, 1, 0), "Tafsut n Yimaziɣen"),
    # "ɣef jjuj n tmeddit, Aseqqamu n uḥuddu n yizerfan idelsanen ..."
    ("ɣef jjuj n tmeddit", (2017, 6, 27, 14, 0), "Tafsut n Yimaziɣen"),
    # "ɣef tizi n jjuj d wezgen n tmeddit"  -- 14:30, still ahead
    ("ɣef jjuj d wezgen n tmeddit", (2017, 6, 27, 14, 30), "Tafsut n Yimaziɣen"),
    # "ɣef tlata n tmeddit, Aseqqamu n uḥuddu ... yessegrew-d azal n 1000"
    ("ɣef tlata n tmeddit", (2017, 6, 27, 15, 0), "Tafsut n Yimaziɣen"),
    # "ɣef ṛṛebɛa d wezgen n tmeddit, llan ugar n 1000 n medden"
    ("ɣef ṛṛebɛa d wezgen n tmeddit", (2017, 6, 27, 16, 30), "Tafsut n Yimaziɣen"),
    # "ɣef lxemsa n tmeddit, anmahal n Ldzayer deg Fṛansa yemlal d weɣlif"
    ("ɣef lxemsa n tmeddit", (2017, 6, 27, 17, 0), "Tafsut n Yimaziɣen"),
    # "ɣef tmanya n tmeddit, Tanegga n Tɣamsa Tadzayrit tenna-d ..."
    ("ɣef tmanya n tmeddit", (2017, 6, 27, 20, 0), "Tafsut n Yimaziɣen"),
    # "ɣef ttesɛa n tṣ̣ebḥit ay mlalen"  -- 09:00, gone by
    ("ɣef ttesɛa n tṣ̣ebḥit", (2017, 6, 28, 9, 0), "Tafsut n Yimaziɣen"),
    # "Lɛecṛa n tṣ̣ebḥit. Ldzayer tamaneɣt, deg Tsenbert n Umezwaru n Mayyu"
    ("Lɛecṛa n tṣ̣ebḥit", (2017, 6, 28, 10, 0), "Tafsut n Yimaziɣen"),
    # "ɣef leḥdac d wezgen n tṣ̣ebḥit, deg tesdawit talemmast n Ldzayer"
    ("ɣef leḥdac d wezgen n tṣ̣ebḥit", (2017, 6, 28, 11, 30), "Tafsut n Yimaziɣen"),
    # "Deg yiḍ n wass n lḥedd d letniyen (ɣef ttnac n yiḍ)"  -- midnight
    ("ɣef ttnac n yiḍ", (2017, 6, 28, 0, 0), "Tafsut n Yimaziɣen"),
    # "ɣef lxemsa u xemsin"  -- the additive connective with spelled minutes
    ("ɣef lxemsa u xemsin", (2017, 6, 28, 5, 50), "Tafsut n Yimaziɣen"),
    # "Neffeɣ-d ɣef lxemsa n ssbaḥ"  -- the plain-s morning spelling
    ("ɣef lxemsa n ssbaḥ", (2017, 6, 28, 5, 0), "Agarsafen"),
    # "Deg wass-nni, ɣef 4:40 n tmeddit, yiwet n terbaεt n yisafagen"
    ("ɣef 4:40 n tmeddit", (2017, 6, 27, 16, 40), "Bgayet"),
    # "azal n 12:30 n tmeddit, takarust n Meɛṭub tettwaḥbes"  -- 12:30, gone by
    ("12:30 n tmeddit", (2017, 6, 28, 12, 30), "Lwennas Meɛṭub"),
    # "Di 7 n tufat n wass n 8 yennayer"  -- CLDR 47's am surface
    ("ɣef 7 n tufat", (2017, 6, 28, 7, 0), "Imenɣi n Lezzayer (1956-1957)"),
]

# The copula "d" ("it is ...") opens the answer to "what time is it".  It is
# the same particle as the additive connective, told apart by position.
_COPULA = [
    ("d lxemsa n tmeddit", (2017, 6, 27, 17, 0)),
    ("d lɛecṛa swaswa", (2017, 6, 28, 10, 0)),
    ("d ṛṛebɛa d wezgen n tmeddit", (2017, 6, 27, 16, 30)),
]


def _at(text, want):
    r = parse(text, A)
    assert r is not None, "%r did not parse" % text
    s = r[0].start
    assert (s.year, s.month, s.day, s.hour, s.minute) == want
    assert r[1] == "", "%r stranded %r" % (text, r[1])


@pytest.mark.parametrize("text,want,source", _CLOCKS)
def test_hour_noun_clock(text, want, source):
    _at(text, want)


@pytest.mark.parametrize("text,want", _COPULA)
def test_copula_opens_a_clock(text, want):
    _at(text, want)


# The hour nouns must not turn an ordinary counted noun phrase into a clock.
# "d tlata n wussan" is "it is three days", not 03:00.
@pytest.mark.parametrize("text", [
    "d tlata n wussan",
    "d setta n yeɣallen",
    "d sebɛa n yiseggasen",
    "d tmanya n yegduden",
])
def test_counted_noun_is_not_a_clock(text):
    nomatch(text, A)


# The quarter ("ṛṛbeɛ") and the subtractive connective ("ɣiṛ"), quoted from
# the Kabyle sentences on Tatoeba with the English they are paired with.
_FRACTIONS = [
    # "Ha-tt-an d leḥḍac u ṛṛbeɛ."   -- "It's a quarter past eleven."
    ("d leḥdac u ṛṛbeɛ", (2017, 6, 28, 11, 15)),
    # "Ha-tt-an d tesɛa u ṛbeɛ."     -- "It's quarter past nine."
    ("d ttesɛa u ṛbeɛ", (2017, 6, 28, 9, 15)),
    # "Ha-tt-an d lɛecṛa ɣiṛ ṛṛbeɛ."  (quarter to ten)
    ("d lɛecṛa u ṛbeɛ", (2017, 6, 28, 10, 15)),
    ("d lɛecṛa ɣiṛ ṛbeɛ", (2017, 6, 28, 9, 45)),
    # "Ha-tt-an d ttmanya ɣiṛ ṛṛbeɛ." -- "It's a quarter to eight."
    ("d tmanya ɣiṛ ṛṛbeɛ", (2017, 6, 28, 7, 45)),
    # "Ha-tt-an d tmenya ɣir ɛecra."  -- "It's ten to eight."  The slot after
    # "ɣiṛ" takes plain minutes, not only the quarter.
    ("d lɛecṛa ɣiṛ xemsa", (2017, 6, 28, 9, 55)),
    # "Ha-tt-an d ssaɛtin ɣiṛ ṛṛbeɛ." -- "It's quarter to two."
    ("d ssaɛtin ɣiṛ ṛṛbeɛ", (2017, 6, 28, 1, 45)),
    ("d ssaɛtin ɣiṛ xemsa", (2017, 6, 28, 1, 55)),
    # "Attan d ssaεtin n tmeddit."    -- "It's two o'clock in the afternoon."
    ("d ssaɛtin n tmeddit", (2017, 6, 27, 14, 0)),
    # "Tella qrib d ttnac uzal."      -- "It was nearly noon."
    ("d ttnac uzal", (2017, 6, 28, 12, 0)),
    # "Ad d-uɣaleɣ ɣef ssetta d wezgen." -- "I will be back at half past six."
    ("ɣef ssetta d wezgen", (2017, 6, 28, 6, 30)),
    # "Ha-tt-an d ssebɛ u ṛṛbeɛ."     -- a seven-o'clock quarter reading.
    ("d ssebɛ u ṛṛbeɛ", (2017, 6, 28, 7, 15)),
    # "Ha-tt-an d ttmanya ɣiṛ ṛṛbeɛ." -- "It's a quarter to eight."
    ("d ttmanya ɣiṛ ṛṛbeɛ", (2017, 6, 28, 7, 45)),
    # "Attan d lεacra d wezgen."      -- "It is ten-thirty."
    ("d lɛacra d wezgen", (2017, 6, 28, 10, 30)),
    # "Ha-tt-an d leḥḍac u ṛṛbeɛ."    -- "It's a quarter past eleven."
    ("d leḥḍac u ṛṛbeɛ", (2017, 6, 28, 11, 15)),
    # "Ha-tt-an d lweḥda d wezgen."   -- "It's half past one."
    ("d lweḥda d wezgen", (2017, 6, 28, 1, 30)),
    # "Attan qrib d lweḥda d uzgen."  -- "It's almost half past one already."
    ("d lweḥda d uzgen", (2017, 6, 28, 1, 30)),
    # "Ha-tt-an d zzuǧ ɣiṛ ṛṛbeɛ."    -- "It's quarter to two."
    ("d zzuǧ ɣiṛ ṛṛbeɛ", (2017, 6, 28, 1, 45)),
    # "Ččiɣ imekli ɣef tnac d wezgen." -- "I ate lunch at twelve-thirty."
    ("ɣef tnac d wezgen", (2017, 6, 28, 12, 30)),
]


@pytest.mark.parametrize("text,want", _FRACTIONS)
def test_fraction_and_minus_clock(text, want):
    _at(text, want)


# Surfaces with no attestation stay unparsed rather than being guessed at.
#   "d lɛecṛa ɣiṛ"    -- not a whole phrase, "ten minus" with nothing after.
#   "d lɛecṛa u wac"  -- "wac" is in no Kabyle source read for this corpus.
#   "n uzal"          -- the daylight noun is attested on the clock only in
#                        bare apposition ("d ttnac uzal"), never with "n".
#   "juǧ"             -- the attested two-o'clock forms are "zzuǧ", "jjuj"
#                        and "ssaɛtin".
#   "d lweḥda"        -- a bare hour noun with nothing after it would make
#                        every dangling connective resolve, so it is refused.
@pytest.mark.parametrize("text", [
    "d lɛecṛa ɣiṛ",
    "d lɛecṛa u wac",
    "d juǧ n uzal",
    "d ttnac n uzal",
    "d lweḥda",
    "d ttnac",
])
def test_unattested_clock_surfaces_refused(text):
    nomatch(text, A)


# The morning word keeps its day-part reading; making it a meridiem must not
# swallow it standing on its own.
def test_dayparts_survive():
    for text, hour in [("ṣṣbeḥ", 6), ("tameddit", 18)]:
        r = parse(text, A)
        assert r is not None and r[0].start.hour == hour, text
