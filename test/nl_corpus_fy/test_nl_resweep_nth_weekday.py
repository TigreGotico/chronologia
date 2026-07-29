# -*- coding: utf-8 -*-
"""Second-pass sweep (fy): "the Nth WEEKDAY of MONTH [YEAR]" -- the
scoped_ordinal WEEKDAY nesting, not previously covered for this locale.
Gold computed independently with ``calendar.Calendar`` (Monday=0), never by
pinning the parser's own output. Fresh years not used elsewhere in the fy
corpus.
"""
from datetime import timedelta

import pytest

from ._corpus import AstroDate, span, start, nomatch


@pytest.mark.parametrize("text,ymd", [
    ('de earste moandei fan jannewaris 2022', (2022, 1, 3)),
    ('de twadde tiisdei fan maart 2023', (2023, 3, 14)),
    ('de tredde woansdei fan maaie 2025', (2025, 5, 21)),
    ('de fjirde tongersdei fan septimber 2027', (2027, 9, 23)),
    ('de earste freed fan novimber 2024', (2024, 11, 1)),
    ('de earste snein fan desimber 2026', (2026, 12, 6)),
    ('de twadde sneon fan july 2029', (2029, 7, 14)),
])
def test_nth_weekday_of_named_month(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


def test_nth_weekday_of_current_month():
    # anchor 2017-06-27 (Tue): the first Monday of June 2017 is June 5.
    assert start('de earste moandei fan de moanne') == AstroDate(2017, 6, 5)


def test_nth_weekday_of_relative_month():
    # "next month" from the June anchor is July 2017; first Monday = July 3.
    assert start('de earste moandei fan folgjende moanne') == AstroDate(2017, 7, 3)
    # "last month" is May 2017; first Monday = May 1.
    assert start('de earste moandei fan ôfrûne moanne') == AstroDate(2017, 5, 1)


@pytest.mark.parametrize("text", ['de 5e moandei fan febrewaris 2021'])
def test_no_fifth_occurrence_in_short_month(text):
    # February 2021 has only four Mondays -- no 5th weekday to resolve.
    nomatch(text)


_LIMITATIONS = [
    pytest.param(
        'de lêste freed fan de moanne',
        marks=pytest.mark.xfail(
            reason="'lêste WEEKDAY' is claimed by the weekday_ref order "
                   "(REL_MARKER WEEKDAY -> 'last Friday' relative to anchor, "
                   "2017-06-23) before the scoped_ordinal 'ordlast WEEKDAY of "
                   "SCOPE_UNIT' order can nest it against the month; 'fan de "
                   "moanne' is stranded in the remainder. Correct gold is the "
                   "last Friday OF THE MONTH (2017-06-30), which the engine "
                   "does not currently produce for this phrasing.",
            strict=True)),
    pytest.param(
        'de lêste freed fan april 2022',
        marks=pytest.mark.xfail(
            reason="same weekday_ref-first limitation with an explicit named "
                   "month: 'lêste freed' resolves relative to the anchor "
                   "(2017-06-23) instead of nesting against April 2022, whose "
                   "correct last Friday is 2022-04-29.",
            strict=True)),
]


_LIMITATION_GOLD = {
    'de lêste freed fan de moanne': AstroDate(2017, 6, 30),
    'de lêste freed fan april 2022': AstroDate(2022, 4, 29),
}


@pytest.mark.parametrize("text", _LIMITATIONS)
def test_last_weekday_of_month_documented_limitation(text):
    # CORRECT gold: the last WEEKDAY of the named/scoped month. The engine
    # currently binds 'lêste WEEKDAY' as a plain weekday_ref instead (see
    # reason above), so this fails until that ordering is fixed.
    assert start(text) == _LIMITATION_GOLD[text]
