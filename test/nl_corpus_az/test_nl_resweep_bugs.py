# -*- coding: utf-8 -*-
"""Second-pass sweep: confirmed degradations found while probing new
Azerbaijani constructions for the resweep.  Each case is a single, pinned
strict xfail with the CORRECT gold (never a guessed/wrong one) and a reason
naming the actual observed (wrong) parser output.  These are documented bugs,
not a sweep to pad numbers with.
"""
import pytest

from chronologia.astrodate import AstroDate

from ._corpus import parse


@pytest.mark.xfail(strict=True, reason=(
    "Locative-suffixed spelled clock hour ('saat <ədəd>-də') fails to parse "
    "at all -- returns None. The bare form 'saat üç' correctly resolves to "
    "the next 03:00 after the anchor (2017-06-28T03:00); the '-də' locative "
    "suffix on the spelled number breaks the match entirely."))
def test_locative_spelled_clock_hour():
    r = parse("saat üçdə")
    assert r is not None
    s = r[0].start
    assert (s.year, s.month, s.day, s.hour, s.minute) == (2017, 6, 28, 3, 0)


@pytest.mark.xfail(strict=True, reason=(
    "Azerbaijani secular fixed holidays from holiday_data/az.tab (e.g. "
    "'Qadınlar günü' = 8 March) are not resolved to their tabulated date "
    "when named with an explicit year: 'qadınlar günü 2020' degrades to the "
    "whole calendar year 2020-01-01..2021-01-01 instead of the single day "
    "2020-03-08..2020-03-09. The bare form (no year) does not parse at all."))
def test_fixed_secular_holiday_with_year():
    r = parse("qadınlar günü 2020")
    assert r is not None
    s, en = r[0].start, r[0].end
    assert s == AstroDate(2020, 3, 8)
    assert en == AstroDate(2020, 3, 9)


@pytest.mark.xfail(strict=True, reason=(
    "The 'ayının N-dən M-dək' day-range phrasing ('<month>ın N-dən M-dək') "
    "degrades to the whole named month instead of the literal N..M day "
    "range: 'iyun ayının 5-dən 10-dək' resolves to 2017-06-01..2017-07-01 "
    "instead of 2017-06-05..2017-06-11. The equivalent digit-range form "
    "'5-10 iyun 2020' (covered in test_nl_resweep_day_ranges.py) parses "
    "correctly, so the bug is specific to this postposed-ordinal phrasing."))
def test_ayinin_day_range_phrasing():
    r = parse("iyun ayının 5-dən 10-dək")
    assert r is not None
    s, en = r[0].start, r[0].end
    assert s == AstroDate(2017, 6, 5)
    assert en == AstroDate(2017, 6, 11)
