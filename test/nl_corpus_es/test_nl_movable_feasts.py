# -*- coding: utf-8 -*-
"""Fiestas móviles ancladas a la Pascua (computus occidental).

"Miércoles de Ceniza", "Jueves Santo" etc. se resuelven por su desfase respecto
al Domingo de Pascua, no como el siguiente día de la semana literal.

    Pascua 2018 = 1 abr    Pascua 2017 = 16 abr

El ancla 2017-06-27 es posterior a la Pascua de 2017, así que un nombre desnudo
avanza a la ocurrencia de 2018.
"""
from datetime import timedelta

import pytest

from ._corpus import AstroDate, parse, span, start  # noqa: F401

_BARE_2018 = [
    ("miércoles de ceniza", (2018, 2, 14)),  # 1 abr 2018 - 46
    ("domingo de ramos", (2018, 3, 25)),     # - 7
    ("jueves santo", (2018, 3, 29)),         # - 3
    ("viernes santo", (2018, 3, 30)),        # - 2
    ("sábado santo", (2018, 3, 31)),         # - 1
    ("pascua", (2018, 4, 1)),
    ("pentecostés", (2018, 5, 20)),          # + 49
]


@pytest.mark.parametrize("text,ymd", _BARE_2018)
def test_fiesta_movil(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)
    r = parse(text)
    assert r[1].strip() == "", f"resto no consumido {r[1]!r} en {text!r}"
