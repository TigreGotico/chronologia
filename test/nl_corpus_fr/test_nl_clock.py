"""French clock notation: the "h" hour separator (20h, 20h30), spelled
hours with "heures", the "et quart" / "moins le quart" / "et demie"
fraction system, du matin / du soir meridiems, and midi / minuit landmarks.

A clock reference is minute-wide; a time already past on the anchor day
(13:04) rolls to the next day (prefer_future).
"""
from datetime import timedelta

import pytest

from ._corpus import span, start, nomatch, AstroDate


@pytest.mark.parametrize("text,y,mo,d,h,mi", [
    # h-separator notation, same-day (after 13:04)
    ("à 20h", 2017, 6, 27, 20, 0),
    ("20h", 2017, 6, 27, 20, 0),
    ("20h30", 2017, 6, 27, 20, 30),
    ("à 20h30", 2017, 6, 27, 20, 30),
    ("18h45", 2017, 6, 27, 18, 45),
    ("huit heures du soir", 2017, 6, 27, 20, 0),
    # rolled to the next day (before 13:04)
    ("à midi", 2017, 6, 28, 12, 0),
    ("à minuit", 2017, 6, 28, 0, 0),
    ("à trois heures", 2017, 6, 28, 3, 0),
    ("sept heures du matin", 2017, 6, 28, 7, 0),
    ("9h", 2017, 6, 28, 9, 0),
    # fraction system
    ("trois heures et quart", 2017, 6, 28, 3, 15),
    ("neuf heures et demie", 2017, 6, 28, 9, 30),
    ("dix heures moins le quart", 2017, 6, 28, 9, 45),
    ("huit heures et quart", 2017, 6, 28, 8, 15),
])
def test_clock(text, y, mo, d, h, mi):
    assert start(text) == AstroDate(y, mo, d, h, mi)


def test_clock_is_minute_wide():
    assert span("à 20h30").width == timedelta(minutes=1)


# -- adversarial: "moins le quart" is a clock fraction, never a range -----

def test_moins_le_quart_not_a_range():
    # "quatre heures moins le quart" must read 3:45, not a "... to ..." range
    assert start("quatre heures moins le quart") == AstroDate(2017, 6, 28, 3, 45)


def test_impossible_hour_no_crash():
    r = span("à 20h30") if False else None  # noqa
    # a malformed 99h must not raise and must not read hour 99
    from ._corpus import parse
    res = parse("à 99h")
    if res is not None:
        assert res[0].start.hour != 99


def test_gibberish_clock_tokens_no_crash():
    from ._corpus import parse
    for tok in ["10sept", "7d", "20h99z"]:
        parse(tok)  # must not raise
