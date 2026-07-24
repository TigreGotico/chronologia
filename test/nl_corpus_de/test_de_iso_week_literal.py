"""The ISO-8601 week designator in German: "2024-W10", "2024-W10-1".

``YYYY-Www`` (ISO 8601 §4.4.4.2) is a numeric international standard, not a
German surface: it carries no language-specific vocabulary, so it must read
identically in every locale.  This is the non-English proof of that -- the
expected dates come from the stdlib ``date.fromisocalendar``, never from the
parser.
"""
from datetime import date, timedelta

import pytest

from chronologia.astrodate import AstroDate
from ._corpus import start_end, nomatch


@pytest.mark.parametrize("text,iy,iw", [
    ("2024-W10", 2024, 10),
    ("2024-w10", 2024, 10),
    ("2020-W53", 2020, 53),
    ("2026-W1", 2026, 1),        # unpadded week number, as often written
])
def test_iso_week_literal_de(text, iy, iw):
    monday = date.fromisocalendar(iy, iw, 1)
    nxt = monday + timedelta(days=7)
    s, e = start_end(text)
    assert s == AstroDate(monday.year, monday.month, monday.day)
    assert e == AstroDate(nxt.year, nxt.month, nxt.day)


def test_iso_week_date_literal_de():
    s, e = start_end("2024-W10-1")
    assert (s, e) == (AstroDate(2024, 3, 4), AstroDate(2024, 3, 5))


@pytest.mark.parametrize("text", ["2024-W53", "2024-W00", "2024-W10-8",
                                  "2026-W0"])
def test_out_of_range_refuses_de(text):
    nomatch(text)
