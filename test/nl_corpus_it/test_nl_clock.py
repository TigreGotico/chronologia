"""Italian clock: "alle N", the "e un quarto" / "meno un quarto" / "e mezza"
fraction system, di sera / di mattina meridiems, mezzogiorno / mezzanotte
landmarks, and the "ore N" prefix.
"""
from datetime import timedelta

import pytest

from ._corpus import span, start, AstroDate


@pytest.mark.parametrize("text,y,mo,d,h,mi", [
    ("7 di sera", 2017, 6, 27, 19, 0),
    ("sette di sera", 2017, 6, 27, 19, 0),
    ("ore 20", 2017, 6, 27, 20, 0),
    ("alle tre", 2017, 6, 28, 3, 0),
    ("sette di mattina", 2017, 6, 28, 7, 0),
    ("alle nove", 2017, 6, 28, 9, 0),
    ("a mezzogiorno", 2017, 6, 28, 12, 0),
    ("a mezzanotte", 2017, 6, 28, 0, 0),
    ("alle tre e un quarto", 2017, 6, 28, 3, 15),
    ("le nove e mezza", 2017, 6, 28, 9, 30),
    ("alle quattro meno un quarto", 2017, 6, 28, 3, 45),
    ("le tre e mezza", 2017, 6, 28, 3, 30),
    ("alle otto e un quarto", 2017, 6, 28, 8, 15),
])
def test_clock(text, y, mo, d, h, mi):
    assert start(text) == AstroDate(y, mo, d, h, mi)


def test_clock_is_minute_wide():
    assert span("alle tre e un quarto").width == timedelta(minutes=1)


def test_meno_un_quarto_not_a_range():
    assert start("alle quattro meno un quarto") == AstroDate(2017, 6, 28, 3, 45)


def test_gibberish_no_crash():
    from ._corpus import parse
    for tok in ["10sett", "7g", "20h99z"]:
        parse(tok)
