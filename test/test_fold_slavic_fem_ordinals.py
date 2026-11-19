# -*- coding: utf-8 -*-
"""The Slavic feminine ordinals fold to whole numbers.

Several period nouns are feminine across the family (неделя/седмица/половина/
декада/четверть ...), and the ordinal that selects one carries the feminine
nominative ending: "третья неделя апреля" is the third week of April.  Each
surface from 3 to 12 must fold to an integer token, never to a fraction
(вторая is the second, not one half).
"""
import pytest

from chronologia.extract import numlayer_slavic as NS
from chronologia.extract.model import Token
from chronologia.extract.numlayer import attach


def _fold(lang, word):
    fold = getattr(NS, f"fold_{lang}")
    tok = Token(text=word, raw=word, index=0, is_number=False,
                char_start=0, char_end=len(word))
    out = fold(attach((tok,), word, lang))
    assert len(out) == 1, f"{lang}:{word!r} did not fold to a single token"
    return out[0]


# feminine nominative ordinals 3..12 (the range #264 missed), per locale.
_CASES = {
    "ru": {"третья": 3, "четвёртая": 4, "четвертая": 4, "пятая": 5,
           "шестая": 6, "седьмая": 7, "восьмая": 8, "девятая": 9,
           "десятая": 10, "одиннадцатая": 11, "двенадцатая": 12},
    "uk": {"третя": 3, "четверта": 4, "п'ята": 5, "шоста": 6, "сьома": 7,
           "восьма": 8, "дев'ята": 9, "десята": 10, "одинадцята": 11,
           "дванадцята": 12},
    "bg": {"трета": 3, "третата": 3, "четвърта": 4, "четвъртата": 4,
           "пета": 5, "петата": 5, "шеста": 6, "седма": 7, "осма": 8,
           "девета": 9, "десета": 10, "единадесета": 11, "дванадесета": 12},
    "cs": {"třetí": 3, "čtvrtá": 4, "pátá": 5, "šestá": 6, "sedmá": 7,
           "osmá": 8, "devátá": 9, "desátá": 10, "jedenáctá": 11,
           "dvanáctá": 12},
    "sk": {"tretia": 3, "štvrtá": 4, "piata": 5, "šiesta": 6, "siedma": 7,
           "ôsma": 8, "deviata": 9, "desiata": 10, "jedenásta": 11,
           "dvanásta": 12},
    "sl": {"tretja": 3, "četrta": 4, "peta": 5, "šesta": 6, "sedma": 7,
           "osma": 8, "deveta": 9, "deseta": 10, "enajsta": 11,
           "dvanajsta": 12},
    "hr": {"treća": 3, "četvrta": 4, "peta": 5, "šesta": 6, "sedma": 7,
           "osma": 8, "deveta": 9, "deseta": 10, "jedanaesta": 11,
           "dvanaesta": 12},
}

_PARAMS = [(lang, w, v) for lang, tbl in _CASES.items() for w, v in tbl.items()]


@pytest.mark.parametrize("lang,word,value", _PARAMS)
def test_feminine_ordinal_folds_to_integer(lang, word, value):
    tok = _fold(lang, word)
    assert tok.is_number, f"{lang}:{word!r} did not fold to a number"
    assert tok.value == value, f"{lang}:{word!r} folded to {tok.value}, want {value}"
    # it must be an INTEGER selector, never the fraction ovos-number-parser reads
    assert isinstance(tok.value, int) and tok.value == int(tok.value)
