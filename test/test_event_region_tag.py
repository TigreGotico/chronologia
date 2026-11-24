"""extract_event resolves a region tag to its base locale."""
from datetime import datetime

import pytest

from chronologia.events import extract_event

_ANCHOR = datetime(2026, 11, 19, 10, 0)


@pytest.mark.parametrize("text,region,base", [
    ("reunião de duas horas em março", "pt-BR", "pt"),
    ("meeting for two hours in march", "en-US", "en"),
])
def test_region_tag_reads_like_base_code(text, region, base):
    expected = extract_event(text, base, _ANCHOR)
    assert expected is not None
    assert extract_event(text, region, _ANCHOR) == expected
