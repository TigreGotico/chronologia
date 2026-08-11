# -*- coding: utf-8 -*-
"""R113: the Turkish day-word 'günü' ("on <weekday>-day") trailing a bare
weekday must be CONSUMED as part of the weekday reference, not stranded in
the remainder -- and must not block the date+time merge chain.

'X günü' is the ordinary way to say "on X" for a weekday in Turkish
("cuma günü" == "on Friday"), exactly as 'X-i' (year_word) and 'X-i'
(month_word/quarter_word) are consumed elsewhere in this locale family (see
hu/fi ``marker_year_word``/``marker_month_word``, tr's own
``marker_quarter_word``).  Before the fix 'günü' survived into the
remainder and, sitting between the weekday and a following clock time,
broke the adjacency check that composes "weekday + clock" into one span
(see ``timespan._compose``).

Expected values are independent arithmetic against this corpus's fixed
anchor (Wednesday, 2026-07-15 12:00), matching the formula already used by
``test_bare_weekday.py`` -- NOT read back from the parser.
"""
from datetime import timedelta

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import ANCHOR, parse, span

WEEKDAY_IDX = {
    "pazartesi": 0,
    "salı": 1,
    "çarşamba": 2,
    "perşembe": 3,
    "cuma": 4,
    "cumartesi": 5,
    "pazar": 6,
}


def _bare_expected(idx):
    """Next strictly-future occurrence of weekday *idx* -- same formula as
    ``test_bare_weekday.py``."""
    base = ANCHOR.replace(hour=0, minute=0, second=0, microsecond=0)
    ahead = (idx - base.weekday()) % 7 or 7
    s = base + timedelta(days=ahead)
    e = s + timedelta(days=1)
    return AstroDate(s.year, s.month, s.day), AstroDate(e.year, e.month, e.day)


# -- 'WEEKDAY günü' reads exactly like the bare weekday, with a CLEAN
#    remainder (no stranded 'günü'). ------------------------------------
CLEAN_CASES = [
    ("cuma günü", "cuma"),
    ("pazartesi günü", "pazartesi"),
    ("çarşamba günü", "çarşamba"),
    ("cumartesi günü", "cumartesi"),
]


@pytest.mark.parametrize("text,weekday", CLEAN_CASES)
def test_weekday_gunu_matches_bare_weekday(text, weekday):
    idx = WEEKDAY_IDX[weekday]
    expected_start, expected_end = _bare_expected(idx)
    r = parse(text)
    assert r is not None, f"{text!r} did not parse"
    sp, remainder = r
    assert (sp.start, sp.end) == (expected_start, expected_end)
    assert remainder.strip() == "", f"{text!r} left a stranded remainder: {remainder!r}"


# -- 'WEEKDAY günü saat H'da' merges into weekday at H:00, same as the
#    günü-less control 'WEEKDAY saat H'da' (only DATE-ONLY spans are the
#    defect; both must produce the SAME merged hour). -------------------
def test_weekday_gunu_saat_merges_to_time():
    idx = WEEKDAY_IDX["cuma"]
    expected_start, _ = _bare_expected(idx)

    with_gunu = parse("cuma günü saat 10'da")
    without_gunu = parse("cuma saat 10'da")
    assert with_gunu is not None and without_gunu is not None

    sp_with, _ = with_gunu
    sp_without, _ = without_gunu

    # both merge to the SAME Friday 10:00 -- 'günü' must not change the
    # resolved time, and must not block the merge that already works
    # without it.
    assert sp_with.start.year == expected_start.year
    assert sp_with.start.month == expected_start.month
    assert sp_with.start.day == expected_start.day
    assert sp_with.start.hour == 10
    assert (sp_with.start.year, sp_with.start.month, sp_with.start.day, sp_with.start.hour) \
        == (sp_without.start.year, sp_without.start.month, sp_without.start.day, sp_without.start.hour)


# -- controls: unaffected by the fix -------------------------------------
def test_bare_cuma_control_unchanged():
    idx = WEEKDAY_IDX["cuma"]
    expected_start, expected_end = _bare_expected(idx)
    r = parse("cuma")
    assert r is not None
    sp, remainder = r
    assert (sp.start, sp.end) == (expected_start, expected_end)
    assert remainder.strip() == ""


def test_cuma_saat_control_still_merges():
    idx = WEEKDAY_IDX["cuma"]
    expected_start, _ = _bare_expected(idx)
    r = parse("cuma saat 10")
    assert r is not None
    sp, remainder = r
    assert (sp.start.year, sp.start.month, sp.start.day) == \
           (expected_start.year, expected_start.month, expected_start.day)
    assert sp.start.hour == 10
    assert remainder.strip() == ""


# -- date + weekday-label + günü: the label-fold in ``timespan._compose``
#    folds the weekday match's tokens (now including 'günü', since it is
#    part of the same weekday_ref match) into the date label, so 'günü'
#    must not strand here either. ----------------------------------------
def test_full_date_weekday_gunu_label_clean():
    r = parse("13 Haziran Cumartesi günü")
    assert r is not None
    sp, remainder = r
    assert (sp.start.month, sp.start.day) == (6, 13)
    assert remainder.strip() == ""
