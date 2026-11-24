"""The da clock word before a digit clock (TigreGotico/chronologia#1375)."""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27)
ISSUE = pytest.mark.xfail(
    strict=True, reason="https://github.com/TigreGotico/chronologia/issues/1375")


@pytest.mark.parametrize("lang, text", [
    ("sv", "Påminn mig klockan 10:45"),
    ("nb", "Minn meg klokka 10:45"),
    ("da", "Påmind mig klokken ti"),
])
def test_the_clock_word_leaves_the_remainder(lang, text):
    span, remainder = extract_timespan(text, lang, ANCHOR)
    assert span.start.hour == 10
    assert remainder.split() == text.split()[:2]


@ISSUE
@pytest.mark.parametrize("text", [
    "Påmind mig klokken 10:45", "Påmind mig kl. 10:45", "Påmind mig kl 10:45"])
def test_da_clock_word_before_a_digit_clock_leaves_the_remainder(text):
    span, remainder = extract_timespan(text, "da", ANCHOR)
    assert (span.start.hour, span.start.minute) == (10, 45)
    assert remainder == "Påmind mig"
