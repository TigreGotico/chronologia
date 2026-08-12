# -*- coding: utf-8 -*-
"""R139: 'öncə' is a standard Azerbaijani past-direction (ago) postposition,
same register as 'əvvəl'/'qabaq' (all mean "before/ago"). It was missing from
marker_past.voc, so '3 gün öncə' silently failed to parse (returned None)
while the semantically identical '3 gün əvvəl' worked.

Independent arithmetic against this corpus's anchor (2017-06-27 13:04):
"N gün öncə/əvvəl" = N days before the anchor, day-wide span at anchor's
truncated-to-midnight day minus N.

Also covers: 'dünən' (yesterday) is untouched by this fix -- 'dün' (Turkish,
NOT standard Azerbaijani; az yesterday is 'dünən') is deliberately NOT added
to the az vocabulary. Bare 'saat HH:MM' clock parsing is unaffected by this
change (pre-existing 'saat' consumption behavior, out of scope for R139)."""
from datetime import timedelta

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import ANCHOR, nomatch, parse, span


def _expected_days_ago(n):
    # "N gün əvvəl/öncə/qabaq" preserves the anchor's time-of-day (it is a
    # relative-duration offset, not a day-naming construct) and yields a
    # 1-day-wide span starting at that offset instant.
    s = ANCHOR - timedelta(days=n)
    e = s + timedelta(days=1)
    return (AstroDate(s.year, s.month, s.day, s.hour, s.minute, s.second, s.microsecond),
            AstroDate(e.year, e.month, e.day, e.hour, e.minute, e.second, e.microsecond))


AGO_FORMS = [
    "3 gün öncə",
    "3 gün əvvəl",
    "3 gün qabaq",
]


@pytest.mark.parametrize("text", AGO_FORMS)
def test_days_ago_all_synonyms_agree(text):
    sp = span(text)
    assert (sp.start, sp.end) == _expected_days_ago(3)


def test_once_alone_2_weeks_ago_parity_with_evvel():
    """'2 həftə öncə' == '2 həftə əvvəl' (both -> 14 days before anchor)."""
    a = span("2 həftə öncə")
    b = span("2 həftə əvvəl")
    assert (a.start, a.end) == (b.start, b.end)


def test_dunen_yesterday_unaffected():
    """'dünən' (correct az "yesterday") still resolves to anchor-1 day,
    unchanged by the öncə fix."""
    base = ANCHOR.replace(hour=0, minute=0, second=0, microsecond=0)
    s = base - timedelta(days=1)
    e = s + timedelta(days=1)
    sp = span("dünən")
    assert (sp.start, sp.end) == (AstroDate(s.year, s.month, s.day),
                                   AstroDate(e.year, e.month, e.day))


def test_dun_turkish_not_added_to_az_vocab():
    """'dün' is Turkish, not standard Azerbaijani ('dünən' is az for
    yesterday) -- it must NOT resolve as a yesterday marker in az. Bare
    'dün' alone (no other temporal content) should not parse."""
    nomatch("dün")


def test_bare_saat_clock_form_parses_hour():
    """Bare 'saat HH:MM' resolves the clock time; 'saat' consumption is a
    pre-existing az behavior independent of this fix (out of scope)."""
    r = parse("saat 15:00")
    assert r is not None
    sp = r[0]
    assert sp.start.hour == 15 and sp.start.minute == 0
