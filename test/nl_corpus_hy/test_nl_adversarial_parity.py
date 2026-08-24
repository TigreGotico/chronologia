"""Adversarial Armenian cases plus the shared English semantic-parity block."""
import pytest

from chronologia import extract_timespan

from ._corpus import ANCHOR, nomatch, parse


@pytest.mark.parametrize("text", [
    "", "   ", "բարև ինչպես ես", "qwerty zxcvb", "այստեղ ամսաթիվ չկա",
])
def test_junk_is_none(text):
    nomatch(text)


@pytest.mark.parametrize("text", [
    "երեք օր", "հինգ շաբաթ", "տասը տարի", "3 օր",
])
def test_offset_without_a_postposition(text):
    """A bare count of units is a quantity, not a point in time: the whole
    direction lives in the postposition this phrase is missing."""
    nomatch(text)


@pytest.mark.parametrize("text", ["առաջ", "անց", "հետո", "ից", "օրեր"])
def test_incomplete_offset(text):
    r = parse(text)
    assert r is None or r[0].start.date() == ANCHOR.date()


@pytest.mark.parametrize("text", ["25:00", "15:99", "99:99"])
def test_impossible_clock(text):
    r = parse(text)
    if r is not None:
        assert 0 <= r[0].start.hour <= 23


@pytest.mark.parametrize("text", [
    "სამი დღის წინ", "hace tres días", "üç gün önce", "سه روز پیش",
])
def test_neighbouring_languages_are_not_matched(text):
    """Georgian, Spanish, Turkish and Persian all express the same offset;
    none of them may read as Armenian."""
    r = parse(text)
    assert r is None or r[0].start.date() == ANCHOR.date()


@pytest.mark.parametrize("text", ["ու", "և", "ամեն"])
def test_a_bare_function_word_names_no_time(text):
    nomatch(text)


def test_a_bare_numeral_is_not_a_year():
    """A spelled numeral folds to a digit, but a small digit is not a year."""
    nomatch("քսանհինգ")


#: (Armenian, English) pairs whose spans must match exactly under ANCHOR.
PAIRS = [
    ("այսօր", "today"),
    ("երեկ", "yesterday"),
    ("վաղը", "tomorrow"),
    ("նախանցյալ օրը", "the day before yesterday"),
    ("վաղը չէ մյուս օրը", "the day after tomorrow"),
    ("երեք օր առաջ", "three days ago"),
    ("տասնհինգ օր առաջ", "fifteen days ago"),
    ("երկու շաբաթ առաջ", "two weeks ago"),
    ("հինգ ամիս առաջ", "five months ago"),
    ("մեկ տարի առաջ", "one year ago"),
    ("տասը րոպե առաջ", "ten minutes ago"),
    ("երեք ժամ առաջ", "three hours ago"),
    ("երեք օրից", "in three days"),
    ("երեք օր անց", "in three days"),
    ("երկու շաբաթից", "in two weeks"),
    ("հինգ ամսից", "in five months"),
    ("երկու տարուց", "in two years"),
    ("քսան րոպեից", "in twenty minutes"),
    ("հաջորդ շաբաթ", "next week"),
    ("նախորդ շաբաթ", "last week"),
    ("այս ամիս", "this month"),
    ("նախորդ ամիս", "last month"),
    ("այս տարի", "this year"),
    ("հաջորդ տարի", "next year"),
    ("հունիսի 5 2027", "June 5th 2027"),
    ("05.06.2027", "June 5 2027"),
    ("2019 թ.", "2019"),
    ("ութ անց կես", "half past eight"),
    ("ժամը յոթը քառորդ անց", "quarter past seven"),
    ("կեսօրին", "noon"),
    ("կեսգիշերին", "midnight"),
    ("գարուն", "spring"),
    ("ձմեռ", "winter"),
    ("առավոտ", "morning"),
    ("մարտ", "March"),
    ("դեկտեմբեր", "December"),
    ("քսաներորդ դար", "the 20th century"),
]


@pytest.mark.parametrize("hy,en", PAIRS, ids=[p[1] for p in PAIRS])
def test_parity(hy, en):
    a = extract_timespan(hy, "hy", ANCHOR)
    b = extract_timespan(en, "en", ANCHOR)
    assert a is not None and b is not None
    assert (a[0].start, a[0].end) == (b[0].start, b[0].end)
