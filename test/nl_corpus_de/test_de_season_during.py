"""German "während" (during) governs the genitive on a named season
("während des Sommers") the way it already governs it on a named month
("während des Januars" reads through ``calendar_date``'s shared "during
MONTH" order) -- ``season_ref`` shipped no matching "during SEASON" order,
so the genitive noun phrase stranded.  Boundaries are computed independently
from the calendar-quarter convention the parser's own docstring documents
(summer = June-August).
"""
from datetime import datetime

import pytest

from chronologia.astrodate import AstroDate
from ._corpus import start_end, nomatch

ANCHOR = datetime(2026, 6, 15, 12, 0)


@pytest.mark.parametrize("text", [
    "während des Sommers",
    "während dem Sommer",
])
def test_during_summer(text):
    s, e = start_end(text, anchor=ANCHOR)
    assert s == AstroDate(2026, 6, 1)
    assert e == AstroDate(2026, 9, 1)


def test_during_unattested_winter_genitive_still_refuses():
    # only "Sommers" is an attested genitive surface; "Winters" was never
    # added, so the genitive winter phrase must refuse rather than silently
    # binding the wrong noun form.
    nomatch("während des Winters", anchor=ANCHOR)
