"""The Belarusian spoken clock, which names the COMING hour in both halves.

Two independent sources, each with worked numeric examples, fix the direction.

Вінцук Вячорка, "Каторая гадзіна?", Радыё Свабода
(https://www.svaboda.org/a/katoraja-hadzina/30449819.html) states the rule and
works it: the first half of the hour takes на plus the accusative ordinal of
the coming hour ("дзесяць хвілін на першую", "палова на пятую"), the second
takes без or за ("безь дзесяці першая", "за квадранец восьмая", "без дваццаці
пяці дзясятая").

The Тлумачальны слоўнік беларускай мовы (Інстытут мовазнаўства імя Якуба
Коласа) gives the same direction independently, in its own worked citations:
s.v. палова, "Момант, які адпавядае сярэдзіне якой-н. гадзіны. Гадзіннік
паказваў палову пятай" -- the middle of the FIFTH hour, 04:30; s.v. палавіна,
"Палавіна восьмай вечара" -- 19:30; s.v. чвэрць, "Чацвёртая частка гадзіны
(пятнаццаць мінут). Гадзіннік паказваў без чвэрці адзінаццаць" -- 10:45; and
s.v. без, "Роўна без дваццаці восем вечара" -- 19:40.

Every case is pinned in BOTH directions: the right reading asserted present
and the inverted reading asserted absent, because a clock whose direction is
flipped still produces a perfectly plausible time.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, nomatch, parse, start


def _next_time(h, mi):
    cand = ANCHOR.replace(hour=h, minute=mi, second=0, microsecond=0)
    if cand <= ANCHOR:
        cand += timedelta(days=1)
    return ad(cand)


#: (surface, hour, minute) -- the first half of the hour, на + the accusative
#: ordinal of the hour being counted toward.  The named ordinal is always ONE
#: MORE than the hour of the resulting time.
TOWARD = [
    ("палова на другую", 1, 30), ("палова на трэцюю", 2, 30),
    ("палова на пятую", 4, 30), ("палова на шостую", 5, 30),
    ("палова на сёмую", 6, 30), ("палова на восьмую", 7, 30),
    ("палова на дзявятую", 8, 30), ("палова на дзясятую", 9, 30),
    ("палавіна на пятую", 4, 30),
    ("чвэрць на другую", 1, 15), ("чвэрць на пятую", 4, 15),
    ("чвэрць на сёмую", 6, 15), ("чвэрць на дванаццатую", 11, 15),
    ("квадранец на сёмую", 6, 15), ("квадранец на пятую", 4, 15),
]


@pytest.mark.parametrize("text,h,mi", TOWARD)
def test_na_names_the_coming_hour(text, h, mi):
    assert start(text) == _next_time(h, mi)


@pytest.mark.parametrize("text,h,mi", TOWARD)
def test_na_is_never_the_stated_hour(text, h, mi):
    """The additive reading -- "палова на пятую" == 05:30 -- must never
    occur."""
    assert start(text).hour != h + 1


def test_the_half_toward_one_is_twelve_thirty():
    """Belarusian reckons the toward-hour clock in twelve hours, so the hour
    that rolls back from one is spoken as twelve, not zero."""
    assert (start("палова на першую").hour,
            start("палова на першую").minute) == (12, 30)


#: The dictionary's connector-less genitive form of the same reading.
GENITIVE_HALF = [
    ("палова пятай", 4, 30), ("палавіна восьмай", 7, 30),
    ("палова дзявятай", 8, 30), ("палова трэцяй", 2, 30),
]


@pytest.mark.parametrize("text,h,mi", GENITIVE_HALF)
def test_bare_genitive_half_names_the_coming_hour(text, h, mi):
    assert start(text) == _next_time(h, mi)


@pytest.mark.parametrize("text,h,mi", GENITIVE_HALF)
def test_bare_genitive_half_is_never_the_stated_hour(text, h, mi):
    assert start(text).hour != h + 1


#: (surface, hour, minute) -- the second half of the hour, без/за subtracting
#: from the coming hour.
SUBTRACTIVE = [
    ("без чвэрці адзінаццаць", 10, 45), ("без чвэрці дзевяць", 8, 45),
    ("без чвэрці шостая", 5, 45), ("бяз чвэрці восьмая", 7, 45),
    ("без дзесяці першая", 12, 50), ("без дзесяці дзявятая", 8, 50),
    ("без пяці восьмая", 7, 55), ("без дваццаці дзясятая", 9, 40),
    ("без пятнаццаці шостая", 5, 45),
    ("за квадранец восьмая", 7, 45), ("за чвэрць шостая", 5, 45),
    ("за дзесяць хвілін дзявятая", 8, 50),
    ("за дваццаць хвілін сёмая", 6, 40),
    ("без дваццаці восем", 7, 40),
]


@pytest.mark.parametrize("text,h,mi", SUBTRACTIVE)
def test_subtractive_names_the_coming_hour(text, h, mi):
    assert start(text) == _next_time(h, mi)


@pytest.mark.parametrize("text,h,mi", SUBTRACTIVE)
def test_subtractive_never_lands_on_the_stated_hour(text, h, mi):
    """"без чвэрці адзінаццаць" is 10:45, never 11:15 and never 11:45."""
    s = start(text)
    assert not (s.hour == h + 1 or (s.hour, s.minute) == (h, 60 - mi))


def test_the_four_worked_dictionary_examples():
    """The exact citations the direction was read off, with their meridiems."""
    assert (start("палова пятай").hour, start("палова пятай").minute) == (4, 30)
    assert (start("палавіна восьмай вечара").hour,
            start("палавіна восьмай вечара").minute) == (19, 30)
    assert (start("без чвэрці адзінаццаць").hour,
            start("без чвэрці адзінаццаць").minute) == (10, 45)
    assert (start("без дваццаці восем вечара").hour,
            start("без дваццаці восем вечара").minute) == (19, 40)


def test_the_three_worked_column_examples():
    """Вячорка's own numeric examples."""
    assert (start("палова на пятую").hour,
            start("палова на пятую").minute) == (4, 30)
    assert (start("без дзесяці першая").hour,
            start("без дзесяці першая").minute) == (12, 50)
    assert (start("за квадранец восьмая").hour,
            start("за квадранец восьмая").minute) == (7, 45)


@pytest.mark.parametrize("text,h", [
    ("а другой", 2), ("а пятай", 5), ("аб адзінаццатай", 11),
    ("а сёмай", 7), ("а другой гадзіне", 2), ("а дзявятай гадзіне", 9),
])
def test_the_kali_answer_names_the_hour_itself(text, h):
    """Answering "калі?" with а/аб plus the locative ordinal names that hour
    on the dot -- no toward-hour arithmetic is involved."""
    s = start(text)
    assert (s.hour, s.minute) == (h, 0)


@pytest.mark.parametrize("text,h", [
    ("а сёмай раніцы", 7), ("а сёмай вечара", 19), ("а дзясятай вечара", 22),
])
def test_meridiem_qualifies_the_spoken_hour(text, h):
    assert start(text).hour == h


@pytest.mark.parametrize("text,h,mi", [
    ("15:30", 15, 30), ("09:05", 9, 5), ("00:00", 0, 0), ("23:59", 23, 59),
    ("07:30", 7, 30), ("12:00", 12, 0),
])
def test_digit_clock(text, h, mi):
    s = start(text)
    assert (s.hour, s.minute) == (h, mi)


@pytest.mark.parametrize("text,h", [("апоўначы", 0), ("апоўдні", 12),
                                    ("поўнач", 0), ("поўдзень", 12)])
def test_clock_landmarks(text, h):
    assert start(text).hour == h


@pytest.mark.parametrize("text", [
    "палова на", "чвэрць на", "без чвэрці", "за квадранец", "палова",
])
def test_an_incomplete_clock_is_not_a_time(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["дзве гадзіны", "тры гадзіны"])
def test_a_cardinal_hour_count_is_not_a_clock_reading(text):
    """"дзве гадзіны" is a DURATION of two hours; only the ordinal plus the
    nominative/locative hour noun ("другая гадзіна") reads as a time."""
    r = parse(text)
    assert r is None or r[0].start.hour != 2


@pytest.mark.parametrize("text,h", [("другая гадзіна", 2),
                                    ("дзясятая гадзіна", 10)])
def test_the_ordinal_hour_noun_is_a_clock_reading(text, h):
    assert start(text).hour == h
