# -*- coding: utf-8 -*-
"""Open-ended ranges (az): Azerbaijani frames the closed end with the
**postposed** "qədər" ("<date>('ə) qədər" = until <date>), so the engine's
postposed open-range scan expresses it natively (open start bounded below by
"now"). The dative suffix on the date noun is a downstream morphology concern;
the engine reads the bare head."""
from datetime import datetime
from chronologia.extract import extract_timespan
from chronologia.astrodate import AstroDate

A = datetime(2017, 6, 27, 13, 4)
NOW = AstroDate.from_datetime(A)


def _span(text):
    r = extract_timespan(text, "az", anchor=A)
    assert r is not None, f"{text!r} did not parse"
    return r[0]


def test_qeder_open_start_year():
    s = _span("2020 qədər")
    assert s.start == NOW and s.end == AstroDate(2021, 1, 1)


def test_bare_qeder_is_not_a_range():
    assert extract_timespan("qədər", "az", anchor=A) is None
