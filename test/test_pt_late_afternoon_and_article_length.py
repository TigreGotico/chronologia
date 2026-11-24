"""pt "ao fim da tarde" is the end of the afternoon, and "na hora" is no length.

"dias de semana" and "na hora" name no length: "na" is "em" fused with the
article (Priberam s.v. "na"), so "na hora de ir" says when, not how long.
Anchor: Tuesday 2017-06-27 13:04.
"""
from datetime import datetime

import pytest

from chronologia import extract_duration, extract_timespan

ISSUE = "https://github.com/TigreGotico/chronologia/issues/1024"
ANCHOR = datetime(2017, 6, 27, 13, 4)


@pytest.mark.xfail(strict=True, reason=ISSUE)
def test_ao_fim_da_tarde_leaves_no_word_of_the_date_in_the_remainder():
    text = "não me deixes esquecer de comprar pão ao fim da tarde"
    found = extract_timespan(text, "pt", ANCHOR)
    assert found.remainder == "não me deixes esquecer de comprar pão"


@pytest.mark.xfail(strict=True, reason=ISSUE)
def test_dias_de_semana_and_na_hora_name_no_length():
    text = ("nos dias de semana às oito da manhã avisa-me que está na hora "
            "de ir trabalhar")
    assert extract_duration(text, "pt", anchor=ANCHOR) is None
