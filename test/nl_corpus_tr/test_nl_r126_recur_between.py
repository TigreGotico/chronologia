# -*- coding: utf-8 -*-
"""R126 -- the RECURRENCE clock-range binder never learned the postposed
"between X and Y" construction PR #677 (R118) added to the single-span
engine (:func:`~chronologia.extract.timespan._extract_range`).

Turkish frames a closed clock range with its "between" word placed AFTER
the pair ("saat 9 ile 17 arasında" == "at 9 and 17 between"), unlike English
"between A and B" which leads the pair.  Before this fix
:func:`~chronologia.extract.nseries._apply_clock_range` only recognised a
LEADING "between"/"from" marker; the clause fell through to
:func:`~chronologia.extract.nseries._apply_clock`'s generic clock reader,
which grounded ``BYHOUR`` off the first clock-shaped match ("9") and left
the connector, right endpoint and trailing marker STRANDED in the
remainder -- correct hour by accident, wrong shape ("her gün saat 9 ile 17
arasında" -> remainder "ile 17 arasında" rather than "").

The fix mirrors #677's own convention: ``BYHOUR`` pins to the range's
left/start endpoint, the whole clause is consumed, and the marker vocab
(``marker_between_post.voc``) is reused unchanged from the single-span fix.
"""
from datetime import datetime

import pytest

from chronologia.extract import extract_recurrence

LANG = "tr"
_A = datetime(2026, 8, 12, 12, 0)


@pytest.mark.parametrize("text,rrule,remainder", [
    # the defect as reported.
    ("her gün saat 9 ile 17 arasında", "FREQ=DAILY;BYHOUR=9", ""),
    # "arası" is the short synonym marker_between_post.voc also carries.
    ("her gün saat 9 ile 17 arası", "FREQ=DAILY;BYHOUR=9", ""),
    # swapped order: BYHOUR pins to whichever number comes FIRST in text.
    ("her gün saat 17 ile 9 arasında", "FREQ=DAILY;BYHOUR=17", ""),
    # weekday-scoped recurrence: composes with an explicit BYDAY base.
    ("her pazartesi saat 9 ile 17 arasında",
     "FREQ=WEEKLY;BYDAY=MO;BYHOUR=9", ""),
    # embedded in a longer sentence.
    ("Toplantı her gün saat 9 ile 17 arasında olacak.",
     "FREQ=DAILY;BYHOUR=9", "Toplantı olacak"),
])
def test_postposed_between_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG, anchor=_A)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


# -- controls: constructions this fix must NOT disturb -----------------

@pytest.mark.parametrize("text,rrule,remainder", [
    ("her gün", "FREQ=DAILY", ""),
    ("her pazartesi", "FREQ=WEEKLY;BYDAY=MO", ""),
])
def test_controls_unaffected(text, rrule, remainder):
    got = extract_recurrence(text, LANG, anchor=_A)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


def test_bare_ile_without_arasinda_stays_stranded():
    # no trailing "arasında"/"arası" -- the postposed range must not fire;
    # bare numbers with no "saat" unit and no marker carry no clock
    # semantics at all, so the clause stays in the remainder.
    got = extract_recurrence("her gün 9 ile 17", LANG, anchor=_A)
    assert got is not None
    rec, remainder = got
    assert rec.to_string() == "FREQ=DAILY"
    assert "9" in remainder and "17" in remainder
