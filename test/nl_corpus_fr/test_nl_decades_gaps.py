"""French decade references and known engine gaps.

The decade family ("les années 1980" = 1980-1989) needs a plural/ordinal
marker the French surface does not carry, so "les années 1980" currently
reads as the single year 1980 -- documented here so the limitation stays
visible.  The scoped-century form ("le 20e siècle") is the working
100-year span and lives in the ranges corpus.
"""
from datetime import timedelta

import pytest

from ._corpus import span, start, AstroDate


def test_decade_reads_as_single_year():
    # engine gap: no plural marker, so "les années 1980" is the year 1980,
    # not the 1980-1989 decade.  Documented, not asserted-as-decade.
    assert start("les années 1980") == AstroDate(1980, 1, 1)
    assert span("les années 1980").width == timedelta(days=366)  # 1980 leap


def test_bare_spelled_clock():
    # dev's SCOPE_UNIT hour-exclusion lets a bare spelled clock ("trois
    # heures") read as 3 o'clock instead of colliding with the scoped
    # "Nth hour" ordinal reading.
    assert start("trois heures") == AstroDate(2017, 6, 28, 3, 0)
