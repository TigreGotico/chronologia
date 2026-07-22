# -*- coding: utf-8 -*-
"""RTL / mixed-direction tokenisation.

Hebrew is right-to-left but the tokenizer is script-agnostic: a digit run
embedded in RTL text is one token.  These assert that dates and offsets
embedded mid-sentence in RTL prose resolve exactly as they do standalone,
and that the gershayim-abbreviated weekend survives the split."""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, AstroDate, ad, start, start_end


def test_date_embedded_in_sentence():
    s, e = start_end("נסעתי ב-15 בינואר 2020 לתל אביב")
    assert s == AstroDate(2020, 1, 15) and e == AstroDate(2020, 1, 16)


def test_offset_embedded_in_sentence():
    s = start("נתראה בעוד 3 ימים אם ירצה השם")
    assert s == ad(ANCHOR + timedelta(days=3))


def test_clock_embedded_in_sentence():
    s = start("הפגישה בשעה 15:30 במשרד")
    assert s == ad(ANCHOR.replace(hour=15, minute=30, second=0,
                                  microsecond=0))


@pytest.mark.parametrize("abbrev,full", [
    ("סופ״ש", "סוף שבוע"),   # gershayim-split abbreviation == the full form
])
def test_gershayim_weekend_equals_full(abbrev, full):
    assert start_end(abbrev) == start_end(full)
