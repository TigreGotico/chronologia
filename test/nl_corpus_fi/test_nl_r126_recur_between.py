# -*- coding: utf-8 -*-
"""R126 -- the RECURRENCE clock-range binder never learned the postposed
"between X and Y" construction PR #677 (R118) added to the single-span
engine (:func:`~chronologia.extract.timespan._extract_range`).

Finnish frames a closed clock range with its "between" word placed AFTER
the pair ("klo 9 ja 17 välillä" == "at 9 and 17 between"), unlike English
"between A and B" which leads the pair.  Before this fix
:func:`~chronologia.extract.nseries._apply_clock_range` only recognised a
LEADING "between"/"from" marker; the clause fell through to
:func:`~chronologia.extract.nseries._apply_clock`'s generic clock reader,
which grounded ``BYHOUR`` off the first clock-shaped match ("9", correct by
accident here) but left the connector, right endpoint and trailing marker
STRANDED in the remainder: "joka päivä klo 9 ja 17 välillä" ->
``BYHOUR=9``, remainder "ja 17 välillä" -- the range's own meaning
(an interval, not a single pin) silently lost even though the hour happened
to match.

The fix mirrors #677's own convention: ``BYHOUR`` pins to the range's
left/start endpoint, the whole clause is consumed (empty remainder), and
the marker vocab (``marker_between_post.voc``) is reused unchanged from the
single-span fix.
"""
from datetime import datetime

import pytest

from chronologia.extract import extract_recurrence

LANG = "fi"
_A = datetime(2026, 8, 12, 12, 0)


@pytest.mark.parametrize("text,rrule,remainder", [
    # the defect as reported.
    ("joka päivä klo 9 ja 17 välillä", "FREQ=DAILY;BYHOUR=9", ""),
    # "välisenä aikana" is the multi-word synonym marker_between_post.voc
    # also carries.
    ("joka päivä klo 9 ja 17 välisenä aikana", "FREQ=DAILY;BYHOUR=9", ""),
    # swapped order: BYHOUR pins to whichever number comes FIRST in text.
    ("joka päivä klo 17 ja 9 välillä", "FREQ=DAILY;BYHOUR=17", ""),
    # weekday-scoped recurrence: composes with an explicit BYDAY base.
    ("joka maanantai klo 9 ja 17 välillä", "FREQ=WEEKLY;BYDAY=MO;BYHOUR=9", ""),
    # embedded in a longer sentence.
    ("Kokous on joka päivä klo 9 ja 17 välillä huomenna.",
     "FREQ=DAILY;BYHOUR=9", "Kokous on huomenna"),
])
def test_postposed_between_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG, anchor=_A)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


# -- controls: constructions this fix must NOT disturb -----------------

@pytest.mark.parametrize("text,rrule,remainder", [
    ("joka päivä", "FREQ=DAILY", ""),
    ("joka maanantai", "FREQ=WEEKLY;BYDAY=MO", ""),
])
def test_controls_unaffected(text, rrule, remainder):
    got = extract_recurrence(text, LANG, anchor=_A)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


def test_bare_numbers_without_klo_stay_stranded():
    # no "klo" unit word anywhere in the clause -- bare numbers carry no
    # clock semantics on their own (mirrors hu's "óra" requirement), so the
    # trailing "välillä" marker alone is not enough to license the range:
    # it must decline rather than fabricate an hour, leaving the whole
    # clause stranded in the remainder.
    got = extract_recurrence("joka päivä 9 ja 17 välillä", LANG, anchor=_A)
    assert got is not None
    rec, remainder = got
    assert rec.to_string() == "FREQ=DAILY"
    assert "9" in remainder and "17" in remainder and "välillä" in remainder
