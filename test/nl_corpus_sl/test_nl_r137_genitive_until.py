# -*- coding: utf-8 -*-
"""R137 -- Slovene holiday names after ``do`` ("until") take the
grammatically OBLIGATORY genitive: "do božiča" (not the ungrammatical
nominative "do božič"). A native speaker never says the nominative form here,
so the parser must accept the genitive as the primary spoken surface.

Anchor 2017-06-27, 13:04 (shared corpus anchor). Expected dates are the same
independently-derived holiday dates used elsewhere in this corpus:
Christmas 2017-12-25, Easter 2018-04-01, New Year 2018-01-01.
"""
from datetime import datetime
import pytest
from chronologia.extract import extract_recurrence
from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)

_UNTIL_GENITIVE = [
    ('vsak ponedeljek do božiča', 'FREQ=WEEKLY;UNTIL=20171225T000000;BYDAY=MO'),
    ('vsak ponedeljek do velike noči', 'FREQ=WEEKLY;UNTIL=20180401T000000;BYDAY=MO'),
    ('vsak ponedeljek do novega leta', 'FREQ=WEEKLY;UNTIL=20180101T000000;BYDAY=MO'),
]


@pytest.mark.parametrize("text,rrule", _UNTIL_GENITIVE)
def test_recurrence_until_genitive_holiday(text, rrule):
    got = extract_recurrence(text, "sl", anchor=ANCHOR)
    assert got is not None, f"{text!r} did not parse"
    assert got[0].to_string() == rrule
    assert got[1] == "", f"holiday stranded in remainder: {got[1]!r}"


def test_recurrence_until_nominative_still_works():
    # the ungrammatical nominative must keep working -- no regression.
    got = extract_recurrence('vsak ponedeljek do božič', "sl", anchor=ANCHOR)
    assert got is not None
    assert got[0].to_string() == 'FREQ=WEEKLY;UNTIL=20171225T000000;BYDAY=MO'
    assert got[1] == ""


def test_timespan_do_bozica_genitive():
    r = extract_timespan('do božiča', "sl", anchor=ANCHOR)
    assert r is not None, "'do božiča' did not parse"
    span = r[0]
    assert span.start.year == 2017 and span.start.month == 6 and span.start.day == 27
    assert span.end.year == 2017 and span.end.month == 12 and span.end.day == 26
    assert r[1] == ""
