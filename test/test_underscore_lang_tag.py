"""A language tag written with an underscore reads like the hyphenated tag."""
from datetime import datetime

import pytest

from chronologia import extract_event, extract_timespan

_ANCHOR = datetime(2026, 11, 19, 10, 0)

_CASES = [
    ("pt_BR", "pt-BR", "reunião de duas horas em março"),
    ("PT_br", "pt-br", "amanhã às 15:00"),
    ("en_US", "en-US", "meeting for two hours in march"),
    ("en_GB", "en-GB", "tomorrow at 3pm"),
]


@pytest.mark.parametrize("underscored,hyphenated,text", _CASES)
@pytest.mark.parametrize("extract", [extract_timespan, extract_event])
def test_underscore_tag_reads_like_hyphen_tag(extract, underscored, hyphenated, text):
    expected = extract(text, hyphenated, _ANCHOR)
    assert expected is not None
    assert extract(text, underscored, _ANCHOR) == expected


@pytest.mark.parametrize("underscored,hyphenated,text,summary", [
    ("pt_BR", "pt-BR", "almoço para amanhã", "almoço"),
    ("es_ES", "es-ES", "cena para el viernes", "cena"),
    ("en_GB", "en-GB", "the meeting on friday to", "meeting"),
])
def test_underscore_tag_cleans_the_event_summary(underscored, hyphenated, text, summary):
    assert extract_event(text, hyphenated, _ANCHOR).summary == summary
    assert extract_event(text, underscored, _ANCHOR).summary == summary


@pytest.mark.parametrize("tag", ["en-GB ", "en_GB ", " en-GB"])
@pytest.mark.parametrize("extract", [extract_timespan, extract_event])
def test_padded_tag_keeps_its_region(extract, tag):
    # en-GB reads 03/04/2026 as the 3rd of April, the US default as the 4th of March
    assert extract("03/04/2026", tag, _ANCHOR).span.start.month == 4
