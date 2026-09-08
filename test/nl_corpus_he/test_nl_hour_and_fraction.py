"""The Hebrew hour closed by an additive fraction.

Hebrew names quarter past and half past by suffixing the fraction with the
conjunction ו־ ("and"): "שלוש ורבע" is three and a quarter, "שלוש וחצי"
three and a half.  The conjunction is part of the word, so the reading is
additive by the surface itself and never counts toward the coming hour the
way Continental-Germanic "halb neun" does.

Anchor 2017-06-27 13:04.
"""
import pytest

from ._corpus import AstroDate, nomatch, parse, start


@pytest.mark.parametrize("text,hour,minute", [
    ("בשעה שלוש ורבע", 3, 15),
    ("בשעה שלוש וחצי", 3, 30),
    ("בשעה שמונה וחצי", 8, 30),
    ("מחר בשעה שלוש וחצי", 3, 30),
])
def test_the_additive_fraction_after_the_hour(text, hour, minute):
    assert start(text) == AstroDate(2017, 6, 28, hour, minute)
    assert parse(text).remainder == ""


def test_the_fraction_reads_through_a_meridiem():
    assert start("בשעה שבע וחצי בבוקר") == AstroDate(2017, 6, 28, 7, 30)
    assert parse("בשעה שבע וחצי בבוקר").remainder == ""


def test_the_bare_hour_is_unchanged():
    assert start("בשעה שלוש") == AstroDate(2017, 6, 28, 3, 0)


# ---------------------------------------------------------------------------
# The clock marker is required, not optional.  Hebrew writes a MEASURED
# QUANTITY with the same numeral-and-fraction surface -- "שתיים וחצי קילו" is
# two and a half kilos, "חמש ורבע מטר" five and a quarter metres -- so a bare
# numeral closed by a fraction names a time only where a marker says a clock
# follows.  Without that the phrase answers an hour and strands the noun that
# says what was being measured.
# ---------------------------------------------------------------------------

QUANTITIES = [
    "שתיים וחצי קילו",          # two and a half kilos
    "חמש ורבע מטר",             # five and a quarter metres
    "ארבע וחצי שנים",           # four and a half years
    "שתיים וחצי מיליון",        # two and a half million
    "עשר ורבע אחוז",            # ten and a quarter percent
    "קניתי שלוש וחצי לחמניות",  # I bought three and a half rolls
]


@pytest.mark.parametrize("text", QUANTITIES)
def test_a_measured_quantity_is_not_a_clock(text):
    nomatch(text)


def test_the_bare_numeral_and_fraction_is_not_a_clock():
    # the same ambiguity the quantities above turn on: with no marker there is
    # nothing to say this is a time rather than a count.
    nomatch("שלוש ורבע")
