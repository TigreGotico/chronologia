"""extract_candidates ranks extract_timespan's answer first for a weekday
whose time has passed on that weekday.

"tuesday at 10am" said on a Tuesday at 13:04 is the next Tuesday at 10:00,
because the 10:00 on the anchor's own day has passed.  The candidate list
must hold that same reading on top, so the two public APIs agree.

Anchor Tuesday 2017-06-27 13:04; the next Tuesday is 2017-07-04.
"""
from datetime import datetime

import pytest

from chronologia import extract_candidates, extract_timespan
from chronologia.astrodate import AstroDate

ANCHOR = datetime(2017, 6, 27, 13, 4)
NEXT_TUESDAY_10 = AstroDate(2017, 7, 4, 10, 0)


@pytest.mark.parametrize("lang,text", [
    ("en", "tuesday at 10am"),
    ("pt", "terça às 10h"),
    ("fr", "mardi à 10h"),
    ("cs", "úterý v 10 hodin"),
])
def test_top_candidate_is_the_timespan_answer(lang, text):
    span, rest = extract_timespan(text, lang, ANCHOR)
    assert span.start == NEXT_TUESDAY_10
    top = extract_candidates(text, lang, ANCHOR)[0]
    assert (top.span.start, top.remainder) == (span.start, rest)
