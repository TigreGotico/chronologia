# -*- coding: utf-8 -*-
"""Second-pass sweep: French clock notation across all spelled hours (deux..
douze), the fraction system ("et quart" / "et demie" / "moins le quart" /
general "moins N"), and the "du matin" / "du soir" / "de l'après-midi"
meridiems -- a comprehensive cross of vocabulary already spot-checked in
test_nl_clock.py, test_nl_moins_minutes.py and test_nl_afternoon_clock.py, but
not swept exhaustively there. Every case already pinned in those three files
is excluded here to avoid duplication.

Gold is plain naive-time arithmetic against the anchor (Tuesday 2017-06-27
13:04): a time already past on the anchor day rolls to the next day
(prefer_future); "du soir" / "de l'après-midi" add twelve hours to the
spelled hour; "moins N" subtracts N minutes from the stated hour, rolling the
hour back by one.

Two adversarial gaps surfaced by this sweep are now closed and swept green
below (they were pinned as strict xfail with the arithmetically-correct gold
until the fix landed):

* the hour word "une heure" (1 o'clock) now composes with every fraction and
  meridiem suffix -- the feminine "une" is position-licensed to HOUR=1 only
  directly before "heure(s)", so it binds the clock the way "deux heures"
  does while the indefinite article ("une semaine") stays a duration.
* "midi moins N" / "minuit moins N" now subtract a bare minute count from the
  landmark, not only the quarter idiom ("moins le quart").
"""
import pytest

from chronologia.astrodate import AstroDate

from ._corpus import start


_OK = [('deux heures et quart', [2017, 6, 28, 2, 15]), ('deux heures et demie', [2017, 6, 28, 2, 30]), ('deux heures moins le quart', [2017, 6, 28, 1, 45]), ('deux heures du matin', [2017, 6, 28, 2, 0]), ('deux heures du soir', [2017, 6, 27, 14, 0]), ('trois heures et quart', [2017, 6, 28, 3, 15]), ('trois heures et demie', [2017, 6, 28, 3, 30]), ('trois heures moins le quart', [2017, 6, 28, 2, 45]), ('trois heures du matin', [2017, 6, 28, 3, 0]), ('trois heures du soir', [2017, 6, 27, 15, 0]), ('quatre heures et quart', [2017, 6, 28, 4, 15]), ('quatre heures et demie', [2017, 6, 28, 4, 30]), ('quatre heures du matin', [2017, 6, 28, 4, 0]), ('quatre heures du soir', [2017, 6, 27, 16, 0]), ('cinq heures et quart', [2017, 6, 28, 5, 15]), ('cinq heures et demie', [2017, 6, 28, 5, 30]), ('cinq heures moins le quart', [2017, 6, 28, 4, 45]), ('cinq heures du matin', [2017, 6, 28, 5, 0]), ('cinq heures du soir', [2017, 6, 27, 17, 0]), ('six heures et quart', [2017, 6, 28, 6, 15]), ('six heures et demie', [2017, 6, 28, 6, 30]), ('six heures moins le quart', [2017, 6, 28, 5, 45]), ('six heures du matin', [2017, 6, 28, 6, 0]), ('six heures du soir', [2017, 6, 27, 18, 0]), ("six heures de l'après-midi", [2017, 6, 27, 18, 0]), ('sept heures et quart', [2017, 6, 28, 7, 15]), ('sept heures et demie', [2017, 6, 28, 7, 30]), ('sept heures moins le quart', [2017, 6, 28, 6, 45]), ('sept heures du soir', [2017, 6, 27, 19, 0]), ("sept heures de l'après-midi", [2017, 6, 27, 19, 0]), ('huit heures et quart', [2017, 6, 28, 8, 15]), ('huit heures et demie', [2017, 6, 28, 8, 30]), ('huit heures moins le quart', [2017, 6, 28, 7, 45]), ('huit heures du matin', [2017, 6, 28, 8, 0]), ("huit heures de l'après-midi", [2017, 6, 27, 20, 0]), ('neuf heures et quart', [2017, 6, 28, 9, 15]), ('neuf heures et demie', [2017, 6, 28, 9, 30]), ('neuf heures moins le quart', [2017, 6, 28, 8, 45]), ('neuf heures du matin', [2017, 6, 28, 9, 0]), ('neuf heures du soir', [2017, 6, 27, 21, 0]), ('dix heures et quart', [2017, 6, 28, 10, 15]), ('dix heures et demie', [2017, 6, 28, 10, 30]), ('dix heures du matin', [2017, 6, 28, 10, 0]), ('dix heures du soir', [2017, 6, 27, 22, 0]), ('onze heures et quart', [2017, 6, 28, 11, 15]), ('onze heures et demie', [2017, 6, 28, 11, 30]), ('onze heures moins le quart', [2017, 6, 28, 10, 45]), ('onze heures du matin', [2017, 6, 28, 11, 0]), ('onze heures du soir', [2017, 6, 27, 23, 0]), ('douze heures et quart', [2017, 6, 28, 12, 15]), ('douze heures et demie', [2017, 6, 28, 12, 30]), ('douze heures moins le quart', [2017, 6, 28, 11, 45]), ('deux heures moins cinq', [2017, 6, 28, 1, 55]), ('deux heures moins dix', [2017, 6, 28, 1, 50]), ('deux heures moins vingt', [2017, 6, 28, 1, 40]), ('deux heures moins vingt-cinq', [2017, 6, 28, 1, 35]), ('trois heures moins cinq', [2017, 6, 28, 2, 55]), ('trois heures moins dix', [2017, 6, 28, 2, 50]), ('trois heures moins vingt', [2017, 6, 28, 2, 40]), ('trois heures moins vingt-cinq', [2017, 6, 28, 2, 35]), ('quatre heures moins cinq', [2017, 6, 28, 3, 55]), ('quatre heures moins dix', [2017, 6, 28, 3, 50]), ('quatre heures moins vingt', [2017, 6, 28, 3, 40]), ('quatre heures moins vingt-cinq', [2017, 6, 28, 3, 35]), ('cinq heures moins cinq', [2017, 6, 28, 4, 55]), ('cinq heures moins dix', [2017, 6, 28, 4, 50]), ('cinq heures moins vingt', [2017, 6, 28, 4, 40]), ('cinq heures moins vingt-cinq', [2017, 6, 28, 4, 35]), ('six heures moins cinq', [2017, 6, 28, 5, 55]), ('six heures moins dix', [2017, 6, 28, 5, 50]), ('six heures moins vingt', [2017, 6, 28, 5, 40]), ('six heures moins vingt-cinq', [2017, 6, 28, 5, 35]), ('sept heures moins cinq', [2017, 6, 28, 6, 55]), ('sept heures moins dix', [2017, 6, 28, 6, 50]), ('sept heures moins vingt', [2017, 6, 28, 6, 40]), ('sept heures moins vingt-cinq', [2017, 6, 28, 6, 35]), ('huit heures moins cinq', [2017, 6, 28, 7, 55]), ('huit heures moins dix', [2017, 6, 28, 7, 50]), ('huit heures moins vingt', [2017, 6, 28, 7, 40]), ('huit heures moins vingt-cinq', [2017, 6, 28, 7, 35]), ('neuf heures moins dix', [2017, 6, 28, 8, 50]), ('neuf heures moins vingt', [2017, 6, 28, 8, 40]), ('neuf heures moins vingt-cinq', [2017, 6, 28, 8, 35]), ('dix heures moins cinq', [2017, 6, 28, 9, 55]), ('dix heures moins vingt-cinq', [2017, 6, 28, 9, 35]), ('onze heures moins cinq', [2017, 6, 28, 10, 55]), ('onze heures moins dix', [2017, 6, 28, 10, 50]), ('onze heures moins vingt-cinq', [2017, 6, 28, 10, 35]), ('douze heures moins cinq', [2017, 6, 28, 11, 55]), ('douze heures moins dix', [2017, 6, 28, 11, 50]), ('douze heures moins vingt', [2017, 6, 28, 11, 40]), ('douze heures moins vingt-cinq', [2017, 6, 28, 11, 35])]


@pytest.mark.parametrize("text,ymdhm", _OK)
def test_clock_resweep(text, ymdhm):
    y, mo, d, h, mi = ymdhm
    assert start(text) == AstroDate(y, mo, d, h, mi), f"{text!r}"


# -- formerly-pinned gaps, now composed: the singular hour name "une heure"
# (1 o'clock) reads as HOUR=1 in every fraction/meridiem/subtractive frame the
# other hours already take (the feminine "une" was left unfolded to protect
# the indefinite article "une semaine", so it is position-licensed to 1 only
# directly before "heure(s)"); and "midi/minuit moins N" subtracts a bare
# minute count from the landmark, not only the quarter idiom.  French reckons
# the clock in twelve hours, so a minute *to* one o'clock is spoken as
# twelve-something ("une heure moins le quart" == 12:45).
_COMPOSED = [('une heure et quart', [2017, 6, 28, 1, 15]), ('une heure et demie', [2017, 6, 28, 1, 30]), ('une heure moins le quart', [2017, 6, 28, 12, 45]), ('une heure du matin', [2017, 6, 28, 1, 0]), ('une heure du soir', [2017, 6, 28, 13, 0]), ("une heure de l'après-midi", [2017, 6, 28, 13, 0]), ('une heure moins cinq', [2017, 6, 28, 12, 55]), ('une heure moins dix', [2017, 6, 28, 12, 50]), ('une heure moins vingt', [2017, 6, 28, 12, 40]), ('une heure moins vingt-cinq', [2017, 6, 28, 12, 35]), ('midi moins cinq', [2017, 6, 28, 11, 55]), ('midi moins dix', [2017, 6, 28, 11, 50]), ('midi moins vingt', [2017, 6, 28, 11, 40]), ('minuit moins cinq', [2017, 6, 27, 23, 55]), ('minuit moins dix', [2017, 6, 27, 23, 50]), ('minuit moins vingt', [2017, 6, 27, 23, 40])]


@pytest.mark.parametrize("text,ymdhm", _COMPOSED)
def test_clock_resweep_une_heure_and_landmark_moins(text, ymdhm):
    y, mo, d, h, mi = ymdhm
    assert start(text) == AstroDate(y, mo, d, h, mi), f"{text!r}"
