"""μεσημέρι as the post-meridiem cue on an explicit hour.

Greek names the early afternoon μεσημέρι and the later afternoon απόγευμα,
and both serve as a +12 cue behind a spoken hour: el.wikipedia writes "από
τις 12 το μεσημέρι μέχρι τις 3 το απόγευμα" in one sentence (Σταύρωση του
Ιησού Χριστού).  The bare noun keeps its landmark reading of noon.

Anchor 2017-06-27 13:04.
"""
import pytest

from ._corpus import AstroDate, parse, start


@pytest.mark.parametrize("text,day,hour", [
    # 13:00 is behind the 13:04 anchor, so one o'clock is tomorrow's
    ("στη μία το μεσημέρι", 28, 13),
    ("μία το μεσημέρι", 28, 13),
    # 14:00 is still ahead of it, so two o'clock is today's
    ("δύο το μεσημέρι", 27, 14),
])
def test_the_hour_takes_the_midday_cue(text, day, hour):
    assert start(text) == AstroDate(2017, 6, day, hour, 0)
    assert parse(text).remainder == ""


@pytest.mark.parametrize("text", ["δώδεκα το μεσημέρι", "στις 12 το μεσημέρι"])
def test_twelve_at_midday_is_noon_not_midnight(text):
    """The cue is not a blind +12: twelve at midday stays twelve."""
    assert start(text) == AstroDate(2017, 6, 28, 12, 0)
    assert parse(text).remainder == ""


def test_the_bare_noun_is_still_the_noon_landmark():
    assert start("το μεσημέρι") == AstroDate(2017, 6, 28, 12, 0)


@pytest.mark.parametrize("text,day,hour", [
    ("μία το απόγευμα", 28, 13),
    ("οκτώ το βράδυ", 27, 20),
])
def test_the_other_daypart_cues_are_unchanged(text, day, hour):
    assert start(text) == AstroDate(2017, 6, day, hour, 0)
