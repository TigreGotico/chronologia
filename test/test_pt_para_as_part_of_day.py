"""pt "N para as H" clock keeps a following part of day and the article "um".

"para" subtracts from the hour that follows, so "um quarto para as três da
tarde" is a quarter before 15:00, that is 14:45, the same time as the
hour-first "às três menos um quarto da tarde".  Priberam s.v. "quarto", 3:
"falta um quarto para as nove".  Every value is worked out by hand from the
anchor, Wednesday 2026-11-25 10:00: "da manhã" has no later reading today,
so 02:45 falls on the next day.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2026, 11, 25, 10, 0)
TODAY_1445 = datetime(2026, 11, 25, 14, 45)

ROWS = [
    ("quinze para as três da tarde", TODAY_1445, ""),
    ("dez para as três da tarde", datetime(2026, 11, 25, 14, 50), ""),
    ("um quarto para as três da tarde", TODAY_1445, ""),
    ("um quarto para as 3 da tarde", TODAY_1445, ""),
    ("um quarto para as três da manhã", datetime(2026, 11, 26, 2, 45), ""),
    ("um quarto para as 3", TODAY_1445, ""),
    ("um quarto para as quinze", TODAY_1445, ""),
    ("marca a reunião para um quarto para as três da tarde", TODAY_1445,
     "marca a reunião para"),
]

CONTROLS = [
    ("às três menos um quarto da tarde", TODAY_1445, ""),
    ("3 menos um quarto", TODAY_1445, ""),
    ("quinze para as três", TODAY_1445, ""),
    ("às três e meia", datetime(2026, 11, 25, 15, 30), ""),
]


@pytest.mark.parametrize("lang", ["pt-PT", "pt-BR"])
@pytest.mark.parametrize("text,expected,remainder", ROWS + CONTROLS)
def test_para_as_clock(lang, text, expected, remainder):
    found = extract_timespan(text, lang, ANCHOR)
    assert found.span.start.datetime() == expected
    assert found.remainder == remainder
