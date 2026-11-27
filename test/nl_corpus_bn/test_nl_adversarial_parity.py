"""Bengali junk rows plus the shared English semantic-parity block.

Each pair is a Bengali phrase and the English staple that means the same.
Both must resolve to the same span under the anchor.  The two-way day words
কাল and পরশু have no pair: the locale refuses them (#1484).
"""
import pytest

from chronologia import extract_timespan

from ._corpus import ANCHOR, nomatch


@pytest.mark.parametrize("text", [
    "", "   ", "নমস্কার, কেমন আছেন?", "qwerty zxcvb", "এখানে কোনো তারিখ নেই।",
])
def test_junk_is_none(text):
    nomatch(text)


PAIRS = [
    ("আজ", "today"),
    ("গতকাল", "yesterday"),
    ("আগামীকাল", "tomorrow"),
    ("গত পরশু", "the day before yesterday"),
    ("আগামী পরশু", "the day after tomorrow"),
    ("তিন দিন আগে", "3 days ago"),
    ("এক দিন আগে", "1 day ago"),
    ("দশ দিন আগে", "10 days ago"),
    ("তিন দিন পরে", "in 3 days"),
    ("এক দিন পরে", "in 1 day"),
    ("দুই সপ্তাহ পরে", "in 2 weeks"),
    ("দুই মাস পরে", "in 2 months"),
    ("পাঁচ বছর পরে", "in 5 years"),
    ("দুই বছর আগে", "2 years ago"),
    ("দশ ঘণ্টা পরে", "in 10 hours"),
    ("পাঁচ মিনিট পরে", "in 5 minutes"),
    ("১৫ মিনিট পরে", "in 15 minutes"),
    ("তিন মাস আগে", "3 months ago"),
    ("এক সপ্তাহ আগে", "1 week ago"),
    ("আগামী সোমবার", "next monday"),
    ("আগামী শুক্রবার", "next friday"),
    ("গত মঙ্গলবার", "last tuesday"),
    ("গত সোমবার", "last monday"),
    ("আগামী সপ্তাহ", "next week"),
    ("গত মাস", "last month"),
    ("আগামী বছর", "next year"),
    ("গত বছর", "last year"),
    ("এই সপ্তাহ", "this week"),
    ("15:30", "15:30"),
    ("১৫:৩০", "15:30"),
    ("০৯:৩০", "09:30"),
    ("০০:০০", "00:00"),
    ("2019", "2019"),
    ("২০১৯", "2019"),
    ("১৯১৮", "1918"),
    ("১৫ আগস্ট", "august 15"),
    ("৫ জুলাই", "july 5"),
    ("15 মার্চ 2024", "15 march 2024"),
    ("১৫ মার্চ ২০২৪", "15 march 2024"),
    ("পয়লা জুলাই", "july 1"),
    ("দোসরা জুলাই", "july 2"),
    ("সোমবার", "monday"),
    ("শুক্রবার", "friday"),
    ("আজ সকাল নয়টায়", "today at 9 am"),
    ("আজ রাত নটায়", "today at 9 pm"),
    ("আজ সকালে", "this morning"),
    ("আজ সন্ধ্যা সাতটায়", "today at 7 pm"),
    ("জুলাই", "july"),
    ("ডিসেম্বর", "december"),
    ("মার্চ 2024", "march 2024"),
]


@pytest.mark.parametrize("bn_text,en_text", PAIRS)
def test_span_parity(bn_text, en_text):
    bn = extract_timespan(bn_text, "bn", ANCHOR)
    en = extract_timespan(en_text, "en", ANCHOR)
    assert bn is not None, f"bn {bn_text!r} did not parse"
    assert en is not None, f"en {en_text!r} did not parse"
    assert (bn[0].start, bn[0].end) == (en[0].start, en[0].end), (bn_text, en_text)
