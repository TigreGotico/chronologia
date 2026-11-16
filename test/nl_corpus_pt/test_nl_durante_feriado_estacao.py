""""durante" antes de um feriado ou de uma estação pertence-lhe.

"durante" é preposição: "Usa-se para designar simultaneidade de tempo ou de
duração" (Dicionário Priberam, s.v. durante).  O verão meteorológico é
junho, julho e agosto (NOAA NCEI, "Meteorological Versus Astronomical
Seasons").  Âncora: 16 de novembro de 2026.
"""
from datetime import datetime

import pytest

from ._corpus import parse

ANCHOR = datetime(2026, 11, 16, 12, 0)


@pytest.mark.parametrize("text, bounds, remainder", [
    ("vamos à praia durante o verão de 2027",
     (datetime(2027, 6, 1), datetime(2027, 9, 1)), "vamos à praia"),
    ("a loja fecha durante o natal",
     (datetime(2026, 12, 25), datetime(2026, 12, 26)), "a loja fecha"),
])
def test_durante_le_se_com_a_referencia(text, bounds, remainder):
    span, rest = parse(text, ANCHOR)
    assert (span.start, span.end) == bounds
    assert rest == remainder


def test_durante_o_verao_le_o_verao():
    span, rest = parse("durante o verão", ANCHOR)
    assert span == parse("o verão", ANCHOR)[0]
    assert rest == ""
