# -*- coding: utf-8 -*-
"""An English clock next to "tonight" reads the night of the anchor day.

"at 8 tonight" is 20:00 of the anchor day.  The small hours 1 to 5 and
twelve fall after the midnight that ends that day, unless the night is
already running when the speaker talks.  With a named day, the night is the
night of that day.  Every expected instant is calendar arithmetic on the
anchor.  Issue: https://github.com/TigreGotico/chronologia/issues/1002
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

TUE = datetime(2017, 6, 27, 13, 4)
FRI_0000 = datetime(2026, 10, 23, 0, 0, 30)
FRI_1500 = datetime(2026, 10, 23, 15, 0)
FRI_2359 = datetime(2026, 10, 23, 23, 59)
SAT_MIDNIGHT = datetime(2026, 10, 24, 0, 0)

ISSUE = "https://github.com/TigreGotico/chronologia/issues/1002"

# lang, text, anchor, expected instant, expected remainder
CASES = [
    ("en", "at 8 tonight", TUE, datetime(2017, 6, 27, 20, 0), ""),
    ("en", "eight tonight", TUE, datetime(2017, 6, 27, 20, 0), ""),
    ("en", "at 8 tonight", datetime(2017, 6, 27, 23, 59),
     datetime(2017, 6, 27, 20, 0), ""),
    ("en", "at 11 tonight", FRI_1500, datetime(2026, 10, 23, 23, 0), ""),
    ("en", "remind me at 9 tonight", TUE, datetime(2017, 6, 27, 21, 0),
     "remind me"),
    # small hours: the next calendar day, unless the night already runs
    ("en", "at 2 tonight", TUE, datetime(2017, 6, 28, 2, 0), ""),
    ("en", "at 2 tonight", datetime(2017, 6, 27, 1, 0),
     datetime(2017, 6, 27, 2, 0), ""),
    # twelve is the midnight that ends the day
    ("en", "at 12 tonight", FRI_0000, SAT_MIDNIGHT, ""),
    ("en", "at 12 tonight", FRI_1500, SAT_MIDNIGHT, ""),
    ("en", "at 12 tonight", FRI_2359, SAT_MIDNIGHT, ""),
    ("en", "at 12:30 tonight", FRI_1500, datetime(2026, 10, 24, 0, 30), ""),
    ("en", "at twelve thirty tonight", FRI_1500,
     datetime(2026, 10, 24, 0, 30), ""),
    ("en", "tonight at 12", FRI_1500, SAT_MIDNIGHT, ""),
    ("en", "tonight at twelve thirty", FRI_2359,
     datetime(2026, 10, 24, 0, 30), ""),
    # a named day: the midnight that ends that day
    ("en", "at 12 tonight today", FRI_1500, SAT_MIDNIGHT, ""),
    ("en", "at 12 tonight on friday", FRI_1500, SAT_MIDNIGHT, ""),
    ("en", "at 12 tonight tomorrow", FRI_1500,
     datetime(2026, 10, 25, 0, 0), ""),
    # a part of the day after the named day
    ("en", "at 7:03 tomorrow evening", TUE, datetime(2017, 6, 28, 19, 3), ""),
    # controls that already read right
    ("en", "tonight at 8", TUE, datetime(2017, 6, 27, 20, 0), ""),
    ("en", "at 8 pm", TUE, datetime(2017, 6, 27, 20, 0), ""),
    ("en", "at 8 this evening", TUE, datetime(2017, 6, 27, 20, 0), ""),
    ("es", "a las 12 esta noche", TUE, datetime(2017, 6, 28, 0, 0), ""),
]

# rows of the issue that still read wrong
OPEN = [
    ("en", "at 12 tonight in 2 days", FRI_1500,
     datetime(2026, 10, 26, 0, 0), ""),
    ("de", "setze den frisörtermin auf halb neun am abend",
     datetime(2017, 6, 27), datetime(2017, 6, 27, 20, 30),
     "setze den frisörtermin auf"),
    ("de", "wie ist das wetter am mittwoch um 7 uhr 30 am abend",
     datetime(2017, 6, 27), datetime(2017, 6, 28, 19, 30),
     "wie ist das wetter"),
    ("de", "wie ist das wetter am mittwoch um 11 uhr mittags",
     datetime(2017, 6, 27), datetime(2017, 6, 28, 11, 0),
     "wie ist das wetter"),
    ("es", "tarde a las 4:30", datetime(2026, 10, 17, 12, 0),
     datetime(2026, 10, 17, 16, 30), ""),
    ("it", "stasera 10", datetime(2026, 10, 17, 12, 0),
     datetime(2026, 10, 17, 22, 0), ""),
    ("fy", "om 9 oere moarns", TUE, datetime(2017, 6, 28, 9, 0), ""),
    ("nl", "om halfacht vanavond", datetime(2026, 10, 17, 12, 0),
     datetime(2026, 10, 17, 19, 30), ""),
]


def _read(lang, text, anchor):
    got = extract_timespan(text, lang, anchor)
    assert got is not None, text
    return got.span.start.datetime(), " ".join(got.remainder.split())


@pytest.mark.parametrize("lang,text,anchor,expected,rest", CASES)
def test_clock_with_tonight(lang, text, anchor, expected, rest):
    assert _read(lang, text, anchor) == (expected, rest)


@pytest.mark.xfail(strict=True, reason=ISSUE)
@pytest.mark.parametrize("lang,text,anchor,expected,rest", OPEN)
def test_open_rows(lang, text, anchor, expected, rest):
    assert _read(lang, text, anchor) == (expected, rest)
