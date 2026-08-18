"""Spelled numerals, which 1..99 must be looked up rather than derived.

Hindi's tens+unit numerals are suppletive: बयालीस (42) is not built from
चालीस and दो, छियालीस (46) and सैंतालीस (47) share no affix, and the nasal in
पैंतीस (35) has no counterpart in बत्तीस (32).  Every value is its own table
entry, so the cases below are chosen where a compositional guess would go
wrong -- the boundaries of each decade, the -आईस / -तीस / -तालीस / -हत्तर /
-असी / -आनवे families, and the alternative spellings the dictionary attests.

Expected values are the ``{{number box|hi|N}}`` headers of the words' own
en.wiktionary.org entries, not the parser's reading of them.
"""
import pytest

from ._corpus import ANCHOR, nomatch, span, start

#: (spelled numeral, its value) -- the boundary of every decade, plus the
#: words a compositional reader would get wrong.
SPELLED = [
    ("एक", 1), ("दो", 2), ("नौ", 9), ("दस", 10),
    ("ग्यारह", 11), ("उन्नीस", 19), ("बीस", 20),
    ("इक्कीस", 21), ("पच्चीस", 25), ("उनतीस", 29), ("तीस", 30),
    ("बत्तीस", 32), ("पैंतीस", 35), ("अड़तीस", 38), ("उनतालीस", 39),
    ("चालीस", 40), ("बयालीस", 42), ("छियालीस", 46), ("सैंतालीस", 47),
    ("उनचास", 49), ("पचास", 50), ("तिरपन", 53), ("उनसठ", 59),
    ("साठ", 60), ("छियासठ", 66), ("सड़सठ", 67), ("उनहत्तर", 69),
    ("सत्तर", 70), ("पचहत्तर", 75), ("अठहत्तर", 78), ("उन्यासी", 79),
    ("अस्सी", 80), ("बयासी", 82), ("अट्ठासी", 88), ("नवासी", 89),
    ("नब्बे", 90), ("इक्यानवे", 91), ("छियानवे", 96), ("निन्यानवे", 99),
]


@pytest.mark.parametrize("word,value", SPELLED)
def test_spelled_numeral_reads_its_own_value(word, value):
    """Read through the past-offset construction, whose magnitude is the
    numeral: "<n> दिन पहले" is n days before the anchor."""
    from datetime import timedelta
    expected = (ANCHOR - timedelta(days=value)).date()
    s = start(f"{word} दिन पहले")
    assert (s.year, s.month, s.day) == (expected.year, expected.month,
                                        expected.day)


@pytest.mark.parametrize("word,value", [
    ("पाँच", 5), ("पांच", 5),          # with and without the candrabindu
    ("छह", 6), ("छः", 6), ("छै", 6),   # three attested spellings of six
    ("सत्रह", 17), ("सत्तरह", 17),
    ("पंद्रह", 15), ("पन्द्रह", 15),
    ("निन्यानवे", 99), ("निनानवे", 99),
    ("नब्बे", 90), ("नव्वे", 90),
])
def test_alternative_spellings_name_the_same_number(word, value):
    from datetime import timedelta
    expected = (ANCHOR - timedelta(days=value)).date()
    s = start(f"{word} दिन पहले")
    assert (s.year, s.month, s.day) == (expected.year, expected.month,
                                        expected.day)


@pytest.mark.parametrize("text,year", [
    ("दो हज़ार चौबीस", 2024),
    ("दो हज़ार", 2000),
    ("उन्नीस सौ नब्बे", 1990),
    ("उन्नीस सौ अठारह", 1918),
    ("दो हज़ार सत्रह", 2017),
])
def test_composed_years(text, year):
    """सौ multiplies the group before it and हज़ार closes it into the total."""
    s = span(text)
    assert s.start.year == year and s.start.month == 1 and s.start.day == 1
    assert s.end.year == year + 1


@pytest.mark.parametrize("text,y,m,d", [
    ("१५ मार्च २०२४", 2024, 3, 15),
    ("१ जनवरी २०००", 2000, 1, 1),
    ("३१ दिसंबर १९९९", 1999, 12, 31),
    ("९ अगस्त २०१७", 2017, 8, 9),
])
def test_devanagari_digits_read_as_numbers(text, y, m, d):
    from chronologia.astrodate import AstroDate
    assert start(text) == AstroDate(y, m, d)


@pytest.mark.parametrize("dev,ascii_text", [
    ("१५ मार्च २०२४", "15 मार्च 2024"),
    ("५ जुलाई", "5 जुलाई"),
    ("३ दिन पहले", "3 दिन पहले"),
    ("१५:३०", "15:30"),
])
def test_the_two_digit_systems_agree(dev, ascii_text):
    assert span(dev).start == span(ascii_text).start
    assert span(dev).end == span(ascii_text).end


@pytest.mark.parametrize("text", ["इक दिन पहले", "यक दिन पहले", "शत साल पहले",
                                  "सद साल पहले"])
def test_bound_and_literary_numerals_do_not_fold(text):
    """इक is a bound prefix and यक a Persian borrowing; शत and सद are the
    literary hundreds.  None is the everyday counting word, so none ships and
    the phrase does not resolve to an offset."""
    nomatch(text)


@pytest.mark.parametrize("text", ["तीन दिन", "पाँच हफ़्ते", "दस साल", "3 दिन"])
def test_a_count_without_a_marker_is_not_a_time(text):
    nomatch(text)
