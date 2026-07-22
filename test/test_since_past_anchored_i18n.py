# -*- coding: utf-8 -*-
"""'since X' is past-anchored in every locale carrying a since marker.

The open-range resolver pins a "since" endpoint to the most recent occurrence
at-or-before the anchor -- so a near-past date is never flung a year forward by
prefer_future.  The logic is shared engine code (a construction property, not a
per-language fact); these hand-derived cases prove the roll-out reaches the
Romance/Germanic locales named in the mission.

Anchor: Wednesday 2026-07-22.  "since the 6th of July" therefore starts on
2026-07-06 (this year, already passed) and runs up to the anchor instant.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate

ANCHOR = datetime(2026, 7, 22)
EXPECTED_START = AstroDate(2026, 7, 6)
EXPECTED_END = AstroDate(2026, 7, 22)


@pytest.mark.parametrize("lang,text", [
    ("de", "seit dem 6. juli"),
    ("fr", "depuis le 6 juillet"),
    ("pt", "desde 6 de julho"),
    ("es", "desde el 6 de julio"),
    ("it", "dal 6 luglio"),
    ("nl", "sinds 6 juli"),
])
def test_since_is_past_anchored(lang, text):
    r = extract_timespan(text, lang, ANCHOR)
    assert r is not None, f"{lang}: {text!r} did not parse"
    span = r[0]
    assert span.start == EXPECTED_START, f"{lang}: {text!r}"
    assert span.end == EXPECTED_END, f"{lang}: {text!r}"
