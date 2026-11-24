"""A dotted clock beside a clock word reads as the colon clock.

"a las 8.30" is "a las 8:30": the lone hour takes the next twelve-hour
reading (ruling 17), so at Friday 2026-09-25 12:00 the evening half is
20:30 and 20:15 the same day.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ISSUE = "https://github.com/TigreGotico/chronologia/issues/1047"
ANCHOR = datetime(2026, 9, 25, 12, 0)
H830 = datetime(2026, 9, 25, 20, 30)
H815 = datetime(2026, 9, 25, 20, 15)


@pytest.mark.xfail(strict=True, reason=ISSUE)
@pytest.mark.parametrize("lang,text,instant", [
    ("es", "a las 8.30", H830),
    ("es", "a las 8.15", H815),
    ("pt", "às 8.30", H830),
    ("pt", "às 8.15", H815),
    ("de", "um 8.15", H815),
    ("de", "um 8.15 Uhr", H815),
    ("it", "alle 8.30", H830),
    ("fr", "à 8.15", H815),
    ("nl", "om 8.30", H830),
    ("ca", "a les 8.30", H830),
    ("gl", "ás 8.30", H830),
])
def test_a_dotted_clock_beside_its_clock_word(lang, text, instant):
    found = extract_timespan(text, lang, ANCHOR)
    assert found.span.start.datetime() == instant
