"""Ukrainian "<ordinal> числа": the day of the month named with the noun.

СУМ-11, s.v. число, sense 2, attests the calendar day as "21 числа", so
"двадцятого числа" names the twentieth of a month.  The bare genitive ordinal
stays unread: "двадцятого" alone can name the twentieth of any noun the
speaker left out.  At the Tuesday 27 June 2017 anchor the 20th, 23rd and 1st of
June have passed, so each rolls to July.
"""
import pytest

from ._corpus import ANCHOR, ad, nomatch, parse


def _day(month, day):
    return ad(ANCHOR.replace(month=month, day=day, hour=0, minute=0,
                             second=0, microsecond=0))


@pytest.mark.parametrize("text,month,day,remainder", [
    ("двадцятого числа", 7, 20, ""),
    ("двадцять третього числа", 7, 23, ""),
    ("першого числа", 7, 1, ""),
    ("нагадай мені двадцятого числа", 7, 20, "нагадай мені"),
])
def test_ordinal_with_chysla_is_a_day_of_month(text, month, day, remainder):
    r = parse(text)
    assert r is not None
    assert (r.span.start, r.span.end) == (_day(month, day),
                                          _day(month, day + 1))
    assert r.remainder == remainder


@pytest.mark.parametrize("text", [
    "двадцятого",            # the twentieth of an unnamed noun
    "20-го",
    "додайте три числа",     # "add three numbers"
    "двадцятого століття",   # "of the twentieth century"
])
def test_without_chysla_or_with_a_count_is_not_a_date(text):
    nomatch(text)
