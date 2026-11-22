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
