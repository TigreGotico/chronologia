"""Adversarial Georgian cases plus the shared English semantic-parity block."""
import pytest

from ._corpus import ANCHOR, nomatch, parse


@pytest.mark.parametrize("text", [
    "", "   ", "გამარჯობა როგორ ხარ", "qwerty zxcvb", "აქ თარიღი არ არის",
])
def test_junk_is_none(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["წინ", "შემდეგ", "დღეები", "თვეები"])
def test_incomplete_offset(text):
    r = parse(text)
    assert r is None or r[0].start.date() == ANCHOR.date()


@pytest.mark.parametrize("text", [
    "hace tres días", "il y a trois jours", "vor drei Tagen",
    "three days ago",
])
def test_other_languages_are_not_matched(text):
    r = parse(text)
    assert r is None or r[0].start.date() == ANCHOR.date()


@pytest.mark.parametrize("text", ["32 იანვარი 2020", "0 მარტი 2020"])
def test_impossible_day_of_month(text):
    r = parse(text)
    if r is not None:
        assert 1 <= r[0].start.day <= 31


#: (Georgian, English) pairs that mean the same thing and must resolve to the
#: same span under the same anchor.
PAIRS = [
    ("დღეს", "today"),
    ("გუშინ", "yesterday"),
    ("ხვალ", "tomorrow"),
    ("გუშინწინ", "the day before yesterday"),
    ("ზეგ", "the day after tomorrow"),
    ("ერთი დღის წინ", "one day ago"),
    ("ორი დღის წინ", "two days ago"),
    ("სამი დღის წინ", "three days ago"),
    ("ხუთი დღის წინ", "five days ago"),
    ("ათი დღის წინ", "ten days ago"),
    ("ოცი დღის წინ", "twenty days ago"),
    ("ოცდაათი დღის წინ", "thirty days ago"),
    ("ორი დღის შემდეგ", "in two days"),
    ("სამი დღის შემდეგ", "in three days"),
    ("სამი თვის წინ", "three months ago"),
    ("ექვსი თვის წინ", "six months ago"),
    ("ორი თვის შემდეგ", "in two months"),
    ("ორი წლის წინ", "two years ago"),
    ("ათი წლის წინ", "ten years ago"),
    ("მომავალი თვე", "next month"),
    ("გასული თვე", "last month"),
    ("მომავალი წელი", "next year"),
    ("გასული წელი", "last year"),
    ("5 ივნისი 2020", "5 june 2020"),
    ("31 დეკემბერი 2000", "31 december 2000"),
    ("ორშაბათი", "monday"),
    ("პარასკევი", "friday"),
    ("2020", "2020"),
    ("15:30", "15:30"),
    ("შუადღე", "noon"),
]
