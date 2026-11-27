"""कल before a verb in the simple future is tomorrow.

Kamta Prasad Guru, Hindi Vyakaran (1927), section "सामान्य भविष्यत् काल":
the simple future is the subjunctive form plus गा, गे or गी, as in जाऊँगा,
जायेंगे, जायगी, जाओगी.  Any verb with such an ending sets the direction, not
only the verbs listed in marker_tense_future.voc.  Anchor: Tuesday
2017-06-27, so tomorrow is 2017-06-28.
"""
from datetime import datetime

import pytest

from ._corpus import parse


@pytest.mark.parametrize("text", [
    "मैं कल जाऊँगा",
    "कल हम उनकी मदद करेंगे",
    "वह कल खाना बनाएगी",
    "तुम कल आओगे",
])
def test_kal_before_a_future_verb_is_tomorrow(text):
    r = parse(text)
    assert r[0].start.datetime() == datetime(2017, 6, 28)


@pytest.mark.parametrize("text,start,end", [
    ("कल सुबह हम उनकी मदद करेंगे", 4, 12),
    ("कल शाम को हम पकौड़े खाएँगे", 16, 20),
])
def test_kal_daypart_before_a_future_verb_is_tomorrow(text, start, end):
    s = parse(text)[0]
    assert (s.start.datetime(), s.end.datetime()) == (
        datetime(2017, 6, 28, start), datetime(2017, 6, 28, end))


def test_a_noun_in_ogi_sets_no_direction():
    assert parse("कल रोगी") is None
