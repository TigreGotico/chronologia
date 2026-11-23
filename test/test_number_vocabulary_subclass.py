"""Each Romance number fold reads its own language's spelled numbers: "tomorrow"
and "three days" resolve in all seven languages below."""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_duration, extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)

# (lang, "tomorrow", "three days")
ROWS = [
    ("oc", "deman", "tres jorns"),
    ("pt", "amanhã", "três dias"),
    ("es", "mañana", "tres días"),
    ("fr", "demain", "trois jours"),
    ("it", "domani", "tre giorni"),
    ("ca", "demà", "tres dies"),
    ("gl", "mañá", "tres días"),
]


@pytest.mark.parametrize("lang,tomorrow,three_days", ROWS)
def test_romance_language_reads_after_the_subclass(lang, tomorrow, three_days):
    span = extract_timespan(tomorrow, lang, anchor=ANCHOR).span
    assert (span.start.year, span.start.month, span.start.day) == (2017, 6, 28)
    assert extract_duration(three_days, lang).duration == timedelta(days=3)
