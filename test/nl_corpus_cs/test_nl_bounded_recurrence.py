# -*- coding: utf-8 -*-
"""Bounded recurrence (cs): base rules plus an until-date (-> UNTIL) via the
open-range marker or a for-duration (-> COUNT). UNTIL resolved against a fixed
anchor. The for-marker 'po dobu' is multiword, so COUNT is xfailed (ro precedent)."""
from datetime import datetime
import pytest
from chronologia.extract import extract_recurrence

ANCHOR = datetime(2017, 6, 27, 13, 4)
_CASES = [('každý pátek', 'FREQ=WEEKLY;BYDAY=FR'), ('každé pondělí', 'FREQ=WEEKLY;BYDAY=MO'), ('každý týden', 'FREQ=WEEKLY'), ('každý měsíc', 'FREQ=MONTHLY'), ('každý pátek do června', 'FREQ=WEEKLY;UNTIL=20170601T000000;BYDAY=FR'), ('každé pondělí do prosince', 'FREQ=WEEKLY;UNTIL=20171201T000000;BYDAY=MO')]


@pytest.mark.parametrize("text,rrule", _CASES)
def test_bounded_recurrence(text, rrule):
    got = extract_recurrence(text, "cs", anchor=ANCHOR)
    assert got is not None, f"{text!r} did not parse"
    assert got[0].to_string() == rrule
    assert got[1] == ""


def test_count_recurrence():
    got = extract_recurrence("každé pondělí po dobu 6 týdnů", "cs", anchor=ANCHOR)
    assert got is not None and got[0].to_string() == "FREQ=WEEKLY;COUNT=6;BYDAY=MO"
    assert got[1] == ""

@pytest.mark.parametrize("text", ['pátek', '5. června'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, "cs", anchor=ANCHOR) is None
