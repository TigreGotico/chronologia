"""কাল and পরশু name a day in EITHER direction, so they are refused.

Thompson (2012) lists "kal tomorrow, yesterday, kalke tomorrow, yesterday".
Only the verb's tense separates the readings, and this engine does not read
verbs.  CLDR 47 gives the one-direction forms আগামীকাল, গতকাল, আগামী পরশু
and গত পরশু, which resolve.  Issue #1484 asks a native speaker how the bare
words are used; the xfails below hold the readings the bench rows expect.
"""
import pytest

from ._corpus import day, nomatch, parse, start


@pytest.mark.parametrize("text", ["কাল", "কালকে", "পরশু"])
def test_a_bidirectional_day_word_is_refused(text):
    nomatch(text)


@pytest.mark.parametrize("text", [
    "কাল সকালে মা বাজারে যাবেন।",
    "কাল সন্ধ্যায় নাটকের মহড়া বসবে।",
    "পরশু দুপুরে ওরা আসবে।",
])
def test_a_bidirectional_day_word_refuses_its_day_part(text):
    nomatch(text)


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="#1484 bn Q1: bare কাল with a future verb")
def test_kal_with_future_verb_is_tomorrow():
    assert start("কাল সকালে মা বাজার থেকে ইলিশ কিনে আনবেন।") == day(1, 6)


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="#1484 bn Q2: bare পরশু with a future verb")
def test_porshu_with_future_verb_is_two_days_on():
    assert start("পরশু আমরা কলকাতা যাব।") == day(2)


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="#1484 bn Q4: বিকেল has no Bengali-script source")
def test_bikel_is_the_afternoon():
    assert start("আজ বিকেল পাঁচটায় চা খাব।") == day(0, 17)


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="#1484 bn Q8: থেকে ... পর্যন্ত clock range")
def test_clock_range():
    s = parse("আজ বিকাল পাঁচটা থেকে ছটা পর্যন্ত আসর চলবে।")[0]
    assert (s.start, s.end) == (day(0, 17), day(0, 18, 1))
