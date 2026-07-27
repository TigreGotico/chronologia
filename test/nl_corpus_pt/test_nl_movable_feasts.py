# -*- coding: utf-8 -*-
"""Festas móveis ancoradas na Páscoa (computus ocidental).

"Quarta-feira de Cinzas", "Quinta-feira Santa" etc. resolvem-se pelo desvio em
relação ao Domingo de Páscoa, não como o próximo dia da semana literal.

    Páscoa 2018 = 1 abr

O âncora 2017-06-27 é posterior à Páscoa de 2017, logo um nome nu avança para a
ocorrência de 2018.
"""
from datetime import timedelta

import pytest

from ._corpus import AstroDate, parse, span, start  # noqa: F401

_BARE_2018 = [
    ("quarta-feira de cinzas", (2018, 2, 14)),  # 1 abr 2018 - 46
    ("domingo de ramos", (2018, 3, 25)),        # - 7
    ("quinta-feira santa", (2018, 3, 29)),      # - 3
    ("sexta-feira santa", (2018, 3, 30)),       # - 2
    ("páscoa", (2018, 4, 1)),
]


@pytest.mark.parametrize("text,ymd", _BARE_2018)
def test_festa_movel(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)
    r = parse(text)
    assert r[1].strip() == "", f"resto não consumido {r[1]!r} em {text!r}"
