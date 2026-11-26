"""Marwari cases with the shared English semantic-parity block."""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)
DEV = str.maketrans("0123456789", "०१२३४५६७८९")

PAIRS = [
    ("आज", "today"),
    ("1 दिन में", "in 1 day"), ("3 दिनां में", "in 3 days"),
    ("10 दिनां में", "in 10 days"), ("2 दिन पछै", "in 2 days"),
    ("३ दिनां में", "in 3 days"), ("१० दिनां पछै", "in 10 days"),
    ("2 बरस पछै", "in 2 years"), ("5 बरसां में", "in 5 years"),
    ("15:30", "15:30"), ("09:30", "09:30"), ("00:00", "00:00"),
    ("१५:३०", "15:30"), ("००:००", "00:00"),
    ("4:30 सांम", "4:30 pm"), ("9:15 सबेरे", "9:15 am"),
    ("2019", "2019"), ("1918", "1918"), ("2017-06-30", "2017-06-30"),
    ("5 जुलाई", "july 5"), ("15 मार्च 2024", "15 march 2024"),
    ("१५ मार्च २०२४", "15 march 2024"), ("1 जनवरी", "january 1"),
    ("20 सितम्बर", "september 20"), ("31 दिसंबर", "december 31"),
    ("अगस्त", "august"), ("अक्टूबर 2020", "october 2020"),
]


@pytest.mark.parametrize("mwr_text,en_text", PAIRS)
def test_span_parity(mwr_text, en_text):
    mwr = extract_timespan(mwr_text, "mwr", ANCHOR)
    en = extract_timespan(en_text, "en", ANCHOR)
    assert mwr is not None, mwr_text
    assert en is not None, en_text
    assert (mwr[0].start, mwr[0].end) == (en[0].start, en[0].end), mwr_text


@pytest.mark.parametrize("n", range(1, 31))
@pytest.mark.parametrize("digits", ["ascii", "devanagari"])
def test_day_offset_by_arithmetic(n, digits):
    text = f"{n} दिनां पछै"
    if digits == "devanagari":
        text = text.translate(DEV)
    s = extract_timespan(text, "mwr", ANCHOR).span.start
    gold = ANCHOR + timedelta(days=n)
    assert (s.year, s.month, s.day, s.hour, s.minute) == \
        (gold.year, gold.month, gold.day, gold.hour, gold.minute)


MONTHS = ["जनवरी", "फरवरी", "मार्च", "अप्रैल", "मई", "जून", "जुलाई",
          "अगस्त", "सितम्बर", "अक्टूबर", "नवंबर", "दिसंबर"]


@pytest.mark.parametrize("month", range(1, 13))
def test_day_month_year(month):
    s = extract_timespan(f"12 {MONTHS[month - 1]} 2019", "mwr",
                         ANCHOR).span.start
    assert (s.year, s.month, s.day) == (2019, month, 12)


@pytest.mark.parametrize("text", [
    "", "   ", "qwerty zxcvb", "म्हैं घरै जासूं", "काल", "परसूं",
])
def test_no_date(text):
    assert extract_timespan(text, "mwr", ANCHOR) is None
