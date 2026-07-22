"""Roman Kalends/Nones/Ides reckoning: inclusive backward counting resolved
by ``roman_to_julian`` directly.

Gold values ported from the reckoning-core assertions the parser exercised
through its ``roman_date`` engine stage (roman_calendar_reckoning_reference.
html).  ``roman_to_julian`` returns the Julian-calendar ``(year, month,
day)`` label; ``count`` is the inclusive backward ordinal (1 == the anchor
day itself, 2 == pridie).  The vocabulary surfaces ("ad III kalendas") are
parser-side; the reckoning values are the core.
"""
import pytest

from chronologia.roman import roman_to_int, roman_to_julian


# -- roman_to_int: strict, canonical Roman-numeral parsing ----------------

@pytest.mark.parametrize("text,value", [
    ("I", 1), ("IV", 4), ("IX", 9), ("XII", 12), ("XIV", 14),
    ("XL", 40), ("XC", 90), ("CD", 400), ("CM", 900),
    ("MMXX", 2020), ("MCMLXXXIV", 1984), ("MMMCMXCIX", 3999),
    ("iii", 3),                         # case-insensitive parse
])
def test_roman_to_int_valid(text, value):
    assert roman_to_int(text) == value


@pytest.mark.parametrize("text", [
    "", "IIII", "VV", "LL", "DD", "IC", "IL", "XD", "IIX", "VX",
    "MMMM", "ABC", "12", "X I",
])
def test_roman_to_int_rejects_malformed(text):
    assert roman_to_int(text) is None


# -- the canonical worked examples ---------------------------------------

def test_ad_iii_kalendas_aprilis_is_march_30():
    # a.d. III Kal. Apr. == 30 March (counting back from 1 April)
    assert roman_to_julian(2017, 4, "kalends", 3) == (2017, 3, 30)


def test_idibus_martiis_is_march_15():
    assert roman_to_julian(2017, 3, "ides", 1) == (2017, 3, 15)


def test_pridie_idus_martias_is_march_14():
    # pridie == the day before == count 2
    assert roman_to_julian(2017, 3, "ides", 2) == (2017, 3, 14)


# -- Nones/Ides late-month rule (March Nones == 7th) ---------------------

def test_nonae_martiae_is_march_7():
    assert roman_to_julian(2017, 3, "nones", 1) == (2017, 3, 7)


def test_nonae_ianuariae_is_january_5():
    # January is not a late month: Nones == 5th
    assert roman_to_julian(2017, 1, "nones", 1) == (2017, 1, 5)


# -- Kalends counting into the previous month ----------------------------

def test_ad_iii_kalendas_martias_is_february_27():
    assert roman_to_julian(2017, 3, "kalends", 3) == (2017, 2, 27)


# -- adversarial: out-of-span ordinals -> None ---------------------------

@pytest.mark.parametrize("year,month,anchor,count", [
    (2017, 4, "kalends", 18),   # overshoots the previous anchor (Ides of March)
    (2017, 4, "kalends", 0),    # count < 1
])
def test_out_of_span_returns_none(year, month, anchor, count):
    assert roman_to_julian(year, month, anchor, count) is None
