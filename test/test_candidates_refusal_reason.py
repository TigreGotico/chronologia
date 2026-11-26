"""In raise mode extract_candidates refuses a phrase with the same reason as
extract_timespan.

"do 25.º dia útil de junho a 30 de fevereiro" names two impossible dates.
Both functions read the range first, and its left end fails first: no June
has more than 22 weekdays, so no June has a 25th business day.
Anchor 2026-03-15, so the June is the next one.
"""
import calendar
from datetime import datetime

import pytest

from chronologia import extract_candidates, extract_timespan
from chronologia.extract.impossible import ImpossibleDateError

ANCHOR = datetime(2026, 3, 15, 9, 0)
REASON = "June has no 25th business day"


def test_june_2026_has_22_weekdays():
    weekdays = sum(calendar.weekday(2026, 6, day) < 5 for day in range(1, 31))
    assert weekdays == 22


@pytest.mark.parametrize("lang,text", [
    ("pt", "do 25.º dia útil de junho a 30 de fevereiro"),
    ("es", "del 25.º día hábil de junio al 30 de febrero"),
])
def test_candidates_refuse_with_the_timespan_reason(lang, text):
    reasons = []
    for extract in (extract_timespan, extract_candidates):
        with pytest.raises(ImpossibleDateError) as err:
            extract(text, lang, anchor=ANCHOR, impossible="raise")
        reasons.append(err.value.reason)
    assert reasons == [REASON, REASON]
