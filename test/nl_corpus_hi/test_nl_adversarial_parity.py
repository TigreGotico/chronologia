"""Adversarial Hindi cases plus the shared English semantic-parity block."""
from datetime import timedelta

import pytest

from chronologia import extract_timespan

from ._corpus import ANCHOR, nomatch, parse, span


@pytest.mark.parametrize("text", [
    "", "   ", "नमस्ते आप कैसे हैं", "qwerty zxcvb", "यहाँ कोई तारीख़ नहीं है",
])
def test_junk_is_none(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["25:00", "15:99", "99:99", "२५:००"])
def test_impossible_clock(text):
    r = parse(text)
    if r is not None:
        assert 0 <= r[0].start.hour <= 23


@pytest.mark.parametrize("text", [
    "przed 2 laty", "через 3 дня", "prieš 3 dienas", "٣ أيام",
])
def test_foreign_not_matched(text):
    """Other languages' phrasings must not read as Hindi."""
    r = parse(text)
    assert r is None or r[0].start.date() == ANCHOR.date()


def test_a_devanagari_word_is_not_shredded_into_consonants():
    """Devanagari writes its vowels as combining marks, so a tokenizer that
    stops a letter run at the first matra turns मार्च into three one-letter
    tokens and no month name can ever match."""
    from chronologia.extract.model import TokenizerModes
    from chronologia.extract.tokenizer import Tokenizer
    tokenizer = Tokenizer(TokenizerModes())
    for text in ["15 मार्च 2024", "साढ़े तीन बजे", "पाँचवीं सदी",
                 "हफ़्ते के बाद", "१५ मार्च २०२४ को"]:
        assert [t.text for t in tokenizer.tokenize(text)] == text.split(), text


def test_bare_weekday_resolves_next():
    # a bare weekday names its next strictly-future occurrence, a day-wide span
    ahead = (4 - ANCHOR.weekday()) % 7 or 7          # 4 == Friday (शुक्रवार)
    s = (ANCHOR + timedelta(days=ahead)).date()
    e = s + timedelta(days=1)
    sp = span("शुक्रवार")
    assert (sp.start.year, sp.start.month, sp.start.day) == (s.year, s.month, s.day)
    assert (sp.end.year, sp.end.month, sp.end.day) == (e.year, e.month, e.day)


PAIRS = [
    ("आज", "today"),
    ("तीन दिन पहले", "3 days ago"), ("एक दिन पहले", "1 day ago"),
    ("दस दिन पहले", "10 days ago"),
    ("तीन दिन बाद", "in 3 days"), ("एक दिन बाद", "in 1 day"),
    ("दो हफ़्ते बाद", "in 2 weeks"), ("दो सप्ताह बाद", "in 2 weeks"),
    ("दो महीने बाद", "in 2 months"), ("पाँच साल बाद", "in 5 years"),
    ("पंद्रह मिनट बाद", "in 15 minutes"), ("दस घंटे बाद", "in 10 hours"),
    ("अगले सोमवार को", "next monday"), ("अगले शुक्रवार को", "next friday"),
    ("पिछले मंगलवार को", "last tuesday"),
    ("अगला सप्ताह", "next week"), ("पिछला महीना", "last month"),
    ("अगला वर्ष", "next year"),
    ("15:30", "15:30"), ("09:30", "09:30"), ("00:00", "00:00"),
    ("१५:३०", "15:30"), ("००:००", "00:00"),
    ("मध्यरात्रि", "midnight"),
    ("2019", "2019"), ("1918", "1918"), ("2017-06-30", "2017-06-30"),
    ("दो हज़ार चौबीस", "2024"), ("उन्नीस सौ नब्बे", "1990"),
    ("गर्मी", "summer"), ("अगली सर्दी", "next winter"),
    ("5 जुलाई", "july 5"), ("15 मार्च 2024", "15 march 2024"),
    ("१५ मार्च २०२४", "15 march 2024"),
    ("इक्कीसवीं सदी", "21st century"),
    ("सप्ताहांत", "weekend"),
]


@pytest.mark.parametrize("hi_text,en_text", PAIRS)
def test_span_parity(hi_text, en_text):
    hi = extract_timespan(hi_text, "hi", ANCHOR)
    en = extract_timespan(en_text, "en", ANCHOR)
    assert hi is not None, f"hi {hi_text!r} did not parse"
    assert en is not None, f"en {en_text!r} did not parse"
    assert hi[0].start == en[0].start and hi[0].end == en[0].end, (hi_text, en_text)
