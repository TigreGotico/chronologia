# -*- coding: utf-8 -*-
"""ru and pl: the half hour with "пол" and "w pół" written apart.

The half hour before the ordinal hour is the hour minus 30 minutes, and the
hour takes the next twelve-hour reading after the anchor.  Anchor: Tuesday
2017-06-27 13:04, so 7:30 is 19:30 the same day, 10:30 is 22:30, 12:30 is
00:30 the next day, and with a morning word 8:30 and 7:30 are the next
morning.  The solid forms "в полвосьмого" and "wpół do ósmej" give 19:30 on
dev.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ISSUE = "https://github.com/TigreGotico/chronologia/issues/1335"
ANCHOR = datetime(2017, 6, 27, 13, 4)


@pytest.mark.xfail(strict=True, reason=ISSUE)
@pytest.mark.parametrize("lang,text,instant", [
    ("ru", "в пол восьмого", datetime(2017, 6, 27, 19, 30)),
    ("ru", "пол восьмого", datetime(2017, 6, 27, 19, 30)),
    ("ru", "в пол-одиннадцатого", datetime(2017, 6, 27, 22, 30)),
    ("ru", "в пол одиннадцатого", datetime(2017, 6, 27, 22, 30)),
    ("ru", "в пол девятого утра", datetime(2017, 6, 28, 8, 30)),
    ("pl", "w pół do ósmej", datetime(2017, 6, 27, 19, 30)),
    ("pl", "w pół do pierwszej", datetime(2017, 6, 28, 0, 30)),
    ("pl", "w pół do ósmej rano", datetime(2017, 6, 28, 7, 30)),
    ("pl", "spotkajmy się w pół do ósmej wieczorem",
     datetime(2017, 6, 27, 19, 30)),
])
def test_the_half_hour_written_apart(lang, text, instant):
    found = extract_timespan(text, lang, ANCHOR)
    assert found.span.start.datetime() == instant
