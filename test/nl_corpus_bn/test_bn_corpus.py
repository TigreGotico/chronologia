"""Bengali dates and times in whole sentences.

Sources of the words are in the headers of ``chronologia/locale/bn``.  The
anchor is Tuesday 2017-06-27 13:04.
"""
import pytest

from ._corpus import ANCHOR, ad, day, nomatch, parse, span, start


@pytest.mark.parametrize("text,offset", [
    ("আজ আমরা সবাই মিলে দিদিমার বাড়িতে যাব।", 0),
    ("আজকে বাজারে খুব ভিড় ছিল।", 0),
    ("গতকাল সারাদিন বৃষ্টি হয়েছিল।", -1),
    ("গতকালের বৃষ্টিতে রাস্তাগুলো জলে ডুবে আছে।", -1),
    ("আগামীকাল আমাদের স্কুল বন্ধ থাকবে।", 1),
    ("গত পরশু মামা এসেছিলেন।", -2),
    ("আগামী পরশু আমরা কলকাতা যাব।", 2),
])
def test_day_words(text, offset):
    s = span(text)
    assert (s.start, s.end) == (day(offset), day(offset + 1))


@pytest.mark.parametrize("text,offset", [
    ("গত সোমবার সারাদিন বৃষ্টি হয়েছিল।", -1),      # Mon 26 Jun
    ("গত বুধবার অফিসে খুব কাজ ছিল।", -6),          # Wed 21 Jun
    ("গত শুক্রবার আমরা সিনেমা দেখেছিলাম।", -4),     # Fri 23 Jun
    ("আগামী সপ্তাহের শনিবার আমরা বেড়াতে যাব।", 11),  # Sat 8 Jul
    ("পরের সপ্তাহের সোমবার মেলা শুরু হবে।", 6),     # Mon 3 Jul
])
def test_weekdays(text, offset):
    assert start(text) == day(offset)


@pytest.mark.parametrize("text,offset", [
    ("চার দিন পরে লাইব্রেরিতে বইমেলা শুরু হবে।", 4),
    ("এক দিন পরেই চিঠিটা পৌঁছে যাবে।", 1),
    ("প্রদর্শনী শুরু হবে আজ থেকে তিন দিন পরে।", 3),
    ("তিন দিন আগে দাদু গ্রাম থেকে ফিরেছেন।", -3),
])
def test_day_offsets(text, offset):
    assert start(text) == day(offset, ANCHOR.hour, ANCHOR.minute)


def test_year_offset_past():
    assert start("দুই বছর আগে আমরা এই বাড়িতে এসেছিলাম।") == ad(
        ANCHOR.replace(year=2015))


@pytest.mark.parametrize("text,offset,h,mi", [
    ("আজ সকাল সাড়ে পাঁচটায় হাঁটতে বেরোব।", 0, 5, 30),
    ("আজ সকাল নয়টায় দুধওয়ালা আসবে।", 0, 9, 0),
    ("আজ সন্ধ্যা পৌনে সাতটায় দোকানে যাব।", 0, 18, 45),
    ("আজ সন্ধ্যা সোয়া ছটায় আড্ডা বসবে।", 0, 18, 15),
    ("আজ রাত নটায় গানের আসর বসবে।", 0, 21, 0),
    ("আজ রাত্রি দশটায় ট্রেন ছাড়বে।", 0, 22, 0),
    ("আজ দুপুর আড়াইটেয় ডাক্তারের কাছে যাব।", 0, 14, 30),
    ("আজ বিকাল চারটেয় খেলা শুরু।", 0, 16, 0),
    ("দুই দিন পরে সন্ধ্যা সাতটায় আসর বসবে।", 2, 19, 0),
    ("পাঁচ দিন পরে রাত নটায় আমরা তারা দেখব।", 5, 21, 0),
])
def test_clock_after_a_day_part(text, offset, h, mi):
    assert start(text) == day(offset, h, mi)


def test_bengali_digits_clock():
    assert start("সভা ১৫:৩০ মিনিটে শুরু হবে।") == day(0, 15, 30)


@pytest.mark.parametrize("text,m,d", [
    ("পয়লা জুলাই আমাদের পরীক্ষা।", 7, 1),
    ("দোসরা জুলাই মামা আসবেন।", 7, 2),
    ("তেসরা আগস্ট ছুটি।", 8, 3),
    ("১৫ আগস্ট স্বাধীনতা দিবস।", 8, 15),
])
def test_calendar_dates(text, m, d):
    assert start(text) == ad(ANCHOR.replace(month=m, day=d, hour=0, minute=0))


def test_precomposed_and_nukta_ya_are_one_letter():
    precomposed = "পয়লা জুলাই"
    nukta = "পয়লা জুলাই"
    assert start(precomposed) == start(nukta) == day(4)


def test_morning_today():
    s = span("আজ সকালে মা পিঠে বানিয়েছেন।")
    assert (s.start, s.end) == (day(0, 6), day(0, 12))


@pytest.mark.parametrize("text", [
    "বাজার থেকে ফেরার পথে মা দুটো পাকা আম কিনে এনেছেন।",
    "মা তিনটে পাকা আম কিনে এনেছেন।",
    "সবার মঙ্গল কামনা করে মা প্রদীপ জ্বালালেন।",
    "শীতের এক সকালে দাদু আমাকে মাছ ধরতে নিয়ে গিয়েছিলেন।",
    "শীতের এক কুয়াশাভরা সকালে দিদিমা গুড় বানাতেন।",
    "শহরের অফিসপাড়ায় কর্মদিবস যেন শেষ হতে চায় না।",
    "নদীর ধারে বসে আমরা গল্প করলাম।",
])
def test_no_date(text):
    nomatch(text)


@pytest.mark.parametrize("text,h", [
    ("রাতে পাড়ার মাঠে গানের আসর বসবে।", 20),
    ("সন্ধ্যায় পাড়ার মাঠে নাটক হবে।", 18),
    ("চলো। সকালে বাজারে যাব।", 6),
])
def test_bare_day_part_at_sentence_start_is_today(text, h):
    assert start(text) == day(0, h)


@pytest.mark.parametrize("text", [
    "বর্ষার ভেজা সকালে অফিসে পৌঁছাতে দেরি হলো।",
    "কারখানার শ্রমিকদের কাছে কর্মদিবস মানে সন্ধ্যায় বাড়ি ফেরার অপেক্ষা।",
    "মা দুটো আম এনেছিলেন, যা আমরা দুপুরে ভাগ করে খেলাম।",
])
def test_bare_day_part_inside_a_sentence_names_no_day(text):
    nomatch(text)
