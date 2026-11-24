"""A plural part of the day before a clock is a recurrence rule.

The en adverb "mornings" means every morning (Wiktionary, "mornings",
Adverb), so "mornings at 8" is a daily rule at 08:00 and "weekday mornings at
8" the same rule on Monday to Friday, as the control "every weekday morning at
8" reads.  Anchor: Friday 2026-09-25 12:00.
"""
from datetime import datetime

import pytest

from chronologia import extract_recurrence

ISSUE = "https://github.com/TigreGotico/chronologia/issues/1052"
ANCHOR = datetime(2026, 9, 25, 12, 0)
DAILY = "FREQ=DAILY;BYHOUR=8"
WEEKDAYS = "FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR;BYHOUR=8"


@pytest.mark.xfail(strict=True, reason=ISSUE)
@pytest.mark.parametrize("lang,text,rule", [
    ("en", "weekday mornings at 8", WEEKDAYS),
    ("en", "mornings at 8", DAILY),
    ("en", "every morning at 8", DAILY),
    ("pt", "todas as manhãs às 8", DAILY),
    ("pt", "nas manhãs às 8", DAILY),
])
def test_a_daypart_before_a_clock_is_a_rule(lang, text, rule):
    assert extract_recurrence(text, lang, ANCHOR).recurrence == rule
