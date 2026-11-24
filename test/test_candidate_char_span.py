"""Candidate.char_span is the half-open [start, end) offset range, into the
text the caller passed, of the characters the reading consumed.

Every offset below is counted by hand from the literal, one character per
code point, and each case also states the words ``text[start:end]`` must be.
Anchor Tuesday 2017-06-27 13:04.
"""
from datetime import datetime

import pytest

from chronologia import extract_candidates, extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)

CASES = [
    # single dates, mixed case, leading and repeated spaces
    ("en", "June 5th 2027", (0, 13), "June 5th 2027"),
    ("en", "  Let's  meet on JUNE 5th 2027 ok", (17, 30), "JUNE 5th 2027"),
    ("pt", "reunião no dia 5 de junho de 2027", (8, 33), "no dia 5 de junho de 2027"),
    ("de", "Wir treffen uns am 5. Juni 2027  um 15 Uhr", (16, 42),
     "am 5. Juni 2027  um 15 Uhr"),
    # clocks and parts of the day
    ("en", "call me tomorrow at 3 pm please", (8, 24), "tomorrow at 3 pm"),
    ("en", "tomorrow evening at 8", (0, 21), "tomorrow evening at 8"),
    ("pt", "amanhã às 3 da tarde, por favor", (0, 20), "amanhã às 3 da tarde"),
    ("es", "nos vemos el 5 de junio de 2027 a las 3 de la tarde", (10, 51),
     "el 5 de junio de 2027 a las 3 de la tarde"),
    ("ru", "завтра в 3 часа дня", (0, 19), "завтра в 3 часа дня"),
    ("ar", "غدا الساعة 3 مساء", (0, 17), "غدا الساعة 3 مساء"),
    # ranges: the lead and the connector are inside the span
    ("en", "from june 5th to june 12th", (0, 26), "from june 5th to june 12th"),
    ("en", "between june 5th and june 12th 2027 sir", (0, 35),
     "between june 5th and june 12th 2027"),
    ("pt", "de 5 a 12 de junho de 2027", (0, 26), "de 5 a 12 de junho de 2027"),
    ("es", "del 5 al 12 de junio", (0, 20), "del 5 al 12 de junio"),
    ("de", "vom 5. Juni bis 12. Juni 2027", (0, 29), "vom 5. Juni bis 12. Juni 2027"),
    ("ru", "встреча   с 5 июня до 12 июня", (10, 29), "с 5 июня до 12 июня"),
    # a range that names the month once: the first day's words are inside
    ("en", "the 5th to the 12th of June", (0, 27), "the 5th to the 12th of June"),
    ("fr", "du 14 au 21 juillet", (0, 19), "du 14 au 21 juillet"),
    ("ru", "с 5 по 12 июня", (0, 14), "с 5 по 12 июня"),
    # a lead word the language leaves in the remainder is outside the span
    ("ar", "الاجتماع من 5 يونيو إلى 12 يونيو", (12, 32), "5 يونيو إلى 12 يونيو"),
    # an open range includes its marker
    ("en", "until friday", (0, 12), "until friday"),
]


@pytest.mark.parametrize("lang,text,char_span,words", CASES)
def test_top_candidate_char_span(lang, text, char_span, words):
    top = extract_candidates(text, lang, ANCHOR)[0]
    assert top.char_span == char_span
    assert text[slice(*top.char_span)] == words


def test_unconsumed_words_between_the_ends_stay_inside_the_span():
    # "frobnitz of" is no part of the reading: it is in the remainder, and the
    # span still runs from the first consumed character to the last.
    text = "3 working days after the frobnitz of march"
    top = extract_candidates(text, "en", ANCHOR)[0]
    assert top.remainder == "frobnitz of"
    assert top.char_span == (0, 42)
    assert text[slice(*top.char_span)] == text


def test_runner_up_candidates_carry_their_own_span():
    text = "call me tomorrow at 3 pm please"
    clocks = {c.char_span for c in extract_candidates(text, "en", ANCHOR)
              if c.construction == "clock_time"}
    assert clocks == {(17, 24), (20, 24)}
    assert text[17:24] == "at 3 pm" and text[20:24] == "3 pm"


def test_extract_timespan_stays_a_two_tuple():
    got = extract_timespan("June 5th 2027", "en", ANCHOR)
    assert len(got) == 2
