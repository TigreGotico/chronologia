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
    # landmark + fraction: "midi"/"minuit" compose with a trailing additive
    # half/quarter exactly as a bare hour does (Academie francaise, 8e ed.,
    # art. "demi": "Midi et demi, minuit et demi"; corroborated by the OQLF).
    ("midi et demi", 2017, 6, 28, 12, 30),
    ("minuit et demi", 2017, 6, 28, 0, 30),
    ("midi et quart", 2017, 6, 28, 12, 15),
    ("minuit et quart", 2017, 6, 28, 0, 15),
    # landmark + "moins le quart" (subtractive) -- "midi moins le quart" = 11:45
    ("midi moins le quart", 2017, 6, 28, 11, 45),
    # landmark + bare-minute subtraction -- "midi/minuit moins N" reads the
    # offset, not only the quarter idiom
    ("midi moins vingt", 2017, 6, 28, 11, 40),
    ("midi moins dix", 2017, 6, 28, 11, 50),
    ("minuit moins cinq", 2017, 6, 27, 23, 55),
    ("minuit moins vingt", 2017, 6, 27, 23, 40),
    # the singular hour "une heure" (1 o'clock) composes with fraction,
    # meridiem and subtractive suffixes like every other hour; a minute *to*
    # one o'clock is spoken twelve-something in French 12h reckoning
    ("à une heure", 2017, 6, 28, 1, 0),
    ("une heure et quart", 2017, 6, 28, 1, 15),
    ("une heure et demie", 2017, 6, 28, 1, 30),
    ("une heure du matin", 2017, 6, 28, 1, 0),
    ("une heure de l'après-midi", 2017, 6, 28, 13, 0),
    ("une heure moins le quart", 2017, 6, 28, 12, 45),
    ("une heure moins dix", 2017, 6, 28, 12, 50),
])
def test_clock(text, y, mo, d, h, mi):
    assert start(text) == AstroDate(y, mo, d, h, mi)


def test_une_heure_stays_a_week_duration_elsewhere():
    # "une" is only the hour 1 directly before "heure(s)"; "une semaine"
    # stays the indefinite-article duration (a week), not "1 week o'clock"
    assert start("à une heure") == AstroDate(2017, 6, 28, 1, 0)
    from ._corpus import parse
    # a bare "une semaine" is a duration phrase, never a clock time
    res = parse("une semaine")
    assert res is None or res[0].start.hour == 0


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
