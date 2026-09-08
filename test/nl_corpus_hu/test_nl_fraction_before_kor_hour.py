"""The Hungarian clock fraction in front of a -kor hour.

Hungarian counts the fraction toward the coming hour, as German and Dutch
do: "fél nyolc" is half past seven, not half past eight.  The temporal case
suffix -kor ("at") glues onto the numeral, so "fél nyolckor" is "at half
past seven".  Wiktionary: -kor, Hungarian temporal case suffix.

Anchor 2017-06-27 13:04; 13:04 is past every hour below, so each resolves to
the following morning.
"""
import pytest

from ._corpus import AstroDate, parse, start


@pytest.mark.parametrize("text,hour,minute", [
    ("fél nyolckor", 7, 30),
    ("negyed nyolckor", 7, 15),
    ("háromnegyed nyolckor", 7, 45),
    ("fél tízkor", 9, 30),
])
def test_fraction_before_a_kor_hour(text, hour, minute):
    assert start(text) == AstroDate(2017, 6, 28, hour, minute)
    assert parse(text).remainder == ""


@pytest.mark.parametrize("text,hour,minute", [
    # the suffixless fraction forms and the bare -kor hour already worked
    ("fél nyolc", 7, 30),
    ("negyed nyolc", 7, 15),
    ("háromnegyed nyolc", 7, 45),
    ("nyolckor", 8, 0),
])
def test_the_forms_that_already_read(text, hour, minute):
    assert start(text) == AstroDate(2017, 6, 28, hour, minute)


def test_the_daypart_still_binds_the_kor_hour():
    assert start("délután háromkor") == AstroDate(2017, 6, 27, 15, 0)
