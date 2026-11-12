# -*- coding: utf-8 -*-
"""A future preposition never trails the count it governs, pt.

"em" is a preposition (Priberam s.v. "em": "preposição ... 2. Usa-se para
indicar tempo (ex.: em janeiro; na próxima semana)"), and "dentro de" and
"daqui a" end in one, so each comes before the count it governs.  Only
"atrás" follows the count ("66 milhões de anos atrás", test_nl_eras).
"ela faz dois anos em maio" read "dois anos em" as two years from now and left "ela faz maio".
The count belongs to "faz" (she turns two); "em maio" is the date.  Anchor
2017-06-27 13:04.
"""
from datetime import datetime

import pytest

from ._corpus import parse, ad


def test_trailing_em_is_not_an_offset():
    span, rest = parse("ela faz dois anos em maio")
    assert span.start.month == 5
    assert rest == "ela faz dois anos"


@pytest.mark.parametrize("text", ["dois anos atrás", "dois anos atras"])
def test_trailing_atras_still_counts_back(text):
    # "atras" is "atrás" as text without diacritics writes it
    span, rest = parse(text)
    assert span.start == ad(datetime(2015, 6, 27, 13, 4))
    assert rest == ""


def test_leading_em_still_counts_forward():
    span, rest = parse("em dois anos")
    assert span.start == ad(datetime(2019, 6, 27, 13, 4))
    assert rest == ""
