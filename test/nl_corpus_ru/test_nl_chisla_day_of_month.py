"""Russian "<ordinal> числа": the day of the month named with the noun.

"число" in its calendar sense is "день календарного месяца" (Wiktionary, s.v.
число, sense 3), so "двадцатого числа" names the twentieth of a month.  The
bare genitive ordinal stays unread: "двадцатого" alone can name the twentieth
of any noun the speaker left out.  At the Tuesday 27 June 2017 anchor the 20th,
23rd and 1st of June have passed, so each rolls to July; the 27th is today.
"""
import pytest

from ._corpus import ANCHOR, ad, nomatch, parse


def _day(month, day):
    return ad(ANCHOR.replace(month=month, day=day, hour=0, minute=0,
                             second=0, microsecond=0))


@pytest.mark.parametrize("text,month,day,remainder", [
    ("двадцатого числа", 7, 20, ""),
    ("двадцать третьего числа", 7, 23, ""),
    ("первого числа", 7, 1, ""),
    ("двадцать седьмого числа", 6, 27, ""),
    ("напомни мне двадцатого числа", 7, 20, "напомни мне"),
])
def test_ordinal_with_chisla_is_a_day_of_month(text, month, day, remainder):
    r = parse(text)
    assert r is not None
    assert (r.span.start, r.span.end) == (_day(month, day),
                                          _day(month, day + 1))
    assert r.remainder == remainder


@pytest.mark.parametrize("text", [
    "двадцатого",           # the twentieth of an unnamed noun
    "20-го",
    "сложите три числа",    # "add three numbers"
    "введите два числа",    # "enter two numbers"
    "двадцатого века",      # "of the twentieth century"
])
def test_without_chisla_or_with_a_count_is_not_a_date(text):
    nomatch(text)
