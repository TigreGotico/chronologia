# -*- coding: utf-8 -*-
"""Second-pass sweep: an explicit date with a postposed, comma-set weekday
label -- ``D Bulan YYYY, Weekday`` -- an idiomatic Indonesian dateline style
(e.g. news datelines, invitations: "15 Maret 2021, Senin").

Not previously exercised anywhere in the id corpus: the existing full-date
sweeps (``test_sweep_full_dates.py``, ``test_nl_calendar.py``) never carry a
trailing weekday, and ``test_bare_weekday.py`` only covers the bare/hari-
classifier weekday forms. Gold is the named calendar day, exactly as for a
plain ``D Bulan YYYY``; the weekday word is real and independently checked
against the date via ``date.weekday()`` (not a random label) so this is
genuine idiomatic Indonesian, not a nonsense probe.

Following the same convention as the other oracle sweeps in this directory
(``test_sweep_full_dates.py`` et al.), only ``start``/``end`` are asserted --
not full consumption of the trailing weekday token.

Years (2021, 2023, 2025) avoid every year already swept elsewhere for full
dates/month-year in this corpus (2019, 2020, 1945, 1990, 2000, 2010, 2027,
2030). Anchor: mission Tuesday 2017-06-27 13:04.

KNOWN BUG (not swept, see ``test_id_bugs_xfail.py``-style handling below):
the mirror PREFIXED form ``Weekday, D Bulan YYYY`` mis-resolves -- the parser
folds only the bare weekday and strands the whole dated tail -- pinned here
as a single strict xfail with the correct gold.
"""
from datetime import date, datetime, timedelta

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import start_end, span

A = datetime(2017, 6, 27, 13, 4)

MON = ("Januari Februari Maret April Mei Juni Juli Agustus September "
       "Oktober November Desember").split()
WD = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]

_YEARS = (2021, 2023, 2025)


def _cases():
    out = []
    for y in _YEARS:
        for m in range(1, 13):
            d = 15
            wd = WD[date(y, m, d).weekday()]
            text = f"{d} {MON[m - 1]} {y}, {wd}"
            nxt = date(y, m, d) + timedelta(days=1)
            out.append((text, AstroDate(y, m, d),
                        AstroDate(nxt.year, nxt.month, nxt.day)))
    return out


@pytest.mark.parametrize("text,s,e", _cases())
def test_date_with_postposed_weekday(text, s, e):
    assert start_end(text, A) == (s, e)


@pytest.mark.xfail(strict=True, reason="id: prefixed 'Weekday, D Bulan YYYY' "
                    "folds only the bare weekday (next Selasa on/after the "
                    "anchor) and strands the whole dated tail as residue, "
                    "instead of resolving to the named calendar day")
def test_prefixed_weekday_comma_date_should_use_full_date():
    s = span("Selasa, 5 Januari 2021", A)
    assert s.start == AstroDate(2021, 1, 5)
