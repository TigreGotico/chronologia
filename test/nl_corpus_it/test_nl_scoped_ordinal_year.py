# -*- coding: utf-8 -*-
"""An explicit trailing year reached through the Italian "del/di" connector
must bind to the Nth-weekday-of-month construction -- it may never be silently
dropped in favour of the anchor year.  The shared scoped_ordinal order now
consumes the connector before the year; the no-year reading is pinned to prove
the fix stays positional.
"""
from ._corpus import AstroDate, parse, start_end


def test_scoped_ordinal_binds_trailing_connector_year():
    # 2nd Tuesday of November 2019 = 2019-11-12.
    assert start_end('il secondo martedì di novembre del 2019') == (
        AstroDate(2019, 11, 12), AstroDate(2019, 11, 13))
    assert parse('il secondo martedì di novembre del 2019')[1] == ''


def test_scoped_ordinal_no_year_stays_anchor_year():
    assert start_end('il secondo martedì di novembre') == (
        AstroDate(2017, 11, 14), AstroDate(2017, 11, 15))
