# -*- coding: utf-8 -*-
"""An explicit trailing year reached through the Romance "de" connector must
bind to the Nth-weekday-of-month construction -- it may never be silently
dropped in favour of the anchor year.

A native es reviewer found the silent-wrong: "el segundo martes de noviembre de
2019" landed the second Tuesday in the anchor year (2017) and stranded "de
2019" in the remainder.  English's bare-year form ("... of November 2019")
already binds (#323); the Romance connector form did not, because the shared
scoped_ordinal order carried a bare "YEAR?" that could not consume the trailing
"de".  The no-year reading is pinned to prove the fix stays positional.
"""
from ._corpus import AstroDate, parse, start_end


def test_scoped_ordinal_binds_trailing_connector_year():
    # 2nd Tuesday of November 2019 = 2019-11-12 (Tuesdays: 5, 12).
    assert start_end('el segundo martes de noviembre de 2019') == (
        AstroDate(2019, 11, 12), AstroDate(2019, 11, 13))
    assert parse('el segundo martes de noviembre de 2019')[1] == ''


def test_scoped_ordinal_no_year_stays_anchor_year():
    # byte-identical historic reading: anchor-year (2017) November.
    assert start_end('el segundo martes de noviembre') == (
        AstroDate(2017, 11, 14), AstroDate(2017, 11, 15))
