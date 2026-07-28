# -*- coding: utf-8 -*-
"""An explicit trailing year reached through the Catalan "de" connector must
bind to the Nth-weekday-of-month construction -- it may never be silently
dropped in favour of the anchor year.

A native ca reviewer found the silent-wrong: "el tercer dilluns de març de
2020" landed the third Monday in the anchor year (2017) and stranded "de 2020"
in the remainder.  The no-year reading is pinned to prove the fix stays
positional.
"""
from ._corpus import AstroDate, parse, start_end


def test_scoped_ordinal_binds_trailing_connector_year():
    # 3rd Monday of March 2020 = 2020-03-16 (Mondays: 2, 9, 16).
    assert start_end('el tercer dilluns de març de 2020') == (
        AstroDate(2020, 3, 16), AstroDate(2020, 3, 17))
    assert parse('el tercer dilluns de març de 2020')[1] == ''


def test_scoped_ordinal_no_year_stays_anchor_year():
    # byte-identical historic reading: anchor-year (2017) March.
    assert start_end('el tercer dilluns de març') == (
        AstroDate(2017, 3, 20), AstroDate(2017, 3, 21))
