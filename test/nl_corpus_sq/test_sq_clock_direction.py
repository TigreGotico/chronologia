"""The Albanian clock, pinned in BOTH directions.

Albanian splits the hour asymmetrically.  Counting forward -- the half, the
quarter past, and any plain minute count -- names the hour already reached and
adds to it, so "shtatë e gjysmë" is 07:30 and never 06:30.  Counting backward
uses ``pa`` ("without, minus") and names the hour being approached, so "tre pa
çerek" is 02:45 and never 03:15.  Each direction is asserted against the other
one's wrong answer as well as its own right one, because the two failure modes
this construction invites are exactly a half read against the current hour and
a ``pa`` read as past the hour.
"""
import pytest

from ._corpus import span, start


def _hm(text):
    s = start(text)
    return s.hour, s.minute


# -- forward: the CURRENT hour ----------------------------------------------

@pytest.mark.parametrize("text,expected", [
    ("shtatë e gjysmë", (7, 30)),
    ("shtatë e gjysëm", (7, 30)),
    ("tetë e gjysmë", (8, 30)),
    ("dhjetë e gjysmë", (10, 30)),
    ("dy e gjysmë", (2, 30)),
])
def test_half_names_the_current_hour(text, expected):
    assert _hm(text) == expected


@pytest.mark.parametrize("text,expected", [
    ("dy e një çerek", (2, 15)),
    ("dy e çerek", (2, 15)),
    ("nëntë e çerek", (9, 15)),
    ("njëmbëdhjetë e çerek", (11, 15)),
])
def test_quarter_past_names_the_current_hour(text, expected):
    assert _hm(text) == expected


@pytest.mark.parametrize("text,expected", [
    ("shtatë e njëzet e pesë", (7, 25)),
    ("tetë e dyzet", (8, 40)),
    ("nëntë e pesë", (9, 5)),
    ("dhjetë e njëzet", (10, 20)),
])
def test_plain_minutes_are_stated_literally(text, expected):
    """Outside the quarter marks Albanian says the hour and the minute count,
    with no idiom: "shtatë e njëzet e pesë" is 07:25."""
    assert _hm(text) == expected


# -- backward: ``pa`` and the NEXT hour -------------------------------------

@pytest.mark.parametrize("text,expected", [
    ("tre pa çerek", (2, 45)),
    ("dhjetë pa çerek", (9, 45)),
    ("gjashtë pa çerek", (5, 45)),
    ("dymbëdhjetë pa çerek", (11, 45)),
])
def test_quarter_to_counts_back_from_the_named_hour(text, expected):
    assert _hm(text) == expected


def test_quarter_to_one_rolls_back_to_twelve():
    """A twelve-hour reckoning spells the hour before one as twelve, so
    "një pa çerek" is 12:45, not 00:45."""
    assert _hm("një pa çerek") == (12, 45)


# -- the adversarial pins: neither direction may become the other -----------

@pytest.mark.parametrize("text,named_hour", [
    ("shtatë e gjysmë", 7), ("tetë e gjysmë", 8), ("dhjetë e gjysmë", 10),
])
def test_half_is_never_the_preceding_hour(text, named_hour):
    """The Icelandic/Latvian/Lithuanian reading -- half TOWARD the named hour
    -- would put "shtatë e gjysmë" at 06:30.  Albanian does not do that."""
    assert _hm(text) != (named_hour - 1, 30)
    assert _hm(text) == (named_hour, 30)


@pytest.mark.parametrize("text,named_hour", [
    ("tre pa çerek", 3), ("dhjetë pa çerek", 10), ("gjashtë pa çerek", 6),
])
def test_pa_never_reads_as_past_the_hour(text, named_hour):
    """``pa`` subtracts.  Read additively it would give (named hour):15; read
    as a bare hour it would give (named hour):00.  Both are wrong."""
    hour, minute = _hm(text)
    assert (hour, minute) != (named_hour, 15)
    assert (hour, minute) != (named_hour, 0)
    assert (hour, minute) == (named_hour - 1, 45)


def test_the_two_fraction_readings_differ_by_half_an_hour():
    """Same quarter word, opposite connectives: "dy e çerek" (02:15) and "tre
    pa çerek" (02:45) sit half an hour apart, which they could not if the
    engine collapsed ``e`` and ``pa`` into one direction."""
    past = span("dy e çerek").start
    to = span("tre pa çerek").start
    assert (to.hour, to.minute) == (past.hour, past.minute + 30)


# -- digital and landmark forms ---------------------------------------------

@pytest.mark.parametrize("text,expected", [
    ("07:30", (7, 30)), ("15:45", (15, 45)), ("00:00", (0, 0)),
    ("23:59", (23, 59)),
])
def test_digital_clock(text, expected):
    assert _hm(text) == expected


@pytest.mark.parametrize("text,expected", [
    ("mesnatë", (0, 0)), ("mesdita", (12, 0)), ("e mesnatës", (0, 0)),
    ("e mesditës", (12, 0)),
])
def test_landmarks(text, expected):
    assert _hm(text) == expected


@pytest.mark.parametrize("text,expected", [
    ("ora 8 e 25 e mëngjesit", (8, 25)),
    ("ora 8 e 40 e mbrëmjes", (20, 40)),
    ("8 e 40 e darkës", (20, 40)),
    ("ora tetë", (8, 0)),
])
def test_the_hour_word_and_the_meridiem(text, expected):
    assert _hm(text) == expected
